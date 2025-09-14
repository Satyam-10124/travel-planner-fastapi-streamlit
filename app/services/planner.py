from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
import math

from sqlmodel import Session, select
from ..models import Place, ItineraryItem
from .google_places import google_places_service

DURATIONS_MIN = {
    "sights": 120,
    "museum": 180,
    "nature": 120,
    "shopping": 90,
    "food": 60,
    "nightlife": 120,
    "activity": 90,
}

PACE_MULT = {"relaxed": 1.2, "standard": 1.0, "packed": 0.8}
MAX_PER_DAY = {"relaxed": 5, "standard": 6, "packed": 8}

def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    R = 6371.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))

@dataclass
class PlanParams:
    destination: str
    start_date: date
    end_date: date
    interests: List[str]
    daily_start: time = time(9, 0)
    daily_end: time = time(19, 0)
    lunch_at: Optional[time] = time(13, 0)
    pace: str = "standard"  # relaxed|standard|packed
    budget_level: Optional[int] = None  # 0-4
    origin: Optional[str] = None
    name: Optional[str] = None
    use_google: bool = False
    country_mode: bool = False

def _pick_places(session: Session, city: str, interests: List[str], count: int, budget_level: Optional[int]) -> List[Place]:
    """Pick places from DB with case-insensitive city matching and filters.
    If DB has none, return an empty list and let caller decide on fallback."""
    q = select(Place)
    places = session.exec(q).all()
    # Case-insensitive city match and allow simple comma suffixes (e.g., "Paris, France")
    city_norm = (city or "").split(",")[0].strip().lower()
    places = [p for p in places if (p.city or "").strip().lower() == city_norm]
    if interests:
        places = [p for p in places if p.category in interests]
    if budget_level is not None:
        places = [p for p in places if p.price_level <= budget_level]
    places.sort(key=lambda p: (-p.rating, p.price_level, p.name))
    return places[: max(count, 0)]

def _nearest_neighbor_order(points: List[Place]) -> List[Place]:
    if not points:
        return points
    unvisited = points.copy()
    route = [unvisited.pop(0)]
    while unvisited:
        last = route[-1]
        unvisited.sort(key=lambda p: haversine_km((last.lat, last.lng), (p.lat, p.lng)))
        route.append(unvisited.pop(0))
    return route

def _duration_for(category: str, pace: str) -> timedelta:
    base = DURATIONS_MIN.get(category, DURATIONS_MIN["activity"])
    mult = PACE_MULT.get(pace, 1.0)
    return timedelta(minutes=int(base * mult))

def _slot_next(curr: time, delta: timedelta) -> time:
    dt = datetime.combine(date.today(), curr) + delta
    return dt.time()

def generate_plan(session: Session, params: PlanParams) -> Dict[str, List[ItineraryItem]]:
    days = (params.end_date - params.start_date).days + 1
    if days <= 0:
        raise ValueError("end_date must be on/after start_date")
    total_needed = days * MAX_PER_DAY.get(params.pace, 6)
    pool = _pick_places(session, params.destination, params.interests, total_needed, params.budget_level)
    # If nothing matched with filters, relax filters gradually
    if not pool:
        pool = _pick_places(session, params.destination, [], total_needed, None)
    if not pool:
        # Loose city substring match ignoring filters
        all_places = session.exec(select(Place)).all()
        city_norm = (params.destination or "").split(",")[0].strip().lower()
        loose = [p for p in all_places if city_norm in (p.city or "").strip().lower()]
        loose.sort(key=lambda p: (-p.rating, p.price_level, p.name))
        pool = loose[: max(total_needed, 0)]
    # Fallback: fetch from Google Places if DB has none, then persist lightweight entries
    if not pool or params.use_google or params.country_mode:
        # Try to fetch a small set per category of interest to diversify
        fetched: List[Place] = []
        try:
            import asyncio
            async def fetch_all():
                out = []
                if not params.interests:
                    params.interests = ["sights", "museum", "food", "nature", "shopping"]
                radius = 150000 if params.country_mode else 50000
                tasks = [google_places_service.search_places(params.destination, cat, radius=radius) for cat in params.interests]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for r in results:
                    if isinstance(r, list):
                        out.extend(r)
                return out
            # Run event loop (works both inside/outside existing loop)
            try:
                fetched_raw = asyncio.run(fetch_all())
            except RuntimeError:
                # If already in an event loop, create a new one
                loop = asyncio.new_event_loop()
                fetched_raw = loop.run_until_complete(fetch_all())
                loop.close()
            # Deduplicate by name and map to Place rows, then persist
            seen = set()
            for pr in fetched_raw:
                key = (pr.get("name"), pr.get("lat"), pr.get("lng"))
                if key in seen:
                    continue
                seen.add(key)
                p = Place(
                    city=params.destination.split(",")[0].strip(),
                    name=pr.get("name", ""),
                    category=pr.get("category", "activity"),
                    lat=float(pr.get("lat", 0.0)),
                    lng=float(pr.get("lng", 0.0)),
                    rating=float(pr.get("rating", 4.5)),
                    price_level=int(pr.get("price_level", 2)),
                    description=pr.get("description", "")
                )
                session.add(p)
                fetched.append(p)
            if fetched:
                session.commit()
                pool = _pick_places(session, params.destination, params.interests, total_needed, params.budget_level)
        except Exception:
            # Silent fallback; keep pool empty if fetch fails
            pass
    per_day = MAX_PER_DAY.get(params.pace, 6)
    schedule: Dict[str, List[ItineraryItem]] = {}
    idx = 0
    for di in range(days):
        d = params.start_date + timedelta(days=di)
        day_key = d.isoformat()
        todays = pool[idx : idx + per_day]
        idx += len(todays)
        todays = _nearest_neighbor_order(todays)
        t = params.daily_start
        day_items: List[ItineraryItem] = []
        lunch_added = False
        for p in todays:
            dur = _duration_for(p.category, params.pace)
            end_t = _slot_next(t, dur)
            if params.lunch_at and not lunch_added and t <= params.lunch_at <= end_t:
                lunch_end = _slot_next(params.lunch_at, timedelta(minutes=60))
                day_items.append(ItineraryItem(
                    trip_id=0, day=d, title="Lunch Break", type="food",
                    location_name="TBD", start_time=params.lunch_at, end_time=lunch_end
                ))
                t = lunch_end
                end_t = _slot_next(t, dur)
                lunch_added = True
            if end_t > params.daily_end:
                break
            day_items.append(ItineraryItem(
                trip_id=0, day=d, title=p.name, type=p.category,
                location_name=p.name, lat=p.lat, lng=p.lng,
                start_time=t, end_time=end_t, notes=p.description
            ))
            t = end_t
        schedule[day_key] = day_items
    return schedule

from datetime import date, time
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session
from ..db import get_session
from ..models import Trip, ItineraryItem, ItineraryItemRead, TripRead
from ..services.planner import PlanParams, generate_plan

router = APIRouter()

class PlanRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    interests: List[str] = Field(default_factory=lambda: ["sights","museum","food","nature","shopping"])
    daily_start: time = time(9,0)
    daily_end: time = time(19,0)
    lunch_at: Optional[time] = time(13,0)
    pace: str = Field(default="standard", pattern=r"^(relaxed|standard|packed)$")
    budget_level: Optional[int] = Field(default=None, ge=0, le=4)
    origin: Optional[str] = None
    name: Optional[str] = None
    travelers: int = 1
    dry_run: bool = True
    use_google: bool = False
    country_mode: bool = False

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v, info):
        if hasattr(info, 'data') and "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on/after start_date")
        return v

@router.post("/generate")
def plan_generate(req: PlanRequest, session: Session = Depends(get_session)):
    try:
        params = PlanParams(
            destination=req.destination,
            start_date=req.start_date,
            end_date=req.end_date,
            interests=req.interests,
            daily_start=req.daily_start,
            daily_end=req.daily_end,
            lunch_at=req.lunch_at,
            pace=req.pace,
            budget_level=req.budget_level,
            origin=req.origin,
            name=req.name or f"{req.destination} Trip",
            use_google=req.use_google,
            country_mode=req.country_mode,
        )
        schedule = generate_plan(session, params)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")

    if req.dry_run:
        preview_days = {}
        for day, items in schedule.items():
            preview_days[day] = [
                ItineraryItem(
                    trip_id=0,
                    day=i.day, title=i.title, type=i.type, location_name=i.location_name,
                    lat=i.lat, lng=i.lng, start_time=i.start_time, end_time=i.end_time, notes=i.notes
                ).model_dump() | {"id": 0} for i in items
            ]
        return {"preview": {"destination": req.destination, "days": preview_days}}

    trip = Trip(
        name=params.name, origin=params.origin, destination=params.destination,
        start_date=params.start_date, end_date=params.end_date, travelers=req.travelers
    )
    session.add(trip)
    session.commit()
    session.refresh(trip)

    out_items = []
    for day, items in schedule.items():
        for i in items:
            itm = ItineraryItem(
                trip_id=trip.id, day=i.day, title=i.title, type=i.type, location_name=i.location_name,
                lat=i.lat, lng=i.lng, start_time=i.start_time, end_time=i.end_time, notes=i.notes
            )
            session.add(itm)
            session.commit()
            session.refresh(itm)
            out_items.append(itm)

    return {
        "trip": TripRead(**trip.model_dump()),
        "items": [ItineraryItemRead(**i.model_dump()) for i in out_items]
    }

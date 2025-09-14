from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from ..db import get_session
from ..models import Trip, TripRead, TripUpdate, ItineraryItem, ItineraryItemRead, ItineraryItemUpdate

router = APIRouter()

@router.post("", response_model=TripRead, status_code=201)
def create_trip(trip: Trip, session: Session = Depends(get_session)):
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@router.get("", response_model=List[TripRead])
def list_trips(session: Session = Depends(get_session)):
    return session.exec(select(Trip).order_by(Trip.start_date)).all()

@router.get("/{trip_id}", response_model=TripRead)
def get_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(404, "Trip not found")
    return trip

@router.patch("/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, patch: TripUpdate, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(404, "Trip not found")
    for k, v in patch.model_dump(exclude_unset=True).items():
        setattr(trip, k, v)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@router.delete("/{trip_id}", status_code=204)
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        return
    session.delete(trip)
    session.commit()

@router.post("/{trip_id}/items", response_model=ItineraryItemRead, status_code=201)
def add_item(trip_id: int, item: ItineraryItem, session: Session = Depends(get_session)):
    if item.trip_id != trip_id:
        item.trip_id = trip_id
    if not session.get(Trip, trip_id):
        raise HTTPException(404, "Trip not found")
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/{trip_id}/items", response_model=List[ItineraryItemRead])
def list_items(trip_id: int, session: Session = Depends(get_session)):
    if not session.get(Trip, trip_id):
        raise HTTPException(404, "Trip not found")
    return session.exec(select(ItineraryItem).where(ItineraryItem.trip_id == trip_id).order_by(ItineraryItem.day, ItineraryItem.start_time)).all()

@router.patch("/{trip_id}/items/{item_id}", response_model=ItineraryItemRead)
def update_item(trip_id: int, item_id: int, patch: ItineraryItemUpdate, session: Session = Depends(get_session)):
    item = session.get(ItineraryItem, item_id)
    if not item or item.trip_id != trip_id:
        raise HTTPException(404, "Item not found")
    for k, v in patch.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.delete("/{trip_id}/items/{item_id}", status_code=204)
def delete_item(trip_id: int, item_id: int, session: Session = Depends(get_session)):
    item = session.get(ItineraryItem, item_id)
    if not item or item.trip_id != trip_id:
        return
    session.delete(item)
    session.commit()

@router.get("/{trip_id}/plan")
def get_plan(trip_id: int, session: Session = Depends(get_session)):
    if not session.get(Trip, trip_id):
        raise HTTPException(404, "Trip not found")
    items = session.exec(select(ItineraryItem).where(ItineraryItem.trip_id == trip_id)).all()
    plan: Dict[str, list] = {}
    for it in items:
        key = (it.day.isoformat() if it.day else "unscheduled")
        plan.setdefault(key, []).append(it)
    for day in plan:
        plan[day].sort(key=lambda x: (x.start_time or None, x.end_time or None, x.title))
    out = {day: [i.model_dump() | {"id": i.id} for i in lst] for day, lst in plan.items()}
    return {"trip_id": trip_id, "days": out}

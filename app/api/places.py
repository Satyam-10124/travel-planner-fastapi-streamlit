from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from ..db import get_session
from ..models import Place, PlaceRead

router = APIRouter()

@router.post("", response_model=PlaceRead, status_code=201)
def add_place(place: Place, session: Session = Depends(get_session)):
    session.add(place)
    session.commit()
    session.refresh(place)
    return place

@router.get("", response_model=List[PlaceRead])
def list_places(city: Optional[str] = None, category: Optional[str] = None, session: Session = Depends(get_session)):
    q = select(Place)
    if city:
        q = q.where(Place.city == city)
    if category:
        q = q.where(Place.category == category)
    return session.exec(q).all()

@router.get("/search", response_model=List[PlaceRead])
def search_places(q: str = Query(..., min_length=2), city: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(Place)
    if city:
        stmt = stmt.where(Place.city == city)
    results = session.exec(stmt).all()
    q_lower = q.lower()
    return [p for p in results if q_lower in p.name.lower() or q_lower in p.description.lower() or q_lower in p.category.lower()]

@router.get("/{place_id}", response_model=PlaceRead)
def get_place(place_id: int, session: Session = Depends(get_session)):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place

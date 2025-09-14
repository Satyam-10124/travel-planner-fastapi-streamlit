from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from ..db import get_session
from ..models import Place, PlaceRead

router = APIRouter()

@router.get("/{city}", response_model=List[PlaceRead])
def recommended_for_city(city: str, session: Session = Depends(get_session)):
    places = session.exec(select(Place).where(Place.city == city)).all()
    if not places:
        raise HTTPException(404, "No recommendations yet for this city")
    places.sort(key=lambda p: (-p.rating, p.price_level, p.name))
    return places[:20]

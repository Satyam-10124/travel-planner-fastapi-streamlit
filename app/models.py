from datetime import date, time
from typing import Optional
from sqlmodel import SQLModel, Field

class TripBase(SQLModel):
    name: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    travelers: int = 1
    notes: Optional[str] = None

class Trip(TripBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class TripRead(TripBase):
    id: int

class TripUpdate(SQLModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    travelers: Optional[int] = None
    notes: Optional[str] = None

class ItineraryItemBase(SQLModel):
    trip_id: int = Field(foreign_key="trip.id")
    day: Optional[date] = None
    title: str
    type: str = "activity"
    location_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

class ItineraryItem(ItineraryItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ItineraryItemRead(ItineraryItemBase):
    id: int

class ItineraryItemUpdate(SQLModel):
    day: Optional[date] = None
    title: Optional[str] = None
    type: Optional[str] = None
    location_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

class PlaceBase(SQLModel):
    city: str
    name: str
    category: str
    lat: float
    lng: float
    rating: float = 4.5
    price_level: int = 2
    description: str = ""

class Place(PlaceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class PlaceRead(PlaceBase):
    id: int

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db import create_db_and_tables
from .api.trips import router as trips_router
from .api.places import router as places_router
from .api.recommendations import router as rec_router
from .api.plan import router as plan_router

app = FastAPI(title="Travel Planner API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Travel Planner API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(trips_router, prefix="/trips", tags=["Trips"])
app.include_router(places_router, prefix="/places", tags=["Places"])
app.include_router(rec_router, prefix="/Recommendations")
app.include_router(plan_router, prefix="/plan", tags=["Planner"])

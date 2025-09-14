#!/usr/bin/env python3
"""
Automated API smoke tester for Travel Planner API

- Reads BASE_URL from env (default to user's production backend)
- Exercises key endpoints with sample payloads
- Prints concise pass/fail and response snippets

Usage:
  python scripts/test_endpoints.py

Environment:
  BASE_URL   # e.g., https://trip-skshi-production.up.railway.app
"""
import os
import sys
import time
import json
from datetime import date, timedelta

import requests

BASE_URL = os.getenv("BASE_URL", "https://trip-skshi-production.up.railway.app")
TIMEOUT = 20


def hr(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def pretty(obj):
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)[:1200]
    except Exception:
        return str(obj)[:1200]


def get(url, **kwargs):
    return requests.get(url, timeout=TIMEOUT, **kwargs)


def post(url, **kwargs):
    return requests.post(url, timeout=TIMEOUT, **kwargs)


def patch(url, **kwargs):
    return requests.patch(url, timeout=TIMEOUT, **kwargs)


def delete(url, **kwargs):
    return requests.delete(url, timeout=TIMEOUT, **kwargs)


def main():
    print(f"BASE_URL = {BASE_URL}")

    # 1) Health
    hr("Health check")
    r = get(f"{BASE_URL}/health")
    print(r.status_code, pretty(r.json() if r.ok else r.text))
    if not r.ok:
        print("Health check failed, exiting.")
        sys.exit(1)

    # 2) Root
    hr("Root")
    r = get(f"{BASE_URL}/")
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 3) List Trips (initial)
    hr("List trips (initial)")
    r = get(f"{BASE_URL}/trips")
    trips = r.json() if r.ok else []
    print(r.status_code, f"Count: {len(trips)}")

    # 4) Create Trip
    hr("Create trip")
    payload = {
        "name": "API Test Trip",
        "origin": "New York",
        "destination": "Paris",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=3)),
        "budget": 1200,
        "travelers": 2,
        "notes": "smoke test"
    }
    r = post(f"{BASE_URL}/trips", json=payload)
    print(r.status_code, pretty(r.json() if r.ok else r.text))
    r.raise_for_status()
    trip = r.json()
    trip_id = trip["id"]

    # 5) Get Trip
    hr("Get trip")
    r = get(f"{BASE_URL}/trips/{trip_id}")
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 6) Update Trip (patch)
    hr("Update trip (patch)")
    r = patch(f"{BASE_URL}/trips/{trip_id}", json={"destination": "Paris, France"})
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 7) Add Item to Trip
    hr("Add itinerary item")
    item_payload = {
        "trip_id": trip_id,
        "day": str(date.today()),
        "title": "Louvre Museum",
        "type": "sights",
        "location_name": "Musée du Louvre",
        "lat": 48.8606,
        "lng": 2.3376,
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "cost": 20,
        "notes": "Buy tickets online"
    }
    r = post(f"{BASE_URL}/trips/{trip_id}/items", json=item_payload)
    print(r.status_code, pretty(r.json() if r.ok else r.text))
    r.raise_for_status()
    item = r.json()
    item_id = item["id"]

    # 8) List Items
    hr("List items")
    r = get(f"{BASE_URL}/trips/{trip_id}/items")
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 9) Update Item
    hr("Update item")
    r = patch(f"{BASE_URL}/trips/{trip_id}/items/{item_id}", json={"notes": "Arrive early"})
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 10) Get Plan For Trip
    hr("Get plan for trip")
    r = get(f"{BASE_URL}/trips/{trip_id}/plan")
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 11) Places: list, search, get recommendations
    hr("List places")
    r = get(f"{BASE_URL}/places", params={"city": "Paris"})
    print(r.status_code, f"Returned: {len(r.json()) if r.ok else 'ERR'}")

    hr("Search places")
    r = get(f"{BASE_URL}/places/search", params={"q": "museum", "city": "Paris"})
    print(r.status_code, f"Returned: {len(r.json()) if r.ok else 'ERR'}")

    hr("Recommendations")
    r = get(f"{BASE_URL}/Recommendations/Paris")
    print(r.status_code, f"Returned: {len(r.json()) if r.ok else 'ERR'}")

    # 12) Planner generate (dry_run)
    hr("Plan generate (dry_run=true)")
    plan_payload = {
        "destination": "Paris",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=2)),
        "interests": ["sights", "museum", "food"],
        "daily_start": "09:00:00",
        "daily_end": "19:00:00",
        "lunch_at": "13:00:00",
        "pace": "standard",
        "budget_level": 2,
        "origin": "New York",
        "name": "Test Plan",
        "travelers": 2,
        "dry_run": True,
        "use_google": False,
        "country_mode": False
    }
    r = post(f"{BASE_URL}/plan/generate", json=plan_payload)
    print(r.status_code, pretty(r.json() if r.ok else r.text))

    # 13) Cleanup: delete item and trip
    hr("Delete item")
    r = delete(f"{BASE_URL}/trips/{trip_id}/items/{item_id}")
    print(r.status_code, r.text if not r.ok else "Deleted")

    hr("Delete trip")
    r = delete(f"{BASE_URL}/trips/{trip_id}")
    print(r.status_code, r.text if not r.ok else "Deleted")

    hr("DONE")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as e:
            print("Request failed:", e)
            sys.exit(1)

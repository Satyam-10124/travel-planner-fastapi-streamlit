import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine
from app.models import Place
from app.db import DATABASE_URL, create_db_and_tables

def main():
    create_db_and_tables()
    engine = create_engine(DATABASE_URL, echo=False)
    with Session(engine) as session:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "places.json")
        with open(data_path, "r", encoding="utf-8") as f:
            places = json.load(f)
        for p in places:
            session.add(Place(**p))
        session.commit()
    print("Seeded sample places.")

if __name__ == "__main__":
    main()

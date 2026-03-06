import time
import os

from sqlalchemy import create_engine

engine = create_engine(os.getenv("DATABASE_URL"))

while True:
    try:
        with engine.connect() as conn:
            print("Database ready")
            break
    except Exception:
        print("Waiting for database...")
        time.sleep(2)
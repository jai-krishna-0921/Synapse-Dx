import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")

def list_tables():
    try:
        engine = create_engine(DB_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in database:")
        for table in tables:
            print(f"- {table}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()

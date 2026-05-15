from sqlalchemy import create_engine,text

DB_URL = "postgresql://admin:admin@localhost:5432/youtube_db"

engine = create_engine(DB_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Database connected!")

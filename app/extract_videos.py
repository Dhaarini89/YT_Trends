from googleapiclient.discovery import build
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json


def run_extract():

   
    # YouTube API key
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    # PostgreSQL connection
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


    print(DATABASE_URL)

    # Create DB engine
    engine = create_engine(DATABASE_URL)

    # Create YouTube client
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )

    # Fetch videos
    request = youtube.search().list(
    q="data engineering",
    part="snippet",
    maxResults=10,
    order="date"
    )

    response = request.execute()

    print("Fetched YouTube data!")

    # Store raw JSON in PostgreSQL
    insert_query = text("""
        INSERT INTO raw_videos (payload)
        VALUES (:payload)
    """)
    
    with engine.begin() as conn:

        conn.execute(
            insert_query,
            {
                "payload": json.dumps(response)
            }
        )
 
        
    print("Raw JSON stored in PostgreSQL!")

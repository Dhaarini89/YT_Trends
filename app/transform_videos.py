from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json

def run_transform():
    # Load environment variables
    load_dotenv()

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

    # Create DB engine
    engine = create_engine(DATABASE_URL)

    # Step 1: Read raw JSON from raw_videos table
    select_query = text("""
        SELECT id, payload
        FROM raw_videos
        ORDER BY id DESC
        LIMIT 1
    """)

    with engine.connect() as conn:

        result = conn.execute(select_query)

        row = result.fetchone()

        if not row:
            print("No raw data found!")
            exit()

        payload = row.payload

    # Convert JSON string to Python dict
    data = payload if isinstance(payload, dict) else json.loads(payload)

    # Extract video items
    items = data.get("items", [])

    print(f"Found {len(items)} videos")

    # Step 2: Insert cleaned data into videos table

    insert_query = text("""
        INSERT INTO videos (
            video_id,
            title,
            description,
            channel_title,
            published_at
        )
        VALUES (
            :video_id,
            :title,
            :description,
            :channel_title,
            :published_at
        )
        ON CONFLICT (video_id)
        DO NOTHING
        """)

    check_query = text("""
        SELECT 1
        FROM videos
        WHERE video_id = :video_id
        """)
    with engine.begin() as conn:
        
        
        for item in items:
            
            
            snippet = item.get("snippet", {})

            video_id = item.get("id", {}).get("videoId")

            title = snippet.get("title")

            description = snippet.get("description")

            channel_title = snippet.get("channelTitle")

            published_at = snippet.get("publishedAt")

            # Skip if no video_id
            if not video_id:
                continue

            existing = conn.execute(check_query,{"video_id": video_id}).fetchone()

            if existing:
               print(f"Skipping existing video: {video_id}")
               continue

            conn.execute(
                insert_query,
                {
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "channel_title": channel_title,
                    "published_at": published_at
                }
            )
            print(f"Inserting video: {title}")


    print("Videos transformed and loaded!")

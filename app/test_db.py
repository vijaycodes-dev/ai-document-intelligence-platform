from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:King001%40@localhost:5432/document_ai"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Database connected successfully!")
except Exception as e:
    print("❌ Error:", e)
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Connect to your local MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "satquery_ai_db"

print(f"🔌 Initializing MongoDB connection at {MONGO_URI}...")
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections for the Agent traces and UI
interactions_collection = db["interactions"]
reports_collection = db["reports"]

async def ping_database():
    """Test the database connection on server startup."""
    try:
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
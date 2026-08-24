import os
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

api_key = os.getenv("GROQ_API_KEY_AGENTIC")


# Paste your API key here
os.environ["GROQ_API_KEY"] = api_key

client = Groq()

print("🔍 Querying active Groq models...")
models = client.models.list()

for m in models.data:
    print(f"✅ {m.id}")
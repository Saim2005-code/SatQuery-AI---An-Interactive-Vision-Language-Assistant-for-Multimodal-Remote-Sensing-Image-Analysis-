import os
from dotenv import load_dotenv
from groq import Groq

# Load the environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY_AGENTIC")

if not api_key:
    print("❌ ERROR: Could not find GROQ_API_KEY_AGENTIC in .env file.")
else:
    print(f"✅ Key loaded successfully! (Starts with: {api_key[:5]}...)")

# Test the connection
print("🌐 Attempting to connect to Groq API...")
try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Reply with the word 'Connected' if you can hear me."}],
        model="llama3-70b-8192"
    )
    print(f"🎉 SUCCESS! Groq says: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ CONNECTION FAILED. Raw error details:\n{repr(e)}")
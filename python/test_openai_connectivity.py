import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise SystemExit("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10,
    )
    print("OpenAI connectivity test succeeded.")
    print("Response:", response.choices[0].message.content.strip())
except Exception as e:
    print("OpenAI connectivity test failed:", e)

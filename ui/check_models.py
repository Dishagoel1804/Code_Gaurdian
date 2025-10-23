import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List models that support generateContent
models = genai.list_models()
print("\n✅ Available models supporting generateContent:\n")
for m in models:
    if "generateContent" in m.supported_generation_methods:
        print(m.name)

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Models available for your API key:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
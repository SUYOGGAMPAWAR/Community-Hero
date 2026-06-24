import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import the NEW SDK
from google import genai
from google.genai import types

# Force load the variables from your .env file
load_dotenv()

# The new client automatically looks for the GEMINI_API_KEY environment variable!
client = genai.Client()

app = FastAPI(title="Community Hero API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/issues/report")
async def report_issue(file: UploadFile = File(...)):
    """
    Accepts an image upload, passes it to the new Gemini SDK, and returns structured JSON.
    """
    try:
        image_bytes = await file.read()
        
        # Format the image for the new SDK
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=file.content_type
        )
        
        prompt = """
        You are a civic infrastructure AI assistant. Analyze this image of a community issue.
        Return ONLY a valid JSON object with the following keys:
        - "category": (Choose the closest match: "Pothole", "Water Leakage", "Broken Streetlight", "Waste Management", "Public Property Damage", or "Other")
        - "severity": ("Low", "Medium", "High")
        - "description": (A concise, 2-sentence summary of the issue tailored for local municipal authorities)
        """
        
        # The new SDK automatically resolves the correct latest version of 1.5-flash
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, image_part]
        )
        
        # Parse the JSON response
        cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
        result_data = json.loads(cleaned_response)
        
        return {"status": "success", "ai_analysis": result_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Community Hero API is running."}
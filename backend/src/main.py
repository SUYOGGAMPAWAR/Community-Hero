import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Imports for serving React
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Database imports
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from google import genai
from google.genai import types

# --- DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./community_hero.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Issue Table (Now with City tracking)
class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    severity = Column(String)
    description = Column(String)
    city = Column(String, index=True) 
    lat = Column(Float)
    lng = Column(Float)

# Create the table in the file
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APP SETUP ---
app = FastAPI(title="Community Hero API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded working key for hackathon sprint
client = genai.Client(api_key="GEMINI API KEY")

# --- ENDPOINTS ---

# 1. Fetch all saved issues for the map
@app.get("/api/issues")
def get_all_issues(db: Session = Depends(get_db)):
    return db.query(Issue).all()

# 2. Report a new issue
@app.post("/api/issues/report")
async def report_issue(
    file: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    city: str = Form("Unknown"),
    db: Session = Depends(get_db)
):
    try:
        image_bytes = await file.read()
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=file.content_type)
        
        prompt = """
        You are a civic infrastructure AI assistant. Analyze this image of a community issue.
        Return a JSON object with the following keys:
        "category": (Choose the closest match: "Pothole", "Water Leakage", "Broken Streetlight", "Waste Management", "Public Property Damage", "Other")
        "severity": ("Low", "Medium", "High")
        "description": (A concise, 2-sentence summary of the issue tailored for local municipal authorities)
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        result_data = json.loads(response.text)
        
        # Save to SQLite Database
        new_issue = Issue(
            category=result_data["category"],
            severity=result_data["severity"],
            description=result_data["description"],
            city=city,
            lat=lat,
            lng=lng
        )
        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)
        
        return {"status": "success", "ai_analysis": new_issue}
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

# --- SERVE REACT FRONTEND ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return FileResponse("static/index.html")

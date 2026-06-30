# 🦸 Community Hero

**Hyperlocal AI-Powered Civic Issue Reporting Platform**

Community Hero empowers citizens to report local infrastructure problems — potholes, water leakages, broken streetlights, waste dumps — by simply dropping a pin on a map and uploading a photo. Google Gemini AI instantly analyzes the image, classifies the issue, assesses severity, and logs a structured report to a database — all in seconds.

---

## ✨ Features

- 📸 **AI Image Analysis** — Powered by **Google Gemini 2.5 Flash**, automatically categorizes issues and assesses severity from a photo
- 🗺️ **Interactive Live Map** — Click anywhere on the map to drop a target pin; all reported issues are visualized as markers with full details
- 📍 **Auto City Detection** — Reverse geocoding via OpenStreetMap Nominatim detects the city/location name automatically from the dropped pin
- 🗄️ **Persistent Storage** — All reported issues are saved to an SQLite database via SQLAlchemy and shown on the map immediately
- 🐳 **Fully Dockerized** — Separate, production-ready Dockerfiles for backend (Python/FastAPI) and frontend (React/Nginx)
- ⚡ **Fast & Modern Stack** — React 19 + Vite + Tailwind CSS frontend; FastAPI backend with sub-100ms API responses

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, React-Leaflet |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| AI Engine | Google Gemini 2.5 Flash (`google-genai`) |
| Database | SQLite via SQLAlchemy ORM |
| Containerization | Docker (multi-stage build for frontend) |
| Geocoding | OpenStreetMap Nominatim API |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- A **Google Gemini API Key** ([get one here](https://aistudio.google.com/app/apikey))
- Docker (optional, for containerized deployment)

---

### 1. Clone the Repository

```bash
git clone https://github.com/SUYOGGAMPAWAR/Community-Hero.git
cd Community-Hero
```

---

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure the API Key

Open `src/main.py` and replace the placeholder with your Gemini API key:

```python
# src/main.py
client = genai.Client(api_key="YOUR_GEMINI_API_KEY_HERE")
```

> **Tip:** For production, use a `.env` file and load it with `python-dotenv` instead of hardcoding the key.

#### Run the Backend

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

The API will be live at `http://localhost:8080`.

---

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

> In development, the frontend proxies API calls to the backend. Make sure the backend is running before submitting issues.

---

## 🐳 Docker Deployment

Each service has its own Dockerfile for containerized deployment.

### Backend

```bash
cd backend
docker build -t community-hero-backend .
docker run -p 8080:8080 community-hero-backend
```

### Frontend

The frontend uses a **multi-stage build** — Vite builds the static assets, then Nginx serves them.

```bash
cd frontend
docker build -t community-hero-frontend .
docker run -p 80:8080 community-hero-frontend
```

> The Nginx configuration automatically picks up the `$PORT` environment variable, making it compatible with platforms like **Google Cloud Run**.

---

## 📖 How It Works

```
User drops a pin on the map
        ↓
Auto-detects city via Nominatim reverse geocoding
        ↓
User uploads a photo of the civic issue
        ↓
Frontend POSTs image + lat/lng/city to FastAPI
        ↓
Gemini 2.5 Flash analyzes the image → returns JSON
  { category, severity, description }
        ↓
Issue saved to SQLite database
        ↓
Map refreshes → new marker appears with full details
```

### Issue Categories

| Category | Examples |
|---|---|
| Pothole | Cracked/damaged road surface |
| Water Leakage | Burst pipe, waterlogged road |
| Broken Streetlight | Non-functional or damaged lamp |
| Waste Management | Overflowing bins, illegal dumping |
| Public Property Damage | Vandalized benches, broken railings |
| Other | Anything not covered above |

### Severity Levels

- 🟢 **Low** — Minor inconvenience, non-urgent
- 🟡 **Medium** — Needs attention within a reasonable timeframe
- 🔴 **High** — Immediate action required

---

## 🗂️ Project Structure

```
Community-Hero/
│
├── backend/
│   ├── src/
│   │   └── main.py          # FastAPI app, DB models, Gemini AI integration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container definition
│   └── community_hero.db    # SQLite database (auto-created on first run)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component (map + upload form)
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile           # Multi-stage Nginx build
│
└── README.md
```

---

## 🔌 API Reference

### `GET /api/issues`

Returns all reported issues from the database.

**Response:**
```json
[
  {
    "id": 1,
    "category": "Pothole",
    "severity": "High",
    "description": "A large pothole...",
    "city": "Pune",
    "lat": 18.5204,
    "lng": 73.8567
  }
]
```

---

### `POST /api/issues/report`

Analyzes an image with Gemini AI and saves the issue to the database.

**Request (multipart/form-data):**

| Field | Type | Description |
|---|---|---|
| `file` | Image file | Photo of the civic issue |
| `lat` | float | Latitude of the dropped pin |
| `lng` | float | Longitude of the dropped pin |
| `city` | string | Detected city name |

**Response:**
```json
{
  "status": "success",
  "ai_analysis": {
    "id": 2,
    "category": "Water Leakage",
    "severity": "Medium",
    "description": "A burst pipe is causing water to overflow...",
    "city": "Pune",
    "lat": 18.5204,
    "lng": 73.8567
  }
}
```

---

## 🌐 Cloud Deployment (Google Cloud Run)

Both Dockerfiles are pre-configured for Cloud Run deployment with dynamic `$PORT` support.

```bash
# Build and push backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/community-hero-backend ./backend

# Deploy backend
gcloud run deploy community-hero-backend \
  --image gcr.io/YOUR_PROJECT_ID/community-hero-backend \
  --platform managed --region asia-south1 --allow-unauthenticated

# Build and push frontend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/community-hero-frontend ./frontend

# Deploy frontend
gcloud run deploy community-hero-frontend \
  --image gcr.io/YOUR_PROJECT_ID/community-hero-frontend \
  --platform managed --region asia-south1 --allow-unauthenticated
```

---

## 🔮 Roadmap

- [ ] User authentication and profiles
- [ ] Municipal authority dashboard for issue triage
- [ ] Push notifications when an issue is resolved
- [ ] Issue upvoting to prioritize community-flagged problems
- [ ] PostgreSQL migration for production-scale persistence
- [ ] Mobile app (React Native)

---

## 👤 Author

**Suyog Gampawar**
B.E. Computer Science (AI & Data Science) — D.Y. Patil Technical Campus, Pune

[![GitHub](https://img.shields.io/badge/GitHub-SUYOGGAMPAWAR-181717?logo=github)](https://github.com/SUYOGGAMPAWAR)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-suyog--gampawar-0A66C2?logo=linkedin)](https://linkedin.com/in/suyog-gampawar-50ab66295)
[![Portfolio](https://img.shields.io/badge/Portfolio-SUYOGGAMPAWAR.github.io-blue)](https://SUYOGGAMPAWAR.github.io)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

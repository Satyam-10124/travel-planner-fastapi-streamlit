# 🧳 Travel Planner - Complete Travel Planning Application

A comprehensive travel planning application with AI-powered itinerary generation, interactive maps, weather integration, and budget tracking.

## ✨ Features

- 🤖 **AI-Powered Itinerary Generation** - Smart route optimization and activity scheduling
- 🗺️ **Interactive Maps** - Visual trip planning with Folium integration
- 🌤️ **Weather Integration** - Real-time weather forecasts for destinations
- 💰 **Budget Tracking** - Expense management and budget planning
- 📱 **Modern UI** - Beautiful Streamlit frontend with responsive design
- 🔍 **Place Discovery** - Google Places API integration for real-world data
- 📊 **Trip Analytics** - Visual insights and trip statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation & Setup

1. **Clone and navigate to the project:**
```bash
cd travel-planner-fastapi-with-planner
```

2. **Create virtual environment:**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables:**
```bash
# Copy the example environment file
copy env.example .env
# Edit .env file and add your API keys (optional for basic functionality)
```

5. **Seed the database with sample places:**
```bash
python scripts/seed.py
```

6. **Run the complete application:**
```bash
python run_app.py
```

This will start both:
- 🔧 **FastAPI Backend** at http://localhost:8000
- 🎨 **Streamlit Frontend** at http://localhost:8501

### Alternative: Run Services Separately

**Terminal 1 - Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py --server.port 8501
```

## 🔑 API Keys (Optional)

For enhanced functionality, add these to your `.env` file:

```env
# Google Places API (for real place data)
GOOGLE_PLACES_API_KEY=your-google-places-api-key

# OpenWeatherMap API (for weather forecasts)
OPENWEATHER_API_KEY=your-openweather-api-key
```

**Get API Keys:**
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service/get-api-key)
- [OpenWeatherMap API](https://openweathermap.org/api)

## 📱 Using the Application

### 1. Plan a New Trip
- Navigate to "✈️ Plan New Trip"
- Enter destination, dates, and preferences
- Choose interests, pace, and budget level
- Generate optimized itinerary with map visualization

### 2. Manage Trips
- View all trips in "📋 My Trips"
- Edit itineraries and add custom activities
- Track trip progress and expenses

### 3. Explore Places
- Browse places by city and category in "🗺️ Explore Places"
- View interactive maps with place markers
- Get recommendations based on ratings

### 4. Budget Planning
- Use "💰 Budget Tracker" for expense management
- Set budget allocations by category
- Visualize spending with charts

### 5. Weather Forecasts
- Check weather conditions in "🌤️ Weather"
- View 5-day forecasts for destinations
- Plan activities based on weather

## 🛠️ API Endpoints

### Core Endpoints
- `POST /plan/generate` - Generate trip itinerary
- `GET /trips` - List all trips
- `GET /places` - Browse places
- `GET /Recommendations/{city}` - Get city recommendations

### Full API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🏗️ Architecture

```
├── app/
│   ├── api/           # FastAPI route handlers
│   ├── core/          # Configuration and settings
│   ├── services/      # Business logic (planner, weather, places)
│   └── models.py      # Database models
├── data/              # Sample data
├── scripts/           # Utility scripts
├── streamlit_app.py   # Streamlit frontend
└── run_app.py         # Application launcher
```

## 🔧 Development

### Adding New Features
1. Backend: Add routes in `app/api/`
2. Frontend: Update `streamlit_app.py`
3. Services: Add business logic in `app/services/`

### Database
- Uses SQLite by default
- Models defined with SQLModel
- Automatic table creation on startup

## 🚀 Deployment

### Local Production
```bash
# Set production environment
export DATABASE_URL=postgresql://user:pass@localhost/travel_db
pip install psycopg2-binary
python run_app.py
```

### Cloud Deployment
- **Railway**: Push to GitHub → Deploy from Repo (see detailed steps below)
- **Heroku**: Add `Procfile` and deploy
- **Docker**: Use included `Dockerfile`

### Deploying on Railway (Docker)

Railway runs one port per service. This repo provides two Dockerfiles so you can deploy the backend and frontend as separate Railway services:

- Backend (FastAPI) service uses the root `Dockerfile`
- Frontend (Streamlit) service uses `Dockerfile.frontend`

Follow these steps:

1. Create a new Railway project and connect your GitHub repo.
2. Add a new service → “Deploy from Repo” → select this repository.
3. For the backend service:
   - Build: Railway uses the root `Dockerfile` automatically
   - Exposed port: Railway will set `PORT` (default 8000 in the image, but it will bind to `$PORT`)
   - Health check: `/health`
   - Environment variables (recommended):
     - `DATABASE_URL` → Use Railway Postgres plugin (recommended) or stick with SQLite for testing
     - `GOOGLE_PLACES_API_KEY` (optional)
     - `OPENWEATHER_API_KEY` (optional)

4. Add another service for the frontend:
   - Build settings: set the Dockerfile path to `Dockerfile.frontend`
   - The container will listen on `$PORT` and start Streamlit automatically
   - Environment variables:
     - `API_BASE` → set to your backend public URL, e.g. `https://<backend-service>.up.railway.app`

Notes:

- SQLite is stored on the container filesystem which is ephemeral on Railway. For production data, provision Railway Postgres and set `DATABASE_URL` accordingly.
- CORS is already open in `app/main.py` via `CORSMiddleware`.
- The frontend reads the backend base URL from `API_BASE` (or `BACKEND_URL`) environment variable, defaulting to `http://localhost:8000` for local dev.

Example env variables:

```env
# Backend service
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB
GOOGLE_PLACES_API_KEY=your-google-places-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Frontend service
API_BASE=https://your-backend.up.railway.app
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

**Common Issues:**

1. **Port already in use:**
   ```bash
   # Kill processes on ports 8000 and 8501
   taskkill /f /im python.exe  # Windows
   pkill -f python             # macOS/Linux
   ```

2. **Module not found:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database issues:**
   ```bash
   # Delete database and restart
   rm travel.db
   python scripts/seed.py
   ```

## 📞 Support

- 📧 Create an issue on GitHub
- 📖 Check the API docs at `/docs`
- 🔍 Review the code examples in this README

---

Made with ❤️ using FastAPI + Streamlit

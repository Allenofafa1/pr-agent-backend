from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize FastAPI
app = FastAPI()

# Enable CORS so WordPress (or any site) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing, allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scheduler for background tasks
scheduler = BackgroundScheduler()

def monitor_media():
    # Simulated background task for media monitoring
    print("🔍 Running predictive monitoring...")

scheduler.add_job(monitor_media, "interval", minutes=30)
scheduler.start()

# --------------------------
# ROUTES
# --------------------------

@app.get("/")
def home():
    return {"message": "✅ AI Agent is live and ready!"}

@app.post("/predict")
def predict(data: dict):
    text = data.get("text", "")
    # Example dummy AI response (replace later with OpenAI API or logic)
    return {"response": f"AI Agent received: '{text}' and generated insights."}

@app.get("/outreach")
def outreach():
    return {"message": "📢 Media outreach simulation complete."}

@app.get("/competitors")
def competitors():
    return {"competitors": ["Company A", "Company B", "Company C"]}

@app.get("/content")
def content():
    return {"content": "Here’s a sample piece of AI-generated content."}

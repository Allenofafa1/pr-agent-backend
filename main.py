from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn

# Create the FastAPI app
app = FastAPI()

# Example scheduled job (replace with your agent logic)
def test_job():
    print("Scheduler is running a test job...")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(test_job, "interval", minutes=1)
scheduler.start()

# Root endpoint
@app.get("/")
def home():
    return {"status": "running", "message": "PR Agent backend is live"}

# Extra test endpoint
@app.get("/ping")
def ping():
    return {"pong": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

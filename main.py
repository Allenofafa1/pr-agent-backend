from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# Example scheduled job (you can replace this with your agent tasks)
def test_job():
    print("Scheduler is running a test job...")

# Create the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(test_job, "interval", minutes=1)

# Create Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "running", "message": "PR Agent backend is live"}

if __name__ == "__main__":
    scheduler.start()
    app.run(host="0.0.0.0", port=5000)

# main.py
import os
import sqlite3
import requests
import asyncio
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import openai

API_KEY = os.getenv("API_KEY", "change-me")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)
DB_PATH = os.getenv("DB_PATH", "/data/data.db")

app = FastAPI(title="PR Agent API")

def init_db():
    os.makedirs("/data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        body TEXT,
        scraped_at TEXT
      )""")
    c.execute("""
      CREATE TABLE IF NOT EXISTS generated (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        content TEXT,
        created_at TEXT
      )""")
    conn.commit()
    conn.close()

init_db()

class TaskRequest(BaseModel):
    task: str
    payload: dict = None

def check_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/api/run-task")
async def run_task(req: TaskRequest, x_api_key: str = Header(None)):
    check_key(x_api_key)
    if req.task == "monitoring":
        res = await run_monitoring()
        return {"status":"ok","result":res}
    elif req.task == "generate_content":
        topic = req.payload.get("topic") if req.payload else "Write about security"
        content = await generate_content(topic)
        return {"status":"ok","content":content}
    else:
        raise HTTPException(status_code=400, detail="Unknown task")


@app.get("/api/status")
def status(x_api_key: str = Header(None)):
    check_key(x_api_key)
    return {"status":"ok"}


# --- Example monitoring job (placeholder) ---
async def run_monitoring():
    """
    Replace this with real scrapers & NLP. This is a minimal example:
    - fetches a sample page and stores a short snippet to SQLite
    """
    sample_url = "https://example.com"
    try:
        r = requests.get(sample_url, timeout=10)
        title = "Example Domain"
        body = (r.text or "")[:2000]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO articles (url,title,body,scraped_at) VALUES (?,?,?,datetime('now'))",
                  (sample_url, title, body))
        conn.commit()
        conn.close()
        return {"scraped": sample_url}
    except Exception as e:
        return {"error": str(e)}


# --- OpenAI content generation ---
async def generate_content(topic: str):
    if not OPENAI_KEY:
        return "OpenAI key not configured on server."
    openai.api_key = OPENAI_KEY
    prompt = (
        f"Write a ~600 word blog post for homeowners in Nairobi about: {topic}. "
        "Include a short intro, 3 short sections, and a CTA: 'Book a free site survey via WhatsApp'."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=900,
            temperature=0.7
        )
        content = resp.choices[0].message.content
    except Exception as e:
        content = f"OpenAI error: {e}"

    # store
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO generated (topic,content,created_at) VALUES (?,?,datetime('now'))",
              (topic, content))
    conn.commit()
    conn.close()
    return content


# --- Scheduler: run monitoring every 10 minutes ---
scheduler = AsyncIOScheduler()
scheduler.add_job(lambda: asyncio.create_task(run_monitoring()), "interval", minutes=10)
scheduler.start()

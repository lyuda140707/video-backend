from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware   # ✅ Додай цей рядок
import os, requests, datetime

app = FastAPI()
# ✅ Додаємо CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# === 1. Віддає mp4-лінк за file_id (як раніше)
@app.get("/get_video/{file_id}")
async def get_video(file_id: str):
    import requests
    import os

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        return {"error": "missing_token"}

    # Запит до Telegram API
    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    r = requests.get(tg_url)
    data = r.json()

    # Якщо Telegram повернув шлях до файлу
    if data.get("ok") and data["result"].get("file_path"):
        file_path = data["result"]["file_path"]
        full_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        print("🎬 Отримано посилання:", full_url)
        return {"url": full_url}

    # Якщо файл не знайдено
    print("⚠️ Не знайдено file_path у відповіді Telegram:", data)
    return {"error": "not_found"}



# === 2. Webhook для отримання нових відео ===
@app.post(f"/bot/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    update = await request.json()
    msg = update.get("message", {})
    video = msg.get("video")
    if video:
        file_id = video["file_id"]
        msg_id = msg.get("message_id")
        print("🎥 Нове відео отримано!")
        print("🆔 Message ID:", msg_id)
        print("📁 File ID:", file_id)
        print("⏰", datetime.datetime.now())
        print("——————————————")
        # Хочеш — можеш записати у файл:
        with open("files_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} | msg:{msg_id} | file_id:{file_id}\n")
        # Відправляємо file_id у той самий чат, де бот отримав відео
        chat_id = msg["chat"]["id"]  # ID чату (канал, група або приват)
        text = f"🎬 File ID:\n`{file_id}`"
        
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={
                "chat_id": chat_id,
                "reply_to_message_id": msg_id,  # відповідає прямо під відео
                "text": text,
                "parse_mode": "Markdown"
            }
        )

    return {"ok": True}


@app.get("/")
def ping():
    return {"ok": True}

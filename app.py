from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests, os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # наприклад, -1001234567890

def get_file_path(message_id):
    # 1. отримуємо file_id з повідомлення
    msg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMessage?chat_id={CHANNEL_ID}&message_id={message_id}"
    msg = requests.get(msg_url).json()
    if not msg.get("ok"):
        raise HTTPException(404, "Message not found")
    file_id = msg["result"]["video"]["file_id"]

    # 2. отримуємо file_path
    info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile", params={"file_id": file_id}).json()
    if not info.get("ok"):
        raise HTTPException(404, "File not found")
    file_path = info["result"]["file_path"]

    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

@app.get("/get_video/{message_id}")
def get_video(message_id: int):
    try:
        url = get_file_path(message_id)
        return JSONResponse({"url": url})
    except Exception as e:
        raise HTTPException(404, f"Error: {e}")

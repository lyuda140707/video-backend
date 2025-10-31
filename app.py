from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os, requests

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # залишаємо лише цей секрет

@app.get("/get_video/{file_id}")
def get_video(file_id: str):
    """Повертає прямий CDN-URL файлу за file_id"""
    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
        params={"file_id": file_id},
        timeout=30
    ).json()
    if not r.get("ok"):
        raise HTTPException(status_code=404, detail="File not found")

    file_path = r["result"]["file_path"]
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return JSONResponse({"url": url})

@app.get("/")
def ping():
    return {"ok": True}

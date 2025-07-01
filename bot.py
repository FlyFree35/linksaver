import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

app = FastAPI()  # FastAPI сервер

telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Link Saver — отправь мне ссылку на видео из TikTok, Instagram, YouTube или Pinterest, и я помогу скачать его."
    )

def detect_service(url: str) -> str:
    if "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "pinterest.com" in url:
        return "pinterest"
    else:
        return "unknown"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    service = detect_service(text)

    if service == "unknown":
        await update.message.reply_text("Похоже, это не ссылка на TikTok, Instagram, YouTube или Pinterest.")
    else:
        await update.message.reply_text(f"Это ссылка на сервис: {service}. Сейчас попробую скачать видео!")

# Регистрируем обработчики
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.on_event("startup")
async def on_startup():
    # Устанавливаем Webhook при старте приложения
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}


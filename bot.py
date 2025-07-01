import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# Читаем переменные окружения
TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

print(f"Запускаем с TOKEN={TOKEN} WEBHOOK_URL={WEBHOOK_URL}")

app = FastAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Link Saver — отправь мне ссылку на TikTok, Instagram, YouTube или Pinterest, и я помогу скачать её."
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
        await update.message.reply_text("Это не ссылка на поддерживаемый сервис.")
    else:
        await update.message.reply_text(f"Это ссылка на сервис: {service}. Сейчас попробую скачать видео!")

# Создаём Telegram приложение
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.on_event("startup")
async def on_startup():
    if not WEBHOOK_URL:
        print("ОШИБКА: переменная окружения WEBHOOK_URL не установлена!")
        return
    webhook_full_url = WEBHOOK_URL.rstrip("/") + "/webhook"
    print(f"Устанавливаем вебхук на: {webhook_full_url}")
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=webhook_full_url)
    await telegram_app.start()
    print(f"Вебхук успешно установлен: {webhook_full_url}")

@app.on_event("shutdown")
async def on_shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

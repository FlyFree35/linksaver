from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7932458839:AAGAQMuoeG9xdVsVTtCVOZOKH0-nacixGUY'  # Твой токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Link Saver — отправь мне ссылку на видео из TikTok, Instagram, YouTube или Pinterest, и я помогу скачать его."
    )

# Функция для определения сервиса по ссылке
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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот Link Saver запущен...")
    app.run_polling()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7932458839:AAGAQMuoeG9xdVsVTtCVOZOKH0-nacixGUY'  # Твой токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Link Saver — отправь мне ссылку на видео из TikTok, Instagram, YouTube или Pinterest, и я помогу скачать его."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Пока просто подтверждаем получение ссылки
    await update.message.reply_text(f"Получил ссылку: {text}\nСкоро добавлю функцию скачивания!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот Link Saver запущен...")
    app.run_polling()

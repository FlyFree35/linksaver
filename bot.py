import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
import yt_dlp

# Получаем токен и URL вебхука из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

print(f"Запускаем с TOKEN={TOKEN} WEBHOOK_URL={WEBHOOK_URL}")

app = FastAPI()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я *Link Saver* — отправь мне ссылку на TikTok, Instagram или YouTube, и я помогу скачать видео.\n\n"
        "✨ А ещё попробуй моего второго бота — [Emotional DJ](https://t.me/emotionaldj_bot), он подбирает музыку под настроение! 🎵",
        parse_mode='Markdown'
    )

# Определяем сервис по ссылке
def detect_service(url: str) -> str:
    url = url.lower()
    if "tiktok.com" in url:
        return "TikTok"
    elif "instagram.com" in url:
        return "Instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    else:
        return "unknown"

# Функция для скачивания видео
async def download_video(url: str, output_path: str, service: str):
    loop = asyncio.get_event_loop()

    def run_yt_dlp():
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'mp4',
        }
        # Добавляем файл cookies, если нужно
        if service == "Instagram":
            ydl_opts['cookiefile'] = 'instagram_cookies.txt'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path

    return await loop.run_in_executor(None, run_yt_dlp)

# Обработка всех текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    service = detect_service(text)

    if service == "unknown":
        await update.message.reply_text(
            "❗ Это не ссылка на поддерживаемый сервис. Я поддерживаю только TikTok, Instagram и YouTube."
        )
        return

    if service == "YouTube":
        await update.message.reply_text(
            "🚀 Функция скачивания видео с YouTube (включая Shorts) скоро будет доступна!\n"
            "Следите за обновлениями 😊"
        )
        return

    await update.message.reply_text(f"🔍 Обнаружен сервис: {service}. Сейчас попробую скачать видео...")

    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/{update.effective_user.id}_{int(update.message.date.timestamp())}.mp4"

    try:
        downloaded_file = await download_video(text, filename, service)

        if not os.path.exists(downloaded_file):
            await update.message.reply_text("😢 Не удалось найти файл после загрузки.")
            return

        with open(downloaded_file, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=(
                    "✅ Скачано с помощью [Link Saver](https://t.me/LinkSaverVideo_Bot)\n"
                    "✨ А ещё попробуй моего второго бота — [Emotional DJ](https://t.me/emotionaldj_bot) 🎵"
                ),
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        await update.message.reply_text(
            "Не удалось скачать видео 😢 Возможно, ссылка неправильная или видео недоступно.\n"
            "Если это Instagram — проверь, что файл cookies лежит в проекте!"
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# Инициализация бота и обработчиков
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Запуск вебхука при старте
@app.on_event("startup")
async def on_startup():
    if not TOKEN:
        print("❌ ОШИБКА: переменная окружения BOT_TOKEN не установлена!")
        return
    if not WEBHOOK_URL:
        print("❌ ОШИБКА: переменная окружения WEBHOOK_URL не установлена!")
        return
    print(f"Устанавливаем вебхук на: {WEBHOOK_URL}")
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    await telegram_app.start()
    print(f"✅ Вебхук успешно установлен: {WEBHOOK_URL}")

# Остановка бота при завершении
@app.on_event("shutdown")
async def on_shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()

# Маршрут для обработки вебхука
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.environ.get("PORT", "10000"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing")

app_web = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

SERVICES = {
    "video": ("🎬 ادیت ویدئو", "ادیت ویدئو برای اینستاگرام و یوتیوب"),
    "photo": ("🖼 ادیت عکس", "بهبود و ادیت عکس"),
    "text": ("✍️ تولید متن", "تولید متن تبلیغاتی و محتوایی"),
}

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🎬 ادیت ویدئو", callback_data="video")],
        [InlineKeyboardButton("🖼 ادیت عکس", callback_data="photo")],
        [InlineKeyboardButton("✍️ تولید متن", callback_data="text")],
        [InlineKeyboardButton("📋 سفارش‌های من", callback_data="orders")],
        [InlineKeyboardButton("💰 موجودی", callback_data="balance")],
    ]
    await update.message.reply_text(
        "🤖 به MNS خوش آمدی!\n\nخدمت موردنظر را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button(update: Update, context):
    q = update.callback_query
    await q.answer()
    if q.data in SERVICES:
        title, desc = SERVICES[q.data]
        await q.edit_message_text(
            f"{title}\n\n{desc}\n\n"
            "برای ثبت سفارش، جزئیات کار و فایل‌های لازم را ارسال کن.\n"
            "قیمت پس از بررسی اعلام می‌شود."
        )
    elif q.data == "orders":
        await q.edit_message_text("📋 فعلاً سفارشی ثبت نشده است.")
    elif q.data == "balance":
        await q.edit_message_text("💰 موجودی فعلی: ۰\n\nپرداخت و پنل درآمد در مرحله بعد اضافه می‌شود.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

@app_web.get("/")
def home():
    return "MNS is online"

@app_web.get("/health")
def health():
    return "ok"

@app_web.post("/telegram/webhook")
def telegram_webhook():
    # The actual Update handling is attached after application initialization.
    return "ok"

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

async def main():
    await telegram_app.initialize()
    if WEBHOOK_URL:
        await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/telegram/webhook")
        await telegram_app.start()
    else:
        await telegram_app.start()
        await telegram_app.updater.start_polling()

if __name__ == "__main__":
    # For the first MVP, polling mode is used unless WEBHOOK_URL is supplied.
    # Render can run this web service; the /health endpoint provides the web layer.
    threading.Thread(target=run_web, daemon=True).start()
    import asyncio
    asyncio.run(main())
    threading.Event().wait()

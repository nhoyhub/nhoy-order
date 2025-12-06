# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import escape_markdown
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Import configuration
import config

# In-memory storage
user_data = {}
pending_approvals = {}
completed_orders = {}

# --- Helper Functions ---
async def send_to_admin(user_id: int, username: str, udid: str, payment_option: str):
    url = f"https://api.telegram.org/bot{config.BOT_2_TOKEN}/sendMessage"
    message = (
        f"🔍 Approval Request\n\n"
        f"User: {username}\nID: {user_id}\nUDID: {udid}\nPayment: {payment_option}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nPlease decide:"
    )
    keyboard = [
        [
            {"text": "✅ Approve", "callback_data": f"approve_{user_id}"},
            {"text": "❌ Reject", "callback_data": f"reject_{user_id}"}
        ],
        [
            {"text": "📋 Copy UDID", "callback_data": f"copyudid_{user_id}"}
        ]
    ]
    payload = {
        'chat_id': config.BOT_2_ADMIN_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps({"inline_keyboard": keyboard})
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

async def notify_user(user_id: int, approved: bool):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"
    user_info = pending_approvals.get(user_id) or completed_orders.get(user_id)
    if not user_info:
        return
    if approved:
        photo = config.SUCCESS_PHOTO_URL
        caption = f"🎉 Order Completed!\nUDID: {user_info['udid']}\nPayment: ${user_info['payment_option']}\nThank you! /start to buy again."
        payload = {
            "user_id": user_id,
            "username": user_info['username'],
            "udid": user_info['udid'],
            "payment_option": user_info['payment_option'],
            "completion_time": datetime.now().isoformat()
        }
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(config.BACKEND_API_URL, json=payload)
            except:
                pass
        completed_orders[user_id] = user_info
    else:
        photo = config.REJECTED_PHOTO_URL
        caption = "❌ Your order was rejected. Try again or contact support."
    async with aiohttp.ClientSession() as session:
        await session.post(url, data={'chat_id': str(user_id), 'photo': photo, 'caption': caption})

# Validate UDID
def validate_udid(udid: str) -> bool:
    return 20 <= len(udid) <= 50 and all(c in '0123456789abcdefABCDEF-' for c in udid)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[InlineKeyboardButton("📱 Download UDID Profile", url="https://udid.tech/download-profile")]]
    await update.message.reply_photo(photo=config.START_PHOTO_URL, caption=f"Welcome {user.first_name}!\nClick the button below to start.", reply_markup=InlineKeyboardMarkup(keyboard))

# Add other handlers here using `config` for URLs and tokens

# --- Main ---
async def main():
    bot_app = Application.builder().token(config.BOT_TOKEN).build()
    admin_app = Application.builder().token(config.BOT_2_TOKEN).build()
    # Add handlers as before...
    async with bot_app, admin_app:
        await asyncio.gather(bot_app.updater.start_polling(), admin_app.updater.start_polling())
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

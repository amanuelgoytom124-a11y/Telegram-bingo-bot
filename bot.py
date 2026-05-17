import os
import asyncio
from flask import Flask
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7901007823:AAElbZ5f7G7bXbZf_z8vX-7X2y4Z5t7W3XQ")
bot = AsyncTeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Hip Games Bot is Running perfectly!"

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    intro_text = (
        "👋 **Welcome to Hip Games!**\n\n"
        "Your ultimate mobile gaming platform. To get started and begin winning, "
        "please choose one of the options below to set up your account, fund your wallet, "
        "or invite your friends to play!"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📝 Register Account", callback_data="menu_register"),
        InlineKeyboardButton("💳 Deposit Funds", callback_data="menu_deposit"),
        InlineKeyboardButton("👥 Invite Friends", callback_data="menu_invite")
    )
    await bot.send_message(message.chat.id, intro_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
async def handle_intro_menu(call):
    if call.data == "menu_register":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "📝 **Registration Portal**\n\nPlease reply with your full name to begin setting up your player profile.")
    elif call.data == "menu_deposit":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "💳 **Deposit Options**\n\nWe support local mobile banking transfer choices. Enter the amount you wish to add.")
    elif call.data == "menu_invite":
        await bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/Hipgamesbot?start=ref_{call.message.chat.id}"
        await bot.send_message(call.message.chat.id, f"👥 **Referral System**\n\nShare your link to earn bonuses:\n{invite_link}")

async def verify_telegram_handshake():
    print("🚀 Starting Hip Games Telegram Bot Handshake...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.polling(non_stop=True)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(verify_telegram_handshake())
    app.run(host='0.0.0.0', port=5000)

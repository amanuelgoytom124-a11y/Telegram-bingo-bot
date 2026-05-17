import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "7901007823:AAElbZ5f7G7bXbZf_z8vX-7X2y4Z5t7W3XQ")
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def home():
    return "Hip Games Bot is Running perfectly!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
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
    bot.send_message(message.chat.id, intro_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_intro_menu(call):
    if call.data == "menu_register":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📝 **Registration Portal**\n\nPlease reply with your full name to begin setting up your player profile.")
    elif call.data == "menu_deposit":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 **Deposit Options**\n\nWe support local mobile banking transfer choices. Enter the amount you wish to add.")
    elif call.data == "menu_invite":
        bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/Hipgamesbot?start=ref_{call.message.chat.id}"
        bot.send_message(call.message.chat.id, f"👥 **Referral System**\n\nShare your link to earn bonuses:\n{invite_link}")

def run_bot_polling():
    print("🚀 Starting Hip Games Telegram Bot Polling Thread...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

# Start polling in a separate background thread so it doesn't block Gunicorn
polling_thread = threading.Thread(target=run_bot_polling, daemon=True)
polling_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

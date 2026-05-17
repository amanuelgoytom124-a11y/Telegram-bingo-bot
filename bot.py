import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8522421089:AAHxRTZH-KdsaQc--11id3oSmLu3Xchs2WM")
bot = telebot.TeleBot(BOT_TOKEN)

# Simple in-memory session tracking for registration states
# Format: { chat_id: { "state": "AWAITING_NAME", "name": "" } }
user_sessions = {}

@app.route('/')
def home():
    return "Hip Games Bot is Running perfectly!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Clear any old session state when /start is used
    if message.chat.id in user_sessions:
        del user_sessions[message.chat.id]
        
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
    chat_id = call.message.chat.id
    
    if call.data == "menu_register":
        bot.answer_callback_query(call.id)
        # Set the user state to expect a text input for their name
        user_sessions[chat_id] = {"state": "AWAITING_NAME", "name": ""}
        bot.send_message(chat_id, "📝 **Registration Portal**\n\nPlease reply directly to this message with your full name to begin setting up your player profile.")
        
    elif call.data == "menu_deposit":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💳 **Deposit Options**\n\nWe support local mobile banking transfer choices. Enter the amount you wish to add.")
        
    elif call.data == "menu_invite":
        bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/Hipgamesbot?start=ref_{chat_id}"
        bot.send_message(chat_id, f"👥 **Referral System**\n\nShare your link to earn bonuses:\n{invite_link}")

# Text message handler to process registration input states
@bot.message_handler(func=lambda message: message.chat.id in user_sessions)
def handle_registration_inputs(message):
    chat_id = message.chat.id
    current_state = user_sessions[chat_id].get("state")

    if current_state == "AWAITING_NAME":
        full_name = message.text.strip()
        
        # Simple verification check to make sure they didn't pass a blank space or command
        if full_name.startswith('/'):
            bot.send_message(chat_id, "❌ Invalid input. Please enter your actual full name to register:")
            return
            
        # Save the name and change state
        user_sessions[chat_id]["name"] = full_name
        user_sessions[chat_id]["state"] = "AWAITING_PHONE"
        
        # Create a native phone sharing button menu layout
        phone_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        phone_button = KeyboardButton(text="📱 Share Contact Number", request_contact=True)
        phone_markup.add(phone_button)
        
        confirmation_msg = f"Thank you, **{full_name}**!\n\nTo complete your secure registration, please tap the button below to automatically share your phone number verified by Telegram."
        bot.send_message(chat_id, confirmation_msg, reply_markup=phone_markup, parse_mode="Markdown")

# Special message handler specifically to capture shared contact fields
@bot.message_handler(content_types=['contact'])
def handle_contact_sharing(message):
    chat_id = message.chat.id
    
    # Check if this user is in the correct step of the signup flow
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "AWAITING_PHONE":
        phone_number = message.contact.phone_number
        saved_name = user_sessions[chat_id].get("name")
        
        # Registration complete - clear state mapping out of tracking dictionary
        del user_sessions[chat_id]
        
        success_text = (
            "✅ **Registration Complete!**\n\n"
            f"👤 **Name:** {saved_name}\n"
            f"📞 **Phone:** {phone_number}\n\n"
            "Your identity has been securely verified. Now you can proceed to deposit funds to start playing games!"
        )
        # Use ReplyKeyboardRemove to hide the big 'Share Contact' button from their screen view
        bot.send_message(chat_id, success_text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "Welcome back! If you need to make changes, type /start to go to the main menu.")

def run_bot_polling():
    print("🚀 Starting Hip Games Telegram Bot Polling Thread...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

polling_thread = threading.Thread(target=run_bot_polling, daemon=True)
polling_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import os
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8522421089:AAHxRTZH-KdsaQc--11id3oSmLu3Xchs2WM")
bot = telebot.TeleBot(BOT_TOKEN)

# In-memory user session state tracking
user_sessions = {}

# Payment Configurations
PAYMENT_METHODS = {
    "telebirr": {"name": "Telebirr", "details": "📱 Telebirr: `0930919830`\n👤 Name: Amanuel Goytom"},
    "mpesa": {"name": "M-Pesa", "details": "📲 M-Pesa: `0721569830`\n👤 Name: Amanuel Goytom"},
    "cbe": {"name": "CBE (Commercial Bank)", "details": "🏦 CBE Account: `1000571734657`\n👤 Name: Amanuel Goytom Mora"},
    "cbebirr": {"name": "CBE Birr", "details": "🪙 CBE Birr: `0930919830`\n👤 Name: Amanuel Goytom"}
}

@app.route('/')
def home():
    return "Hip Games Bot is Running perfectly!"

def get_main_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📝 Register Account", callback_data="menu_register"),
        InlineKeyboardButton("💳 Deposit Funds", callback_data="menu_deposit"),
        InlineKeyboardButton("🎱 Play Bingo", callback_data="menu_bingo"),
        InlineKeyboardButton("👥 Invite Friends", callback_data="menu_invite")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id in user_sessions:
        del user_sessions[message.chat.id]
    intro_text = (
        "👋 **Welcome to Hip Games!**\n\n"
        "Your ultimate mobile gaming platform. To get started and begin winning, "
        "please choose one of the options below to set up your account, fund your wallet, "
        "or invite your friends to play!"
    )
    bot.send_message(message.chat.id, intro_text, reply_markup=get_main_menu_markup(), parse_mode="Markdown")

@bot.message_handler(commands=['deposit'])
def deposit_command_handler(message):
    start_deposit_flow(message.chat.id)

@bot.message_handler(commands=['bingo'])
def bingo_command_handler(message):
    start_bingo_flow(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_intro_menu(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    if call.data == "menu_register":
        user_sessions[chat_id] = {"state": "AWAITING_NAME", "name": ""}
        bot.send_message(chat_id, "📝 **Registration Portal**\n\nPlease reply directly to this message with your full name to begin setting up your player profile.")
        
    elif call.data == "menu_deposit":
        start_deposit_flow(chat_id)
        
    elif call.data == "menu_bingo":
        start_bingo_flow(chat_id)
        
    elif call.data == "menu_invite":
        invite_link = f"https://t.me/Hipgamesbot?start=ref_{chat_id}"
        bot.send_message(chat_id, f"👥 **Referral System**\n\nShare your link to earn bonuses:\n{invite_link}")

# --- DEPOSIT FLOW MECHANICS ---
def start_deposit_flow(chat_id):
    user_sessions[chat_id] = {"state": "AWAITING_DEPOSIT_AMOUNT", "amount": "", "method": ""}
    bot.send_message(chat_id, "💳 **Deposit Portal**\n\nPlease enter the amount you want to deposit (e.g., 100, 500):")

def show_deposit_methods(chat_id, amount):
    user_sessions[chat_id]["state"] = "AWAITING_DEPOSIT_METHOD"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr"),
        InlineKeyboardButton("📲 M-Pesa", callback_data="pay_mpesa"),
        InlineKeyboardButton("🏦 CBE", callback_data="pay_cbe"),
        InlineKeyboardButton("🪙 CBE Birr", callback_data="pay_cbebirr")
    )
    bot.send_message(chat_id, f"💰 Amount to Deposit: **{amount} ETB**\n\nPlease select your preferred payment method below:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment_method_selection(call):
    chat_id = call.message.chat.id
    selected_method = call.data.split("_")[1]
    
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "AWAITING_DEPOSIT_METHOD":
        bot.answer_callback_query(call.id)
        user_sessions[chat_id]["method"] = selected_method
        user_sessions[chat_id]["state"] = "AWAITING_SMS_RECEIPT"
        
        amount = user_sessions[chat_id]["amount"]
        method_info = PAYMENT_METHODS[selected_method]
        
        instruction_msg = (
            f"📥 **የክፍያ መረጃ (Payment Details)**\n\n"
            f"እባክዎ የተመረጠውን መንገድ በመጠቀም **{amount} ETB** ይላኩ:\n\n"
            f"{method_info['details']}\n\n"
            f"⚠️ **ቀጣይ መመሪያ (Instructions):**\n"
            f"ብር ካስተላለፉ በኋላ ከባንክ የደረሰዎትን **የማረጋገጫ አጭር የፅሁፍ መልዕክት (SMS)** ሙሉ በሙሉ ኮፒ (Copy) በማድረግ እዚህ የመልዕክት ማስገቢያ ቦታ ላይ ፔስት (Paste) አድርገው ይላኩት።"
        )
        bot.send_message(chat_id, instruction_msg, parse_mode="Markdown")

# --- BINGO GAME TIERS FLOW ---
def start_bingo_flow(chat_id):
    user_sessions[chat_id] = {"state": "SELECTING_STAKE"}
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💵 Play 10 ETB", callback_data="stake_10"),
        InlineKeyboardButton("💵 Play 20 ETB", callback_data="stake_20"),
        InlineKeyboardButton("💵 Play 50 ETB", callback_data="stake_50"),
        InlineKeyboardButton("💵 Play 100 ETB", callback_data="stake_100")
    )
    bot.send_message(chat_id, "🎱 **Play Bingo**\n\nPlease select your entry stake preference for this round:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stake_'))
def handle_stake_selection(call):
    chat_id = call.message.chat.id
    selected_stake = call.data.split("_")[1]
    
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "SELECTING_STAKE":
        bot.answer_callback_query(call.id)
        user_sessions[chat_id]["stake"] = selected_stake
        user_sessions[chat_id]["state"] = "SELECTING_BOARD"
        
        # Show your custom Bingo Board layout from yesterday
        show_board_selection(chat_id, selected_stake)

def show_board_selection(chat_id, stake):
    markup = InlineKeyboardMarkup(row_width=3)
    # Creating boards 1 through 6
    buttons = [InlineKeyboardButton(f"📋 Board {i}", callback_data=f"board_{i}") for i in range(1, 7)]
    markup.add(*buttons)
    
    bot.send_message(
        chat_id, 
        f"🎯 **Game Stake Selected:** {stake} ETB\n\n"
        "Now, pick an available game board grid card layout below to place your entry ticket:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('board_'))
def handle_board_selection(call):
    chat_id = call.message.chat.id
    board_num = call.data.split("_")[1]
    
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "SELECTING_BOARD":
        bot.answer_callback_query(call.id)
        stake = user_sessions[chat_id].get("stake")
        
        success_msg = (
            f"🎮 **Game Entry Locked In!**\n\n"
            f"🎟️ **Card:** Board {board_num}\n"
            f"💰 **Stake Fee:** {stake} ETB\n\n"
            "Waiting for other players to fill up the room grid. The automated host numbers draw will pop up live as soon as the session fills!"
        )
        del user_sessions[chat_id]
        bot.send_message(chat_id, success_msg, reply_markup=get_main_menu_markup(), parse_mode="Markdown")

# --- GENERAL CONTROLLERS ---
@bot.message_handler(func=lambda message: message.chat.id in user_sessions)
def handle_text_inputs(message):
    chat_id = message.chat.id
    current_state = user_sessions[chat_id].get("state")
    user_input = message.text.strip()

    if current_state == "AWAITING_NAME":
        if user_input.startswith('/'):
            bot.send_message(chat_id, "❌ Invalid input. Enter your full name:")
            return
        user_sessions[chat_id]["name"] = user_input
        user_sessions[chat_id]["state"] = "AWAITING_PHONE"
        phone_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        phone_markup.add(KeyboardButton(text="📱 Share Contact Number", request_contact=True))
        bot.send_message(chat_id, f"Thank you, **{user_input}**!\n\nTap below to share your phone number.", reply_markup=phone_markup, parse_mode="Markdown")

    elif current_state == "AWAITING_DEPOSIT_AMOUNT":
        if not user_input.isdigit() or int(user_input) <= 0:
            bot.send_message(chat_id, "❌ እባክዎ ትክክለኛ የብር መጠን ቁጥር ብቻ ያስገቡ:")
            return
        user_sessions[chat_id]["amount"] = user_input
        show_deposit_methods(chat_id, user_input)

    elif current_state == "AWAITING_SMS_RECEIPT":
        if user_input.startswith('/'):
            bot.send_message(chat_id, "❌ እባክዎ የባንክ የደረሰኝ የፅሁፍ መልዕክት እዚህ ላይ ይላኩ:")
            return
        amount = user_sessions[chat_id]["amount"]
        method_name = PAYMENT_METHODS[user_sessions[chat_id]["method"]]["name"]
        
        success_text = (
            "⏳ **ደረሰኝዎ በተሳካ ሁኔታ ቀርቧል!**\n\n"
            f"💰 **የገንዘብ መጠን:** {amount} ETB\n"
            f"🏦 **የክፍያ መንገድ:** {method_name}\n\n"
            "የላኩት የግብይት መረጃ (SMS) በአስተዳዳሪዎች እየተረጋገጠ ነው። በ 10-15 ደቂቃዎች ውስጥ ሂሳብዎ ላይ ይደመራል!"
        )
        del user_sessions[chat_id]
        bot.send_message(chat_id, success_text, reply_markup=get_main_menu_markup(), parse_mode="Markdown")

@bot.message_handler(content_types=['contact'])
def handle_contact_sharing(message):
    chat_id = message.chat.id
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "AWAITING_PHONE":
        phone_number = message.contact.phone_number
        saved_name = user_sessions[chat_id].get("name")
        del user_sessions[chat_id]
        
        success_text = f"✅ **Registration Complete!**\n\n👤 **Name:** {saved_name}\n📞 **Phone:** {phone_number}"
        bot.send_message(chat_id, success_text, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
        bot.send_message(chat_id, "What would you like to do next?", reply_markup=get_main_menu_markup())
    else:
        bot.send_message(chat_id, "Welcome!", reply_markup=get_main_menu_markup())

def run_bot_polling():
    print("🚀 Starting Hip Games Telegram Bot Polling Thread...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

polling_thread = threading.Thread(target=run_bot_polling, daemon=True)
polling_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

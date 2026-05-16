import asyncio
from flask import Flask, render_template, request, jsonify
from telegram import Bot
from telegram.request import HTTPXRequest

app = Flask(__name__)

TELEGRAM_TOKEN = "8522421089:AAHxRTZH-KdsaQc--11id3oSmLu3Xchs2WM"

# Configure a robust connection pool with an extended 30-second timeout window
tg_request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
bot = Bot(token=TELEGRAM_TOKEN, request=tg_request)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

async def verify_telegram_handshake():
    try:
        # Give the server an extended chance to handshake over slower mobile networks
        print("📡 Attempting secure handshake with Telegram servers...")
        bot_info = await bot.get_me()
        print(f"✅ Connection Stable! Active Bot: @{bot_info.username}")
    except Exception as network_error:
        print("\n⚠️  [Network Notice]: Telegram handshake took too long to respond.")
        print("👉 Local server will remain ONLINE so you can test your game layout locally.")
        print(f"👉 Error Details: {network_error}\n")
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(commands=['start', 'menu'])
async def send_welcome(message):
    welcome_text = "Welcome to Hip Games! Choose an option from the main menu below to manage your account or play:"
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn_play = InlineKeyboardButton("🎮 Play Bingo", callback_data="cmd_play")
    btn_balance = InlineKeyboardButton("💰 Check Balance", callback_data="cmd_balance")
    btn_deposit = InlineKeyboardButton("💳 Deposit Funds", callback_data="cmd_deposit")
    btn_withdraw = InlineKeyboardButton("🏦 Withdraw Cash", callback_data="cmd_withdraw")
    btn_help = InlineKeyboardButton("❓ Help & Rules", callback_data="cmd_help")
    
    markup.add(btn_play)
    markup.add(btn_balance, btn_deposit)
    markup.add(btn_withdraw, btn_help)
    
    await bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cmd_'))
async def handle_menu_clicks(call):
    if call.data == "cmd_play":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "Opening your Bingo Board... Use /play if it doesn't pop up instantly.")
    elif call.data == "cmd_balance":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "💰 Your current balance is: 0.00 ETB")
    elif call.data == "cmd_deposit":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "💳 Please enter the amount you want to deposit.")
    elif call.data == "cmd_withdraw":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "🏦 Enter your withdrawal details.")
    elif call.data == "cmd_help":
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "❓ Rules: Match numbers on your grid to claim a Bingo row victory!")

 if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(verify_telegram_handshake())
    
    # Run the server locally on all internal network paths
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    # Professional introduction text guiding them on what to do next
    intro_text = (
        "👋 **Welcome to Hip Games!**\n\n"
        "Your ultimate mobile gaming platform. To get started and begin winning, "
        "please choose one of the options below to set up your account, fund your wallet, "
        "or invite your friends to play!"
    )
    
    # Create the clean, easy-to-tap button menu layout
    markup = InlineKeyboardMarkup(row_width=1)
    
    btn_register = InlineKeyboardButton("📝 Register Account", callback_data="menu_register")
    btn_deposit = InlineKeyboardButton("💳 Deposit Funds", callback_data="menu_deposit")
    btn_invite = InlineKeyboardButton("👥 Invite Friends", callback_data="menu_invite")
    
    # Adding them vertically for perfect mobile rendering
    markup.add(btn_register, btn_deposit, btn_invite)
    
    await bot.send_message(
        message.chat.id, 
        intro_text, 
        reply_markup=markup, 
        parse_mode="Markdown"
    @bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
async def handle_intro_menu(call):
    if call.data == "menu_register":
        await bot.answer_callback_query(call.id)
        await bot.send_message(
            call.message.chat.id, 
            "📝 **Registration Portal**\n\nPlease reply with your full name to begin setting up your player profile."
        )
        
    elif call.data == "menu_deposit":
        await bot.answer_callback_query(call.id)
        await bot.send_message(
            call.message.chat.id, 
            "💳 **Deposit Options**\n\nWe support local mobile banking transfer options. Enter the amount you wish to add to your gaming balance."
        )
        
    elif call.data == "menu_invite":
        await bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/Hipgamesbot?start=ref_{call.message.chat.id}"
        await bot.send_message(
            call.message.chat.id, 
            "👥 **Referral System**\n\nShare your unique link below with your friends. You will earn bonus tokens for every active player you bring in!\n\n" + invite_link
        )


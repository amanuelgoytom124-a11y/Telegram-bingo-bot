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

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(verify_telegram_handshake())
    
    # Run the server locally on all internal network paths
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

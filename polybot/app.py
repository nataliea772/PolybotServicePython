import flask
from flask import request
import os
from bot import Bot, QuoteBot, ImageProcessingBot

app = flask.Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BOT_APP_URL = os.environ['BOT_APP_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_BOT_TOKEN}/', methods=['POST'])
def webhook():
    try:
        req = request.get_json()
        print("✅ Webhook payload received:", req)

        message = req.get('message')
        if not message:
            print("⚠️ No 'message' field found in payload!")
            return "Bad request", 400

        bot.handle_message(req['message'])
        return 'Ok'
    except Exception as e:
        print("❌ ERROR inside webhook:", e)
        import traceback
        traceback.print_exc()
        return 'Internal Error', 500


bot = ImageProcessingBot(TELEGRAM_BOT_TOKEN, BOT_APP_URL)

if __name__ == "__main__":
    # bot.setWebhook(f"{BOT_APP_URL}/{TELEGRAM_BOT_TOKEN}/")  #This tells Telegram where to send updates

    app.run(host='0.0.0.0', port=8443)

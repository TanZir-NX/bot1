import os
import telebot
from flask import Flask
from openai import OpenAI
from threading import Thread

# 1. Environment Variables
# These will be set in the Render Dashboard
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Flask Server Setup (To keep Render alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 4. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am a DeepSeek-powered AI bot. Send me a message to start chatting!")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    # Send a "typing..." action so the user knows the bot is processing
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Call Hugging Face Router with DeepSeek Model
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # Or the specific "novita" variant if required
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )
        
        # Get response text
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I encountered an error while processing your request.")

# 5. Main Entry Point
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Start Telegram Bot Polling
    print("Bot is starting...")
    bot.infinity_polling()

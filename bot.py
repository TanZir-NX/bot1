import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# 1. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. Load Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

# 3. Initialize OpenAI Client (pointing to Hugging Face Router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# Function to get response from DeepSeek via Hugging Face
async def get_ai_response(user_text):
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # You can use the specific string you provided as well
            messages=[
                {"role": "user", "content": user_text}
            ],
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error calling HF API: {e}")
        return "Sorry, I'm having trouble thinking right now. Please try again later."

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hello! I am an AI Bot powered by DeepSeek. Send me a message to start chatting!"
    )

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Send a "typing..." action so the user knows the bot is working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get AI response
    ai_response = await get_ai_response(user_text)
    
    # Reply to user
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    # Build the Telegram Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add Handlers
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    print("Bot is running...")
    application.run_polling()

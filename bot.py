import os
import logging
from moviepy.video.io.VideoFileClip import VideoFileClip
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from flask import Flask
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/health')
def health_check():
    return 'Healthy', 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Send me a movie file and I will extract a 30-second sample.')

async def handle_document(update: Update, context: CallbackContext):
    if update.message.document.mime_type == "video/mp4":
        file = await update.message.document.get_file()
        await file.download('movie.mp4')

        with VideoFileClip('movie.mp4') as video:
            duration = video.duration
            start_time = max(0, duration / 2 - 15)  # Get the middle 30 seconds
            end_time = start_time + 30
            clip = video.subclip(start_time, end_time)
            clip.write_videofile('sample.mp4', codec='libx264')

        with open('sample.mp4', 'rb') as video_file:
            await update.message.reply_video(video=InputFile(video_file, 'sample.mp4'))

def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    main()

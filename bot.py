import logging
from pyrogram import Client, filters
from moviepy.editor import VideoFileClip
from io import BytesIO
import os
from flask import Flask
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize Flask app
bot = Flask(__name__)

@bot.route('/')
def hello_world():
    return 'Hello, World!'

@bot.route('/health')
def health_check():
    return 'Healthy', 200

def run_flask():
    bot.run(host='0.0.0.0', port=8080)

# Fetch API credentials from environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize the Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply(
        "Hello! I'm your video processing bot. Send me a video, and I'll send you a 30-second sample from it."
    )
    logger.info("Sent start message to user: %s", message.from_user.id)

@app.on_message(filters.video & filters.private)
async def handle_video(client, message):
    logger.info("Received a video from user: %s", message.from_user.id)
    
    video_stream = BytesIO()
    try:
        await message.download(file=video_stream)
        video_stream.seek(0)

        logger.info("Processing video...")
        
        with VideoFileClip(video_stream) as video:
            sample_duration = min(30, video.duration)
            sample = video.subclip(0, sample_duration)
            
            sample_stream = BytesIO()
            sample.write_videofile(sample_stream, codec="libx264", threads=4, audio_codec="aac")
            sample_stream.seek(0)
            
            await message.reply_video(sample_stream, caption="Here is your 30-second sample video!")
            logger.info("Sample video sent to user: %s", message.from_user.id)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        await message.reply(f"An error occurred: {e}")
    finally:
        video_stream.close()
        if 'sample_stream' in locals():
            sample_stream.close()
        logger.info("Cleanup completed")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    
    # Start the Pyrogram Client
    app.run()

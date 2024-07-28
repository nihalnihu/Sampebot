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
api_id = os.getenv("25731065")
api_hash = os.getenv("be534fb5a5afd8c3308c9ca92afde672")
bot_token = os.getenv("7309568989:AAH665zjDcbdAokYpWySy09B_3EGBRDctpQ")

# Initialize the Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

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

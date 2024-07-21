from config import api_hash, api_id, bot_token, instagram_username, instagram_password
from telethon import TelegramClient, events
import instaloader
import logging
import re
import os

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO, datefmt='%m-%d-%Y %I:%M:%S')

# Initialize the Telegram client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Initialize the Instagram downloader
L = instaloader.Instaloader()

# Log in to Instagram
L.login(instagram_username, instagram_password)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello! Send me an Instagram post, reel, or story link to download.')
    raise events.StopPropagation

def download_instagram_content(url):
    # Identify the type of content
    if "/p/" in url:
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        L.download_post(post, target='downloads')
    elif "/reel/" in url:
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        L.download_post(post, target='downloads')
    elif "/stories/" in url:
        username = url.split("/")[-3]
        L.download_stories(userids=[L.check_profile_id(username)], filename_target='downloads/stories')
    else:
        raise ValueError("Unsupported URL format")

@client.on(events.NewMessage)
async def handle_message(event):
    message = event.message.message
    # Regular expression to match Instagram URLs
    url_pattern = r'(https?://www\.instagram\.com/(p|reel|stories)/[^/]+/)'
    match = re.search(url_pattern, message)
    
    if match:
        url = match.group(1)
        await event.respond('Downloading from Instagram...')
        
        try:
            download_instagram_content(url)

            for root, dirs, files in os.walk('downloads'):
                for filename in files:
                    if filename.endswith(".jpg") or filename.endswith(".mp4"):
                        await event.respond(file=os.path.join(root, filename))
                        os.remove(os.path.join(root, filename))
                        
            os.rmdir('downloads')

        except Exception as e:
            await event.respond(f'Failed to download: {str(e)}')
    else:
        await event.respond('Please send a valid Instagram post, reel, or story link.')

def main():
    logging.info('Starting...')
    client.start()
    logging.info("Bot Started Successfully!")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()

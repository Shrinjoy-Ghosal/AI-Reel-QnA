import os
import uuid
import yt_dlp
from config import DATA_DIR

def download_reel(url: str) -> dict:
    """
    Downloads an Instagram reel using yt-dlp and returns metadata.
    Returns a dict with 'video_path', 'title', 'description', etc.
    """
    video_id = str(uuid.uuid4())
    output_template = os.path.join(DATA_DIR, f"{video_id}.%(ext)s")
    
    browsers_to_try = [None, 'chrome', 'edge', 'firefox', 'brave']
    last_err = None
    
    # Check if user provided a cookies.txt file
    cookie_file = os.path.join(os.path.dirname(DATA_DIR), 'cookies.txt')
    if os.path.exists(cookie_file):
        browsers_to_try = ['USE_COOKIE_FILE']
    
    for browser in browsers_to_try:
        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        if browser == 'USE_COOKIE_FILE':
            ydl_opts['cookiefile'] = cookie_file
            print("Trying to download using cookies.txt file...")
        elif browser:
            ydl_opts['cookiesfrombrowser'] = (browser,)
            print(f"Trying to download using cookies from {browser}...")
        else:
            print("Trying to download without cookies...")
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                downloaded_file = ydl.prepare_filename(info)
                if not os.path.exists(downloaded_file):
                    base, _ = os.path.splitext(downloaded_file)
                    if os.path.exists(base + ".mp4"):
                        downloaded_file = base + ".mp4"
                    elif os.path.exists(base + ".mkv"):
                        downloaded_file = base + ".mkv"
                
                return {
                    "video_path": downloaded_file,
                    "title": info.get("title", ""),
                    "description": info.get("description", ""),
                    "uploader": info.get("uploader", ""),
                    "duration": info.get("duration", 0),
                }
        except Exception as e:
            last_err = e
            print(f"Failed with {browser if browser else 'no cookies'}: {e}")
            continue
            
    raise RuntimeError(f"Failed to download reel after trying all options. Last error: {str(last_err)}")

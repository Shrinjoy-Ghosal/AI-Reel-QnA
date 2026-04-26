import os
import google.generativeai as genai
from config import GEMINI_API_KEY
import time

genai.configure(api_key=GEMINI_API_KEY)

def transcribe_audio(video_path: str) -> str:
    """
    Transcribes audio using Gemini 1.5 Flash API directly from the video file.
    This bypasses local CPU hangs and is 100x faster than local Whisper.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    try:
        import subprocess
        audio_path = video_path + ".mp3"
        print("Extracting audio layer to prevent upload timeouts...")
        subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ar", "16000", "-ac", "1", "-b:a", "32k", audio_path], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        print("Uploading lightweight audio to Gemini...")
        audio_file = genai.upload_file(path=audio_path)
        
        # Wait for the file to be processed by Google if needed
        while audio_file.state.name == 'PROCESSING':
            print("Gemini is processing the file...")
            time.sleep(2)
            audio_file = genai.get_file(audio_file.name)
            
        if audio_file.state.name == 'FAILED':
            raise RuntimeError("Gemini failed to process the audio file.")
            
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content([
            audio_file,
            "Transcribe all the spoken audio word-for-word. If there is absolutely no speech, just output 'No speech detected.'"
        ])
        
        # Clean up the file from Google's servers and locally
        try:
            genai.delete_file(audio_file.name)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass
            
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini transcription: {str(e)}")
        raise RuntimeError(f"Audio transcription failed: {str(e)}")

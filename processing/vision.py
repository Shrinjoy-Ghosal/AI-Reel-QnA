import os
import time
from google import genai
from config import GEMINI_API_KEY

# DEBUG: Verify if the API key is actually present
if not GEMINI_API_KEY:
    print("CRITICAL: GEMINI_API_KEY is EMPTY in the environment!")
else:
    # Print only first and last 4 to keep it secure
    masked_key = f"{GEMINI_API_KEY[:4]}...{GEMINI_API_KEY[-4:]}"
    print(f"DEBUG: GEMINI_API_KEY detected: {masked_key}")

# Force the SDK to use the stable 'v1' API instead of 'v1beta'
client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

def transcribe_audio(video_path: str) -> str:
    return "Transcribed via Gemini Video API"

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Uses the modern google-genai SDK with forced v1 API version.
    """
    video_file = None
    try:
        print(f"DEBUG: Starting V1 analyze_video_one_shot for {video_path}")
        
        print(f"DEBUG: Uploading file...")
        video_file = client.files.upload(file=video_path)
        print(f"DEBUG: Upload successful, name: {video_file.name}")
        
        while video_file.state == 'PROCESSING':
            print("DEBUG: Gemini processing state: PROCESSING...")
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        print(f"DEBUG: Processing complete, state: {video_file.state}")
            
        if video_file.state == 'FAILED':
            raise RuntimeError("Gemini failed to process the video.")
            
        print("DEBUG: Calling Gemini 1.5-flash (v1) for analysis...")
        
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[video_file, prompt]
        )
        
        print("DEBUG: Analysis successful!")
        
        full_text = response.text
        transcript = "No speech detected"
        visual = "No visual analysis available"
        
        if "TRANSCRIPT:" in full_text and "VISUAL:" in full_text:
            parts = full_text.split("VISUAL:")
            transcript = parts[0].replace("TRANSCRIPT:", "").strip()
            visual = parts[1].strip()
        
        return {
            "transcript": transcript,
            "visual_description": visual
        }
    except Exception as e:
        print(f"CRITICAL V1 ERROR: {str(e)}")
        return {
            "transcript": "Analysis failed.",
            "visual_description": f"Error: {str(e)}"
        }

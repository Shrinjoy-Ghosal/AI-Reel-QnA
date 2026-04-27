import os
import time
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(video_path: str) -> str:
    return "Transcribed via Gemini Video API"

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Uses the modern google-genai SDK with audited syntax and stable model.
    """
    video_file = None
    try:
        print(f"DEBUG: Starting audited analyze_video_one_shot for {video_path}")
        
        print(f"DEBUG: Uploading file...")
        # Audited: 'file' is the correct argument for the local path in google-genai V1
        video_file = client.files.upload(file=video_path)
        print(f"DEBUG: Upload successful, name: {video_file.name}")
        
        # Audited: client.files.get() is the correct method name
        while video_file.state == 'PROCESSING':
            print("DEBUG: Gemini processing state: PROCESSING...")
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        print(f"DEBUG: Processing complete, state: {video_file.state}")
            
        if video_file.state == 'FAILED':
            raise RuntimeError("Gemini failed to process the video.")
            
        print("DEBUG: Calling Gemini 1.5-flash (Stable) for analysis...")
        
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
        print(f"CRITICAL AUDIT ERROR: {str(e)}")
        return {
            "transcript": "Analysis failed.",
            "visual_description": f"Error: {str(e)}"
        }

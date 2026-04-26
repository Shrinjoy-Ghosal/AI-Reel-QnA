import os
import time
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(video_path: str) -> str:
    return "Transcribed via Gemini Video API"

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Uses the modern google-genai SDK for single-pass analysis.
    """
    try:
        print(f"DEBUG: Starting analyze_video_one_shot for {video_path}")
        
        print(f"DEBUG: Uploading file using new SDK...")
        # Uploading using the new SDK syntax
        video_file = client.files.upload(path=video_path)
        print(f"DEBUG: Upload successful, name: {video_file.name}")
        
        # Wait for processing
        while video_file.state == 'PROCESSING':
            print("DEBUG: Gemini processing state: PROCESSING...")
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        print(f"DEBUG: Processing complete, state: {video_file.state}")
            
        if video_file.state == 'FAILED':
            raise RuntimeError("Gemini failed to process the video.")
            
        print("DEBUG: Calling Gemini (New SDK) for analysis...")
        
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
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
        print(f"NEW SDK ERROR in vision.py: {str(e)}")
        # If 2.0 fails, try 1.5 as fallback
        try:
            print("DEBUG: Falling back to 1.5-flash...")
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[video_file, prompt]
            )
            full_text = response.text
            parts = full_text.split("VISUAL:")
            return {
                "transcript": parts[0].replace("TRANSCRIPT:", "").strip() if "TRANSCRIPT:" in full_text else "No speech",
                "visual_description": parts[1].strip() if len(parts) > 1 else "No visual"
            }
        except Exception as e2:
            print(f"DOUBLE ERROR: {str(e2)}")
            return {
                "transcript": "Analysis failed.",
                "visual_description": f"Error: {str(e2)}"
            }

import os
import google.generativeai as genai
from config import GEMINI_API_KEY
import time

genai.configure(api_key=GEMINI_API_KEY)

def transcribe_audio(video_path: str) -> str:
    return "Transcribed via Gemini Video API"

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Extremely detailed logging to find the exact crash point.
    """
    try:
        print(f"DEBUG: Starting analyze_video_one_shot for {video_path}")
        
        print(f"DEBUG: Uploading file...")
        video_file = genai.upload_file(path=video_path)
        print(f"DEBUG: Upload successful, name: {video_file.name}")
        
        # Wait for the file to be processed
        while video_file.state.name == 'PROCESSING':
            print("DEBUG: Gemini processing state: PROCESSING...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        print(f"DEBUG: Processing complete, state: {video_file.state.name}")
            
        if video_file.state.name == 'FAILED':
            print("DEBUG: Processing FAILED on Google side")
            raise RuntimeError("Gemini failed to process the video.")
            
        print("DEBUG: Initializing model gemini-1.5-flash...")
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """
        
        print("DEBUG: Calling model.generate_content (This is the likely crash point)...")
        # Added a 2-minute timeout to the request itself
        response = model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 120}
        )
        print("DEBUG: model.generate_content returned successfully!")
        
        # Clean up
        try:
            print(f"DEBUG: Deleting remote file {video_file.name}")
            genai.delete_file(video_file.name)
        except Exception as e:
            print(f"DEBUG: Cleanup warning: {str(e)}")
        
        full_text = response.text
        print(f"DEBUG: Full AI response received ({len(full_text)} chars)")
        
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
        print(f"CRITICAL ERROR in vision.py: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "transcript": "Analysis failed.",
            "visual_description": f"Error: {type(e).__name__}: {str(e)}"
        }

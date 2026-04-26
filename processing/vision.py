import os
import google.generativeai as genai
from config import GEMINI_API_KEY
import time

genai.configure(api_key=GEMINI_API_KEY)

def transcribe_audio(video_path: str) -> str:
    # Integrated into the one-shot analysis
    return "Transcribed via Gemini Video API"

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Uploads the video to Gemini and gets a full transcript + visual analysis in one go.
    Using gemini-1.5-flash for maximum stability and speed.
    """
    try:
        print(f"Uploading video to Gemini: {video_path}")
        video_file = genai.upload_file(path=video_path)
        
        # Wait for the file to be processed by Google
        while video_file.state.name == 'PROCESSING':
            print("Gemini is watching the video...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == 'FAILED':
            raise RuntimeError("Gemini failed to process the video.")
            
        print("AI is analyzing video content...")
        # Using the most stable multimodal model
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """
        
        response = model.generate_content([video_file, prompt])
        
        # Clean up the file from Google's servers
        try:
            genai.delete_file(video_file.name)
        except:
            pass
        
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
        print(f"STABILITY ERROR in vision.py: {str(e)}")
        # Provide fallback data so the app doesn't crash
        return {
            "transcript": "Analysis timed out or failed.",
            "visual_description": f"Error: {str(e)}"
        }

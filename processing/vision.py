import os
import google.generativeai as genai
from config import GEMINI_API_KEY
import time

genai.configure(api_key=GEMINI_API_KEY)

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Tries multiple model names to find the one available in the user's region.
    """
    try:
        print(f"DEBUG: Starting analyze_video_one_shot for {video_path}")
        
        # Log available models to help debugging
        try:
            print("DEBUG: Listing available models for this API key:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"  - {m.name}")
        except Exception as list_err:
            print(f"DEBUG: Could not list models: {str(list_err)}")

        print(f"DEBUG: Uploading file...")
        video_file = genai.upload_file(path=video_path)
        print(f"DEBUG: Upload successful, name: {video_file.name}")
        
        while video_file.state.name == 'PROCESSING':
            print("DEBUG: Gemini processing state: PROCESSING...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        print(f"DEBUG: Processing complete, state: {video_file.state.name}")
            
        # Try different model names in order of preference
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro-vision']
        response = None
        last_err = None
        
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """

        for model_name in models_to_try:
            try:
                print(f"DEBUG: Attempting analysis with model: {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    [video_file, prompt],
                    request_options={"timeout": 120}
                )
                print(f"DEBUG: SUCCESS with model {model_name}!")
                break
            except Exception as e:
                print(f"DEBUG: Model {model_name} failed: {str(e)}")
                last_err = e
                continue
        
        if not response:
            raise last_err if last_err else RuntimeError("All models failed.")

        # Clean up
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
        print(f"CRITICAL ERROR in vision.py: {type(e).__name__}: {str(e)}")
        return {
            "transcript": "Analysis failed.",
            "visual_description": f"Error: {type(e).__name__}: {str(e)}"
        }

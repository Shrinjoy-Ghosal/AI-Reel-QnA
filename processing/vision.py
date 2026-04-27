import os
import time
from google import genai
from config import GEMINI_API_KEY

# Clean the API key (removes hidden Windows characters or spaces)
CLEAN_KEY = GEMINI_API_KEY.strip() if GEMINI_API_KEY else ""

client = genai.Client(api_key=CLEAN_KEY)

def analyze_video_one_shot(video_path: str) -> dict:
    """
    Cleans the API key and uses a fixed discovery logic.
    """
    video_file = None
    try:
        print(f"DEBUG: Starting Clean-Discovery analysis for {video_path}")
        
        # 1. Discover available models using fixed syntax
        available_models = []
        try:
            print("DEBUG: Fetching available models...")
            # In the new SDK, we check the 'supported_methods' or just try the names
            for m in client.models.list():
                # Correct attribute is 'supported_actions' or checking for 'generate_content'
                name = m.name.replace('models/', '')
                available_models.append(name)
            print(f"DEBUG: Discovered models: {available_models}")
        except Exception as list_err:
            print(f"DEBUG: Model discovery failed: {str(list_err)}")
            # Robust fallbacks
            available_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-2.0-flash-exp']

        if not available_models:
            raise RuntimeError("No models available for this API key.")

        # 2. Upload video
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
            
        # 3. Try discovered models
        prompt = """
        Watch this video carefully and provide two things:
        1. A word-for-word transcript of all spoken audio.
        2. A detailed description of the visual events, people, and objects.
        
        Format your response exactly like this:
        TRANSCRIPT: [text]
        VISUAL: [description]
        """

        response = None
        last_err = None
        
        for model_name in available_models:
            try:
                print(f"DEBUG: Trying model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[video_file, prompt]
                )
                print(f"DEBUG: SUCCESS with {model_name}!")
                break
            except Exception as e:
                print(f"DEBUG: {model_name} failed: {str(e)}")
                last_err = e
                continue
                
        if not response:
            raise last_err if last_err else RuntimeError("All available models failed.")
        
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
        print(f"CLEAN-DISCOVERY ERROR: {str(e)}")
        return {
            "transcript": "Analysis failed.",
            "visual_description": f"Error: {str(e)}"
        }

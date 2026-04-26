import os
import google.generativeai as genai
from PIL import Image
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def analyze_frames(frame_paths: list[str]) -> str:
    """
    Analyzes a list of image frames using Gemini to generate a description.
    """
    if not GEMINI_API_KEY:
        return "Vision analysis unavailable: GEMINI_API_KEY not set."
        
    if not frame_paths:
        return "No frames provided."
        
    # We can use gemini-2.5-flash for multimodal tasks
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Load all frames
    images = []
    for path in frame_paths:
        if os.path.exists(path):
            images.append(Image.open(path))
            
    # To avoid rate limits or token limits, limit to say, 10 frames
    max_frames = 10
    if len(images) > max_frames:
        # Sample evenly
        step = max(1, len(images) // max_frames)
        images = images[::step][:max_frames]
        
    prompt = "Describe what is happening in this sequence of video frames. Be concise but cover the main visual events, objects, and text on screen."
    
    try:
        response = model.generate_content([prompt, *images])
        return response.text
    except Exception as e:
        print(f"Error during vision analysis: {e}")
        return f"Error analyzing visual content: {str(e)}"

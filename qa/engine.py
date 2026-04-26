import os
import json
import google.generativeai as genai
from config import DATA_DIR, GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def build_knowledge_base(reel_id: str, transcript: str, visual_description: str):
    """
    Saves the reel data as a simple JSON file.
    """
    kb_path = os.path.join(DATA_DIR, f"{reel_id}.json")
    data = {
        "reel_id": reel_id,
        "transcript": transcript,
        "visual_description": visual_description
    }
    with open(kb_path, "w") as f:
        json.dump(data, f)
    print(f"Knowledge base saved for {reel_id}")

def ask_question(reel_id: str, question: str) -> str:
    """
    Loads the reel data and asks Gemini to answer based on the full context.
    Using gemini-1.5-flash for stability.
    """
    kb_path = os.path.join(DATA_DIR, f"{reel_id}.json")
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"No knowledge base found for reel {reel_id}")
        
    with open(kb_path, "r") as f:
        data = json.load(f)
        
    context = f"""
    TRANSCRIPT: {data['transcript']}
    VISUAL ANALYSIS: {data['visual_description']}
    """
    
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = f"""
    You are an AI assistant analyzing an Instagram Reel. 
    Based on the context below, answer the user's question accurately.
    
    CONTEXT:
    {context}
    
    QUESTION:
    {question}
    
    ANSWER:
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

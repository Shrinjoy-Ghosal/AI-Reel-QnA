import os
import json
import google.generativeai as genai
from config import DATA_DIR, GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def build_knowledge_base(reel_id: str, transcript: str, visual_description: str):
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
    kb_path = os.path.join(DATA_DIR, f"{reel_id}.json")
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"No knowledge base found for reel {reel_id}")
        
    with open(kb_path, "r") as f:
        data = json.load(f)
        
    context = f"""
    TRANSCRIPT: {data['transcript']}
    VISUAL ANALYSIS: {data['visual_description']}
    """
    
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro']
    last_err = None
    
    for model_name in models_to_try:
        try:
            print(f"DEBUG_QA: Attempting Q&A with model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"CONTEXT:\n{context}\n\nQUESTION: {question}")
            return response.text.strip()
        except Exception as e:
            print(f"DEBUG_QA: Model {model_name} failed: {str(e)}")
            last_err = e
            continue
            
    raise last_err if last_err else RuntimeError("All QA models failed.")

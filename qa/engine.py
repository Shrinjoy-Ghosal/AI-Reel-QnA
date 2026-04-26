import os
import json
from google import genai
from config import DATA_DIR, GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

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
    
    try:
        print(f"DEBUG_QA: Asking question using new SDK...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"CONTEXT:\n{context}\n\nQUESTION: {question}"
        )
        return response.text.strip()
    except Exception as e:
        print(f"QA SDK ERROR: {str(e)}, falling back...")
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"CONTEXT:\n{context}\n\nQUESTION: {question}"
        )
        return response.text.strip()

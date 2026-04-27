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
    
    # Discover available models
    available_models = []
    try:
        for m in client.models.list():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace('models/', '')
                available_models.append(name)
        print(f"DEBUG_QA: Discovered models: {available_models}")
    except Exception as list_err:
        print(f"DEBUG_QA: Discovery failed: {str(list_err)}")
        available_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']

    last_err = None
    for model_name in available_models:
        try:
            print(f"DEBUG_QA: Trying model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=f"CONTEXT:\n{context}\n\nQUESTION: {question}"
            )
            return response.text.strip()
        except Exception as e:
            print(f"DEBUG_QA: {model_name} failed: {str(e)}")
            last_err = e
            continue
            
    raise last_err if last_err else RuntimeError("All QA models failed.")

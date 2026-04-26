import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Q&A and Vision features will fail.")

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

from fastapi import FastAPI, HTTPException, UploadFile, File
import uuid
import os
import shutil
import sys

# Ensure ffmpeg.exe in the current directory is detected by whisper and yt-dlp
os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from api.models import ProcessRequest, ProcessResponse, QueryRequest, QueryResponse
from extractor.instagram import download_reel
from processing.video import extract_frames
from processing.audio import transcribe_audio
from processing.vision import analyze_frames
from qa.engine import build_knowledge_base, ask_question
from config import DATA_DIR

app = FastAPI(title="AI Reel Understanding System", description="System for processing and querying Instagram Reels.")

@app.post("/process_reel_upload", response_model=ProcessResponse)
async def process_reel_upload(file: UploadFile = File(...)):
    try:
        reel_id = str(uuid.uuid4())
        video_path = os.path.join(DATA_DIR, f"{reel_id}_{file.filename}")
        
        print(f"Saving uploaded reel: {file.filename}")
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Extract Audio & Transcribe
        print("Transcribing audio...")
        transcript = transcribe_audio(video_path)
        
        # 3. Extract Frames & Vision Analysis
        print("Extracting frames...")
        frames = extract_frames(video_path, interval_seconds=2)
        print("Analyzing frames...")
        visual_desc = analyze_frames(frames)
        
        # 4. Build Knowledge Base
        print("Building knowledge base...")
        build_knowledge_base(reel_id, transcript, visual_desc)
        
        # 5. Automated Cleanup
        print("Cleaning up temporary files...")
        try:
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
            if frames and len(frames) > 0:
                frames_dir = os.path.dirname(frames[0])
                if os.path.exists(frames_dir):
                    shutil.rmtree(frames_dir)
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")
            
        return ProcessResponse(
            reel_id=reel_id,
            message="Uploaded reel processed successfully",
            transcript=transcript,
            visual_description=visual_desc
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_reel", response_model=ProcessResponse)
def process_reel(request: ProcessRequest):
    try:
        reel_id = str(uuid.uuid4())
        
        # 1. Extract Reel
        print(f"Downloading reel: {request.url}")
        metadata = download_reel(request.url)
        video_path = metadata.get("video_path")
        
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=500, detail="Failed to download video")
            
        # 2. Extract Audio & Transcribe
        print("Transcribing audio...")
        transcript = transcribe_audio(video_path)
        
        # 3. Extract Frames & Vision Analysis
        print("Extracting frames...")
        frames = extract_frames(video_path, interval_seconds=2)
        print("Analyzing frames...")
        visual_desc = analyze_frames(frames)
        
        # 4. Build Knowledge Base
        print("Building knowledge base...")
        build_knowledge_base(reel_id, transcript, visual_desc)
        
        # 5. Automated Cleanup
        print("Cleaning up temporary files...")
        try:
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
            if frames and len(frames) > 0:
                frames_dir = os.path.dirname(frames[0])
                if os.path.exists(frames_dir):
                    shutil.rmtree(frames_dir)
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")
        
        return ProcessResponse(
            reel_id=reel_id,
            message="Reel processed successfully",
            transcript=transcript,
            visual_description=visual_desc
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask_question", response_model=QueryResponse)
def query_reel(request: QueryRequest):
    try:
        answer = ask_question(request.reel_id, request.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

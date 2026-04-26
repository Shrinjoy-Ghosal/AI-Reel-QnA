import cv2
import os
import uuid
from config import DATA_DIR

def extract_frames(video_path: str, interval_seconds: int = 2) -> list[str]:
    """
    Extracts frames from a video at a specified interval.
    Returns a list of file paths to the extracted frames.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    frames_dir = os.path.join(DATA_DIR, f"frames_{uuid.uuid4().hex[:8]}")
    os.makedirs(frames_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30 # fallback
        
    frame_interval = int(fps * interval_seconds)
    
    extracted_frames = []
    count = 0
    saved_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if count % frame_interval == 0:
            frame_path = os.path.join(frames_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            extracted_frames.append(frame_path)
            saved_count += 1
            
        count += 1
        
    cap.release()
    return extracted_frames

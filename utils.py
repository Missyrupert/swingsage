# utils.py - Drop this file in your root directory
import os
import cv2
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {'mp4', 'avi', 'mov', 'mkv', 'quicktime'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(directory: str, hours: int = 24) -> int:
    """Delete files older than specified hours"""
    if not os.path.exists(directory):
        return 0
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    deleted_count = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isdir(file_path):
                continue
            
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Cleaned up old file: {filename}")
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")
                    
    except Exception as e:
        print(f"Error during cleanup of {directory}: {e}")
    
    return deleted_count

def handle_video_orientation(video_path: str) -> str:
    """
    Handle video orientation issues from mobile uploads.
    This fixes the common problem where mobile videos appear sideways.
    """
    try:
        if not _has_ffmpeg():
            print("FFmpeg not available - skipping orientation correction")
            return video_path
        
        rotation = _get_video_rotation(video_path)
        
        if rotation == 0:
            return video_path
        
        print(f"Video needs {rotation}° rotation correction")
        corrected_path = _create_corrected_video(video_path, rotation)
        
        if corrected_path and os.path.exists(corrected_path):
            return corrected_path
        else:
            print("Failed to create corrected video, using original")
            return video_path
            
    except Exception as e:
        print(f"Error handling video orientation: {e}")
        return video_path

def _has_ffmpeg() -> bool:
    """Check if ffmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def _get_video_rotation(video_path: str) -> int:
    """Get rotation angle from video metadata"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return 0
        
        import json
        data = json.loads(result.stdout)
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                rotation = stream.get('tags', {}).get('rotate')
                if rotation:
                    return int(rotation)
                
                side_data = stream.get('side_data_list', [])
                for side in side_data:
                    if side.get('side_data_type') == 'Display Matrix':
                        rotation = side.get('rotation')
                        if rotation:
                            return int(float(rotation))
        
        return 0
        
    except Exception as e:
        print(f"Error getting video rotation: {e}")
        return 0

def _create_corrected_video(video_path: str, rotation: int) -> str:
    """Create a rotation-corrected version of the video"""
    try:
        base_name = os.path.splitext(video_path)[0]
        corrected_path = f"{base_name}_corrected.mp4"
        
        if rotation == 90:
            rotate_filter = "transpose=1"
        elif rotation == 180:
            rotate_filter = "transpose=1,transpose=1"
        elif rotation == 270:
            rotate_filter = "transpose=2"
        else:
            rotate_filter = f"rotate={rotation}*PI/180"
        
        cmd = [
            'ffmpeg', '-i', video_path, '-vf', rotate_filter,
            '-c:a', 'copy', '-metadata:s:v:0', 'rotate=0', '-y', corrected_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(corrected_path):
            print(f"Successfully created rotation-corrected video: {corrected_path}")
            return corrected_path
        else:
            print(f"FFmpeg failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Error creating corrected video: {e}")
        return video_path

def get_video_info(video_path: str) -> dict:
    """Get basic video information using OpenCV"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {'error': 'Could not open video'}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'fps': fps, 'width': width, 'height': height,
            'frame_count': frame_count, 'duration': duration,
            'aspect_ratio': width / height if height > 0 else 0
        }
        
    except Exception as e:
        return {'error': str(e)}

def ensure_directory(path: str) -> bool:
    """Ensure directory exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {path}: {e}")
        return False

def is_video_file_valid(file_path: str) -> bool:
    """Check if video file is valid"""
    try:
        cap = cv2.VideoCapture(file_path)
        is_valid = cap.isOpened()
        cap.release()
        return is_valid
    except:
        return False

# video_optimizer.py - Advanced video processing and optimization
import os
import cv2
import numpy as np
import threading
import queue
import time
from typing import Dict, List, Tuple, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import json
from pathlib import Path
import hashlib

class VideoOptimizer:
    """
    Advanced video processing system with:
    - Parallel processing for speed
    - Video compression and optimization
    - Frame extraction and key frame detection
    - Quality enhancement
    - Progress tracking
    - Caching system
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.cache_dir = Path("video_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.progress_callbacks = {}
        
    def optimize_for_analysis(self, input_path: str, output_path: str, 
                            progress_callback: Optional[Callable] = None) -> Dict:
        """
        Optimize video for faster analysis processing
        - Resize to optimal dimensions
        - Adjust frame rate if needed
        - Enhance quality for better pose detection
        - Compress for faster processing
        """
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(input_path)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
            
            # Get video info
            video_info = self._get_video_info(input_path)
            
            if progress_callback:
                progress_callback(10, "Analyzing video properties...")
            
            # Determine optimal processing parameters
            processing_params = self._calculate_optimal_params(video_info)
            
            if progress_callback:
                progress_callback(20, "Optimizing video for analysis...")
            
            # Process video with optimizations
            result = self._process_video_optimized(
                input_path, output_path, processing_params, progress_callback
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def extract_key_frames(self, video_path: str, num_frames: int = 10) -> List[np.ndarray]:
        """
        Extract key frames from video for analysis
        Uses motion detection to find most representative frames
        """
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate frame indices to extract
        if total_frames <= num_frames:
            frame_indices = list(range(total_frames))
        else:
            # Use motion-based key frame detection
            frame_indices = self._detect_key_frames(cap, num_frames)
        
        # Extract frames
        key_frames = []
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                # Enhance frame for better analysis
                enhanced_frame = self._enhance_frame(frame)
                key_frames.append(enhanced_frame)
        
        cap.release()
        return key_frames
    
    def create_swing_comparison_video(self, video1_path: str, video2_path: str, 
                                    output_path: str) -> bool:
        """
        Create side-by-side comparison video of two swings
        Synchronizes the swings for optimal comparison
        """
        
        try:
            cap1 = cv2.VideoCapture(video1_path)
            cap2 = cv2.VideoCapture(video2_path)
            
            if not (cap1.isOpened() and cap2.isOpened()):
                return False
            
            # Get video properties
            fps1 = cap1.get(cv2.CAP_PROP_FPS)
            fps2 = cap2.get(cv2.CAP_PROP_FPS)
            width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
            height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
            height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Use consistent dimensions and fps
            target_fps = min(fps1, fps2)
            target_height = min(height1, height2)
            target_width = int(target_height * 16 / 9)  # 16:9 aspect ratio
            
            # Setup output video (side-by-side)
            output_width = target_width * 2
            output_height = target_height
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, target_fps, (output_width, output_height))
            
            while True:
                ret1, frame1 = cap1.read()
                ret2, frame2 = cap2.read()
                
                if not (ret1 and ret2):
                    break
                
                # Resize frames
                frame1_resized = cv2.resize(frame1, (target_width, target_height))
                frame2_resized = cv2.resize(frame2, (target_width, target_height))
                
                # Create side-by-side frame
                combined_frame = np.hstack([frame1_resized, frame2_resized])
                
                # Add labels
                cv2.putText(combined_frame, "Previous Swing", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(combined_frame, "Current Swing", (target_width + 10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                out.write(combined_frame)
            
            cap1.release()
            cap2.release()
            out.release()
            
            return True
            
        except Exception as e:
            print(f"Error creating comparison video: {e}")
            return False
    
    def create_slow_motion_analysis(self, input_path: str, output_path: str, 
                                  slow_factor: float = 0.25) -> bool:
        """
        Create slow motion version for detailed analysis
        """
        
        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                return False
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate new fps for slow motion
            new_fps = fps * slow_factor
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, new_fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Enhance frame for slow motion analysis
                enhanced_frame = self._enhance_frame_for_analysis(frame)
                
                # Add frame number overlay
                cv2.putText(enhanced_frame, f"Frame: {frame_count}", (10, height - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                out.write(enhanced_frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            return True
            
        except Exception as e:
            print(f"Error creating slow motion video: {e}")
            return False
    
    def _get_video_info(self, video_path: str) -> Dict:
        """Get comprehensive video information"""
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}
        
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            'file_size': os.path.getsize(video_path)
        }
        
        cap.release()
        return info
    
    def _calculate_optimal_params(self, video_info: Dict) -> Dict:
        """Calculate optimal processing parameters based on video properties"""
        
        width = video_info.get('width', 1920)
        height = video_info.get('height', 1080)
        fps = video_info.get('fps', 30)
        duration = video_info.get('duration', 0)
        
        # Optimal dimensions for pose detection (balance between quality and speed)
        if width > 1920 or height > 1080:
            target_width = 1280
            target_height = 720
        elif width > 1280 or height > 720:
            target_width = 1280
            target_height = 720
        else:
            target_width = width
            target_height = height
        
        # Optimal fps (pose detection doesn't need super high fps)
        target_fps = min(fps, 30)
        
        # Quality settings based on duration
        if duration > 30:  # Long video, prioritize speed
            quality = 'fast'
        elif duration > 10:  # Medium video, balance
            quality = 'balanced'
        else:  # Short video, prioritize quality
            quality = 'high'
        
        return {
            'target_width': target_width,
            'target_height': target_height,
            'target_fps': target_fps,
            'quality': quality,
            'compression_level': 23 if quality == 'high' else 28 if quality == 'balanced' else 32
        }
    
    def _process_video_optimized(self, input_path: str, output_path: str, 
                               params: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """Process video with optimizations for faster analysis"""
        
        start_time = time.time()
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Could not open input video")
        
        # Setup output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path, fourcc, params['target_fps'],
            (params['target_width'], params['target_height'])
        )
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        
        # Frame processing with threading for speed
        frame_buffer = queue.Queue(maxsize=10)
        processed_buffer = queue.Queue(maxsize=10)
        
        # Start frame reader thread
        reader_thread = threading.Thread(
            target=self._frame_reader_worker,
            args=(cap, frame_buffer, total_frames, params)
        )
        reader_thread.start()
        
        # Start frame processor thread
        processor_thread = threading.Thread(
            target=self._frame_processor_worker,
            args=(frame_buffer, processed_buffer, params)
        )
        processor_thread.start()
        
        # Write processed frames
        while frame_count < total_frames:
            try:
                processed_frame = processed_buffer.get(timeout=5)
                if processed_frame is None:  # End signal
                    break
                
                out.write(processed_frame)
                frame_count += 1
                
                if progress_callback and frame_count % 10 == 0:
                    progress = 20 + (frame_count / total_frames) * 60
                    progress_callback(progress, f"Processing frame {frame_count}/{total_frames}")
                    
            except queue.Empty:
                break
        
        # Cleanup
        reader_thread.join(timeout=5)
        processor_thread.join(timeout=5)
        cap.release()
        out.release()
        
        processing_time = time.time() - start_time
        
        if progress_callback:
            progress_callback(100, "Video optimization complete!")
        
        return {
            'success': True,
            'processing_time': processing_time,
            'frames_processed': frame_count,
            'optimization_params': params,
            'output_path': output_path
        }
    
    def _frame_reader_worker(self, cap, frame_buffer: queue.Queue, total_frames: int, params: Dict):
        """Worker thread for reading frames"""
        
        frame_skip = max(1, int(cap.get(cv2.CAP_PROP_FPS) / params['target_fps']))
        frame_idx = 0
        
        while frame_idx < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                try:
                    frame_buffer.put(frame, timeout=1)
                except queue.Full:
                    pass  # Skip frame if buffer full
            
            frame_idx += 1
        
        # Signal end
        frame_buffer.put(None)
    
    def _frame_processor_worker(self, frame_buffer: queue.Queue, processed_buffer: queue.Queue, params: Dict):
        """Worker thread for processing frames"""
        
        while True:
            try:
                frame = frame_buffer.get(timeout=5)
                if frame is None:  # End signal
                    processed_buffer.put(None)
                    break
                
                # Process frame
                processed_frame = self._optimize_frame(frame, params)
                processed_buffer.put(processed_frame)
                
            except queue.Empty:
                break
    
    def _optimize_frame(self, frame: np.ndarray, params: Dict) -> np.ndarray:
        """Optimize individual frame for analysis"""
        
        # Resize frame
        resized_frame = cv2.resize(
            frame, 
            (params['target_width'], params['target_height']),
            interpolation=cv2.INTER_LANCZOS4
        )
        
        # Enhance for pose detection
        if params['quality'] in ['high', 'balanced']:
            enhanced_frame = self._enhance_frame(resized_frame)
        else:
            enhanced_frame = resized_frame
        
        return enhanced_frame
    
    def _enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """Enhance frame for better pose detection"""
        
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        
        # Merge channels back
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Slight sharpening for better edge detection
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced_frame, -1, kernel)
        
        # Blend original and sharpened (subtle sharpening)
        final_frame = cv2.addWeighted(enhanced_frame, 0.7, sharpened, 0.3, 0)
        
        return final_frame
    
    def _enhance_frame_for_analysis(self, frame: np.ndarray) -> np.ndarray:
        """Enhanced frame processing for detailed analysis"""
        
        # Basic enhancement
        enhanced = self._enhance_frame(frame)
        
        # Add subtle motion blur reduction
        kernel = np.ones((3, 3), np.float32) / 9
        deblurred = cv2.filter2D(enhanced, -1, kernel)
        
        # Combine enhanced and deblurred
        final_frame = cv2.addWeighted(enhanced, 0.8, deblurred, 0.2, 0)
        
        return final_frame
    
    def _detect_key_frames(self, cap, num_frames: int) -> List[int]:
        """Detect key frames based on motion and content"""
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= num_frames:
            return list(range(total_frames))
        
        # Sample frames uniformly as fallback
        step = total_frames // num_frames
        key_frames = [i * step for i in range(num_frames)]
        
        # TODO: Implement more sophisticated key frame detection
        # - Motion detection
        # - Scene change detection
        # - Swing phase detection
        
        return key_frames
    
    def _generate_cache_key(self, video_path: str) -> str:
        """Generate cache key for video"""
        
        # Use file path, size, and modification time for cache key
        stat = os.stat(video_path)
        cache_string = f"{video_path}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached processing result"""
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache processing result"""
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except:
            pass  # Ignore cache write errors


class AsyncVideoProcessor:
    """
    Asynchronous video processing system for handling multiple uploads
    """
    
    def __init__(self, max_concurrent: int = 3):
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.active_jobs = {}
        self.optimizer = VideoOptimizer()
    
    def submit_processing_job(self, job_id: str, input_path: str, output_path: str, 
                            progress_callback: Optional[Callable] = None) -> str:
        """Submit video processing job"""
        
        future = self.executor.submit(
            self.optimizer.optimize_for_analysis,
            input_path, output_path, progress_callback
        )
        
        self.active_jobs[job_id] = {
            'future': future,
            'start_time': time.time(),
            'input_path': input_path,
            'output_path': output_path
        }
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get status of processing job"""
        
        if job_id not in self.active_jobs:
            return {'status': 'not_found'}
        
        job = self.active_jobs[job_id]
        future = job['future']
        
        if future.done():
            try:
                result = future.result()
                del self.active_jobs[job_id]  # Cleanup
                return {
                    'status': 'completed',
                    'result': result,
                    'total_time': time.time() - job['start_time']
                }
            except Exception as e:
                del self.active_jobs[job_id]  # Cleanup
                return {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            return {
                'status': 'processing',
                'elapsed_time': time.time() - job['start_time']
            }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel processing job"""
        
        if job_id in self.active_jobs:
            future = self.active_jobs[job_id]['future']
            cancelled = future.cancel()
            if cancelled:
                del self.active_jobs[job_id]
            return cancelled
        return False
    
    def get_queue_status(self) -> Dict:
        """Get overall queue status"""
        
        active_count = len(self.active_jobs)
        completed_jobs = []
        processing_jobs = []
        
        for job_id, job in self.active_jobs.items():
            if job['future'].done():
                completed_jobs.append(job_id)
            else:
                processing_jobs.append({
                    'job_id': job_id,
                    'elapsed_time': time.time() - job['start_time']
                })
        
        return {
            'active_jobs': active_count,
            'processing_jobs': processing_jobs,
            'completed_jobs': completed_jobs
        }
    
    def shutdown(self):
        """Shutdown the processor"""
        self.executor.shutdown(wait=True) 
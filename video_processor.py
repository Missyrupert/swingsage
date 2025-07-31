"""
Video Processing Module for Swing Sage
Handles video analysis, pose detection, and fault identification
"""

import cv2
import mediapipe as mp
import numpy as np
from math import atan2, degrees
from typing import Dict, List
import traceback

class SwingAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )
    
    def analyze_swing(self, input_path: str, output_path: str) -> Dict:
        """Main analysis function"""
        try:
            return self._process_video(input_path, output_path)
        except Exception as e:
            print(f"Swing analysis error: {e}")
            traceback.print_exc()
            return {
                'total_frames': 0,
                'collapse_frames': 0,
                'collapse_percentage': 0.0,
                'posture_loss_frames': 0,
                'posture_loss_percentage': 0.0,
                'error': str(e)
            }
    
    def _process_video(self, input_path: str, output_path: str) -> Dict:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        collapse_frames = 0
        posture_loss_frames = 0
        processed_frames = 0
        
        print(f"Processing {total_video_frames} frames...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Draw skeleton
                self._draw_pose_landmarks(frame, results.pose_landmarks)
                
                # Detect faults
                arm_fault = self._detect_trail_arm_collapse(results.pose_landmarks.landmark)
                posture_fault = self._detect_posture_loss(results.pose_landmarks.landmark)
                
                # Update counters
                if arm_fault['is_collapsing']:
                    collapse_frames += 1
                if posture_fault['is_losing_posture']:
                    posture_loss_frames += 1
                
                # Add visual feedback
                self._add_frame_annotations(frame, arm_fault, posture_fault)
                processed_frames += 1
            else:
                cv2.putText(frame, "No golfer detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            out.write(frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                progress = (frame_count / total_video_frames) * 100
                print(f"Progress: {progress:.1f}%")
        
        cap.release()
        out.release()
        
        print(f"Analysis complete. Processed {processed_frames} frames with pose data.")
        
        return self._calculate_metrics(frame_count, collapse_frames, posture_loss_frames, processed_frames)
    
    def _draw_pose_landmarks(self, frame, landmarks):
        self.mp_drawing.draw_landmarks(
            frame, landmarks, self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
    
    def _detect_trail_arm_collapse(self, landmarks) -> Dict:
        try:
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            elbow_angle = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
            is_collapsing = elbow_angle < 90.0
            
            return {
                'is_collapsing': is_collapsing,
                'elbow_angle': float(elbow_angle),
                'severity': 'high' if elbow_angle < 70 else 'moderate' if elbow_angle < 90 else 'low'
            }
        except Exception as e:
            return {'is_collapsing': False, 'elbow_angle': 0.0, 'severity': 'unknown'}
    
    def _detect_posture_loss(self, landmarks) -> Dict:
        try:
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_center_x = (left_hip.x + right_hip.x) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2
            
            spine_angle = abs(degrees(atan2(hip_center_x - shoulder_center_x, hip_center_y - shoulder_center_y)))
            is_losing_posture = spine_angle < 12.0
            
            return {
                'is_losing_posture': is_losing_posture,
                'spine_angle': float(spine_angle),
                'severity': 'high' if spine_angle < 8 else 'moderate' if spine_angle < 12 else 'low'
            }
        except Exception as e:
            return {'is_losing_posture': False, 'spine_angle': 0.0, 'severity': 'unknown'}
    
    def _calculate_angle(self, a, b, c) -> float:
        try:
            angle = degrees(atan2(c.y - b.y, c.x - b.x) - atan2(a.y - b.y, a.x - b.x))
            return abs(angle + 360) if angle < 0 else abs(angle)
        except:
            return 0.0
    
    def _add_frame_annotations(self, frame, arm_fault: Dict, posture_fault: Dict):
        y_offset = 30
        
        # Trail arm status
        if arm_fault['is_collapsing']:
            color, text = (0, 0, 255), f"Trail Arm: {arm_fault['elbow_angle']:.0f}° (Collapsing)"
        else:
            color, text = (0, 255, 0), f"Trail Arm: {arm_fault['elbow_angle']:.0f}° (Good)"
        
        cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y_offset += 25
        
        # Posture status
        if posture_fault['is_losing_posture']:
            color, text = (0, 0, 255), f"Posture: {posture_fault['spine_angle']:.0f}° (Early Extension)"
        else:
            color, text = (0, 255, 0), f"Posture: {posture_fault['spine_angle']:.0f}° (Stable)"
        
        cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _calculate_metrics(self, total_frames: int, collapse_frames: int, posture_loss_frames: int, processed_frames: int) -> Dict:
        if total_frames == 0:
            return {
                'total_frames': 0, 'collapse_frames': 0, 'collapse_percentage': 0.0,
                'posture_loss_frames': 0, 'posture_loss_percentage': 0.0, 'processed_frames': 0
            }
        
        return {
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'collapse_frames': collapse_frames,
            'collapse_percentage': float((collapse_frames / total_frames) * 100),
            'posture_loss_frames': posture_loss_frames,
            'posture_loss_percentage': float((posture_loss_frames / total_frames) * 100)
        }
    
    def __del__(self):
        if hasattr(self, 'pose'):
            self.pose.close()

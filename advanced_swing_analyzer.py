# advanced_swing_analyzer.py - Drop this file in your root directory
import cv2
import mediapipe as mp
import numpy as np
from math import atan2, degrees, sqrt
from typing import Dict, List, Tuple
import traceback


class AdvancedSwingAnalyzer:
    """
    Next-generation swing analysis detecting 5+ common faults:
    1. Trail arm collapse
    2. Early extension (posture loss) 
    3. Over-the-top swing plane
    4. Sway (lateral movement)
    5. Reverse pivot
    6. Head movement
    7. Weight shift issues
    """

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Higher accuracy
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )

        # Swing phase detection thresholds
        self.swing_phases = {
            'address': (0, 10),
            'takeaway': (10, 30),
            'backswing': (30, 50),
            'transition': (50, 60),
            'downswing': (60, 80),
            'impact': (80, 85),
            'follow_through': (85, 100)
        }

    def analyze_swing(self, input_path: str, output_path: str) -> Dict:
        """Enhanced analysis with multiple fault detection"""
        try:
            return self._process_video_advanced(input_path, output_path)
        except Exception as e:
            print(f"Advanced swing analysis error: {e}")
            traceback.print_exc()
            return self._get_error_result(str(e))

    def _process_video_advanced(self, input_path: str, output_path: str) -> Dict:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")

        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup video writer with better quality
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Analysis data storage
        frame_data = []
        fault_counters = {
            'trail_arm_collapse': 0,
            'early_extension': 0,
            'over_the_top': 0,
            'sway': 0,
            'reverse_pivot': 0,
            'head_movement': 0,
            'weight_shift': 0
        }

        processed_frames = 0
        swing_landmarks_history = []

        print(f"Processing {total_frames} frames with advanced analysis...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_number = len(frame_data)
            swing_progress = (frame_number / total_frames) * 100

            # Convert and process with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            frame_analysis = {
                'frame_number': frame_number,
                'swing_progress': swing_progress,
                'swing_phase': self._determine_swing_phase(swing_progress),
                'faults_detected': {}
            }

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                swing_landmarks_history.append(landmarks)

                # Draw enhanced skeleton
                self._draw_advanced_skeleton(frame, results.pose_landmarks)

                # Multi-fault analysis
                faults = self._analyze_all_faults(
                    landmarks,
                    swing_landmarks_history,
                    frame_analysis['swing_phase']
                )

                frame_analysis['faults_detected'] = faults

                # Update counters
                for fault_name, fault_data in faults.items():
                    if fault_data.get('detected', False):
                        fault_counters[fault_name] += 1

                # Add comprehensive visual feedback
                self._add_advanced_annotations(
                    frame, faults, frame_analysis['swing_phase'])
                processed_frames += 1

            else:
                cv2.putText(frame, "No golfer detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            frame_data.append(frame_analysis)
            out.write(frame)

            # Progress indicator
            if frame_number % 30 == 0:
                progress = (frame_number / total_frames) * 100
                print(f"Progress: {progress:.1f}%")

        cap.release()
        out.release()

        return self._calculate_advanced_metrics(
            total_frames, fault_counters, processed_frames, frame_data
        )

    def _analyze_all_faults(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Analyze all possible swing faults"""
        faults = {}

        # 1. Trail arm collapse (enhanced)
        faults['trail_arm_collapse'] = self._detect_trail_arm_collapse_advanced(
            landmarks, swing_phase)

        # 2. Early extension (enhanced)
        faults['early_extension'] = self._detect_early_extension_advanced(
            landmarks, swing_phase)

        # 3. Over-the-top swing plane
        faults['over_the_top'] = self._detect_over_the_top(
            landmarks, history, swing_phase)

        # 4. Lateral sway
        faults['sway'] = self._detect_sway(landmarks, history, swing_phase)

        # 5. Reverse pivot
        faults['reverse_pivot'] = self._detect_reverse_pivot(
            landmarks, history, swing_phase)

        # 6. Head movement
        faults['head_movement'] = self._detect_head_movement(
            landmarks, history, swing_phase)

        # 7. Weight shift issues
        faults['weight_shift'] = self._detect_weight_shift_issues(
            landmarks, history, swing_phase)

        return faults

    def _detect_trail_arm_collapse_advanced(self, landmarks, swing_phase: str) -> Dict:
        """Enhanced trail arm analysis with swing phase context"""
        try:
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]

            elbow_angle = self._calculate_angle(
                right_shoulder, right_elbow, right_wrist)

            # Different thresholds for different swing phases
            if swing_phase in ['backswing', 'transition']:
                threshold = 100  # More extension needed in backswing
            elif swing_phase == 'downswing':
                threshold = 90   # Some folding expected in downswing
            else:
                threshold = 95

            is_collapsing = elbow_angle < threshold
            confidence = max(0, (threshold - elbow_angle) /
                             threshold) if is_collapsing else 0

            return {
                'detected': is_collapsing,
                'severity': self._calculate_severity(confidence),
                'confidence': confidence,
                'elbow_angle': float(elbow_angle),
                'phase_appropriate': swing_phase in ['downswing', 'impact'],
                'recommendation': self._get_trail_arm_recommendation(elbow_angle, swing_phase)
            }
        except:
            return self._get_fault_error()

    def _detect_over_the_top(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Detect over-the-top swing plane issues"""
        try:
            if len(history) < 10 or swing_phase not in ['transition', 'downswing']:
                return {'detected': False, 'confidence': 0}

            # Compare hand path in transition vs backswing
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            # Calculate swing plane deviation
            shoulder_line_y = (left_shoulder.y + right_shoulder.y) / 2
            hand_plane_deviation = abs(right_wrist.y - shoulder_line_y)

            # Compare with recent history
            recent_deviations = []
            for past_landmarks in history[-10:]:
                past_wrist = past_landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
                past_deviation = abs(past_wrist.y - shoulder_line_y)
                recent_deviations.append(past_deviation)

            avg_deviation = np.mean(recent_deviations)
            is_over_top = hand_plane_deviation > avg_deviation * 1.3
            confidence = min(1.0, (hand_plane_deviation -
                             avg_deviation) / avg_deviation)

            return {
                'detected': is_over_top,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'deviation': float(hand_plane_deviation),
                'recommendation': "Focus on dropping your hands more from the inside during transition"
            }
        except:
            return self._get_fault_error()

    def _detect_sway(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Detect lateral sway during backswing"""
        try:
            if len(history) < 5:
                return {'detected': False, 'confidence': 0}

            # Track hip movement laterally
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            hip_center_x = (left_hip.x + right_hip.x) / 2

            # Compare with address position (first few frames)
            address_hip_positions = []
            for past_landmarks in history[:5]:  # First 5 frames as address
                past_left_hip = past_landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
                past_right_hip = past_landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
                address_hip_positions.append(
                    (past_left_hip.x + past_right_hip.x) / 2)

            address_hip_center = np.mean(address_hip_positions)
            lateral_movement = abs(hip_center_x - address_hip_center)

            # Sway threshold
            sway_threshold = 0.05  # 5% of frame width
            is_swaying = lateral_movement > sway_threshold and swing_phase in [
                'takeaway', 'backswing']
            confidence = min(1.0, lateral_movement /
                             sway_threshold) if is_swaying else 0

            return {
                'detected': is_swaying,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'lateral_movement': float(lateral_movement),
                'recommendation': "Try to keep your weight centered over your feet during the backswing"
            }
        except:
            return self._get_fault_error()

    def _detect_reverse_pivot(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Detect reverse pivot (weight moving toward target in backswing)"""
        try:
            if len(history) < 10 or swing_phase not in ['backswing', 'transition']:
                return {'detected': False, 'confidence': 0}

            # Analyze spine tilt direction
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

            # Calculate spine tilt
            shoulder_tilt = left_shoulder.x - right_shoulder.x
            hip_tilt = left_hip.x - right_hip.x
            spine_tilt = shoulder_tilt - hip_tilt

            # In proper backswing, spine should tilt away from target (negative tilt for right-handed)
            is_reverse_pivot = spine_tilt > 0.02 and swing_phase == 'backswing'
            confidence = min(1.0, spine_tilt / 0.02) if is_reverse_pivot else 0

            return {
                'detected': is_reverse_pivot,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'spine_tilt': float(spine_tilt),
                'recommendation': "Feel like you're loading into your right side during the backswing"
            }
        except:
            return self._get_fault_error()

    def _detect_head_movement(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Detect excessive head movement during swing"""
        try:
            if len(history) < 5:
                return {'detected': False, 'confidence': 0}

            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]

            # Track head position over time
            head_positions = []
            for past_landmarks in history[-10:]:  # Last 10 frames
                past_nose = past_landmarks[self.mp_pose.PoseLandmark.NOSE]
                head_positions.append((past_nose.x, past_nose.y))

            if len(head_positions) < 5:
                return {'detected': False, 'confidence': 0}

            # Calculate head movement variance
            x_positions = [pos[0] for pos in head_positions]
            y_positions = [pos[1] for pos in head_positions]

            x_variance = np.var(x_positions)
            y_variance = np.var(y_positions)
            total_movement = sqrt(x_variance + y_variance)

            movement_threshold = 0.01  # 1% of frame
            excessive_movement = total_movement > movement_threshold
            confidence = min(1.0, total_movement /
                             movement_threshold) if excessive_movement else 0

            return {
                'detected': excessive_movement,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'movement_amount': float(total_movement),
                'recommendation': "Try to keep your head steady - imagine it's in a box"
            }
        except:
            return self._get_fault_error()

    def _detect_early_extension_advanced(self, landmarks, swing_phase: str) -> Dict:
        """Enhanced early extension detection with phase awareness"""
        try:
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

            # Calculate spine angle
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_center_x = (left_hip.x + right_hip.x) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2

            spine_angle = abs(degrees(
                atan2(hip_center_x - shoulder_center_x, hip_center_y - shoulder_center_y)))

            # Phase-specific thresholds
            if swing_phase in ['downswing', 'impact']:
                threshold = 15  # More critical in impact zone
            else:
                threshold = 12

            is_extending = spine_angle < threshold and swing_phase in [
                'downswing', 'impact']
            confidence = max(0, (threshold - spine_angle) /
                             threshold) if is_extending else 0

            return {
                'detected': is_extending,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'spine_angle': float(spine_angle),
                'phase_critical': swing_phase in ['downswing', 'impact'],
                'recommendation': self._get_posture_recommendation(spine_angle, swing_phase)
            }
        except:
            return self._get_fault_error()

    def _detect_weight_shift_issues(self, landmarks, history: List, swing_phase: str) -> Dict:
        """Detect improper weight shift patterns"""
        try:
            if len(history) < 10:
                return {'detected': False, 'confidence': 0}

            # Track foot pressure indicators (ankle positions relative to hips)
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

            # Calculate weight distribution approximation
            left_weight_indicator = abs(left_ankle.x - left_hip.x)
            right_weight_indicator = abs(right_ankle.x - right_hip.x)
            weight_ratio = left_weight_indicator / \
                (left_weight_indicator + right_weight_indicator + 0.001)

            # Expected weight shift patterns
            improper_shift = False
            if swing_phase == 'backswing' and weight_ratio > 0.6:  # Should be on right side
                improper_shift = True
            # Should shift to left
            elif swing_phase in ['downswing', 'impact'] and weight_ratio < 0.4:
                improper_shift = True

            confidence = abs(weight_ratio - 0.5) * 2 if improper_shift else 0

            return {
                'detected': improper_shift,
                'confidence': confidence,
                'severity': self._calculate_severity(confidence),
                'weight_ratio': float(weight_ratio),
                'recommendation': self._get_weight_shift_recommendation(weight_ratio, swing_phase)
            }
        except:
            return self._get_fault_error()

    def _determine_swing_phase(self, progress: float) -> str:
        """Determine current swing phase based on video progress"""
        for phase, (start, end) in self.swing_phases.items():
            if start <= progress < end:
                return phase
        return 'follow_through'

    def _calculate_severity(self, confidence: float) -> str:
        """Convert confidence to severity rating"""
        if confidence > 0.7:
            return 'high'
        elif confidence > 0.4:
            return 'moderate'
        elif confidence > 0.1:
            return 'mild'
        else:
            return 'none'

    def _get_trail_arm_recommendation(self, angle: float, phase: str) -> str:
        """Phase-specific trail arm recommendations"""
        if phase == 'backswing':
            return f"Keep your trail arm more extended in the backswing - current angle {angle:.0f}°"
        elif phase == 'transition':
            return "Maintain arm structure through transition for better sequence"
        else:
            return "Focus on keeping connected arms through the swing"

    def _get_posture_recommendation(self, angle: float, phase: str) -> str:
        """Phase-specific posture recommendations"""
        if phase in ['downswing', 'impact']:
            return f"Stay in your posture through impact - spine angle {angle:.0f}°"
        else:
            return "Maintain your setup posture throughout the swing"

    def _get_weight_shift_recommendation(self, ratio: float, phase: str) -> str:
        """Weight shift recommendations"""
        if phase == 'backswing':
            return "Feel more weight loading into your right side during backswing"
        elif phase in ['downswing', 'impact']:
            return "Shift your weight more aggressively to your left side through impact"
        else:
            return "Work on proper weight shift sequence"

    def _draw_advanced_skeleton(self, frame, landmarks):
        """Draw enhanced skeleton with swing plane indicators"""
        # Standard skeleton
        self.mp_drawing.draw_landmarks(
            frame, landmarks, self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )

        # Add swing plane visualization
        # (Could add more sophisticated visualization here)

    def _add_advanced_annotations(self, frame, faults: Dict, swing_phase: str):
        """Add comprehensive visual feedback"""
        y_offset = 30

        # Show swing phase
        cv2.putText(frame, f"Phase: {swing_phase.title()}", (15, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_offset += 25

        # Show top 3 most confident faults
        fault_scores = [(name, data.get('confidence', 0))
                        for name, data in faults.items()]
        fault_scores.sort(key=lambda x: x[1], reverse=True)

        for fault_name, confidence in fault_scores[:3]:
            if confidence > 0.1:  # Only show significant faults
                fault_data = faults[fault_name]
                color = (0, 0, 255) if fault_data['detected'] else (0, 255, 0)
                severity = fault_data.get('severity', 'none')

                display_name = fault_name.replace('_', ' ').title()
                text = f"{display_name}: {severity} ({confidence:.1%})"

                cv2.putText(frame, text, (15, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                y_offset += 20

    def _calculate_angle(self, a, b, c) -> float:
        """Calculate angle between three points"""
        try:
            angle = degrees(atan2(c.y - b.y, c.x - b.x) -
                            atan2(a.y - b.y, a.x - b.x))
            return abs(angle + 360) if angle < 0 else abs(angle)
        except:
            return 0.0

    def _get_fault_error(self) -> Dict:
        """Standard error response for fault detection"""
        return {
            'detected': False,
            'confidence': 0,
            'severity': 'unknown',
            'recommendation': 'Unable to analyze this aspect'
        }

    def _get_error_result(self, error_msg: str) -> Dict:
        """Standard error response for full analysis"""
        return {
            'total_frames': 0,
            'processed_frames': 0,
            'faults': {},
            'overall_score': 0,
            'primary_issues': [],
            'error': error_msg
        }

    def _calculate_advanced_metrics(self, total_frames: int, fault_counters: Dict,
                                    processed_frames: int, frame_data: List) -> Dict:
        """Calculate comprehensive analysis metrics"""

        if total_frames == 0:
            return self._get_error_result("No frames processed")

        # Calculate fault percentages
        fault_percentages = {}
        for fault_name, count in fault_counters.items():
            fault_percentages[fault_name] = (count / total_frames) * 100

        # Determine primary issues (top 3 faults)
        primary_issues = sorted(fault_percentages.items(),
                                key=lambda x: x[1], reverse=True)[:3]
        primary_issues = [{'fault': fault, 'percentage': pct}
                          for fault, pct in primary_issues if pct > 10]

        # Calculate overall swing score (0-100)
        total_fault_impact = sum(fault_percentages.values())
        overall_score = max(
            0, 100 - (total_fault_impact / len(fault_percentages)))

        # Swing phase analysis
        phase_analysis = self._analyze_swing_phases(frame_data)

        return {
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'fault_percentages': fault_percentages,
            'primary_issues': primary_issues,
            'overall_score': round(overall_score, 1),
            'swing_phases': phase_analysis,
            'recommendation_priority': [issue['fault'] for issue in primary_issues[:2]]
        }

    def _analyze_swing_phases(self, frame_data: List) -> Dict:
        """Analyze fault distribution across swing phases"""
        phase_faults = {}
        for frame in frame_data:
            phase = frame.get('swing_phase', 'unknown')
            if phase not in phase_faults:
                phase_faults[phase] = []

            faults = frame.get('faults_detected', {})
            detected_faults = [
                name for name, data in faults.items() if data.get('detected', False)]
            phase_faults[phase].extend(detected_faults)

        return phase_faults

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'pose'):
            self.pose.close()

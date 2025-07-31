# progress_tracker.py - Drop this file in your root directory
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
import numpy as np
from pathlib import Path

class ProgressTracker:
    """
    Tracks user progress over time, compares swings, identifies trends.
    Creates a personalized improvement journey for each golfer.
    """
    
    def __init__(self, db_path: str = "swing_progress.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for progress tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_date TEXT,
                golfer_type TEXT,
                experience_level TEXT,
                handicap INTEGER,
                goals TEXT,
                last_active TEXT
            )
        ''')
        
        # Swing analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swing_analyses (
                analysis_id TEXT PRIMARY KEY,
                user_id TEXT,
                analysis_date TEXT,
                video_path TEXT,
                overall_score REAL,
                fault_percentages TEXT,  -- JSON string
                primary_issues TEXT,     -- JSON string
                coaching_tip TEXT,
                session_notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Progress milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                milestone_id TEXT PRIMARY KEY,
                user_id TEXT,
                milestone_type TEXT,
                milestone_date TEXT,
                description TEXT,
                achievement_data TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Practice sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS practice_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_date TEXT,
                focus_areas TEXT,       -- JSON string
                session_duration INTEGER,
                swings_analyzed INTEGER,
                improvement_notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_or_get_user(self, session_id: str, golfer_type: str = "weekend_player", 
                          experience: str = "intermediate") -> str:
        """Create new user or return existing user ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user exists (using session_id as temporary user_id for demo)
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (session_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Update last active
            cursor.execute("UPDATE users SET last_active = ? WHERE user_id = ?",
                         (datetime.now().isoformat(), session_id))
            conn.commit()
            conn.close()
            return session_id
        
        # Create new user
        cursor.execute('''
            INSERT INTO users (user_id, created_date, golfer_type, experience_level, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), golfer_type, experience, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return session_id
    
    def save_swing_analysis(self, user_id: str, analysis_result: Dict, 
                           coaching_tip: str, video_path: str) -> str:
        """Save swing analysis results for progress tracking"""
        analysis_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO swing_analyses 
            (analysis_id, user_id, analysis_date, video_path, overall_score, 
             fault_percentages, primary_issues, coaching_tip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id,
            user_id,
            datetime.now().isoformat(),
            video_path,
            analysis_result.get('overall_score', 0),
            json.dumps(analysis_result.get('fault_percentages', {})),
            json.dumps(analysis_result.get('primary_issues', [])),
            coaching_tip
        ))
        
        conn.commit()
        conn.close()
        
        # Check for milestones
        self._check_and_create_milestones(user_id, analysis_result)
        
        return analysis_id
    
    def get_user_progress(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive user progress data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent analyses
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT analysis_date, overall_score, fault_percentages, primary_issues, coaching_tip
            FROM swing_analyses 
            WHERE user_id = ? AND analysis_date > ?
            ORDER BY analysis_date DESC
        ''', (user_id, cutoff_date))
        
        analyses = cursor.fetchall()
        
        if not analyses:
            conn.close()
            return self._get_empty_progress_response()
        
        # Process progress data
        progress_data = self._calculate_progress_metrics(analyses)
        
        # Get milestones
        cursor.execute('''
            SELECT milestone_type, milestone_date, description
            FROM milestones 
            WHERE user_id = ? AND milestone_date > ?
            ORDER BY milestone_date DESC
        ''', (user_id, cutoff_date))
        
        milestones = cursor.fetchall()
        
        conn.close()
        
        return {
            'user_id': user_id,
            'total_swings': len(analyses),
            'days_tracked': days,
            'progress_metrics': progress_data,
            'recent_milestones': [
                {
                    'type': milestone[0],
                    'date': milestone[1],
                    'description': milestone[2]
                } for milestone in milestones
            ],
            'improvement_trend': self._calculate_improvement_trend(analyses),
            'next_focus_areas': self._recommend_focus_areas(analyses)
        }
    
    def compare_swings(self, user_id: str, limit: int = 5) -> Dict:
        """Compare recent swings to show improvement patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT analysis_date, overall_score, fault_percentages, primary_issues
            FROM swing_analyses 
            WHERE user_id = ?
            ORDER BY analysis_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        analyses = cursor.fetchall()
        conn.close()
        
        if len(analyses) < 2:
            return {'comparison_available': False, 'message': 'Need at least 2 swings to compare'}
        
        # Compare latest vs previous
        latest = analyses[0]
        previous = analyses[1]
        
        latest_faults = json.loads(latest[2])
        previous_faults = json.loads(previous[2])
        
        improvements = []
        regressions = []
        
        for fault, latest_pct in latest_faults.items():
            previous_pct = previous_faults.get(fault, 0)
            difference = previous_pct - latest_pct  # Positive = improvement
            
            if difference > 5:  # 5% improvement threshold
                improvements.append({
                    'fault': fault.replace('_', ' ').title(),
                    'improvement': difference,
                    'description': f"Reduced {fault.replace('_', ' ')} by {difference:.1f}%"
                })
            elif difference < -5:  # 5% regression threshold
                regressions.append({
                    'fault': fault.replace('_', ' ').title(),
                    'regression': abs(difference),
                    'description': f"Increased {fault.replace('_', ' ')} by {abs(difference):.1f}%"
                })
        
        score_change = latest[1] - previous[1]
        
        return {
            'comparison_available': True,
            'latest_score': latest[1],
            'previous_score': previous[1],
            'score_change': score_change,
            'improvements': improvements,
            'regressions': regressions,
            'overall_trend': 'improving' if score_change > 2 else 'declining' if score_change < -2 else 'stable',
            'swing_count': len(analyses)
        }
    
    def get_practice_recommendations(self, user_id: str) -> Dict:
        """Generate personalized practice recommendations based on history"""
        progress = self.get_user_progress(user_id, days=14)  # Last 2 weeks
        
        if progress['total_swings'] == 0:
            return self._get_beginner_recommendations()
        
        # Analyze consistent problem areas
        fault_frequency = {}
        for metric in progress['progress_metrics']:
            for fault, percentage in metric['faults'].items():
                if fault not in fault_frequency:
                    fault_frequency[fault] = []
                fault_frequency[fault].append(percentage)
        
        # Find persistent issues
        persistent_issues = []
        for fault, percentages in fault_frequency.items():
            if len(percentages) >= 3:  # At least 3 occurrences
                avg_percentage = np.mean(percentages)
                if avg_percentage > 15:  # Persistent issue threshold
                    persistent_issues.append({
                        'fault': fault,
                        'average_percentage': avg_percentage,
                        'frequency': len(percentages)
                    })
        
        # Sort by severity
        persistent_issues.sort(key=lambda x: x['average_percentage'], reverse=True)
        
        # Generate practice plan
        practice_plan = self._create_practice_plan(persistent_issues[:3])
        
        return {
            'user_id': user_id,
            'analysis_period': '14 days',
            'persistent_issues': persistent_issues[:3],
            'practice_plan': practice_plan,
            'estimated_improvement_time': self._estimate_improvement_time(persistent_issues)
        }
    
    def _calculate_progress_metrics(self, analyses: List) -> List[Dict]:
        """Calculate detailed progress metrics from analyses"""
        metrics = []
        
        for analysis in analyses:
            date, score, fault_json, issues_json, tip = analysis
            faults = json.loads(fault_json)
            issues = json.loads(issues_json)
            
            metrics.append({
                'date': date,
                'overall_score': score,
                'faults': faults,
                'primary_issues': issues,
                'coaching_tip': tip
            })
        
        return metrics
    
    def _calculate_improvement_trend(self, analyses: List) -> str:
        """Calculate overall improvement trend"""
        if len(analyses) < 3:
            return 'insufficient_data'
        
        scores = [analysis[1] for analysis in analyses]  # overall_score is index 1
        scores.reverse()  # Oldest to newest
        
        # Simple linear trend
        x = list(range(len(scores)))
        trend = np.polyfit(x, scores, 1)[0]  # Slope of trend line
        
        if trend > 1:
            return 'improving'
        elif trend < -1:
            return 'declining'
        else:
            return 'stable'
    
    def _recommend_focus_areas(self, analyses: List) -> List[str]:
        """Recommend areas to focus on based on recent performance"""
        if not analyses:
            return ['basic_fundamentals']
        
        # Get most recent primary issues
        latest_issues = json.loads(analyses[0][3])  # primary_issues is index 3
        
        focus_areas = []
        for issue in latest_issues[:2]:  # Top 2 issues
            fault_name = issue.get('fault', '')
            focus_areas.append(fault_name.replace('_', ' ').title())
        
        return focus_areas if focus_areas else ['tempo_and_rhythm']
    
    def _check_and_create_milestones(self, user_id: str, analysis_result: Dict):
        """Check for achievement milestones and create them"""
        overall_score = analysis_result.get('overall_score', 0)
        
        milestones_to_check = [
            (70, 'first_good_swing', 'First swing with 70+ overall score!'),
            (80, 'great_swing', 'Excellent swing with 80+ score!'),
            (90, 'outstanding_swing', 'Outstanding swing technique!'),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for score_threshold, milestone_type, description in milestones_to_check:
            if overall_score >= score_threshold:
                # Check if milestone already exists
                cursor.execute('''
                    SELECT COUNT(*) FROM milestones 
                    WHERE user_id = ? AND milestone_type = ?
                ''', (user_id, milestone_type))
                
                if cursor.fetchone()[0] == 0:  # Milestone doesn't exist
                    cursor.execute('''
                        INSERT INTO milestones (milestone_id, user_id, milestone_type, milestone_date, description)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (str(uuid.uuid4()), user_id, milestone_type, datetime.now().isoformat(), description))
        
        conn.commit()
        conn.close()
    
    def _create_practice_plan(self, persistent_issues: List) -> Dict:
        """Create personalized practice plan based on issues"""
        if not persistent_issues:
            return self._get_maintenance_plan()
        
        primary_issue = persistent_issues[0]['fault']
        
        practice_plans = {
            'trail_arm_collapse': {
                'focus': 'Trail Arm Extension',
                'drills': [
                    'Practice slow-motion swings focusing on keeping right arm extended',
                    'Use alignment stick across chest for connection drill',
                    'Practice "pushing heavy door" feel during backswing'
                ],
                'duration': '15-20 minutes',
                'frequency': '3-4 times per week'
            },
            'early_extension': {
                'focus': 'Posture Maintenance',
                'drills': [
                    'Practice swings against a wall to maintain spine angle',
                    'Use chair drill to feel proper hip hinge',
                    'Mirror work focusing on staying in posture'
                ],
                'duration': '10-15 minutes',
                'frequency': '4-5 times per week'
            },
            'over_the_top': {
                'focus': 'Swing Plane',
                'drills': [
                    'Practice "slot" drill with alignment stick',
                    'Work on shallow approach with pump drills',
                    'Use headcover under right armpit drill'
                ],
                'duration': '20-25 minutes',
                'frequency': '3-4 times per week'
            }
        }
        
        return practice_plans.get(primary_issue, self._get_general_plan())
    
    def _get_beginner_recommendations(self) -> Dict:
        """Get recommendations for new users"""
        return {
            'user_id': 'new_user',
            'analysis_period': 'first_time',
            'persistent_issues': [],
            'practice_plan': {
                'focus': 'Fundamentals',
                'drills': [
                    'Practice address position in mirror',
                    'Slow motion swing focusing on balance',
                    'Grip and stance fundamentals'
                ],
                'duration': '10-15 minutes',
                'frequency': 'Daily for first week'
            },
            'estimated_improvement_time': '2-3 weeks for basic improvement'
        }
    
    def _get_maintenance_plan(self) -> Dict:
        """Get maintenance plan for good swings"""
        return {
            'focus': 'Maintenance & Consistency',
            'drills': [
                'Continue current swing pattern',
                'Focus on tempo and rhythm',
                'Practice under pressure situations'
            ],
            'duration': '15-20 minutes',
            'frequency': '2-3 times per week'
        }
    
    def _get_general_plan(self) -> Dict:
        """Get general practice plan"""
        return {
            'focus': 'General Improvement',
            'drills': [
                'Full swing practice with focus on balance',
                'Short swing drills for control',
                'Mirror work for position awareness'
            ],
            'duration': '15-20 minutes',
            'frequency': '3-4 times per week'
        }
    
    def _estimate_improvement_time(self, persistent_issues: List) -> str:
        """Estimate time needed for improvement"""
        if not persistent_issues:
            return '1-2 weeks for consistency'
        
        severity = persistent_issues[0]['average_percentage']
        
        if severity > 50:
            return '4-6 weeks with consistent practice'
        elif severity > 30:
            return '2-4 weeks with regular practice'
        else:
            return '1-2 weeks with focused practice'
    
    def _get_empty_progress_response(self) -> Dict:
        """Get empty progress response for new users"""
        return {
            'total_swings': 0,
            'progress_metrics': [],
            'recent_milestones': [],
            'improvement_trend': 'no_data',
            'next_focus_areas': ['basic_fundamentals']
        }
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get quick user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total swings
        cursor.execute("SELECT COUNT(*) FROM swing_analyses WHERE user_id = ?", (user_id,))
        total_swings = cursor.fetchone()[0]
        
        # Best score
        cursor.execute("SELECT MAX(overall_score) FROM swing_analyses WHERE user_id = ?", (user_id,))
        best_score = cursor.fetchone()[0] or 0
        
        # Recent average (last 5 swings)
        cursor.execute('''
            SELECT AVG(overall_score) FROM (
                SELECT overall_score FROM swing_analyses 
                WHERE user_id = ? 
                ORDER BY analysis_date DESC 
                LIMIT 5
            )
        ''', (user_id,))
        recent_average = cursor.fetchone()[0] or 0
        
        # Days active
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(analysis_date)) 
            FROM swing_analyses WHERE user_id = ?
        ''', (user_id,))
        days_active = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_swings': total_swings,
            'best_score': round(best_score, 1),
            'recent_average': round(recent_average, 1),
            'days_active': days_active,
            'improvement': round(recent_average - (best_score * 0.8), 1) if total_swings > 3 else 0
        } 
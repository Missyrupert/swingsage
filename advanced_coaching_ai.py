# advanced_coaching_ai.py - Drop this file in your root directory
import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

class AdvancedCoachingAI:
    """
    Next-generation AI coaching that provides:
    - Contextual feedback based on user history
    - Progressive learning paths
    - Personalized coaching personality
    - Drill prescriptions
    - Motivational messaging
    - Adaptive difficulty
    """
    
    def __init__(self):
        self.coaching_personalities = self._build_coaching_personalities()
        self.progressive_curricula = self._build_learning_curricula()
        self.drill_database = self._build_drill_database()
        self.motivation_engine = self._build_motivation_engine()
        self.fault_relationships = self._build_fault_relationships()
    
    def generate_coaching_session(self, analysis_result: Dict, user_progress: Dict, 
                                user_profile: Dict) -> Dict:
        """
        Generate comprehensive coaching session with multiple components:
        - Primary coaching message
        - Drill recommendations
        - Progress acknowledgment
        - Motivation/encouragement
        - Next session preview
        """
        
        # Determine coaching personality based on user preferences
        personality = self._select_coaching_personality(user_profile)
        
        # Analyze current performance in context of user history
        performance_context = self._analyze_performance_context(analysis_result, user_progress)
        
        # Generate primary coaching message
        primary_coaching = self._generate_contextual_coaching(
            analysis_result, performance_context, personality, user_profile
        )
        
        # Recommend specific drills
        drill_recommendations = self._recommend_drills(
            analysis_result, user_progress, user_profile
        )
        
        # Generate progress acknowledgment
        progress_message = self._generate_progress_acknowledgment(
            user_progress, performance_context, personality
        )
        
        # Add motivational component
        motivation = self._generate_motivation(
            performance_context, user_profile, personality
        )
        
        # Preview next session focus
        next_session = self._preview_next_session(analysis_result, user_progress)
        
        return {
            'coaching_session': {
                'primary_coaching': primary_coaching,
                'progress_acknowledgment': progress_message,
                'motivation': motivation,
                'personality': personality['name'],
                'session_focus': performance_context['primary_focus']
            },
            'drill_recommendations': drill_recommendations,
            'next_session_preview': next_session,
            'estimated_practice_time': self._estimate_practice_time(drill_recommendations),
            'difficulty_level': performance_context['difficulty_level']
        }
    
    def _select_coaching_personality(self, user_profile: Dict) -> Dict:
        """Select appropriate coaching personality based on user preferences"""
        golfer_type = user_profile.get('golfer_type', 'weekend_player')
        experience = user_profile.get('experience', 'intermediate')
        
        # Personality matching logic
        if golfer_type == 'junior':
            return self.coaching_personalities['encouraging_mentor']
        elif golfer_type == 'competitive':
            return self.coaching_personalities['technical_expert']
        elif golfer_type == 'senior':
            return self.coaching_personalities['patient_guide']
        elif experience == 'beginner':
            return self.coaching_personalities['supportive_teacher']
        else:
            return self.coaching_personalities['friendly_coach']
    
    def _analyze_performance_context(self, analysis_result: Dict, user_progress: Dict) -> Dict:
        """Analyze current performance in context of user's history"""
        current_score = analysis_result.get('overall_score', 0)
        primary_issues = analysis_result.get('primary_issues', [])
        
        # Determine improvement trend
        recent_scores = []
        for metric in user_progress.get('progress_metrics', [])[-5:]:  # Last 5 swings
            recent_scores.append(metric.get('overall_score', 0))
        
        if len(recent_scores) >= 2:
            trend = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
            trend_strength = abs(recent_scores[-1] - recent_scores[0])
        else:
            trend = 'establishing_baseline'
            trend_strength = 0
        
        # Determine session difficulty
        if current_score >= 80:
            difficulty_level = 'refinement'
        elif current_score >= 60:
            difficulty_level = 'intermediate'
        elif current_score >= 40:
            difficulty_level = 'fundamental'
        else:
            difficulty_level = 'basic'
        
        # Identify primary focus area
        if primary_issues:
            primary_focus = primary_issues[0].get('fault', 'general_improvement')
        else:
            primary_focus = 'consistency'
        
        return {
            'current_score': current_score,
            'trend': trend,
            'trend_strength': trend_strength,
            'difficulty_level': difficulty_level,
            'primary_focus': primary_focus,
            'session_number': len(user_progress.get('progress_metrics', [])) + 1,
            'is_breakthrough': current_score > max([m.get('overall_score', 0) for m in user_progress.get('progress_metrics', [])], default=0)
        }
    
    def _generate_contextual_coaching(self, analysis_result: Dict, context: Dict, 
                                    personality: Dict, user_profile: Dict) -> str:
        """Generate sophisticated contextual coaching message"""
        
        # Base coaching for primary issue
        primary_issue = context['primary_focus']
        base_coaching = self._get_advanced_fault_coaching(primary_issue, context['difficulty_level'])
        
        # Add personality flavor
        personality_style = personality['style']
        if personality_style == 'encouraging':
            opener = random.choice([
                "I can see you're really working hard on this!",
                "Your dedication is showing in your swings.",
                "Great effort - let's build on what you're doing well."
            ])
        elif personality_style == 'technical':
            opener = random.choice([
                "Looking at your swing mechanics,",
                "From a technical standpoint,",
                "Analyzing your movement patterns,"
            ])
        elif personality_style == 'supportive':
            opener = random.choice([
                "Remember, every golfer works through these challenges.",
                "You're making progress, even if it doesn't always feel like it.",
                "Let's focus on one thing at a time."
            ])
        else:  # friendly
            opener = random.choice([
                "Hey, nice work out there!",
                "I noticed something interesting in your swing.",
                "Here's what I'm seeing that we can work on together."
            ])
        
        # Add context-specific elements
        if context['is_breakthrough']:
            breakthrough_msg = " That's actually your best swing yet - really solid fundamentals coming together!"
            base_coaching += breakthrough_msg
        
        if context['trend'] == 'improving':
            trend_msg = f" I can see the improvement from your recent sessions - keep this momentum going."
            base_coaching += trend_msg
        elif context['trend'] == 'declining':
            trend_msg = f" Don't worry about the recent numbers - sometimes we need to take a step back to move forward."
            base_coaching += trend_msg
        
        # Add session-specific context
        session_context = ""
        if context['session_number'] == 1:
            session_context = " Since this is our first session together, let's establish a solid foundation."
        elif context['session_number'] < 5:
            session_context = f" We're building good habits together - this is session {context['session_number']}."
        elif context['session_number'] >= 10:
            session_context = f" You've been really consistent with practice - {context['session_number']} sessions shows real commitment!"
        
        return f"{opener} {base_coaching}{session_context}"
    
    def _get_advanced_fault_coaching(self, fault: str, difficulty_level: str) -> str:
        """Get sophisticated fault-specific coaching based on difficulty level"""
        
        coaching_matrix = {
            'trail_arm_collapse': {
                'basic': "Your right arm is folding too early. Think of reaching out to give someone a high-five and hold that position longer.",
                'fundamental': "I see your trail arm collapsing in the backswing. Try this: imagine you're pushing open a heavy door with your right hand - maintain that extension through the first part of your swing.",
                'intermediate': "Your trail arm is losing structure through transition. Focus on maintaining the width in your backswing by keeping that right arm extended until your hands reach about hip height in the downswing.",
                'refinement': "There's some premature trail arm folding that's affecting your power and consistency. Work on maintaining the connection between your arms and torso - think 'wide to narrow' rather than early collapse."
            },
            'early_extension': {
                'basic': "You're standing up too much during your swing. Try to stay bent over like you started - imagine you're looking under a low branch.",
                'fundamental': "I see some early extension - you're coming out of your posture too soon. Practice staying in your spine angle by feeling like your belt buckle stays pointing down toward the ball longer.",
                'intermediate': "Your hip thrust pattern is causing early extension through impact. Focus on rotating your hips rather than pushing them toward the ball - think 'turn, don't thrust.'",
                'refinement': "The early extension is subtle but it's costing you consistency and power. Work on maintaining your spine angle while allowing your hips to turn more aggressively in a rotational pattern."
            },
            'over_the_top': {
                'basic': "Your swing is coming from outside to inside. Try to feel like you're swinging more from the inside - like you're hitting a ball that's behind you.",
                'fundamental': "I see an over-the-top move in your downswing. Focus on dropping your hands and arms down before rotating through impact - think 'drop then turn.'",
                'intermediate': "Your swing plane is getting steep in transition. Work on feeling like your right elbow drops into your side as you start down - this will shallow out your attack angle.",
                'refinement': "The over-the-top pattern is creating inconsistent ball flight. Focus on the sequence: lower body starts, arms drop into the slot, then everything rotates through together."
            }
        }
        
        return coaching_matrix.get(fault, {}).get(difficulty_level, 
            "Let's work on improving your swing fundamentals through focused practice.")
    
    def _recommend_drills(self, analysis_result: Dict, user_progress: Dict, 
                         user_profile: Dict) -> List[Dict]:
        """Recommend specific practice drills based on analysis"""
        primary_issues = analysis_result.get('primary_issues', [])
        if not primary_issues:
            return self._get_maintenance_drills()
        
        primary_fault = primary_issues[0].get('fault', '')
        fault_percentage = primary_issues[0].get('percentage', 0)
        
        # Get drill recommendations for primary fault
        fault_drills = self.drill_database.get(primary_fault, [])
        
        # Select drills based on severity and user level
        recommended_drills = []
        experience = user_profile.get('experience', 'intermediate')
        
        if fault_percentage > 50:  # Severe issue - focus on fundamentals
            recommended_drills = [drill for drill in fault_drills if drill['level'] in ['beginner', 'fundamental']][:2]
        elif fault_percentage > 25:  # Moderate issue
            recommended_drills = [drill for drill in fault_drills if drill['level'] in ['fundamental', 'intermediate']][:3]
        else:  # Minor issue - refinement drills
            recommended_drills = [drill for drill in fault_drills if drill['level'] in ['intermediate', 'advanced']][:2]
        
        # Add progression tracking
        for drill in recommended_drills:
            drill['estimated_improvement_time'] = self._estimate_drill_effectiveness(drill, fault_percentage)
        
        return recommended_drills
    
    def _generate_progress_acknowledgment(self, user_progress: Dict, context: Dict, 
                                        personality: Dict) -> str:
        """Generate personalized progress acknowledgment"""
        total_swings = user_progress.get('total_swings', 0)
        improvement_trend = context.get('trend', 'establishing_baseline')
        
        if total_swings == 0:
            return "Welcome to your golf improvement journey! Every great player started with their first swing."
        
        if improvement_trend == 'improving':
            messages = [
                f"I can see real improvement over your last {min(total_swings, 5)} swings - you're building great habits!",
                f"Your consistency has been getting better - that's {total_swings} swings of valuable data we're working with.",
                f"The upward trend in your scores shows your practice is paying off. Keep it up!"
            ]
        elif improvement_trend == 'declining':
            messages = [
                f"Everyone has ups and downs - with {total_swings} swings recorded, we have great data to help you bounce back.",
                f"Sometimes we need to work through challenges to reach the next level. Your {total_swings} sessions show real commitment.",
                f"Don't let recent scores discourage you - improvement in golf isn't always linear."
            ]
        else:
            messages = [
                f"You've completed {total_swings} analysis sessions - that's dedication to improvement!",
                f"Building a solid foundation with {total_swings} swings of data to guide your practice.",
                f"Consistency is key, and you're showing it with {total_swings} sessions recorded."
            ]
        
        return random.choice(messages)
    
    def _generate_motivation(self, context: Dict, user_profile: Dict, personality: Dict) -> str:
        """Generate personalized motivational message"""
        
        motivational_themes = {
            'breakthrough': [
                "This is what happens when you stick with the process - breakthrough moments like this!",
                "You just proved to yourself that improvement is possible. Build on this feeling!",
                "This is your new baseline - now let's make swings like this more consistent."
            ],
            'steady_progress': [
                "Small improvements compound over time - you're on the right track.",
                "Every session is building toward better golf. Stay patient with the process.",
                "Consistency beats perfection - keep showing up and working at it."
            ],
            'working_through_challenges': [
                "Champions are made by working through exactly these kinds of challenges.",
                "This is where the real improvement happens - in the struggle to get better.",
                "Every great golfer has been where you are right now. Keep pushing forward."
            ],
            'beginner_encouragement': [
                "You're learning one of the most challenging and rewarding sports in the world.",
                "Every golf professional started exactly where you are now. Enjoy the journey!",
                "The fundamentals you're building now will serve you for years to come."
            ]
        }
        
        # Select appropriate theme
        if context.get('is_breakthrough'):
            theme = 'breakthrough'
        elif context.get('trend') == 'improving':
            theme = 'steady_progress'
        elif context.get('trend') == 'declining':
            theme = 'working_through_challenges'
        elif user_profile.get('experience') == 'beginner':
            theme = 'beginner_encouragement'
        else:
            theme = 'steady_progress'
        
        return random.choice(motivational_themes[theme])
    
    def _preview_next_session(self, analysis_result: Dict, user_progress: Dict) -> Dict:
        """Generate preview of what to focus on in next session"""
        primary_issues = analysis_result.get('primary_issues', [])
        
        if not primary_issues:
            return {
                'focus': 'Consistency and rhythm',
                'goal': 'Maintain your solid swing fundamentals',
                'preparation': 'Continue your current practice routine'
            }
        
        primary_fault = primary_issues[0].get('fault', '')
        
        next_session_focuses = {
            'trail_arm_collapse': {
                'focus': 'Arm extension and connection',
                'goal': 'Reduce trail arm collapse by 10-15%',
                'preparation': 'Practice extension drills 2-3 times before next session'
            },
            'early_extension': {
                'focus': 'Posture stability through impact',
                'goal': 'Maintain spine angle longer in downswing',
                'preparation': 'Work on hip rotation vs. hip thrust pattern'
            },
            'over_the_top': {
                'focus': 'Swing plane and approach angle',
                'goal': 'Develop more inside-out swing path',
                'preparation': 'Practice slot drill and inside approach work'
            }
        }
        
        return next_session_focuses.get(primary_fault, {
            'focus': 'General swing improvement',
            'goal': 'Continue building consistent fundamentals',
            'preparation': 'Focus on balance and tempo in practice'
        })
    
    def _estimate_practice_time(self, drill_recommendations: List[Dict]) -> str:
        """Estimate total practice time needed"""
        total_minutes = sum(drill.get('duration_minutes', 10) for drill in drill_recommendations)
        
        if total_minutes <= 15:
            return "10-15 minutes"
        elif total_minutes <= 25:
            return "20-25 minutes"
        elif total_minutes <= 35:
            return "30-35 minutes"
        else:
            return "35-45 minutes"
    
    def _estimate_drill_effectiveness(self, drill: Dict, fault_percentage: float) -> str:
        """Estimate how long drill will take to show results"""
        drill_effectiveness = drill.get('effectiveness', 'medium')
        
        if fault_percentage > 50:  # Severe issue
            if drill_effectiveness == 'high':
                return "2-3 weeks"
            else:
                return "3-4 weeks"
        elif fault_percentage > 25:  # Moderate issue
            if drill_effectiveness == 'high':
                return "1-2 weeks"
            else:
                return "2-3 weeks"
        else:  # Minor issue
            return "1-2 weeks"
    
    def _build_coaching_personalities(self) -> Dict:
        """Build different coaching personality profiles"""
        return {
            'encouraging_mentor': {
                'name': 'Encouraging Mentor',
                'style': 'encouraging',
                'traits': ['supportive', 'patient', 'celebration-focused'],
                'best_for': ['junior', 'beginner', 'confidence-building']
            },
            'technical_expert': {
                'name': 'Technical Expert',
                'style': 'technical',
                'traits': ['analytical', 'precise', 'detail-oriented'],
                'best_for': ['competitive', 'advanced', 'serious-improvement']
            },
            'patient_guide': {
                'name': 'Patient Guide',
                'style': 'supportive',
                'traits': ['understanding', 'gentle', 'wisdom-sharing'],
                'best_for': ['senior', 'recreational', 'stress-free']
            },
            'supportive_teacher': {
                'name': 'Supportive Teacher',
                'style': 'supportive',
                'traits': ['educational', 'patient', 'fundamentals-focused'],
                'best_for': ['beginner', 'learning-focused']
            },
            'friendly_coach': {
                'name': 'Friendly Coach',
                'style': 'friendly',
                'traits': ['conversational', 'relatable', 'motivational'],
                'best_for': ['weekend_player', 'intermediate', 'general']
            }
        }
    
    def _build_drill_database(self) -> Dict:
        """Build comprehensive drill database"""
        return {
            'trail_arm_collapse': [
                {
                    'name': 'Right Arm Extension Drill',
                    'description': 'Practice backswing with focus on maintaining right arm extension',
                    'instructions': 'Take your normal setup. Practice slow backswings, focusing on keeping your right arm extended like you are reaching to shake hands with someone behind you.',
                    'level': 'beginner',
                    'duration_minutes': 10,
                    'effectiveness': 'high',
                    'equipment': 'none'
                },
                {
                    'name': 'Connection Drill with Towel',
                    'description': 'Use towel under both arms to maintain connection',
                    'instructions': 'Place a towel under both armpits. Make practice swings keeping the towel in place to maintain arm connection to body.',
                    'level': 'fundamental',
                    'duration_minutes': 15,
                    'effectiveness': 'high',
                    'equipment': 'towel'
                },
                {
                    'name': 'Wall Drill for Extension',
                    'description': 'Practice extension against wall',
                    'instructions': 'Stand arm\'s length from wall. Practice backswing reaching toward wall with right hand to feel proper extension.',
                    'level': 'intermediate',
                    'duration_minutes': 12,
                    'effectiveness': 'medium',
                    'equipment': 'wall'
                }
            ],
            'early_extension': [
                {
                    'name': 'Chair Drill',
                    'description': 'Practice with chair behind you to maintain posture',
                    'instructions': 'Place chair just behind your backside at address. Practice swings without standing up into the chair.',
                    'level': 'beginner',
                    'duration_minutes': 10,
                    'effectiveness': 'high',
                    'equipment': 'chair'
                },
                {
                    'name': 'Wall Spine Angle Drill',
                    'description': 'Practice maintaining spine angle against wall',
                    'instructions': 'Stand with back against wall in golf posture. Practice rotation while maintaining contact with wall.',
                    'level': 'fundamental',
                    'duration_minutes': 15,
                    'effectiveness': 'high',
                    'equipment': 'wall'
                }
            ],
            'over_the_top': [
                {
                    'name': 'Slot Drill',
                    'description': 'Practice dropping hands into proper slot',
                    'instructions': 'From top of backswing, feel like you drop your hands straight down before rotating through.',
                    'level': 'intermediate',
                    'duration_minutes': 15,
                    'effectiveness': 'high',
                    'equipment': 'none'
                },
                {
                    'name': 'Inside Approach Drill',
                    'description': 'Practice swinging from inside with alignment stick',
                    'instructions': 'Place alignment stick on ground pointing to target. Practice swinging from inside the stick line.',
                    'level': 'fundamental',
                    'duration_minutes': 20,
                    'effectiveness': 'medium',
                    'equipment': 'alignment_stick'
                }
            ]
        }
    
    def _build_motivation_engine(self) -> Dict:
        """Build motivational messaging system"""
        return {
            'achievement_messages': [
                "Outstanding improvement!",
                "That's what I'm talking about!",
                "You're really getting the hang of this!",
                "Excellent work - keep this up!"
            ],
            'encouragement_messages': [
                "Every pro has worked through exactly this challenge",
                "Progress in golf takes patience - you're doing great",
                "Small improvements compound into big changes",
                "Stay committed to the process - results will come"
            ],
            'milestone_celebrations': [
                "This is a breakthrough moment - celebrate it!",
                "You just reached a new level in your golf game!",
                "This is what dedication looks like - amazing work!",
                "Your hard work is paying off in a big way!"
            ]
        }
    
    def _build_fault_relationships(self) -> Dict:
        """Build understanding of how faults relate to each other"""
        return {
            'trail_arm_collapse': {
                'often_causes': ['loss_of_power', 'inconsistent_contact'],
                'often_caused_by': ['poor_setup', 'early_rotation'],
                'compensations': ['over_the_top', 'early_extension']
            },
            'early_extension': {
                'often_causes': ['thin_shots', 'loss_of_power'],
                'often_caused_by': ['poor_hip_movement', 'balance_issues'],
                'compensations': ['over_the_top', 'arm_swing']
            }
        }
    
    def _get_maintenance_drills(self) -> List[Dict]:
        """Get drills for players with good swing fundamentals"""
        return [
            {
                'name': 'Tempo and Rhythm Practice',
                'description': 'Maintain smooth swing tempo',
                'instructions': 'Practice with 3:1 tempo ratio - three counts back, one count down',
                'level': 'maintenance',
                'duration_minutes': 15,
                'effectiveness': 'medium',
                'equipment': 'none'
            },
            {
                'name': 'Balance Drill',
                'description': 'Finish in perfect balance',
                'instructions': 'Practice swings holding finish position for 3 seconds in perfect balance',
                'level': 'maintenance',
                'duration_minutes': 10,
                'effectiveness': 'high',
                'equipment': 'none'
            }
        ]
    
    def _build_learning_curricula(self) -> Dict:
        """Build progressive learning curricula"""
        return {
            'beginner': {
                'stages': ['fundamentals', 'basic_movement', 'coordination'],
                'focus_areas': ['grip', 'stance', 'posture', 'basic_swing']
            },
            'intermediate': {
                'stages': ['consistency', 'power_development', 'shot_shaping'],
                'focus_areas': ['tempo', 'balance', 'weight_shift', 'swing_plane']
            },
            'advanced': {
                'stages': ['refinement', 'specialization', 'mental_game'],
                'focus_areas': ['precision', 'pressure_performance', 'course_management']
            }
        } 
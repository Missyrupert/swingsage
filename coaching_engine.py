"""
Coaching Engine Module for Swing Sage
Handles personalized coaching feedback generation
"""

from typing import Dict
import random

class CoachingEngine:
    def __init__(self):
        self.feedback_database = self._build_feedback_database()
        self.encouragement_phrases = [
            "You're on the right track",
            "I can see the improvement already", 
            "That's a solid foundation to build on",
            "Great effort out there",
            "You're swinging with more confidence"
        ]
    
    def generate_feedback(self, analysis_result: Dict, golfer_type: str = "weekend_player", experience: str = "intermediate") -> str:
        primary_fault = self._identify_primary_fault(analysis_result)
        base_feedback = self._get_fault_feedback(primary_fault, golfer_type, experience)
        return self._personalize_feedback(base_feedback, analysis_result, golfer_type)
    
    def _identify_primary_fault(self, analysis_result: Dict) -> str:
        collapse_pct = analysis_result.get('collapse_percentage', 0)
        posture_pct = analysis_result.get('posture_loss_percentage', 0)
        
        if collapse_pct > 60:
            return "severe_trail_arm_collapse"
        elif posture_pct > 60:
            return "severe_posture_loss"
        elif collapse_pct > 30:
            return "moderate_trail_arm_collapse"
        elif posture_pct > 30:
            return "moderate_posture_loss"
        elif collapse_pct > 15:
            return "mild_trail_arm_collapse"
        elif posture_pct > 15:
            return "mild_posture_loss"
        else:
            return "good_swing"
    
    def _get_fault_feedback(self, fault: str, golfer_type: str, experience: str) -> str:
        fault_feedback = self.feedback_database.get(fault, {})
        feedback = fault_feedback.get(golfer_type) or fault_feedback.get('default') or "Keep working on your swing fundamentals."
        return self._adjust_for_experience(feedback, experience)
    
    def _adjust_for_experience(self, feedback: str, experience: str) -> str:
        if experience == "beginner":
            feedback = feedback.replace("trail arm", "right arm")
            feedback = feedback.replace("posture", "body position")
        return feedback
    
    def _personalize_feedback(self, base_feedback: str, analysis_result: Dict, golfer_type: str) -> str:
        if random.random() < 0.3:
            encouragement = random.choice(self.encouragement_phrases)
            base_feedback = f"{encouragement}! {base_feedback}"
        
        total_frames = analysis_result.get('total_frames', 0)
        if total_frames > 60:
            base_feedback += " I can see you're really committed to getting this right."
        
        return base_feedback
    
    def _build_feedback_database(self) -> Dict:
        return {
            "severe_trail_arm_collapse": {
                "weekend_player": "I notice your right arm is folding quite early in your swing. Try this: imagine you're pushing a heavy door open with your right hand through the entire backswing. This will help you maintain that extension and give you much more power and consistency.",
                "beginner": "Your right arm is bending too much too soon! Think of it like you're reaching to give someone a high-five - keep that arm extended longer. This one change will make your shots much more solid.",
                "junior": "Hey, your arm is collapsing a bit early! Try to keep your right arm straighter, like you're reaching for something on a high shelf. This will help you hit the ball much better!",
                "senior": "I can see your right arm folding early in the swing. A simple feel: imagine you're slowly pushing something heavy away from you. This will help you maintain better arm structure and timing.",
                "competitive": "There's significant trail arm collapse happening through transition. Focus on maintaining that right arm extension deeper into the downswing - think 'wide to narrow' rather than collapsing early.",
                "default": "Your right arm is folding too early in the swing. Try to keep it extended longer, like you're reaching out to shake someone's hand. This will help you hit more consistent shots."
            },
            
            "moderate_trail_arm_collapse": {
                "weekend_player": "Your right arm could stay a bit straighter through the swing. Think about keeping your arms connected to your body - like you're wearing a sweater that's just slightly too tight. This will help you stay more compact and powerful.",
                "beginner": "Good swing overall! Just try to keep your right arm a little straighter for a bit longer. Think of it like you're slowly reaching out to touch something in front of you.",
                "junior": "Nice swing! Just keep that right arm strong for a little longer - it'll help you hit the ball straighter and farther.",
                "senior": "Looking good! Just a small adjustment: try to feel like your right arm stays extended a touch longer. This will help with your timing and contact.",
                "competitive": "There's some trail arm bend showing up in transition. Work on maintaining that structure through the first move down - it'll help your sequence and contact.",
                "default": "Try to keep your right arm extended just a bit longer through the swing. This will help with consistency and power."
            },
            
            "mild_trail_arm_collapse": {
                "weekend_player": "Really solid swing foundation! Just a tiny thing - keep that right arm reaching just a touch longer. You're very close to having something really repeatable here.",
                "beginner": "Great job! Your swing is looking really good. Just think about keeping your arms extended through the whole motion - you're doing most things right!",
                "junior": "Awesome swing! Keep that right arm strong and you'll be hitting it great!",
                "senior": "Excellent form! Just a small detail - maintain that right arm extension just a fraction longer and you'll have even better results.",
                "competitive": "Solid swing mechanics overall. Minor trail arm folding - just maintain that structure a touch longer for optimal sequence.",
                "default": "Nice swing! Just keep that right arm extended a bit longer and you'll see even better results."
            },
            
            "severe_posture_loss": {
                "weekend_player": "I can see you're coming up out of your address posture quite a bit during the swing. Here's a feel that really works: imagine you're looking under a low branch through impact. Stay bent over just like you started. This will transform your contact.",
                "beginner": "You're standing up too much during your swing! Try to stay bent over in the same position you started in. Think of it like you're looking down at the ball the whole time - don't lift your head up too early.",
                "junior": "You're popping up during your swing! Stay down like you're trying to look under something low. Keep your eyes on the ball and stay bent over!",
                "senior": "I notice you're straightening up during the swing. A good feel is to imagine you're staying bent over to look into a short mirror. Maintain that spine angle through impact for much better contact.",
                "competitive": "Significant early extension showing up. Focus on maintaining your address spine angle through impact. Think 'chest down' rather than standing up to the ball.",
                "default": "You're standing up too much during the swing. Try to maintain the same bent-over position you started with throughout the entire swing."
            },
            
            "moderate_posture_loss": {
                "weekend_player": "Your body position is mostly good, but you're straightening up just a little through impact. Try to feel like you're staying bent over the ball longer - like you're afraid you might hit your head on something low above you.",
                "beginner": "Good swing! Just try to stay bent over the ball a little longer. Keep looking down at where the ball was even after you hit it.",
                "junior": "Nice job! Just stay down a little longer - don't pop your head up too fast!",
                "senior": "Looking good! Just maintain that bent-over feeling a touch longer through the swing. This will help your consistency a lot.",
                "competitive": "Some early extension present. Work on maintaining spine angle through impact - think about keeping your chest pointing down longer.",
                "default": "Try to maintain your posture a bit longer through the swing. Stay bent over like you started."
            },
            
            "mild_posture_loss": {
                "weekend_player": "Really nice swing overall! Just the tiniest thing - try to feel like you stay bent over just a fraction longer. You're already swinging really well.",
                "beginner": "Excellent swing! You're doing almost everything right. Just remember to stay looking down at the ball area through your swing.",
                "junior": "Great swing! Just keep your head down a tiny bit longer and you'll be perfect!",
                "senior": "Beautiful swing mechanics! Just a minor detail - hold that spine angle a touch longer for even better contact.",
                "competitive": "Solid swing. Minor posture change through impact - just maintain that spine angle a fraction longer for optimal results.",
                "default": "Great swing! Just maintain your posture a tiny bit longer and you'll have even better results."
            },
            
            "good_swing": {
                "weekend_player": "That's a really solid swing! Your fundamentals look great. Keep practicing this same motion and you'll see consistent improvement. Maybe work on tempo next - smooth and rhythmic swings often produce the best results.",
                "beginner": "Excellent work! Your swing is looking really good. You're doing the important things right. Keep practicing and focus on making smooth, balanced swings.",
                "junior": "Awesome swing! You're doing great! Keep practicing just like this and you'll keep getting better and better!",
                "senior": "Beautiful swing mechanics! You've got the fundamentals down well. Focus on making smooth, controlled swings and you'll keep seeing great results.",
                "competitive": "Solid swing mechanics across the board. Your fundamentals are sound - now it's about consistency and fine-tuning timing. Keep building on this foundation.",
                "default": "Great swing! Your mechanics look solid. Keep practicing this same motion and focus on smooth tempo and balance."
            }
        }

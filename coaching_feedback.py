def get_coaching_tip(fault: str, golfer_type: str = "weekend") -> str:
    """
    Returns a feel-based coaching tip based on the detected fault and user type.
    """
    fault = fault.lower()
    golfer_type = golfer_type.lower()

    advice_map = {
        "trail_arm_collapse": {
            "weekend": "Looks like your trail arm folded a bit early. Try feeling like you're keeping your elbows closer for longer to stay connected.",
            "beginner": "Great swing effort! Try to keep your right arm straighter through the backswing for more control.",
            "competitive": "Trail arm collapse spotted. Try working on maintaining a tighter structure through transition.",
            "junior": "Nice swing! Keep that trail arm strong — it'll help you hit the ball straighter.",
            "senior": "Looks like the trail arm folded a bit. A little more extension will help improve your timing and contact.",
            "default": "Trail arm collapsed slightly. Try keeping the arm extended a bit longer during the backswing."
        },
        "posture_loss": {
            "weekend": "We noticed your posture changed a bit during your swing. Try to keep your spine angle consistent — like you're holding a beach ball under your chest.",
            "beginner": "Try to stay in your setup posture all the way through your swing. It'll help you hit more consistently.",
            "competitive": "There's a slight early extension. Focus on maintaining your spine angle through impact.",
            "junior": "Keep your body still like a statue during the swing — it helps with balance.",
            "senior": "Looks like you came up out of your posture. Staying down just a touch longer can add control.",
            "default": "Posture change detected — try to stay in your setup shape throughout the swing."
        }
    }

    # Fallback logic
    tip = advice_map.get(fault, {}).get(golfer_type)
    if not tip:
        tip = advice_map.get(fault, {}).get("default", "Keep swinging! You're on the right track.")
    return tip 
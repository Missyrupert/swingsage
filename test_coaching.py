from coaching_feedback import get_coaching_tip


def test_coaching_feedback():
    """Test the coaching feedback system with different scenarios"""

    print("🏌️ Swing Sage - Coaching Feedback Test")
    print("=" * 50)

    # Test trail arm collapse for different golfer types
    print("\n📊 Trail Arm Collapse Scenarios:")
    print("-" * 30)

    golfer_types = ["weekend", "beginner", "competitive", "junior", "senior"]

    for golfer_type in golfer_types:
        feedback = get_coaching_tip(
            "trail_arm_collapse", golfer_type=golfer_type)
        print(f"\n🎯 {golfer_type.title()} Golfer:")
        print(f"   {feedback}")

    # Test posture loss for different golfer types
    print("\n📊 Posture Loss Scenarios:")
    print("-" * 30)

    for golfer_type in golfer_types:
        feedback = get_coaching_tip("posture_loss", golfer_type=golfer_type)
        print(f"\n🎯 {golfer_type.title()} Golfer:")
        print(f"   {feedback}")

    # Test unknown fault type
    print("\n📊 Unknown Fault Test:")
    print("-" * 30)
    feedback = get_coaching_tip("unknown_fault", golfer_type="weekend")
    print(f"   {feedback}")

    # Test unknown golfer type
    print("\n📊 Unknown Golfer Type Test:")
    print("-" * 30)
    feedback = get_coaching_tip("trail_arm_collapse", golfer_type="pro")
    print(f"   {feedback}")


if __name__ == "__main__":
    test_coaching_feedback()

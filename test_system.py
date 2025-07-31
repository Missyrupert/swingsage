# test_system.py - Quick system verification
import os
import sys
from pathlib import Path

def test_system_setup():
    """Test that all components are properly installed"""
    print("🧪 Testing Swing Sage System Setup...")
    print("=" * 50)
    
    # Check file structure
    required_files = [
        'app.py',
        'video_processor.py', 
        'coaching_engine.py',
        'utils.py',
        'requirements.txt',
        'templates/landing.html',
        'templates/calibrate.html',
        'templates/upload.html',
        'templates/results.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # Test imports
    print(f"\n🔍 Testing imports...")
    try:
        import cv2
        print("✅ OpenCV")
        
        import mediapipe
        print("✅ MediaPipe") 
        
        import numpy
        print("✅ NumPy")
        
        from flask import Flask
        print("✅ Flask")
        
        # Test our modules
        from video_processor import SwingAnalyzer
        print("✅ SwingAnalyzer")
        
        from coaching_engine import CoachingEngine  
        print("✅ CoachingEngine")
        
        from utils import allowed_file
        print("✅ Utils")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Test directories
    print(f"\n📁 Checking directories...")
    directories = ['user_videos', 'processed_videos']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    print(f"\n🎉 System setup complete!")
    print("🚀 Run: python app.py")
    print("🌐 Open: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = test_system_setup()
    sys.exit(0 if success else 1) 
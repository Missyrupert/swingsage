"""
Vercel Serverless Function Entry Point for Swing Sage
Adapted for serverless deployment
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import time
import uuid

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modular components with graceful fallbacks
try:
    from video_processor import SwingAnalyzer
    from coaching_engine import CoachingEngine
    from utils import cleanup_old_files, allowed_file, handle_video_orientation
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some dependencies not available: {e}")
    MEDIAPIPE_AVAILABLE = False
    # Create dummy classes for serverless environment

    class SwingAnalyzer:
        def analyze_swing(self, input_path, output_path):
            return {
                'total_frames': 0,
                'collapse_frames': 0,
                'collapse_percentage': 0.0,
                'posture_loss_frames': 0,
                'posture_loss_percentage': 0.0,
                'error': 'MediaPipe not available in serverless environment'
            }

    class CoachingEngine:
        def generate_feedback(self, analysis_result, golfer_type="weekend_player", experience="intermediate"):
            return "Video analysis requires MediaPipe which is not available in serverless environment. Please use local deployment for full functionality."

# Create Flask app
app = Flask(__name__)

# Use environment variable for secret key
app.secret_key = os.environ.get('SECRET_KEY', 'swing-sage-secret-change-in-production')

# Configure for serverless environment
app.config['UPLOAD_FOLDER'] = '/tmp/user_videos'
app.config['PROCESSED_FOLDER'] = '/tmp/processed_videos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure directories exist with better error handling
try:
    Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
    Path(app.config['PROCESSED_FOLDER']).mkdir(exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# Initialize components
try:
    swing_analyzer = SwingAnalyzer()
    coaching_engine = CoachingEngine()
except Exception as e:
    print(f"Warning: Could not initialize components: {e}")
    swing_analyzer = None
    coaching_engine = None

@app.route('/')
def index():
    try:
        # Check if template exists
        template_path = os.path.join(app.root_path, 'templates', 'landing.html')
        if not os.path.exists(template_path):
            return jsonify({
                'message': 'Swing Sage Landing Page',
                'status': 'Template not found, but app is running'
            })
        return render_template('landing.html')
    except Exception as e:
        print(f"Index route error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/calibrate')
def calibrate():
    try:
        session['session_id'] = str(uuid.uuid4())
        template_path = os.path.join(app.root_path, 'templates', 'calibrate.html')
        if not os.path.exists(template_path):
            return jsonify({
                'message': 'Calibration page',
                'session_id': session['session_id']
            })
        return render_template('calibrate.html')
    except Exception as e:
        print(f"Calibrate route error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload')
def upload():
    try:
        if 'session_id' not in session:
            return redirect(url_for('calibrate'))
        template_path = os.path.join(app.root_path, 'templates', 'upload.html')
        if not os.path.exists(template_path):
            return jsonify({
                'message': 'Upload page',
                'session_id': session.get('session_id')
            })
        return render_template('upload.html')
    except Exception as e:
        print(f"Upload route error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'session_id' not in session:
            return jsonify({'error': 'Session expired. Please recalibrate.'}), 400

        if 'video' not in request.files:
            return jsonify({'error': 'No video uploaded'}), 400

        file = request.files['video']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large. Maximum 16MB allowed.'}), 400

        # For serverless, return a demo response instead of processing
        return jsonify({
            'success': True,
            'message': 'Video analysis is not available in serverless environment',
            'demo_data': {
                'total_frames': 120,
                'collapse_frames': 15,
                'collapse_percentage': 12.5,
                'posture_loss_frames': 8,
                'posture_loss_percentage': 6.7
            },
            'redirect_url': '/results'
        })

    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

@app.route('/results')
def results():
    try:
        if 'last_analysis' not in session:
            return redirect(url_for('index'))
        template_path = os.path.join(app.root_path, 'templates', 'results.html')
        if not os.path.exists(template_path):
            return jsonify({
                'message': 'Results page',
                'analysis': session.get('last_analysis', {})
            })
        return render_template('results.html', analysis=session['last_analysis'])
    except Exception as e:
        print(f"Results route error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/videos/<filename>')
def serve_video(filename):
    try:
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename)
    except Exception as e:
        print(f"Video serve error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    try:
        return jsonify({
            'message': 'Swing Sage is working!',
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('VERCEL_ENV', 'unknown')
        })
    except Exception as e:
        print(f"Test route error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'mediapipe_available': MEDIAPIPE_AVAILABLE,
            'environment': os.environ.get('VERCEL_ENV', 'unknown')
        })
    except Exception as e:
        print(f"Health route error: {e}")
        return jsonify({'error': str(e)}), 500

# Vercel serverless handler - this is the main entry point for Vercel
def handler(request, context):
    try:
        return app(request, context)
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'body': f'Internal server error: {str(e)}'
        }

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

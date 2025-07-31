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
app.secret_key = 'swing-sage-secret-change-in-production'

# Configure for serverless environment
app.config['UPLOAD_FOLDER'] = '/tmp/user_videos'
app.config['PROCESSED_FOLDER'] = '/tmp/processed_videos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure directories exist
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
        return render_template('landing.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/calibrate')
def calibrate():
    try:
        session['session_id'] = str(uuid.uuid4())
        return render_template('calibrate.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload')
def upload():
    try:
        if 'session_id' not in session:
            return redirect(url_for('calibrate'))
        return render_template('upload.html')
    except Exception as e:
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

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Upload MP4, MOV, or AVI only.'}), 400

        # Generate unique filenames
        session_id = session['session_id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        unique_name = f"{session_id}_{timestamp}_{filename}"

        # Save uploaded file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(upload_path)

        # Handle video orientation
        corrected_path = handle_video_orientation(upload_path)

        # Process the video
        output_path = os.path.join(
            app.config['PROCESSED_FOLDER'], f"analyzed_{unique_name}")
        analysis_result = swing_analyzer.analyze_swing(
            corrected_path, output_path)

        # Get user context
        golfer_type = request.form.get('golfer_type', 'weekend_player')
        experience = request.form.get('experience', 'intermediate')

        # Generate coaching feedback
        coaching_tip = coaching_engine.generate_feedback(
            analysis_result,
            golfer_type=golfer_type,
            experience=experience
        )

        # Store results in session
        session['last_analysis'] = {
            'video_url': f'/videos/{os.path.basename(output_path)}',
            'coaching_tip': coaching_tip,
            'metrics': analysis_result,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
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
        return render_template('results.html', analysis=session['last_analysis'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/videos/<filename>')
def serve_video(filename):
    try:
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test')
def test():
    try:
        return jsonify({
            'message': 'Swing Sage is working!',
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'mediapipe_available': MEDIAPIPE_AVAILABLE
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless handler - this is the main entry point for Vercel


def handler(request, context):
    try:
        return app(request, context)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Internal server error: {str(e)}'
        }


# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

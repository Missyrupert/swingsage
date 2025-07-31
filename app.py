# app.py - COMPLETE REPLACEMENT
import os
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import time
from pathlib import Path

# Import our modular components (create these next)
from video_processor import SwingAnalyzer
from coaching_engine import CoachingEngine
from utils import cleanup_old_files, allowed_file, handle_video_orientation

app = Flask(__name__)
app.secret_key = 'swing-sage-secret-change-in-production'
app.config['UPLOAD_FOLDER'] = 'user_videos'
app.config['PROCESSED_FOLDER'] = 'processed_videos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['PROCESSED_FOLDER']).mkdir(exist_ok=True)

# Initialize components
swing_analyzer = SwingAnalyzer()
coaching_engine = CoachingEngine()

# Background cleanup task


def background_cleanup():
    while True:
        try:
            cleanup_old_files(app.config['UPLOAD_FOLDER'], hours=24)
            cleanup_old_files(app.config['PROCESSED_FOLDER'], hours=48)
        except Exception as e:
            print(f"Cleanup error: {e}")
        time.sleep(3600)


cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/calibrate')
def calibrate():
    session['session_id'] = str(uuid.uuid4())
    return render_template('calibrate.html')


@app.route('/upload')
def upload():
    if 'session_id' not in session:
        return redirect(url_for('calibrate'))
    return render_template('upload.html')


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
    if 'last_analysis' not in session:
        return redirect(url_for('index'))
    return render_template('results.html', analysis=session['last_analysis'])


@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

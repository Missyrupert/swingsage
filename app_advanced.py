# app_advanced.py - REPLACE your current app.py with this enhanced version
import os
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import time
from pathlib import Path

# Import our advanced components
from advanced_swing_analyzer import AdvancedSwingAnalyzer
from advanced_coaching_ai import AdvancedCoachingAI
from progress_tracker import ProgressTracker
from utils import cleanup_old_files, allowed_file, handle_video_orientation

app = Flask(__name__)
app.secret_key = 'swing-sage-advanced-secret-change-in-production'
app.config['UPLOAD_FOLDER'] = 'user_videos'
app.config['PROCESSED_FOLDER'] = 'processed_videos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure directories exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['PROCESSED_FOLDER']).mkdir(exist_ok=True)

# Initialize advanced components
swing_analyzer = AdvancedSwingAnalyzer()
coaching_ai = AdvancedCoachingAI()
progress_tracker = ProgressTracker()

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

        # Process with ADVANCED analyzer
        output_path = os.path.join(
            app.config['PROCESSED_FOLDER'], f"analyzed_{unique_name}")
        analysis_result = swing_analyzer.analyze_swing(
            corrected_path, output_path)

        # Get user context
        golfer_type = request.form.get('golfer_type', 'weekend_player')
        experience = request.form.get('experience', 'intermediate')

        # Create/get user for progress tracking
        user_id = progress_tracker.create_or_get_user(
            session_id, golfer_type, experience)

        # Get user progress history
        user_progress = progress_tracker.get_user_progress(user_id)

        # Create user profile
        user_profile = {
            'golfer_type': golfer_type,
            'experience': experience,
            'user_id': user_id
        }

        # Generate ADVANCED coaching session
        coaching_session = coaching_ai.generate_coaching_session(
            analysis_result,
            user_progress,
            user_profile
        )

        # Save analysis to progress tracker
        analysis_id = progress_tracker.save_swing_analysis(
            user_id,
            analysis_result,
            coaching_session['coaching_session']['primary_coaching'],
            output_path
        )

        # Get swing comparison data
        swing_comparison = progress_tracker.compare_swings(user_id)

        # Get user stats
        user_stats = progress_tracker.get_user_stats(user_id)

        # Store comprehensive results in session
        session['last_analysis'] = {
            'analysis_id': analysis_id,
            'video_url': f'/videos/{os.path.basename(output_path)}',
            'analysis_result': analysis_result,
            'coaching_session': coaching_session,
            'swing_comparison': swing_comparison,
            'user_stats': user_stats,
            'user_progress': user_progress,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'redirect_url': '/results'
        })

    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500


@app.route('/results')
def results():
    if 'last_analysis' not in session:
        return redirect(url_for('index'))
    return render_template('advanced_results.html', data=session['last_analysis'])


@app.route('/progress')
def progress():
    """User progress dashboard"""
    if 'session_id' not in session:
        return redirect(url_for('index'))

    user_id = session['session_id']
    user_progress = progress_tracker.get_user_progress(
        user_id, days=90)  # Last 3 months
    practice_recommendations = progress_tracker.get_practice_recommendations(
        user_id)
    user_stats = progress_tracker.get_user_stats(user_id)

    return render_template('progress_dashboard.html',
                           progress=user_progress,
                           recommendations=practice_recommendations,
                           stats=user_stats)


@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


@app.route('/api/progress/<user_id>')
def api_get_progress(user_id):
    """API endpoint for progress data"""
    try:
        progress = progress_tracker.get_user_progress(user_id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations/<user_id>')
def api_get_recommendations(user_id):
    """API endpoint for practice recommendations"""
    try:
        recommendations = progress_tracker.get_practice_recommendations(
            user_id)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connection
        progress_tracker.get_user_stats("test")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

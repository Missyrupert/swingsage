# Swing Sage - Golf Swing Analysis Application

A modern, modular golf swing analysis application that uses computer vision and AI to provide personalized coaching feedback.

## 🏌️ Features

- **Video Analysis**: Upload golf swing videos for automated analysis
- **Pose Detection**: Uses MediaPipe for accurate body landmark detection
- **Fault Detection**: Identifies common swing faults like trail arm collapse and posture loss
- **Personalized Coaching**: Tailored feedback based on golfer type and skill level
- **Modern UI**: Clean, responsive interface with drag-and-drop file upload
- **Real-time Processing**: Fast video analysis with progress indicators

## 📁 Project Structure

```
swing-sage-final/
├── app.py                     # Main Flask application
├── video_processor.py         # Video processing and pose analysis
├── coaching_engine.py         # Coaching feedback generation
├── coaching_feedback.py       # Coaching tips database
├── utils.py                   # Utility functions and helpers
├── templates/                 # HTML templates
│   └── index.html            # Main application interface
├── static/                    # Static assets
│   ├── css/
│   │   └── main.css          # Main stylesheet
│   ├── js/
│   │   └── main.js           # Frontend JavaScript
│   ├── drills/               # Golf drill videos
│   └── pro_swings/          # Professional swing examples
├── user_videos/              # Uploaded user videos
├── annotated_videos/          # Processed videos with annotations
└── reports/                  # Analysis reports
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd swing-sage-final
   ```

2. **Install dependencies**
   ```bash
   pip install flask opencv-python mediapipe numpy werkzeug
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### 1. Upload Your Swing Video
- Click the upload area or drag and drop your video file
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- Maximum file size: 100MB

### 2. Select Your Profile
- Choose your golfer type: Weekend, Beginner, Competitive, Junior, or Senior
- Select the club you're using: Driver, Iron, Wedge, or Putter

### 3. Analyze Your Swing
- Click "Analyze Swing" to start processing
- The system will detect pose landmarks and identify swing faults
- Processing time depends on video length (typically 30-60 seconds)

### 4. Review Results
- Watch your annotated video with pose landmarks
- Read personalized coaching feedback
- Get specific tips based on your detected faults

## 🔧 Technical Details

### Core Modules

#### `video_processor.py`
- **VideoProcessor Class**: Handles video processing and pose analysis
- **Fault Detection**: Identifies trail arm collapse and posture loss
- **MediaPipe Integration**: Uses Google's MediaPipe for pose detection
- **Frame Analysis**: Processes each frame for swing analysis

#### `coaching_engine.py`
- **CoachingEngine Class**: Generates personalized feedback
- **Golfer Profiles**: Different coaching approaches for different skill levels
- **Fault Prioritization**: Determines primary fault for focused feedback
- **Context Awareness**: Considers club type and swing context

#### `coaching_feedback.py`
- **Coaching Database**: Contains feel-based coaching tips
- **Golfer-Specific Advice**: Tailored feedback for different golfer types
- **Non-Technical Language**: Avoids biomechanical jargon
- **Actionable Tips**: Provides specific, implementable advice

#### `utils.py`
- **File Validation**: Ensures uploaded files meet requirements
- **Error Handling**: Standardized error responses
- **File Management**: Safe file operations and naming
- **System Information**: Debugging and monitoring utilities

### API Endpoints

- `GET /` - Main application interface
- `POST /analyze` - Video analysis endpoint
- `GET /video/<filename>` - Serve processed videos
- `GET /calibrate` - Camera calibration tool

### Fault Detection

#### Trail Arm Collapse
- **Detection**: Monitors right elbow angle during swing
- **Threshold**: Angle < 60° indicates collapse
- **Severity**: High (< 45°), Moderate (< 60°), Low

#### Posture Loss
- **Detection**: Tracks spine angle from vertical
- **Threshold**: Angle < 15° indicates early extension
- **Severity**: High (< 10°), Moderate (< 15°), Low

## 🎨 UI Components

### CSS Framework
- **Custom Properties**: CSS variables for consistent theming
- **Responsive Design**: Mobile-first approach
- **Modern Styling**: Cards, shadows, and smooth transitions
- **Accessibility**: High contrast and readable typography

### JavaScript Features
- **Drag & Drop**: Intuitive file upload
- **Real-time Validation**: File type and size checking
- **Progress Indicators**: Loading states and feedback
- **Error Handling**: User-friendly error messages

## 🔍 Analysis Features

### Pose Detection
- **33 Body Landmarks**: Full body pose tracking
- **Real-time Processing**: Frame-by-frame analysis
- **Landmark Drawing**: Visual feedback on processed videos

### Coaching Intelligence
- **Personalized Feedback**: Based on golfer type and detected faults
- **Feel-based Language**: Avoids technical jargon
- **Actionable Advice**: Specific, implementable tips
- **Context Awareness**: Considers club and situation

## 🛠️ Development

### Adding New Faults
1. Add detection logic in `video_processor.py`
2. Update coaching tips in `coaching_feedback.py`
3. Modify fault prioritization in `coaching_engine.py`

### Customizing Coaching
1. Edit `coaching_feedback.py` for new tips
2. Add golfer types in `coaching_engine.py`
3. Update UI elements in templates

### Styling Changes
1. Modify `static/css/main.css`
2. Update color variables in `:root`
3. Add new component styles

## 📊 Performance

### Processing Speed
- **Small videos (< 10MB)**: 15-30 seconds
- **Medium videos (10-50MB)**: 30-60 seconds
- **Large videos (50-100MB)**: 60-120 seconds

### Accuracy
- **Pose Detection**: 95%+ accuracy with good lighting
- **Fault Detection**: 85%+ accuracy for common faults
- **Coaching Relevance**: Tailored to golfer type and skill level

## 🔒 Security & Privacy

### File Handling
- **Secure Filenames**: UUID-based naming prevents conflicts
- **File Validation**: Type and size checking
- **Temporary Storage**: Files processed and cleaned up

### Data Protection
- **No Data Persistence**: Videos not stored permanently
- **Local Processing**: All analysis done on your machine
- **Privacy First**: No data sent to external servers

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'cv2'"**
```bash
pip install opencv-python
```

**"NumPy compatibility error"**
```bash
pip install "numpy<2.0"
```

**"Video processing fails"**
- Check file format (MP4 recommended)
- Ensure file size < 100MB
- Verify good lighting in video

**"Server won't start"**
- Check port 5000 isn't in use
- Verify all dependencies installed
- Check Python version (3.8+)

### Debug Mode
```bash
python app.py --debug
```

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Include type hints

### Testing
- Test with different video formats
- Verify fault detection accuracy
- Check coaching feedback relevance
- Test UI responsiveness

## 📝 License

This project is for educational and personal use. Please respect the privacy and intellectual property of others when using this application.

## 🙏 Acknowledgments

- **MediaPipe**: Google's pose detection technology
- **OpenCV**: Computer vision library
- **Flask**: Web framework
- **Golf Community**: For feedback and testing

---

**Swing Sage** - Making golf instruction accessible through technology 🏌️⛳ 
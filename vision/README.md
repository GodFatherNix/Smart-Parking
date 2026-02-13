# SmartPark Vision Service - Phase 1 Setup

## Overview

Vision Service is a Python-based vehicle detection and tracking module that processes video feeds for parking management. Phase 1 establishes the foundation with:

- ✅ Project structure
- ✅ Dependencies (YOLOv8, ByteTrack, OpenCV)
- ✅ Configuration system
- ✅ Logging framework
- ✅ Core services (Detector, Tracker, EventHandler)
- ✅ API client for backend integration

## Directory Structure

```
vision/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── detector.py        # YOLOv8 vehicle detector
│   │   ├── tracker.py         # ByteTrack vehicle tracker
│   │   ├── event_handler.py   # Line crossing detection
│   │   └── api_client.py      # Backend API communication
│   └── __init__.py
├── config/
│   └── cameras.json            # Camera configuration
├── models/
│   └── README.md               # Models directory info
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── .gitignore
└── main.py                     # Entry point
```

## Installation

### 1. Prerequisites

- Python 3.10+
- pip package manager

### 2. Create Virtual Environment (Recommended)

```bash
cd vision
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: YOLOv8 and torch can take several minutes to install.

### 4. Download YOLOv8 Model

The YOLOv8 model will auto-download on first run, or manually:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

This creates `~/.cache/ultralytics/` with the model files (~6.3 MB).

## Configuration

### Environment File (.env)

```env
# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_EVENT_ENDPOINT=/events

# Model
MODEL_NAME=yolov8n.pt
MODEL_CONFIDENCE_THRESHOLD=0.5
DEVICE=cpu

# Video Input
VIDEO_INPUT_TYPE=file
VIDEO_INPUT_PATH=./data/sample_video.mp4
VIDEO_FPS=15

# Tracking
TRACKER_TYPE=ByteTrack
TRACKER_TRACK_BUFFER=30

# Camera
CAMERA_ID=cam_001
FLOOR_ID=1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Camera Configuration (config/cameras.json)

```json
{
  "camera_id": "cam_001",
  "floor_id": 1,
  "video_source": "rtsp://camera_ip:554/stream",
  "line_crossing_points": [[0, 360], [1280, 360]]
}
```

## Core Services

### 1. VehicleDetector
Detects vehicles in video frames using YOLOv8.

**Features**:
- Classes: car, motorcycle, bus, truck
- Confidence filtering
- Bounding box extraction
- Centroid calculation

### 2. VehicleTracker
Tracks vehicles across frames using ByteTrack.

**Features**:
- Unique track ID assignment
- Track state management
- Occlusion handling

### 3. EventHandler
Detects line crossing events for entry/exit tracking.

**Features**:
- Configurable crossing line definition
- Direction classification (entry/exit)
- Cross product geometry for accurate detection

### 4. BackendClient
Communicates with backend API for event submission.

**Features**:
- HTTP retry logic
- Batch event submission
- Health checks

## Running the Service

### Start Vision Service

```bash
python main.py
```

**Expected Output**:
```
SmartPark Vision Service Starting
Loading YOLOv8 model from ./models/yolov8n.pt
Model loaded successfully on device: cpu
Initializing ByteTrack tracker...
Initializing event handler...
Initializing backend API client...
Backend health check passed
Vision Service initialized successfully
```

## Testing

### 1. Check Logging

Logs are stored in:
- Console: Real-time output
- File: `./logs/vision_service.log` (configurable)

### 2. Test API Connection

```python
from app.services.api_client import BackendClient
from app.core.config import settings

client = BackendClient(settings.full_api_url)
is_healthy = client.health_check()
print(f"Backend healthy: {is_healthy}")
```

### 3. Test Detection

```python
from app.services.detector import VehicleDetector
import cv2

detector = VehicleDetector("models/yolov8n.pt")
frame = cv2.imread("test_image.jpg")
detections = detector.detect(frame)
print(f"Detected {len(detections)} vehicles")
```

## Dependencies

### Core Vision
- `ultralytics` (8.0.235) - YOLOv8 implementation
- `opencv-python` (4.8.1) - Image processing
- `torch` (2.1.2) - PyTorch ML framework
- `supervision` (0.18.0) - Detection utilities & ByteTrack

### Utilities
- `numpy` - Numerical computing
- `requests` - HTTP client
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation

## Troubleshooting

### Issue: CUDA/GPU Not Available
**Solution**: Model uses CPU by default. Set `DEVICE=cpu` in `.env`

### Issue: Model Download Fails
**Solution**: 
```bash
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Issue: API Connection Errors
**Solution**: Ensure backend is running on http://localhost:8000

### Issue: Memory Issues
**Solution**: Use smaller model `yolov8n.pt` or reduce frame resolution

## Phase 2 - Next Steps

- Implement video frame acquisition (RTSP/MP4)
- Develop complete processing pipeline
- Add frame rate regulation
- Implement local event logging
- Add retry and persistence mechanisms

## Development Notes

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Use logging instead of print statements

### Adding Features
1. Create service in `app/services/`
2. Add configuration to `app/core/config.py`
3. Update `main.py` to initialize service
4. Add tests in `tests/` (Phase 2)

## Architecture

```
Video Input (RTSP/MP4)
        ↓
   [Detector] → YOLOv8 Vehicle Detection
        ↓
   [Tracker] → ByteTrack Vehicle Tracking
        ↓
 [EventHandler] → Line Crossing Detection
        ↓
  [APIClient] → Backend Event Submission
```

## Performance

**Expected Performance** (on CPU):
- Detection: 30-50ms per frame
- Tracking: 5-10ms per frame
- Event processing: 2-5ms per frame
- Total: ~50-60ms per frame (~15 FPS)

## Support

For issues or questions:
1. Check logs: `./logs/vision_service.log`
2. Enable debug mode: `DEBUG=true` in `.env`
3. Review component docstrings in `app/services/`

---

**Status**: Phase 1 ✅ Complete
**Next**: Phase 2 - Video Processing Pipeline

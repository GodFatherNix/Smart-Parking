# Vision Service Models Directory

This directory stores pre-trained machine learning models used for vehicle detection.

## Models

### YOLOv8 (yolov8n.pt)
- **Size**: Nano model (~6.3 MB)
- **Inference Time**: ~30-50ms per frame on CPU
- **Detection Classes**: car, motorcycle, bus, truck

Download the model from Ultralytics:
```bash
python -m pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"  # Auto-downloads
```

Or manually download from: https://github.com/ultralytics/assets/releases

**Note**: Do not commit model files to git (already in .gitignore)

"""Configuration Management for Vision Service"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # API Configuration
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    BACKEND_EVENT_ENDPOINT: str = os.getenv("BACKEND_EVENT_ENDPOINT", "/event")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "5"))
    API_RETRY_ATTEMPTS: int = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    API_RETRY_DELAY: int = int(os.getenv("API_RETRY_DELAY", "1"))
    EVENT_LOCAL_LOG_PATH: str = os.getenv("EVENT_LOCAL_LOG_PATH", "./logs/events_local.jsonl")
    EVENT_QUEUE_PATH: str = os.getenv("EVENT_QUEUE_PATH", "./logs/events_queue.jsonl")
    EVENT_FLUSH_INTERVAL_FRAMES: int = int(os.getenv("EVENT_FLUSH_INTERVAL_FRAMES", "30"))
    EVENT_FLUSH_BATCH_SIZE: int = int(os.getenv("EVENT_FLUSH_BATCH_SIZE", "100"))
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "yolov8n.pt")
    MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "../../models", MODEL_NAME)
    MODEL_CONFIDENCE_THRESHOLD: float = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.5"))
    MODEL_IOU_THRESHOLD: float = float(os.getenv("MODEL_IOU_THRESHOLD", "0.45"))
    DEVICE: str = os.getenv("DEVICE", "cpu")
    MODEL_TARGET_CLASSES: str = os.getenv("MODEL_TARGET_CLASSES", "car,motorcycle,bus,truck")
    DETECTION_VISUALIZE: bool = os.getenv("DETECTION_VISUALIZE", "false").lower() == "true"
    
    # Video Input Configuration
    VIDEO_INPUT_TYPE: str = os.getenv("VIDEO_INPUT_TYPE", "file")  # file or rtsp
    VIDEO_INPUT_PATH: str = os.getenv("VIDEO_INPUT_PATH", "./data/sample_video.mp4")
    VIDEO_FPS: int = int(os.getenv("VIDEO_FPS", "15"))
    VIDEO_FRAME_WIDTH: int = int(os.getenv("VIDEO_FRAME_WIDTH", "1280"))
    VIDEO_FRAME_HEIGHT: int = int(os.getenv("VIDEO_FRAME_HEIGHT", "720"))
    VIDEO_RECONNECT_DELAY_SECONDS: float = float(os.getenv("VIDEO_RECONNECT_DELAY_SECONDS", "1.0"))
    MAX_FRAMES: int = int(os.getenv("MAX_FRAMES", "0"))  # 0 means unlimited
    
    # Tracking Configuration
    TRACKER_TYPE: str = os.getenv("TRACKER_TYPE", "ByteTrack")
    TRACKER_CONF_THRESHOLD: float = float(os.getenv("TRACKER_CONF_THRESHOLD", "0.5"))
    TRACKER_TRACK_BUFFER: int = int(os.getenv("TRACKER_TRACK_BUFFER", "30"))
    
    # Camera Configuration
    CAMERA_ID: str = os.getenv("CAMERA_ID", "cam_001")
    FLOOR_ID: int = int(os.getenv("FLOOR_ID", "1"))
    CAMERA_CONFIG_PATH: str = os.getenv("CAMERA_CONFIG_PATH", "./config/cameras.json")
    
    # Line Crossing Configuration
    AREA_THRESHOLD: int = int(os.getenv("AREA_THRESHOLD", "100"))
    EVENT_DUPLICATE_COOLDOWN_FRAMES: int = int(os.getenv("EVENT_DUPLICATE_COOLDOWN_FRAMES", "12"))
    EVENT_OCCLUSION_TOLERANCE_FRAMES: int = int(os.getenv("EVENT_OCCLUSION_TOLERANCE_FRAMES", "20"))
    EVENT_MIN_CROSSING_DISTANCE_PX: int = int(os.getenv("EVENT_MIN_CROSSING_DISTANCE_PX", "5"))
    EVENT_REVERSAL_SUPPRESSION_FRAMES: int = int(os.getenv("EVENT_REVERSAL_SUPPRESSION_FRAMES", "20"))

    # Low-Light Handling
    DARK_FRAME_BRIGHTNESS_THRESHOLD: float = float(os.getenv("DARK_FRAME_BRIGHTNESS_THRESHOLD", "60"))
    LOW_LIGHT_CONFIDENCE_FACTOR: float = float(os.getenv("LOW_LIGHT_CONFIDENCE_FACTOR", "0.8"))
    LOW_LIGHT_MIN_CONFIDENCE: float = float(os.getenv("LOW_LIGHT_MIN_CONFIDENCE", "0.25"))
    LOW_LIGHT_ENHANCE_FRAME: bool = os.getenv("LOW_LIGHT_ENHANCE_FRAME", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/vision_service.log")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or standard
    MONITOR_DASHBOARD_PATH: str = os.getenv("MONITOR_DASHBOARD_PATH", "./logs/monitoring_dashboard.json")
    MONITOR_WRITE_INTERVAL_FRAMES: int = int(os.getenv("MONITOR_WRITE_INTERVAL_FRAMES", "15"))
    BACKEND_HEALTH_CHECK_INTERVAL_FRAMES: int = int(os.getenv("BACKEND_HEALTH_CHECK_INTERVAL_FRAMES", "60"))
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))
    
    # Debug Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SAVE_FRAMES: bool = os.getenv("SAVE_FRAMES", "false").lower() == "true"
    FRAME_OUTPUT_DIR: str = os.getenv("FRAME_OUTPUT_DIR", "./frames/")
    
    def __init__(self):
        """Initialize and validate settings"""
        # Create necessary directories
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        if self.SAVE_FRAMES:
            os.makedirs(self.FRAME_OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
    
    @property
    def full_api_url(self) -> str:
        """Get full API URL for event submission"""
        return f"{self.BACKEND_API_URL}{self.BACKEND_EVENT_ENDPOINT}"

    @property
    def target_class_names(self) -> list[str]:
        """Configured detection class names."""
        return [item.strip().lower() for item in self.MODEL_TARGET_CLASSES.split(",") if item.strip()]


# Global settings instance
settings = Settings()

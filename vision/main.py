"""Main entry point for Vision Service"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json
import time
from pathlib import Path

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.services.detector import VehicleDetector
from app.services.tracker import VehicleTracker
from app.services.event_handler import EventHandler
from app.services.api_client import BackendClient
from app.services.video_source import VideoSource, VideoSourceConfig, FrameRateRegulator
from app.services.monitoring import CameraStatus, PerformanceMonitor

if settings.SENTRY_DSN:
    try:
        import sentry_sdk  # pylint: disable=import-outside-toplevel

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )
        logger.info("Vision Sentry error tracking initialized")
    except Exception as exc:
        logger.warning(f"Vision Sentry initialization skipped: {exc}")


def load_camera_config(config_file: str = "config/cameras.json") -> dict:
    """Load camera configuration"""
    try:
        with open(config_file, 'r') as f:
            cameras = json.load(f)
        logger.info(f"Loaded {len(cameras)} camera configurations")
        return {cam["camera_id"]: cam for cam in cameras}
    except FileNotFoundError:
        logger.warning(f"Camera config not found: {config_file}")
        return {}


def initialize_vision_pipeline(camera_config: Optional[dict] = None):
    """Initialize vision processing pipeline"""
    logger.info("Initializing Vision Service Pipeline")
    logger.info(f"Backend API: {settings.full_api_url}")
    logger.info(f"Model: {settings.MODEL_NAME}")
    logger.info(f"Device: {settings.DEVICE}")
    logger.info(f"Camera ID: {settings.CAMERA_ID}")
    
    try:
        # Initialize components
        logger.info("Loading YOLOv8 detector...")
        detector = VehicleDetector(
            model_path=settings.MODEL_PATH,
            confidence_threshold=settings.MODEL_CONFIDENCE_THRESHOLD,
            iou_threshold=settings.MODEL_IOU_THRESHOLD,
            device=settings.DEVICE,
            target_classes=settings.target_class_names,
            dark_frame_brightness_threshold=settings.DARK_FRAME_BRIGHTNESS_THRESHOLD,
            low_light_confidence_factor=settings.LOW_LIGHT_CONFIDENCE_FACTOR,
            low_light_min_confidence=settings.LOW_LIGHT_MIN_CONFIDENCE,
            low_light_enhance_frame=settings.LOW_LIGHT_ENHANCE_FRAME,
        )
        detector.warm_up(
            frame_width=settings.VIDEO_FRAME_WIDTH,
            frame_height=settings.VIDEO_FRAME_HEIGHT,
        )
        
        logger.info("Initializing ByteTrack tracker...")
        tracker = VehicleTracker(
            track_buffer=settings.TRACKER_TRACK_BUFFER,
            conf_threshold=settings.TRACKER_CONF_THRESHOLD
        )
        
        line_points = [[0, 360], [1280, 360]]
        direction_mapping = {"up": "entry", "down": "exit"}
        camera_id = settings.CAMERA_ID
        floor_id = settings.FLOOR_ID

        if camera_config:
            line_points = camera_config.get("line_crossing_points", line_points)
            direction_mapping = camera_config.get("direction_mapping", direction_mapping)
            camera_id = camera_config.get("camera_id", camera_id)
            floor_id = int(camera_config.get("floor_id", floor_id))

        logger.info("Initializing event handler...")
        event_handler = EventHandler(
            line_points=line_points,
            area_threshold=settings.AREA_THRESHOLD,
            camera_id=camera_id,
            floor_id=floor_id,
            direction_mapping=direction_mapping,
            duplicate_cooldown_frames=settings.EVENT_DUPLICATE_COOLDOWN_FRAMES,
            occlusion_tolerance_frames=settings.EVENT_OCCLUSION_TOLERANCE_FRAMES,
            min_crossing_distance_px=settings.EVENT_MIN_CROSSING_DISTANCE_PX,
            reversal_suppression_frames=settings.EVENT_REVERSAL_SUPPRESSION_FRAMES,
        )
        
        logger.info("Initializing backend API client...")
        api_client = BackendClient(
            api_url=settings.full_api_url,
            timeout=settings.API_TIMEOUT,
            retry_attempts=settings.API_RETRY_ATTEMPTS,
            retry_delay=settings.API_RETRY_DELAY,
            local_log_path=settings.EVENT_LOCAL_LOG_PATH,
            queue_path=settings.EVENT_QUEUE_PATH,
        )
        
        # Health check
        if not api_client.health_check():
            logger.warning("Backend API health check failed - will retry on first event")
        
        return {
            "detector": detector,
            "tracker": tracker,
            "event_handler": event_handler,
            "api_client": api_client,
        }
    
    except Exception as e:
        logger.error(f"Failed to initialize vision pipeline: {e}")
        raise


def initialize_video_source(camera_config: Optional[dict]) -> tuple[VideoSource, FrameRateRegulator]:
    """Initialize frame acquisition components (source + FPS regulator)."""
    source = settings.VIDEO_INPUT_PATH
    source_type = settings.VIDEO_INPUT_TYPE

    if camera_config:
        source = camera_config.get("video_source", source)
        source_type = camera_config.get("video_type", source_type)

    if not source_type:
        source_type = VideoSource.infer_source_type(source)

    source_config = VideoSourceConfig(
        source=source,
        source_type=source_type,
        width=settings.VIDEO_FRAME_WIDTH,
        height=settings.VIDEO_FRAME_HEIGHT,
        target_fps=settings.VIDEO_FPS,
        reconnect_delay_seconds=settings.VIDEO_RECONNECT_DELAY_SECONDS,
    )
    video_source = VideoSource(source_config)
    regulator = FrameRateRegulator(settings.VIDEO_FPS)
    return video_source, regulator


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("SmartPark Vision Service Starting")
    logger.info("=" * 60)
    
    try:
        cameras = load_camera_config(settings.CAMERA_CONFIG_PATH)
        camera_config = cameras.get(settings.CAMERA_ID)

        if camera_config:
            logger.info(
                f"Using camera config: id={camera_config['camera_id']} "
                f"type={camera_config.get('video_type')} "
                f"source={camera_config.get('video_source')}"
            )
        else:
            logger.warning(
                f"No camera config found for {settings.CAMERA_ID}, "
                "falling back to environment VIDEO_INPUT_* settings"
            )

        # Initialize pipeline
        pipeline = initialize_vision_pipeline(camera_config)
        video_source, regulator = initialize_video_source(camera_config)
        camera_status = CameraStatus(
            camera_id=settings.CAMERA_ID,
            source=video_source.config.source,
            status="running",
        )
        monitor = PerformanceMonitor(settings.MONITOR_DASHBOARD_PATH)

        logger.info("Vision Service initialized successfully")
        logger.info("Starting video frame acquisition loop...")

        if not video_source.open():
            raise RuntimeError("Unable to open configured video source")

        frame_count = 0
        started_at = time.time()
        visualization_dir: Optional[Path] = None
        if settings.DETECTION_VISUALIZE and settings.SAVE_FRAMES:
            visualization_dir = Path(settings.FRAME_OUTPUT_DIR)
            visualization_dir.mkdir(parents=True, exist_ok=True)

        while True:
            regulator.tick()
            ok, frame = video_source.read_frame()

            if not ok:
                camera_status.consecutive_read_failures += 1
                camera_status.status = "offline" if camera_status.consecutive_read_failures >= 5 else "degraded"
                logger.warning("No more frames available or source temporarily unavailable")
                # For files, break at EOF. For RTSP, VideoSource already reconnects.
                if video_source.config.source_type == "file":
                    break
                continue
            camera_status.consecutive_read_failures = 0
            camera_status.status = "running"
            camera_status.last_frame_at = time.time()

            frame_count += 1
            detect_start = time.perf_counter()
            detections = pipeline["detector"].detect(frame)
            monitor.record_stage_latency("detect", (time.perf_counter() - detect_start) * 1000)

            track_start = time.perf_counter()
            tracked_objects = pipeline["tracker"].update(detections, frame_count)
            monitor.record_stage_latency("track", (time.perf_counter() - track_start) * 1000)

            event_start = time.perf_counter()
            events = pipeline["event_handler"].process_frame(tracked_objects, frame_count)
            monitor.record_stage_latency("event", (time.perf_counter() - event_start) * 1000)
            pipeline["event_handler"].clear_old_tracks(
                max_age=max(120, settings.TRACKER_TRACK_BUFFER * 2),
                current_frame=frame_count,
            )
            tracking_metrics = pipeline["tracker"].get_tracking_metrics()
            transmitted = 0
            queued = pipeline["api_client"].queue_size()
            monitor.totals["frames"] = frame_count
            monitor.totals["detections"] += len(detections)
            monitor.totals["tracked_objects"] += len(tracked_objects)
            monitor.totals["events_generated"] += len(events)

            # Event transmission: local log first, then submit/queue.
            tx_start = time.perf_counter()
            for event in events:
                if pipeline["api_client"].process_event(event):
                    transmitted += 1
                queued = pipeline["api_client"].queue_size()
            monitor.record_stage_latency("transmit", (time.perf_counter() - tx_start) * 1000)
            monitor.totals["events_transmitted"] += transmitted
            monitor.totals["events_queued"] = queued

            # Graceful recovery: periodically flush queued events.
            if frame_count % max(1, settings.EVENT_FLUSH_INTERVAL_FRAMES) == 0:
                flush_result = pipeline["api_client"].flush_queued_events(
                    max_events=settings.EVENT_FLUSH_BATCH_SIZE
                )
                queued = pipeline["api_client"].queue_size()
                if flush_result["flushed"] or flush_result["failed"]:
                    logger.info(
                        f"Event queue flush: flushed={flush_result['flushed']} "
                        f"failed={flush_result['failed']} remaining={queued}"
                    )

            # Periodic backend connectivity status refresh.
            if frame_count % max(1, settings.BACKEND_HEALTH_CHECK_INTERVAL_FRAMES) == 0:
                pipeline["api_client"].health_check()

            if settings.DETECTION_VISUALIZE:
                try:
                    annotated = pipeline["detector"].visualize_detections(frame, tracked_objects or detections)
                    if visualization_dir is not None:
                        try:
                            import cv2  # pylint: disable=import-outside-toplevel

                            output_path = visualization_dir / f"frame_{frame_count:06d}.jpg"
                            cv2.imwrite(str(output_path), annotated)
                        except ImportError:
                            logger.warning("OpenCV not installed, skipping annotated frame save")
                            visualization_dir = None
                except RuntimeError as exc:
                    logger.warning(str(exc))

            # Phase 4 Step 1 complete: frame acquisition + FPS regulation.
            # Phase 4 Step 2 detection complete: inference pipeline now runs per frame.
            # Phase 4 Step 3 tracking complete: ByteTrack IDs + active track state are updated per frame.
            if frame_count % max(1, settings.VIDEO_FPS) == 0:
                elapsed = max(time.time() - started_at, 1e-6)
                current_fps = frame_count / elapsed
                logger.info(
                    f"Frames acquired: {frame_count} (avg FPS: {current_fps:.2f}) "
                    f"latest detections: {len(detections)} tracked: {len(tracked_objects)} "
                    f"active_tracks: {tracking_metrics['active_tracks']} events: {len(events)} "
                    f"tx_ok: {transmitted} queued: {queued} camera_status: {camera_status.status}"
                )

            if frame_count % max(1, settings.MONITOR_WRITE_INTERVAL_FRAMES) == 0:
                monitor.write_dashboard(
                    frame_count=frame_count,
                    camera=camera_status,
                    backend_online=pipeline["api_client"].is_online,
                    queue_size=queued,
                )

            if settings.MAX_FRAMES > 0 and frame_count >= settings.MAX_FRAMES:
                logger.info(f"Reached MAX_FRAMES={settings.MAX_FRAMES}, stopping acquisition loop")
                break

        video_source.close()
        monitor.write_dashboard(
            frame_count=frame_count,
            camera=camera_status,
            backend_online=pipeline["api_client"].is_online,
            queue_size=pipeline["api_client"].queue_size(),
        )
        logger.info(f"Frame acquisition finished. Total frames read: {frame_count}")

    except KeyboardInterrupt:
        logger.info("Vision Service interrupted by user")
    except Exception as e:
        logger.error(f"Vision Service error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

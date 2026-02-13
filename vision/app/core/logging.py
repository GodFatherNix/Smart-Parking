"""Logging Configuration for Vision Service"""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Optional
from .config import settings


class JSONFormatter(logging.Formatter):
    """JSON Log Formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(name: str = "vision_service") -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if settings.LOG_FORMAT == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        standard_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(standard_formatter)
    
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        if settings.LOG_FORMAT == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            standard_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(standard_formatter)
        
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


# Initialize default logger
logger = setup_logging()

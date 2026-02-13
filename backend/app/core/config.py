from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./smartpark.db"
    database_echo: bool = True
    log_level: str = "INFO"
    log_format: str = "standard"
    log_file: str = "./backend.log"
    api_rate_limit: int = 1000
    api_rate_limit_window_seconds: int = 60
    api_key_header: str = "X-API-Key"
    api_keys: str = "smartpark-dev-key"
    cors_allow_origins: str = "*"
    cors_allow_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_allow_headers: str = "*"
    project_name: str = "SmartPark API"
    debug: bool = False
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.0
    monitoring_history_size: int = 300
    monitoring_error_rate_threshold: float = 0.1
    monitoring_latency_ms_threshold: float = 500.0
    monitoring_low_availability_threshold: int = 5
    vision_frame_dir: str = "../vision/frames"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    def parse_csv_setting(self, raw_value: str) -> list[str]:
        return [item.strip() for item in raw_value.split(",") if item.strip()]


@lru_cache()
def get_settings():
    return Settings()

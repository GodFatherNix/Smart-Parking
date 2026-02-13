import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _clear_backend_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "main" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)


@pytest.fixture()
def app_module(tmp_path, monkeypatch):
    db_path = Path(tmp_path) / "smartpark_test.db"

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("DATABASE_ECHO", "False")
    monkeypatch.setenv("API_KEYS", "test-api-key")
    monkeypatch.setenv("API_RATE_LIMIT", "10000")
    monkeypatch.setenv("API_RATE_LIMIT_WINDOW_SECONDS", "60")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "*")
    monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
    monkeypatch.setenv("CORS_ALLOW_HEADERS", "*")

    _clear_backend_modules()
    main_module = importlib.import_module("main")

    if main_module.create_tables and not main_module.check_tables_exist():
        main_module.create_tables()
    if main_module.seed_floors:
        main_module.seed_floors()
    if main_module.seed_sample_events:
        main_module.seed_sample_events()

    return main_module


@pytest.fixture()
def client(app_module):
    with TestClient(app_module.app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": "test-api-key"}

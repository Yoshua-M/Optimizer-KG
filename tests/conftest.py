import os
from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load .env from project root so integration tests use the same API key as the app."""
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: end-to-end tests that call OpenAI (requires OPENAI_API_KEY)",
    )

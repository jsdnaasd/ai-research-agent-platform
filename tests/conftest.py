import os


os.environ.setdefault("APP_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("APP_TAVILY_API_KEY", "test-key")

import pytest

from app.db import Base, engine
from app import models  # noqa: F401


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

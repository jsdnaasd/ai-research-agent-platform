import os


os.environ.setdefault("APP_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_REDIS_URL", "redis://localhost:6379/0")

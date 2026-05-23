from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable


class _CompatTask:
    def __init__(self, func: Callable[..., Any], name: str) -> None:
        self._func = func
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    def delay(self, *args: Any, **kwargs: Any) -> Any:
        try:
            result = self._func(*args, **kwargs)
            return SimpleNamespace(result=result, failed=False)
        except Exception as exc:  # pragma: no cover - used to mimic async task isolation
            return SimpleNamespace(result=None, failed=True, exception=exc)


class _CompatCelery:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        self.conf = SimpleNamespace(task_always_eager=True)

    def task(self, name: str | None = None, **_kwargs: Any) -> Callable[[Callable[..., Any]], _CompatTask]:
        def decorator(func: Callable[..., Any]) -> _CompatTask:
            return _CompatTask(func, name or func.__name__)

        return decorator


try:
    from celery import Celery as Celery  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised by import path in tests
    Celery = _CompatCelery

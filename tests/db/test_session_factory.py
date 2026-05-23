from sqlalchemy import text

from app.db import SessionLocal


def test_session_factory_executes_simple_query() -> None:
    with SessionLocal() as session:
        value = session.execute(text("select 1")).scalar_one()

    assert value == 1

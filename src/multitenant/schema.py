from __future__ import annotations

from contextlib import contextmanager

from django.db import connection

PUBLIC_SCHEMA_NAME = "public"


def _quote(name: str) -> str:
    return f'"{name}"'


def set_schema(schema_name: str) -> None:
    if connection.vendor != "postgresql":  # pragma: no cover
        return
    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {_quote(schema_name)}, {PUBLIC_SCHEMA_NAME}")
    connection.schema_name = schema_name  # type: ignore[attr-defined]


def get_current_schema() -> str:
    return getattr(connection, "schema_name", PUBLIC_SCHEMA_NAME)


def create_schema(schema_name: str) -> None:
    if connection.vendor != "postgresql":  # pragma: no cover
        return
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_quote(schema_name)}")


def drop_schema(schema_name: str) -> None:
    """Drop a schema (for rollback scenarios)."""
    if connection.vendor != "postgresql":  # pragma: no cover
        return
    with connection.cursor() as cursor:
        cursor.execute(f"DROP SCHEMA IF EXISTS {_quote(schema_name)} CASCADE")


@contextmanager
def schema_context(schema_name: str):
    previous = get_current_schema()
    set_schema(schema_name)
    try:
        yield
    finally:
        set_schema(previous)

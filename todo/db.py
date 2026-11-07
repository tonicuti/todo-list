"""SQLite connection management and task persistence."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

FILTERS = {
    "all": "",
    "active": "WHERE completed = 0",
    "completed": "WHERE completed = 1",
}


def get_db() -> sqlite3.Connection:
    """Return the current request's SQLite connection."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    """Close the request-scoped database connection, if one was opened."""
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    """Create the database directory and schema when the app starts."""
    database_path = Path(current_app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def _to_task(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def list_tasks(filter_name: str) -> list[dict[str, Any]]:
    """Return tasks matching a validated filter, with active tasks first."""
    if filter_name not in FILTERS:
        raise ValueError("Unsupported task filter")

    rows = get_db().execute(
        f"SELECT id, title, completed, created_at, updated_at FROM tasks "
        f"{FILTERS[filter_name]} ORDER BY completed ASC, created_at DESC, id DESC"
    )
    return [_to_task(row) for row in rows.fetchall()]


def create_task(title: str) -> dict[str, Any]:
    """Insert a task and return its persisted representation."""
    connection = get_db()
    cursor = connection.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    connection.commit()
    row = connection.execute(
        "SELECT id, title, completed, created_at, updated_at FROM tasks WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    return _to_task(row)


def update_task(task_id: int, fields: dict[str, Any]) -> dict[str, Any] | None:
    """Apply validated task fields and return the updated task, if found."""
    assignments: list[str] = []
    values: list[Any] = []
    if "title" in fields:
        assignments.append("title = ?")
        values.append(fields["title"])
    if "completed" in fields:
        assignments.append("completed = ?")
        values.append(int(fields["completed"]))

    if not assignments:
        return None

    connection = get_db()
    cursor = connection.execute(
        f"UPDATE tasks SET {', '.join(assignments)}, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (*values, task_id),
    )
    connection.commit()
    if cursor.rowcount == 0:
        return None

    row = connection.execute(
        "SELECT id, title, completed, created_at, updated_at FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    return _to_task(row)


def delete_task(task_id: int) -> bool:
    """Delete one task and report whether it existed."""
    connection = get_db()
    cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    return cursor.rowcount > 0


def init_app(app) -> None:
    """Register database teardown on the Flask application."""
    app.teardown_appcontext(close_db)

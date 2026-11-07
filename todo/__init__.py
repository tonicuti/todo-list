"""Flask application factory and extension setup."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from . import db


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        root_path=str(project_root),
        instance_path=str(project_root / "instance"),
        instance_relative_config=True,
    )
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=16 * 1024,
        DATABASE=os.environ.get(
            "TODO_DATABASE", str(Path(app.instance_path) / "tasks.sqlite3")
        )
    )

    if test_config:
        app.config.update(test_config)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    from .routes import tasks_bp

    app.register_blueprint(tasks_bp)
    with app.app_context():
        db.init_db()

    return app

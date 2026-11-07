"""Flask application factory and extension setup."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from flask import Flask, request

from . import db


def _local_secret_key(instance_path: Path) -> str:
    """Keep a stable random session signing key in the local instance folder."""
    secret_path = instance_path / "secret_key"
    try:
        descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as secret_file:
            secret_file.write(secrets.token_hex(32))

    key = secret_path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("The local session secret is empty.")
    return key


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
        SECRET_KEY=os.environ.get("TODO_SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        DATABASE=os.environ.get(
            "TODO_DATABASE", str(Path(app.instance_path) / "tasks.sqlite3")
        )
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = _local_secret_key(Path(app.instance_path))

    from .auth import auth_bp, get_csrf_token

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": get_csrf_token}

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
        if request.path.startswith("/api/") or request.path in {"/", "/login", "/register", "/logout"}:
            response.headers["Cache-Control"] = "no-store"
        return response

    db.init_app(app)

    from .routes import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    with app.app_context():
        db.init_db()

    return app

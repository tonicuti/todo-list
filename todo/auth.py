"""Account pages, signed sessions, and request protection."""

from __future__ import annotations

import hmac
import re
import secrets
import sqlite3
from functools import wraps

from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


auth_bp = Blueprint("auth", __name__)
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_]{3,30}\Z")


def get_csrf_token() -> str:
    """Return a stable token for the current browser session."""
    token = session.get("_csrf_token")
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def csrf_required(view):
    """Require the session's CSRF token for state-changing requests."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
            expected = session.get("_csrf_token")
            supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
            if (
                not isinstance(expected, str)
                or not isinstance(supplied, str)
                or not hmac.compare_digest(expected, supplied)
            ):
                if request.path.startswith("/api/"):
                    return jsonify({"error": {
                        "code": "CSRF_FAILED",
                        "message": "Session expired. Reload the page and try again.",
                    }}), 403
                abort(400, description="Session expired. Reload the page and try again.")
        return view(*args, **kwargs)

    return wrapped_view


def login_required(view):
    """Require a signed-in account for page and API views."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                return jsonify({"error": {
                    "code": "UNAUTHORIZED",
                    "message": "Log in to manage your tasks.",
                }}), 401
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.before_app_request
def load_logged_in_user() -> None:
    """Resolve the signed session's user ID on each request."""
    user_id = session.get("user_id")
    g.user = db.get_user_by_id(user_id) if isinstance(user_id, int) else None


def _sign_in(user_id: int):
    session.clear()
    session["user_id"] = user_id
    session["_csrf_token"] = secrets.token_urlsafe(32)
    return redirect(url_for("tasks.index"))


@auth_bp.route("/register", methods=("GET", "POST"))
@csrf_required
def register():
    if g.user is not None:
        return redirect(url_for("tasks.index"))

    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not USERNAME_PATTERN.fullmatch(username):
            error = "Use 3–30 letters, numbers, or underscores for the username."
        elif not 8 <= len(password) <= 128:
            error = "Use a password between 8 and 128 characters."
        elif password != confirmation:
            error = "Passwords do not match."
        else:
            try:
                user = db.create_user(username, generate_password_hash(password))
            except sqlite3.IntegrityError:
                error = "That username is already taken."
            else:
                return _sign_in(user["id"])

    return render_template("auth.html", mode="register", error=error, username=username), (
        400 if error else 200
    )


@auth_bp.route("/login", methods=("GET", "POST"))
@csrf_required
def login():
    if g.user is not None:
        return redirect(url_for("tasks.index"))

    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Incorrect username or password."
        else:
            return _sign_in(user["id"])

    return render_template("auth.html", mode="login", error=error, username=username), (
        401 if error else 200
    )


@auth_bp.post("/logout")
@login_required
@csrf_required
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

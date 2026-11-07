"""Page and JSON routes for task management."""

from __future__ import annotations

from flask import Blueprint, g, jsonify, render_template, request

from . import db
from .auth import csrf_required, login_required


tasks_bp = Blueprint("tasks", __name__)
VALID_FILTERS = {"all", "active", "completed"}
VALID_TASK_FIELDS = {"title", "completed"}


def _error(message: str, status: int, code: str = "INVALID_REQUEST"):
    return jsonify({"error": {"code": code, "message": message}}), status


def _json_object():
    if not request.is_json:
        return None, _error("Send a JSON request body.", 400)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, _error("The request body must be a JSON object.", 400)
    return payload, None


def _clean_title(value):
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


@tasks_bp.get("/")
@login_required
def index():
    return render_template("index.html")


@tasks_bp.get("/api/tasks")
@login_required
def get_tasks():
    filter_name = request.args.get("filter", "all")
    if filter_name not in VALID_FILTERS:
        return _error("Filter must be all, active, or completed.", 400)
    return jsonify({"tasks": db.list_tasks(g.user["id"], filter_name)})


@tasks_bp.post("/api/tasks")
@login_required
@csrf_required
def add_task():
    payload, error = _json_object()
    if error:
        return error
    if set(payload) != {"title"}:
        return _error("Provide only a title when creating a task.", 400)

    title = _clean_title(payload["title"])
    if title is None:
        return _error("Task title cannot be empty.", 400, "VALIDATION_ERROR")

    return jsonify(db.create_task(g.user["id"], title)), 201


@tasks_bp.patch("/api/tasks/<int:task_id>")
@login_required
@csrf_required
def edit_task(task_id: int):
    payload, error = _json_object()
    if error:
        return error
    if not payload or not set(payload).issubset(VALID_TASK_FIELDS):
        return _error("Provide a title and/or completed value to update.", 400)

    fields = {}
    if "title" in payload:
        title = _clean_title(payload["title"])
        if title is None:
            return _error("Task title cannot be empty.", 400, "VALIDATION_ERROR")
        fields["title"] = title
    if "completed" in payload:
        if not isinstance(payload["completed"], bool):
            return _error("Completed must be true or false.", 400, "VALIDATION_ERROR")
        fields["completed"] = payload["completed"]

    task = db.update_task(g.user["id"], task_id, fields)
    if task is None:
        return _error("Task not found.", 404, "NOT_FOUND")
    return jsonify(task)


@tasks_bp.delete("/api/tasks/<int:task_id>")
@login_required
@csrf_required
def remove_task(task_id: int):
    if not db.delete_task(g.user["id"], task_id):
        return _error("Task not found.", 404, "NOT_FOUND")
    return "", 204

# To-Do List

A small, responsive task manager built with Flask, SQLite, HTML, CSS, and
vanilla JavaScript. Each account has a private task list stored locally in
SQLite. Tasks remain available after the app is closed.

## Requirements

- Python 3.10 or newer
- `pip` (included with most Python installations)

## Set up

Open a terminal in this project folder and create a virtual environment:

```powershell
py -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux, use:

```sh
source .venv/bin/activate
```

Install Flask:

```sh
python -m pip install -r requirements.txt
```

## Run locally

Start the development server:

```sh
python app.py
```

Open <http://127.0.0.1:5000> in a browser. Stop the server with `Ctrl+C`.

The app creates `instance/tasks.sqlite3` automatically the first time it
starts. On your first visit, choose **Create an account**. The first account
receives any tasks already in the existing database. Later accounts have
separate, empty task lists. Log out to switch accounts.

There is no password recovery flow yet, so keep your password somewhere safe.

If the existing tasks are important, make a copy of `instance/tasks.sqlite3`
while the server is stopped before starting this version. The app adds account
ownership to the database automatically; it does not delete existing tasks.

The database and the randomly generated `instance/secret_key` file are local
and excluded from version control. Keep both files to preserve tasks and
browser sessions across restarts. To store the database elsewhere, set the
`TODO_DATABASE` environment variable to a SQLite file path before starting
the app. You can set `TODO_SECRET_KEY` to provide your own session signing key.

This setup is intended for `localhost` over HTTP. A public deployment would
need HTTPS and `SESSION_COOKIE_SECURE=True`.

## Features

- Add, edit, complete, and delete tasks
- Filter tasks by All, Active, and Completed
- Register, log in, and log out with private task lists
- Responsive layout with keyboard-operable controls
- SQLite persistence across restarts

# To-Do List

A small, responsive task manager built with Flask, SQLite, HTML, CSS, and
vanilla JavaScript. Tasks are stored locally in SQLite and remain available
after the app is closed.

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
starts. This local database contains your tasks and is excluded from version
control. To store it elsewhere, set the `TODO_DATABASE` environment variable
to a SQLite file path before starting the app.

## Features

- Add, edit, complete, and delete tasks
- Filter tasks by All, Active, and Completed
- Responsive layout with keyboard-operable controls
- SQLite persistence across restarts

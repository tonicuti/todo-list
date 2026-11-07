# To-Do List App Design

## Goal

Build a small, responsive browser-based task manager using Python, SQLite,
HTML, CSS, and JavaScript. Tasks must survive app restarts. The project should
be straightforward to initialize and run locally.

## Scope

The app supports:

- Creating a task with a non-empty title.
- Editing a task title.
- Deleting a task.
- Marking tasks complete or active.
- Filtering the visible list by All, Active, or Completed.
- Persisting task records in a local SQLite database.

The app is for a single local user. Authentication, due dates, priorities,
sharing, and external integrations are out of scope.

## Architecture

Use Flask for the local HTTP server and Python's built-in `sqlite3` module for
storage. Keep request routes and database helpers in a small `todo` package.
Serve one HTML page and static CSS/JavaScript from Flask. Browser interactions
use JSON requests to create, update, delete, and toggle tasks; the browser
refreshes the task list after a successful response.

### Proposed codebase structure

```text
todo-list/
├── app.py                 # Flask application entry point
├── todo/
│   ├── __init__.py        # Application factory
│   ├── db.py              # SQLite connection, schema, and task operations
│   └── routes.py          # Page route and task JSON endpoints
├── templates/
│   └── index.html         # Accessible task manager markup
├── static/
│   ├── styles.css         # Responsive interface styles
│   └── app.js             # Browser interactions and rendering
├── requirements.txt       # Flask dependency
├── .gitignore             # Ignore local database and Python artifacts
└── README.md              # Setup and run instructions
```

## Data model

The `tasks` table contains:

- `id`: integer primary key.
- `title`: non-empty text.
- `completed`: integer boolean, defaulting to false.
- `created_at`: timestamp set on creation.
- `updated_at`: timestamp refreshed on edits and completion changes.

Initialize the schema automatically when the application starts. Keep the
database file in a local data location and exclude it from version control.

## HTTP interface

- `GET /`: render the task manager page.
- `GET /api/tasks?filter=all|active|completed`: return matching tasks.
- `POST /api/tasks`: create a task from a JSON title.
- `PATCH /api/tasks/<id>`: update a title and/or completion state.
- `DELETE /api/tasks/<id>`: delete a task.

Validate input on the server. Return JSON errors with appropriate HTTP status
codes for empty or malformed titles, invalid filters, and unknown task IDs.
Use parameterized SQL statements for all task values.

## Interface behavior

Present a clear heading, task entry form, task list, completion controls, edit
and delete actions, and All / Active / Completed filters with the active filter
visually identified. Use semantic labels and keyboard-operable controls.
Styles adapt to narrow and wide browser windows. Display useful feedback when
there are no tasks, when a filter has no matches, or when a request fails.

## Verification and delivery

The implementation should include focused automated checks for database and
route behavior, but execution of the app and tests is excluded from this task
at the user's request. Provide README instructions to create a virtual
environment, install dependencies, and start the Flask development server.

# Local Accounts and Private Tasks Design

## Outcome

Add registration, login, and logout to the existing local Flask app. Each
account sees and changes only its own tasks. The first account created on this
localhost app receives all tasks already stored in `instance/tasks.sqlite3`.

## User flow

- An unauthenticated visitor is redirected from `/` to `/login`.
- `/register` creates an account with a unique username and password, then
  signs that account in.
- `/login` signs in an existing account. `/logout` ends its session.
- The task page shows the signed-in username and a logout control.
- An unauthenticated API request receives JSON 401. A task owned by another
  account is treated as unavailable and returns JSON 404.

## Codebase changes

- `todo/auth.py`: account routes, user loading, login requirement, and CSRF
  validation.
- `todo/db.py`: users table, task ownership migration, account queries, and
  owner-scoped task operations.
- `todo/__init__.py`: stable local secret key, cookie settings, auth blueprint,
  and CSRF template helper.
- `todo/routes.py`: require a session and pass the signed-in user ID to each
  task operation.
- `templates/auth.html`: shared login and registration page.
- `templates/index.html`, `static/app.js`, `static/styles.css`: show the account,
  support logout, and send the CSRF token with task mutations.
- `README.md` and `.gitignore`: explain setup and protect the local secret.

## Storage and migration

Create a `users` table with a case-insensitive unique username and password
hash. Add a nullable `user_id` foreign key to the existing `tasks` table; the
column is nullable only so older tasks can be migrated. When the first user is
registered, one transaction creates that user and assigns all unowned tasks to
it. Every subsequent task query includes the current `user_id`, and all new
tasks are created with that ID. Other accounts never see unowned or foreign
tasks.

## Security choices

- Hash passwords with Werkzeug's `generate_password_hash` and verify with
  `check_password_hash`; never store a raw password.
- Store only the user ID and CSRF token in Flask's signed session cookie. Use a
  random secret key saved in the ignored local `instance` folder so sessions
  survive restarts. Allow an environment variable to override it.
- Require CSRF tokens for registration, login, logout, and task mutations.
- Use HttpOnly and SameSite=Lax session cookies. Keep Secure disabled for the
  requested HTTP localhost setup.
- Validate usernames and password length at the server boundary. Do not reveal
  whether a username or password was incorrect during login.

## Delivery constraint

The user previously requested that the app not be run by the assistant. The
implementation will be reviewed statically, and the README will explain how
to run and check the updated app locally.

## Sources

- Flask authentication tutorial:
  https://flask.palletsprojects.com/en/stable/tutorial/views/
- Flask session and CSRF guidance:
  https://flask.palletsprojects.com/en/stable/web-security/
- Werkzeug password hashing:
  https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security

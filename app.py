"""Development entry point for the To-Do List application."""

from todo import create_app

app = create_app()


if __name__ == "__main__":
    app.run()

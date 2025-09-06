from app.database import create_tables
import app.todo_ui


def startup() -> None:
    # this function is called before the first request
    create_tables()
    app.todo_ui.create()

"""Todo list UI components and functionality."""

from datetime import date
from nicegui import ui
from app.task_service import TaskService
from app.models import TaskCreate, TaskUpdate, TaskPriority


def create():
    """Create the todo list UI page."""

    @ui.page("/")
    def todo_page():
        """Main todo list page."""

        # Apply modern theme
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        # Page header
        with ui.row().classes("w-full items-center justify-between mb-6 p-4 bg-white shadow-sm rounded-lg"):
            ui.label("📝 My Todo List").classes("text-3xl font-bold text-gray-800")
            ui.label("Stay organized and get things done!").classes("text-gray-600")

        # Main container
        with ui.column().classes("max-w-4xl mx-auto p-4 gap-6"):
            # Task creation form
            create_task_form()

            # Task list container
            task_list_container = ui.column().classes("w-full")

            # Load and display tasks
            refresh_task_list(task_list_container)

        # Add custom styles for better aesthetics
        ui.add_head_html("""
        <style>
            .task-card {
                transition: all 0.2s ease;
            }
            .task-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }
            .completed-task {
                opacity: 0.7;
            }
            .priority-urgent { border-left: 4px solid #ef4444; }
            .priority-high { border-left: 4px solid #f59e0b; }
            .priority-medium { border-left: 4px solid #3b82f6; }
            .priority-low { border-left: 4px solid #10b981; }
        </style>
        """)


def create_task_form():
    """Create the task creation form."""

    with ui.card().classes("w-full p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500"):
        ui.label("✨ Add New Task").classes("text-xl font-bold text-gray-800 mb-4")

        with ui.row().classes("w-full gap-4 items-end"):
            # Task title input
            title_input = (
                ui.input(label="Task Title", placeholder="What needs to be done?")
                .classes("flex-1")
                .props("outlined dense")
            )

            # Priority selector
            priority_select = (
                ui.select(
                    label="Priority",
                    options={
                        TaskPriority.LOW: "Low 🟢",
                        TaskPriority.MEDIUM: "Medium 🟡",
                        TaskPriority.HIGH: "High 🟠",
                        TaskPriority.URGENT: "Urgent 🔴",
                    },
                    value=TaskPriority.MEDIUM,
                )
                .classes("w-32")
                .props("outlined dense")
            )

            # Due date picker
            due_date_input = ui.date().classes("w-40").props("outlined dense")

            # Add task button
            ui.button(
                "Add Task",
                icon="add",
                on_click=lambda: add_new_task(title_input, priority_select, due_date_input, description_input),
            ).classes("px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium")

        # Description input (full width)
        description_input = (
            ui.textarea(label="Description (optional)", placeholder="Add more details...")
            .classes("w-full mt-4")
            .props("outlined dense rows=2")
        )

        # Add task button
        ui.button(
            "Add Task",
            icon="add",
            on_click=lambda: add_new_task(title_input, priority_select, due_date_input, description_input),
        ).classes("px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium")


def add_new_task(title_input, priority_select, due_date_input, description_input):
    """Add a new task to the database."""

    title = title_input.value.strip()
    if not title:
        ui.notify("Please enter a task title", type="negative")
        return

    task_service = None
    try:
        task_service = TaskService()

        # Parse due date
        due_date = None
        if due_date_input.value:
            if isinstance(due_date_input.value, str):
                from datetime import datetime

                due_date = datetime.fromisoformat(due_date_input.value).date()
            else:
                due_date = due_date_input.value

        # Get description
        description = description_input.value.strip()

        # Create task
        task_data = TaskCreate(title=title, description=description, priority=priority_select.value, due_date=due_date)

        task = task_service.create_task(task_data)

        # Clear form
        title_input.value = ""
        description_input.value = ""
        due_date_input.value = None
        priority_select.value = TaskPriority.MEDIUM

        ui.notify(f'Task "{task.title}" added successfully!', type="positive")

        # Refresh the page to show new task
        ui.navigate.reload()

    except Exception as e:
        import logging

        logging.error(f"Error adding task: {str(e)}")
        ui.notify(f"Error adding task: {str(e)}", type="negative")
    finally:
        if task_service:
            task_service.close()


def refresh_task_list(container):
    """Refresh the task list display."""

    container.clear()

    task_service = None
    try:
        task_service = TaskService()
        tasks = task_service.get_all_tasks()

        if not tasks:
            # Empty state
            with container:
                with ui.card().classes("w-full p-12 text-center bg-gray-50 border-dashed border-2 border-gray-300"):
                    ui.icon("task_alt", size="4rem").classes("text-gray-400 mb-4")
                    ui.label("No tasks yet!").classes("text-xl text-gray-600 mb-2")
                    ui.label("Add your first task above to get started.").classes("text-gray-500")
            return

        # Group tasks by completion status
        pending_tasks = [t for t in tasks if not t.completed]
        completed_tasks = [t for t in tasks if t.completed]

        # Display pending tasks
        if pending_tasks:
            with container:
                ui.label(f"📋 Pending Tasks ({len(pending_tasks)})").classes(
                    "text-lg font-semibold text-gray-700 mb-3 mt-6"
                )
                for task in pending_tasks:
                    create_task_card(task, container)

        # Display completed tasks
        if completed_tasks:
            with container:
                ui.label(f"✅ Completed Tasks ({len(completed_tasks)})").classes(
                    "text-lg font-semibold text-gray-700 mb-3 mt-6"
                )
                for task in completed_tasks:
                    create_task_card(task, container)

    except Exception as e:
        import logging

        logging.error(f"Error loading tasks: {str(e)}")
        with container:
            ui.notify(f"Error loading tasks: {str(e)}", type="negative")
    finally:
        if task_service:
            task_service.close()


def create_task_card(task, container):
    """Create a task card UI component."""

    # Determine priority styling
    priority_class = f"priority-{task.priority.value}"
    card_classes = f"w-full p-4 task-card {priority_class}"
    if task.completed:
        card_classes += " completed-task bg-gray-50"
    else:
        card_classes += " bg-white shadow-md hover:shadow-lg"

    with container:
        with ui.card().classes(card_classes):
            with ui.row().classes("w-full items-start justify-between"):
                # Left side: checkbox and task info
                with ui.row().classes("flex-1 items-start gap-3"):
                    # Completion checkbox
                    ui.checkbox(
                        value=task.completed, on_change=lambda e, task_id=task.id: toggle_task_completion(task_id)
                    ).classes("mt-1")

                    # Task content
                    with ui.column().classes("flex-1 gap-1"):
                        # Title with strikethrough if completed
                        title_classes = "text-lg font-medium"
                        if task.completed:
                            title_classes += " line-through text-gray-500"
                        else:
                            title_classes += " text-gray-800"

                        ui.label(task.title).classes(title_classes)

                        # Description if present
                        if task.description:
                            desc_classes = "text-sm text-gray-600"
                            if task.completed:
                                desc_classes += " line-through"
                            ui.label(task.description).classes(desc_classes)

                        # Task metadata row
                        with ui.row().classes("gap-4 mt-2"):
                            # Priority badge
                            priority_colors = {
                                TaskPriority.LOW: "bg-green-100 text-green-800",
                                TaskPriority.MEDIUM: "bg-blue-100 text-blue-800",
                                TaskPriority.HIGH: "bg-orange-100 text-orange-800",
                                TaskPriority.URGENT: "bg-red-100 text-red-800",
                            }
                            priority_icons = {
                                TaskPriority.LOW: "🟢",
                                TaskPriority.MEDIUM: "🟡",
                                TaskPriority.HIGH: "🟠",
                                TaskPriority.URGENT: "🔴",
                            }

                            ui.label(f"{priority_icons[task.priority]} {task.priority.value.title()}").classes(
                                f"text-xs px-2 py-1 rounded-full {priority_colors[task.priority]}"
                            )

                            # Due date if present
                            if task.due_date:
                                due_classes = "text-xs px-2 py-1 rounded-full"
                                if task.due_date < date.today() and not task.completed:
                                    due_classes += " bg-red-100 text-red-800"
                                else:
                                    due_classes += " bg-gray-100 text-gray-700"
                                ui.label(f"📅 Due: {task.due_date.strftime('%b %d')}").classes(due_classes)

                # Right side: action buttons
                with ui.row().classes("gap-1"):
                    # Edit button
                    ui.button(icon="edit", on_click=lambda _, task_id=task.id: edit_task_dialog(task_id)).classes(
                        "text-blue-600 hover:bg-blue-50"
                    ).props("flat round size=sm")

                    # Delete button
                    ui.button(icon="delete", on_click=lambda _, task_id=task.id: delete_task_confirm(task_id)).classes(
                        "text-red-600 hover:bg-red-50"
                    ).props("flat round size=sm")


def toggle_task_completion(task_id: int):
    """Toggle task completion status."""

    task_service = None
    try:
        task_service = TaskService()
        updated_task = task_service.toggle_completed(task_id)

        if updated_task:
            status = "completed" if updated_task.completed else "pending"
            ui.notify(f"Task marked as {status}!", type="positive")
            ui.navigate.reload()
        else:
            ui.notify("Task not found", type="negative")

    except Exception as e:
        import logging

        logging.error(f"Error updating task {task_id}: {str(e)}")
        ui.notify(f"Error updating task: {str(e)}", type="negative")
    finally:
        if task_service:
            task_service.close()


async def delete_task_confirm(task_id: int):
    """Show confirmation dialog before deleting task."""

    with ui.dialog() as dialog, ui.card():
        ui.label("🗑️ Delete Task").classes("text-lg font-semibold mb-3")
        ui.label("Are you sure you want to delete this task? This action cannot be undone.").classes("mb-4")

        with ui.row().classes("gap-2 justify-end"):
            ui.button("Cancel", on_click=lambda: dialog.submit("cancel")).props("flat")
            ui.button("Delete", on_click=lambda: dialog.submit("delete"), color="negative")

    result = await dialog

    if result == "delete":
        task_service = None
        try:
            task_service = TaskService()
            success = task_service.delete_task(task_id)

            if success:
                ui.notify("Task deleted successfully!", type="positive")
                ui.navigate.reload()
            else:
                ui.notify("Task not found", type="negative")

        except Exception as e:
            import logging

            logging.error(f"Error deleting task {task_id}: {str(e)}")
            ui.notify(f"Error deleting task: {str(e)}", type="negative")
        finally:
            if task_service:
                task_service.close()


async def edit_task_dialog(task_id: int):
    """Show dialog to edit an existing task."""

    task_service = None
    try:
        task_service = TaskService()
        task = task_service.get_task(task_id)

        if not task:
            ui.notify("Task not found", type="negative")
            return

        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("✏️ Edit Task").classes("text-lg font-semibold mb-4")

            # Edit form fields
            title_input = ui.input(label="Task Title", value=task.title).classes("w-full mb-3").props("outlined")

            description_input = (
                ui.textarea(label="Description", value=task.description or "")
                .classes("w-full mb-3")
                .props("outlined rows=3")
            )

            priority_select = (
                ui.select(
                    label="Priority",
                    options={
                        TaskPriority.LOW: "Low 🟢",
                        TaskPriority.MEDIUM: "Medium 🟡",
                        TaskPriority.HIGH: "High 🟠",
                        TaskPriority.URGENT: "Urgent 🔴",
                    },
                    value=task.priority,
                )
                .classes("w-full mb-3")
                .props("outlined")
            )

            due_date_input = (
                ui.date(value=task.due_date.isoformat() if task.due_date else None)
                .classes("w-full mb-4")
                .props("outlined")
            )

            with ui.row().classes("gap-2 justify-end w-full"):
                ui.button("Cancel", on_click=lambda: dialog.submit("cancel")).props("flat")
                ui.button("Save Changes", on_click=lambda: dialog.submit("save"), color="primary")

        result = await dialog

        if result == "save":
            # Validate and save changes
            title = title_input.value.strip()
            if not title:
                ui.notify("Please enter a task title", type="negative")
                return

            # Parse due date
            due_date = None
            if due_date_input.value:
                if isinstance(due_date_input.value, str):
                    from datetime import datetime

                    due_date = datetime.fromisoformat(due_date_input.value).date()
                else:
                    due_date = due_date_input.value

            # Update task
            update_data = TaskUpdate(
                title=title,
                description=description_input.value.strip(),
                priority=priority_select.value,
                due_date=due_date,
            )

            updated_task = task_service.update_task(task_id, update_data)

            if updated_task:
                ui.notify("Task updated successfully!", type="positive")
                ui.navigate.reload()
            else:
                ui.notify("Error updating task", type="negative")

    except Exception as e:
        import logging

        logging.error(f"Error editing task {task_id}: {str(e)}")
        ui.notify(f"Error editing task: {str(e)}", type="negative")
    finally:
        if task_service:
            task_service.close()

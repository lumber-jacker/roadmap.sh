from datetime import datetime
import json
from pathlib import Path
import sys
import traceback
from typing import List, Dict, Any, Optional, Union

class TaskStorage:
    """Handles persistent storage of tasks in a JSON file."""
    
    def __init__(self) -> None:
        """Initialize the task storage system."""
        self.filename = 'tasks.json'
        storage = Path(self.filename)

        # Initialize with default empty data
        self.data: Dict[str, Any] = {"tasks": [], "count": 0}
        
        if not storage.exists() or storage.stat().st_size == 0:
            # File doesn't exist or is empty, create with defaults
            self._save_data()
        else:
            try:
                with open(self.filename, 'r') as file:
                    data = json.load(file)
                    # Validate expected structure
                    if "tasks" in data and "count" in data:
                        self.data = data
            except json.JSONDecodeError:
                # Invalid JSON, use defaults and save
                self._save_data()
    
    def _save_data(self) -> None:
        """Save current data to the JSON file."""
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)
    
    def new_task(self, description: str) -> int:
        """
        Create a new task with the given description.
        
        Args:
            description: Task description text
            
        Returns:
            ID of the newly created task
        """
        if not description.strip():
            raise ValueError("Task description cannot be empty")
            
        new_count = self.data["count"] + 1
        new_task = {
            "id": new_count,
            "description": description,
            "status": "todo",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": None
        }

        self.data["tasks"].append(new_task)
        self.data["count"] = new_count
        self._save_data()

        return new_count

    def update_task(self, task_id: Union[str, int], description: str = "", status: Optional[str] = None) -> None:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            description: New description (if empty, keep existing)
            status: New status (if None, keep existing)
            
        Raises:
            ValueError: If task_id is invalid or task not found
        """
        try:
            task_id = int(task_id)
        except ValueError:
            raise ValueError(f"Invalid task ID: {task_id}. Must be a number.")
        
        # Check if status is valid when provided
        valid_statuses = ["todo", "in-progress", "done"]
        if status and status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        # Find and update the task
        task_found = False
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task_found = True
                if description:
                    task["description"] = description
                if status:
                    task["status"] = status
                task["updatedAt"] = datetime.now().isoformat()
                break
        
        if not task_found:
            raise ValueError(f"Task with ID {task_id} not found")
        
        self._save_data()

    def delete_task(self, task_id: Union[str, int]) -> None:
        """
        Delete a task by its ID.
        
        Args:
            task_id: ID of the task to delete
            
        Raises:
            ValueError: If task_id is invalid or task not found
        """
        try:
            task_id = int(task_id)
        except ValueError:
            raise ValueError(f"Invalid task ID: {task_id}. Must be a number.")
            
        # Check if task exists
        original_count = len(self.data["tasks"])
        self.data["tasks"] = [task for task in self.data["tasks"] if task["id"] != task_id]
        
        if len(self.data["tasks"]) == original_count:
            raise ValueError(f"Task with ID {task_id} not found")
            
        self._save_data()

    def list_tasks(self, status_filter: str = "") -> None:
        """
        Print a formatted list of tasks, optionally filtered by status.
        
        Args:
            status_filter: Filter tasks by this status, if provided
        """
        tasks = self.data["tasks"]
        
        if not tasks:
            print("No tasks found.")
            return
        
        if status_filter:
            tasks = [task for task in tasks if task["status"] == status_filter]
            if not tasks:
                print(f"No tasks with status '{status_filter}' found.")
                return
        
        # Print header
        print("\n{:<5} {:<30} {:<12} {:<20}".format("ID", "Description", "Status", "Created"))
        print("-" * 70)
        
        # Print each task with formatted date
        for task in tasks:
            created_date = datetime.fromisoformat(task["createdAt"]).strftime("%Y-%m-%d %H:%M")
            
            # Truncate long descriptions with ellipsis
            description = task["description"]
            if len(description) > 27:
                description = description[:27] + "..."
                
            print("{:<5} {:<30} {:<12} {:<20}".format(
                task["id"],
                description,
                task["status"],
                created_date
            ))
        print()  # Add a newline at the end for better readability


class TaskTrackerCli:
    """Command Line Interface for the Task Tracker application."""
    
    def __init__(self) -> None:
        """Initialize the CLI interface."""
        self.task_storage = TaskStorage()
        self.options: List[str] = []

    def add_task(self) -> None:
        """Add a new task with the description provided in options."""
        if not self.options:
            raise ValueError("Missing task description for 'add' command")

        description = self.options[0]
        task_id = self.task_storage.new_task(description)
        print(f"Task added successfully (ID: {task_id})")

    def update_task(self) -> None:
        """Update an existing task with new description."""
        if len(self.options) < 2:
            raise ValueError("Missing task ID or description for 'update' command")

        task_id, description = self.options[0], self.options[1]
        self.task_storage.update_task(task_id, description)
        print(f"Task {task_id} updated successfully")

    def delete_task(self) -> None:
        """Delete an existing task by ID."""
        if not self.options:
            raise ValueError("Missing task ID for 'delete' command")

        task_id = self.options[0]
        self.task_storage.delete_task(task_id)
        print(f"Task {task_id} deleted successfully")

    def mark_task(self, status: str) -> None:
        """Mark a task with the specified status."""
        if not self.options:
            raise ValueError(f"Missing task ID for '{status}' command")

        task_id = self.options[0]
        self.task_storage.update_task(task_id, status=status)
        print(f"Task {task_id} marked as '{status}' successfully")

    def execute(self) -> None:
        """Parse command line arguments and execute the appropriate action."""
        if len(sys.argv) < 2:
            self._print_usage()
            return
            
        action = sys.argv[1]
        self.options = sys.argv[2:]

        try:
            match action:
                case "add":
                    self.add_task()
                case "update":
                    self.update_task()
                case "delete":
                    self.delete_task()
                case "mark-in-progress":
                    self.mark_task("in-progress")
                case "mark-done":
                    self.mark_task("done")
                case "list":
                    status_filter = self.options[0] if self.options else ""
                    self.task_storage.list_tasks(status_filter)
                case _:
                    print(f"Unknown action: {action}")
                    self._print_usage()
        except ValueError as e:
            print(f"Error: {str(e)}")
            
    def _print_usage(self) -> None:
        """Print usage instructions."""
        print("Task Tracker CLI Usage:")
        print("  task-cli add \"Task description\"")
        print("  task-cli update <task_id> \"Updated description\"")
        print("  task-cli delete <task_id>")
        print("  task-cli mark-in-progress <task_id>")
        print("  task-cli mark-done <task_id>")
        print("  task-cli list [done|todo|in-progress]")


def main() -> None:
    """Entry point for the application."""
    task_tracker = TaskTrackerCli()
    
    try:
        task_tracker.execute()
    except Exception as e:
        print(f"Error: {str(e)}")
        if "--debug" in sys.argv:
            print("\nStack trace:")
            print(traceback.format_exc())


if __name__ == "__main__":
    main()

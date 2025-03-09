# Roadmap.sh - Task Tracker CLI

A simple command-line application to track and manage your tasks built with Python.

## Features

- Add, update, and delete tasks
- Mark tasks as in-progress or done
- List all tasks with different filtering options
- Persistent storage using JSON
- Simple command-line interface
- No external dependencies

## Installation

### Using Symbolic Link (Linux/Mac)

1. Clone this repository:

2. Make the script executable:
   ```bash
   chmod +x task_tracker.py
   ```

3. Create a symbolic link to make it available as `task-cli`:
   ```bash
   sudo ln -s "$(pwd)/task_tracker.py" /usr/local/bin/task-cli
   ```

### For Windows Users

Create a batch file named `task-cli.bat` in a directory that's in your PATH:

```batch
@echo off
python path\to\task_tracker.py %*
```

Replace `path\to\task_tracker.py` with the actual path to your script.

## Usage

```bash
# Adding a new task
task-cli add "Buy groceries"
# Output: Task added successfully (ID: 1)

# Updating a task
task-cli update 1 "Buy groceries and cook dinner"

# Deleting a task
task-cli delete 1

# Marking a task as in progress
task-cli mark-in-progress 1

# Marking a task as done
task-cli mark-done 1

# Listing all tasks
task-cli list

# Listing tasks by status
task-cli list done
task-cli list todo
task-cli list in-progress
```

---

- [roadmap.sh - Task Tracker](https://roadmap.sh/projects/task-tracker)

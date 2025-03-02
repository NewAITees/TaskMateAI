# TaskMateAI
## AI/MCP TODO Task Management Application

TaskMateAI is a simple task management application that allows AI to autonomously manage and execute tasks through MCP (Model Context Protocol).

[日本語版 README はこちら](README.md)

## Features

- Task creation and management through MCP
- Subtask support
- Priority-based task processing
- Task progress management and reporting
- Note-taking functionality
- Data persistence via JSON files
- Multiple agent management through agent IDs
- Project-based task organization

## Installation

### Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- WSL (Windows Subsystem for Linux) *for Windows environments

### Installation Steps

1. Clone or download the repository:

```bash
git clone https://github.com/YourUsername/TaskMateAI.git
cd TaskMateAI
```

2. Install required packages:

```bash
uv install -r requirements.txt
```

## Usage

### Starting the Application

In a WSL environment, you can run the application as follows:

```bash
cd /path/to/TaskMateAI/src/TaskMateAI
uv run TaskMateAI
```

### MCP Configuration

Example configuration for use with MCP:

```json
{
    "mcpServers": {
      "TodoApplication": {
        "command": "uv",
        "args": [
          "--directory", 
          "/absolute/path/TaskMateAI",
          "run",
          "TaskMateAI"
        ],
        "env": {},
        "alwaysAllow": [
          "get_tasks", "get_next_task", "create_task", "update_progress", 
          "complete_task", "add_subtask", "update_subtask", "add_note",
          "list_agents", "list_projects"
        ],
        "defaultArguments": {
          "agent_id": "agent_123",
          "project_name": ""
        }
      }
    }
}
```

```json
{
    "mcpServers": {
      "TodoApplication": {
        "command": "wsl.exe",
        "args": [
          "-e", 
          "bash", 
          "-c", 
          "cd /absolute/path/TaskMateAI && /home/user/.local/bin/uv run TaskMateAI"
        ],
        "env": {},
        "alwaysAllow": [
          "get_tasks", "get_next_task", "create_task", "update_progress", 
          "complete_task", "add_subtask", "update_subtask", "add_note",
          "list_agents", "list_projects"
        ],
        "defaultArguments": {
          "agent_id": "agent_123",
          "project_name": ""
        }
      }
    }
}
```

### Available MCP Tools

TaskMateAI provides the following MCP tools:

1. **get_tasks** - Retrieve task list (filterable by status and priority)
2. **get_next_task** - Get the next highest priority task (automatically updates to in-progress status)
3. **create_task** - Create a new task (with subtasks)
4. **update_progress** - Update task progress
5. **complete_task** - Mark a task as complete
6. **add_subtask** - Add a subtask to an existing task
7. **update_subtask** - Update subtask status
8. **add_note** - Add a note to a task
9. **list_agents** - Get a list of available agent IDs
10. **list_projects** - Get a list of projects associated with a specific agent

### Data Format

Tasks are managed with the following structure:

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Detailed task description",
  "priority": 3,
  "status": "todo",  // one of "todo", "in_progress", "done"
  "progress": 0,     // progress percentage 0-100
  "subtasks": [
    {
      "id": 1,
      "description": "Subtask description",
      "status": "todo"  // one of "todo", "in_progress", "done"
    }
  ],
  "notes": [
    {
      "id": 1,
      "content": "Note content",
      "timestamp": "2025-02-28T09:22:53.532808"
    }
  ]
}
```

## Data Storage

Task data is stored in a hierarchical structure:

```
output/
├── tasks.json                  # Default tasks file
├── agent1/
│   ├── tasks.json              # Tasks for agent1
│   ├── project1/
│   │   └── tasks.json          # Tasks for agent1's project1
│   └── project2/
│       └── tasks.json          # Tasks for agent1's project2
└── agent2/
    ├── tasks.json              # Tasks for agent2
    └── projectA/
        └── tasks.json          # Tasks for agent2's projectA
```

## Project Structure

```
TaskMateAI/
├── src/
│   └── TaskMateAI/
│       ├── __init__.py      # Package initialization
│       └── __main__.py      # Main application code
├── output/                  # Data storage directory
│   └── tasks.json           # Task data (auto-generated)
├── tests/                   # Test code directory
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── requirements.txt         # Dependency package list
└── README.md                # This file
```

## Testing

TaskMateAI provides a comprehensive test suite to ensure reliability of all features.

### Test Structure

Tests are organized in the following directory structure:

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Test fixtures definition
├── unit/                 # Unit tests
│   ├── __init__.py
│   ├── test_task_utils.py       # Tests for task-related utilities
│   ├── test_mcp_tools.py        # Tests for MCP tool functionality
│   └── test_agent_projects.py   # Tests for agent and project management
└── integration/          # Integration tests
    └── __init__.py
```

### Types of Tests

1. **Unit Tests**: Verify that individual components of the application function correctly
   - `test_task_utils.py`: Tests basic functionality like task reading/writing and ID generation
   - `test_mcp_tools.py`: Tests MCP tool functionality (creating, updating, completing tasks, etc.)
   - `test_agent_projects.py`: Tests agent ID and project management features

2. **Integration Tests**: Verify that multiple components work correctly together (planned for future expansion)

### Running Tests

You can run tests using the following commands:

1. Run all tests:

```bash
cd /path/to/TaskMateAI
uv run python -m pytest -xvs
```

2. Run a specific test file:

```bash
uv run python -m pytest -xvs tests/unit/test_task_utils.py
```

3. Run a specific test class:

```bash
uv run python -m pytest -xvs tests/unit/test_mcp_tools.py::TestMCPTools
```

4. Run a specific test function:

```bash
uv run python -m pytest -xvs tests/unit/test_task_utils.py::TestTaskUtils::test_read_tasks_with_data
```

Test argument explanation:
- `-x`: Stop testing when an error occurs
- `-v`: Show verbose output
- `-s`: Show standard output during tests

## Planned Improvements

- Add task template functionality
- Implement task dependencies
- Add scheduling features
- Implement tagging system for tasks
- Add milestone tracking

## License

MIT

## Author

[NewAITees](https://github.com/NewAITees)


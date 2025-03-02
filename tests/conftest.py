"""
Test fixtures for TaskMateAI test suite.
"""
import os
import json
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_tasks_file():
    """Create a temporary tasks file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        temp_file.write(json.dumps([]))
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def mock_tasks():
    """Return sample task data for testing."""
    return [
        {
            "id": 1,
            "title": "Test Task 1",
            "description": "Description for test task 1",
            "priority": 3,
            "status": "todo",
            "progress": 0,
            "subtasks": [
                {
                    "id": 1,
                    "description": "Subtask 1",
                    "status": "todo"
                }
            ],
            "notes": []
        },
        {
            "id": 2,
            "title": "Test Task 2",
            "description": "Description for test task 2",
            "priority": 5,
            "status": "in_progress",
            "progress": 50,
            "subtasks": [],
            "notes": [
                {
                    "id": 1,
                    "content": "Sample note",
                    "timestamp": "2023-01-01T12:00:00"
                }
            ]
        },
        {
            "id": 3,
            "title": "Test Task 3",
            "description": "Description for test task 3",
            "priority": 1,
            "status": "done",
            "progress": 100,
            "subtasks": [],
            "notes": []
        }
    ]


@pytest.fixture
def temp_tasks_file_with_data(temp_tasks_file, mock_tasks):
    """Create a temporary tasks file with sample data."""
    with open(temp_tasks_file, 'w') as f:
        json.dump(mock_tasks, f)
    return temp_tasks_file


@pytest.fixture
def mock_output_dir():
    """Create a temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir) 
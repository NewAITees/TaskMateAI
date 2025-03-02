"""
Unit tests for TaskMateAI task utility functions.
"""
import os
import json
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the functions to test
from taskmateai.server import (
    read_tasks, 
    write_tasks, 
    generate_task_id, 
    generate_subtask_id
)


class TestTaskUtils:
    """Tests for task utility functions."""

    def test_read_tasks_empty_file(self, temp_tasks_file):
        """Test reading an empty tasks file."""
        with patch('taskmateai.server.TASKS_FILE', temp_tasks_file):
            tasks = read_tasks()
            assert tasks == []
    
    def test_read_tasks_with_data(self, temp_tasks_file_with_data, mock_tasks):
        """Test reading a tasks file with data."""
        with patch('taskmateai.server.TASKS_FILE', temp_tasks_file_with_data):
            tasks = read_tasks()
            assert tasks == mock_tasks
    
    def test_read_tasks_nonexistent_file(self):
        """Test reading a non-existent tasks file."""
        with patch('taskmateai.server.TASKS_FILE', '/nonexistent/file.json'):
            tasks = read_tasks()
            assert tasks == []
    
    def test_read_tasks_invalid_json(self, temp_tasks_file):
        """Test reading an invalid JSON file."""
        with open(temp_tasks_file, 'w') as f:
            f.write("This is not valid JSON")
        
        with patch('taskmateai.server.TASKS_FILE', temp_tasks_file):
            tasks = read_tasks()
            assert tasks == []
    
    def test_write_tasks(self, temp_tasks_file, mock_tasks):
        """Test writing tasks to a file."""
        with patch('taskmateai.server.TASKS_FILE', temp_tasks_file):
            write_tasks(mock_tasks)
            
            with open(temp_tasks_file, 'r') as f:
                saved_tasks = json.load(f)
            
            assert saved_tasks == mock_tasks
    
    def test_write_tasks_error(self):
        """Test error handling when writing tasks."""
        mock_open = MagicMock(side_effect=Exception("Test error"))
        
        with patch('builtins.open', mock_open):
            with pytest.raises(RuntimeError):
                write_tasks([{"id": 1}])
    
    def test_generate_task_id_empty(self):
        """Test generating a task ID with an empty task list."""
        task_id = generate_task_id([])
        assert task_id == 1
    
    def test_generate_task_id_with_tasks(self):
        """Test generating a task ID with existing tasks."""
        tasks = [{"id": 5}, {"id": 10}, {"id": 3}]
        task_id = generate_task_id(tasks)
        assert task_id == 11  # max(5, 10, 3) + 1
    
    def test_generate_subtask_id_empty(self):
        """Test generating a subtask ID with an empty subtask list."""
        subtask_id = generate_subtask_id([])
        assert subtask_id == 1
    
    def test_generate_subtask_id_with_subtasks(self):
        """Test generating a subtask ID with existing subtasks."""
        subtasks = [{"id": 2}, {"id": 7}, {"id": 1}]
        subtask_id = generate_subtask_id(subtasks)
        assert subtask_id == 8  # max(2, 7, 1) + 1 
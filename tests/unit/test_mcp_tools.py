"""
Unit tests for TaskMateAI MCP tools functionality.
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import functions to test
from taskmateai.server import call_tool, get_tasks_file_path


class TestMCPTools:
    """Tests for MCP tools functionality."""
    
    @pytest.mark.asyncio
    async def test_get_tasks_no_filter(self, temp_tasks_file_with_data, mock_tasks):
        """Test getting all tasks without filtering."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("get_tasks", {})
            assert len(result) == 1
            assert json.loads(result[0].text) == mock_tasks
    
    @pytest.mark.asyncio
    async def test_get_tasks_status_filter(self, temp_tasks_file_with_data, mock_tasks):
        """Test getting tasks filtered by status."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("get_tasks", {"status": "todo"})
            assert len(result) == 1
            
            tasks = json.loads(result[0].text)
            assert len(tasks) == 1
            assert tasks[0]["id"] == 1
            assert tasks[0]["status"] == "todo"
    
    @pytest.mark.asyncio
    async def test_get_tasks_priority_filter(self, temp_tasks_file_with_data, mock_tasks):
        """Test getting tasks filtered by minimum priority."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("get_tasks", {"priority_min": 3})
            assert len(result) == 1
            
            tasks = json.loads(result[0].text)
            assert len(tasks) == 2  # Should get task 1 (priority 3) and task 2 (priority 5)
            assert all(task["priority"] >= 3 for task in tasks)
    
    @pytest.mark.asyncio
    async def test_get_next_task(self, temp_tasks_file_with_data, mock_tasks):
        """Test getting the next highest priority task."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("get_next_task", {})
            assert len(result) == 1
            
            task = json.loads(result[0].text)
            # Should return Task 2 (highest priority = 5)
            assert task["id"] == 2
            
            # Verify the task was updated to in_progress
            updated_tasks = json.load(open(temp_tasks_file_with_data))
            task_2 = next(t for t in updated_tasks if t["id"] == 2)
            assert task_2["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_get_next_task_empty(self, temp_tasks_file):
        """Test getting the next task when there are no tasks."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file):
            result = await call_tool("get_next_task", {})
            assert len(result) == 1
            assert "利用可能なタスクはありません" in result[0].text
    
    @pytest.mark.asyncio
    async def test_create_task(self, temp_tasks_file):
        """Test creating a new task."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file):
            task_data = {
                "title": "Test New Task",
                "description": "Test description",
                "priority": 4,
                "subtasks": ["Subtask 1", "Subtask 2"]
            }
            
            result = await call_tool("create_task", task_data)
            assert len(result) == 1
            assert "作成されました" in result[0].text
            
            # Verify the task was saved
            tasks = json.load(open(temp_tasks_file))
            assert len(tasks) == 1
            assert tasks[0]["title"] == "Test New Task"
            assert tasks[0]["description"] == "Test description"
            assert tasks[0]["priority"] == 4
            assert len(tasks[0]["subtasks"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_task_missing_params(self):
        """Test creating a task with missing required parameters."""
        result = await call_tool("create_task", {"title": "Test Task"})
        assert len(result) == 1
        assert "予期せぬエラーが発生しました" in result[0].text
        assert "Missing required parameters" in result[0].text
    
    @pytest.mark.asyncio
    async def test_update_progress(self, temp_tasks_file_with_data):
        """Test updating task progress."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("update_progress", {"task_id": 1, "progress": 75})
            assert len(result) == 1
            assert "進捗が 75% に更新されました" in result[0].text
            
            # Verify the task was updated
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 1)
            assert task["progress"] == 75
            assert task["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_update_progress_to_100(self, temp_tasks_file_with_data):
        """Test updating task progress to 100% (completion)."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("update_progress", {"task_id": 1, "progress": 100})
            assert len(result) == 1
            assert "進捗が 100% に更新されました" in result[0].text
            
            # Verify the task status was updated to done
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 1)
            assert task["progress"] == 100
            assert task["status"] == "done"
    
    @pytest.mark.asyncio
    async def test_complete_task(self, temp_tasks_file_with_data):
        """Test marking a task as complete."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("complete_task", {"task_id": 1})
            assert len(result) == 1
            assert "完了としてマークされました" in result[0].text
            
            # Verify the task was marked complete
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 1)
            assert task["status"] == "done"
            assert task["progress"] == 100
    
    @pytest.mark.asyncio
    async def test_add_subtask(self, temp_tasks_file_with_data):
        """Test adding a subtask to a task."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("add_subtask", {
                "task_id": 2,
                "description": "New subtask"
            })
            assert len(result) == 1
            assert "サブタスク" in result[0].text
            assert "追加されました" in result[0].text
            
            # Verify the subtask was added
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 2)
            assert len(task["subtasks"]) == 1
            assert task["subtasks"][0]["description"] == "New subtask"
    
    @pytest.mark.asyncio
    async def test_update_subtask(self, temp_tasks_file_with_data):
        """Test updating a subtask status."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("update_subtask", {
                "task_id": 1,
                "subtask_id": 1,
                "status": "done"
            })
            assert len(result) == 1
            assert "サブタスク (ID: 1) のステータスが 'done' に更新されました" in result[0].text
            
            # Verify the subtask was updated
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 1)
            subtask = next(s for s in task["subtasks"] if s["id"] == 1)
            assert subtask["status"] == "done"
            
            # Verify main task progress was updated
            assert task["progress"] == 100
            assert task["status"] == "done"
    
    @pytest.mark.asyncio
    async def test_add_note(self, temp_tasks_file_with_data):
        """Test adding a note to a task."""
        with patch('taskmateai.server.get_tasks_file_path', return_value=temp_tasks_file_with_data):
            result = await call_tool("add_note", {
                "task_id": 1,
                "content": "Test note"
            })
            assert len(result) == 1
            assert "ノートがタスク (ID: 1) に追加されました" in result[0].text
            
            # Verify the note was added
            tasks = json.load(open(temp_tasks_file_with_data))
            task = next(t for t in tasks if t["id"] == 1)
            assert len(task["notes"]) == 1
            assert task["notes"][0]["content"] == "Test note"
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool."""
        with pytest.raises(ValueError):
            await call_tool("unknown_tool", {}) 
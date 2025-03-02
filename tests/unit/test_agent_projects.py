"""
Unit tests for TaskMateAI agent ID and project management functionality.
"""
import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the functions to test (these will be implemented)
from taskmateai.server import (
    get_tasks_file_path,
    read_tasks,
    write_tasks,
    call_tool
)


class TestAgentProjects:
    """Tests for agent ID and project management functionality."""
    
    @pytest.fixture
    def setup_agent_projects_dirs(self):
        """Create and clean up temporary directories for different agents and projects."""
        base_dir = tempfile.mkdtemp()
        
        # Create directories for agents and projects
        agent_dirs = {
            "agent1": ["project1", "project2"],
            "agent2": ["projectA"]
        }
        
        for agent, projects in agent_dirs.items():
            agent_dir = os.path.join(base_dir, agent)
            os.makedirs(agent_dir, exist_ok=True)
            
            for project in projects:
                project_dir = os.path.join(agent_dir, project)
                os.makedirs(project_dir, exist_ok=True)
                
                # Create empty tasks file
                tasks_file = os.path.join(project_dir, "tasks.json")
                with open(tasks_file, 'w') as f:
                    json.dump([], f)
        
        yield base_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(base_dir)
    
    def test_get_tasks_file_path_default(self, mock_output_dir):
        """Test getting tasks file path with default agent and project."""
        with patch('taskmateai.server.OUTPUT_DIR', mock_output_dir):
            path = get_tasks_file_path()
            assert path == os.path.join(mock_output_dir, "tasks.json")
    
    def test_get_tasks_file_path_with_agent(self, mock_output_dir):
        """Test getting tasks file path with a specific agent and default project."""
        with patch('taskmateai.server.OUTPUT_DIR', mock_output_dir):
            path = get_tasks_file_path(agent_id="test_agent")
            assert path == os.path.join(mock_output_dir, "test_agent", "tasks.json")
    
    def test_get_tasks_file_path_with_agent_and_project(self, mock_output_dir):
        """Test getting tasks file path with a specific agent and project."""
        with patch('taskmateai.server.OUTPUT_DIR', mock_output_dir):
            path = get_tasks_file_path(agent_id="test_agent", project_name="test_project")
            assert path == os.path.join(mock_output_dir, "test_agent", "test_project", "tasks.json")
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_agent_id(self, setup_agent_projects_dirs):
        """Test getting tasks with a specific agent ID."""
        test_agent1_task = {
            "id": 1,
            "title": "Agent 1 Task",
            "description": "Task for Agent 1",
            "priority": 3,
            "status": "todo",
            "progress": 0,
            "subtasks": [],
            "notes": []
        }
        
        # Setup a task for agent1/project1
        agent1_project1_path = os.path.join(setup_agent_projects_dirs, "agent1", "project1", "tasks.json")
        with open(agent1_project1_path, 'w') as f:
            json.dump([test_agent1_task], f)
        
        with patch('taskmateai.server.OUTPUT_DIR', setup_agent_projects_dirs):
            result = await call_tool("get_tasks", {"agent_id": "agent1", "project_name": "project1"})
            assert len(result) == 1
            
            tasks = json.loads(result[0].text)
            assert len(tasks) == 1
            assert tasks[0]["title"] == "Agent 1 Task"
    
    @pytest.mark.asyncio
    async def test_create_task_with_agent_id(self, setup_agent_projects_dirs):
        """Test creating a task with a specific agent ID and project."""
        with patch('taskmateai.server.OUTPUT_DIR', setup_agent_projects_dirs):
            task_data = {
                "title": "New Agent Task",
                "description": "Task for a specific agent",
                "priority": 4,
                "agent_id": "agent2",
                "project_name": "projectA"
            }
            
            result = await call_tool("create_task", task_data)
            assert len(result) == 1
            assert "作成されました" in result[0].text
            
            # Verify the task was saved in the correct location
            tasks_file = os.path.join(setup_agent_projects_dirs, "agent2", "projectA", "tasks.json")
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
                
            assert len(tasks) == 1
            assert tasks[0]["title"] == "New Agent Task"
    
    @pytest.mark.asyncio
    async def test_list_agents(self, setup_agent_projects_dirs):
        """Test listing all available agents."""
        with patch('taskmateai.server.OUTPUT_DIR', setup_agent_projects_dirs):
            result = await call_tool("list_agents", {})
            assert len(result) == 1
            
            agents = json.loads(result[0].text)
            assert len(agents) == 2
            assert set(agents) == {"agent1", "agent2"}
    
    @pytest.mark.asyncio
    async def test_list_projects(self, setup_agent_projects_dirs):
        """Test listing projects for a specific agent."""
        with patch('taskmateai.server.OUTPUT_DIR', setup_agent_projects_dirs):
            result = await call_tool("list_projects", {"agent_id": "agent1"})
            assert len(result) == 1
            
            projects = json.loads(result[0].text)
            assert len(projects) == 2
            assert set(projects) == {"project1", "project2"} 
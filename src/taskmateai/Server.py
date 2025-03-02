import os
import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Sequence
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)
from pydantic import AnyUrl

# 環境変数の読み込み
load_dotenv()

# ログの準備
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskmate-server")

# JSONファイルのパス設定
OUTPUT_DIR = "output"
DEFAULT_TASKS_FILE = os.path.join(OUTPUT_DIR, "tasks.json")

# 出力ディレクトリが存在しない場合は作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

# サーバの準備
app = Server("taskmate-server")

# タスクファイルのパスを取得する関数
def get_tasks_file_path(agent_id: Optional[str] = None, project_name: Optional[str] = None) -> str:
    """
    タスクファイルのパスを生成する関数。
    
    Args:
        agent_id: エージェントID（オプション）
        project_name: プロジェクト名（オプション）
        
    Returns:
        str: タスクファイルのパス
    """
    path_components = [OUTPUT_DIR]
    
    if agent_id:
        path_components.append(agent_id)
        
        if project_name:
            path_components.append(project_name)
    
    path_components.append("tasks.json")
    tasks_file_path = os.path.join(*path_components)
    
    # 親ディレクトリが存在することを確認
    os.makedirs(os.path.dirname(tasks_file_path), exist_ok=True)
    
    return tasks_file_path

# JSONファイルから全タスクを読み込む関数
def read_tasks(agent_id: Optional[str] = None, project_name: Optional[str] = None) -> List[Dict]:
    """
    JSONファイルからタスクを読み込む関数。
    
    Args:
        agent_id: エージェントID（オプション）
        project_name: プロジェクト名（オプション）
        
    Returns:
        List[Dict]: タスクのリスト
    """
    tasks_file = get_tasks_file_path(agent_id, project_name)
    
    if not os.path.exists(tasks_file):
        # ファイルが存在しない場合は空のリストを返す
        return []
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error("JSONファイルの解析エラー")
        return []
    except Exception as e:
        logger.error(f"タスクの読み込みエラー: {str(e)}")
        return []

# JSONファイルにタスクを書き込む関数
def write_tasks(tasks: List[Dict], agent_id: Optional[str] = None, project_name: Optional[str] = None) -> None:
    """
    JSONファイルにタスクを書き込む関数。
    
    Args:
        tasks: 書き込むタスクのリスト
        agent_id: エージェントID（オプション）
        project_name: プロジェクト名（オプション）
        
    Raises:
        RuntimeError: タスクの保存に失敗した場合
    """
    tasks_file = get_tasks_file_path(agent_id, project_name)
    
    try:
        # 親ディレクトリが存在することを確認
        os.makedirs(os.path.dirname(tasks_file), exist_ok=True)
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"タスクの書き込みエラー: {str(e)}")
        raise RuntimeError(f"タスクの保存に失敗しました: {str(e)}")

# 利用可能なエージェントの一覧を取得する関数
def list_agents() -> List[str]:
    """
    利用可能なエージェントの一覧を取得する関数。
    
    Returns:
        List[str]: エージェントIDのリスト
    """
    agents = []
    
    try:
        # エージェントディレクトリを検索
        for item in os.listdir(OUTPUT_DIR):
            item_path = os.path.join(OUTPUT_DIR, item)
            if os.path.isdir(item_path):
                agents.append(item)
    except Exception as e:
        logger.error(f"エージェント一覧の取得エラー: {str(e)}")
    
    return agents

# 特定のエージェントに関連するプロジェクトの一覧を取得する関数
def list_projects(agent_id: str) -> List[str]:
    """
    特定のエージェントに関連するプロジェクトの一覧を取得する関数。
    
    Args:
        agent_id: エージェントID
        
    Returns:
        List[str]: プロジェクト名のリスト
    """
    projects = []
    agent_dir = os.path.join(OUTPUT_DIR, agent_id)
    
    if not os.path.exists(agent_dir) or not os.path.isdir(agent_dir):
        return projects
    
    try:
        # プロジェクトディレクトリを検索
        for item in os.listdir(agent_dir):
            item_path = os.path.join(agent_dir, item)
            if os.path.isdir(item_path):
                projects.append(item)
    except Exception as e:
        logger.error(f"プロジェクト一覧の取得エラー: {str(e)}")
    
    return projects

# 新しいタスクIDを生成する関数
def generate_task_id(tasks):
    if not tasks:
        return 1
    return max(task.get("id", 0) for task in tasks) + 1

# 新しいサブタスクIDを生成する関数
def generate_subtask_id(subtasks):
    if not subtasks:
        return 1
    return max(subtask.get("id", 0) for subtask in subtasks) + 1

# 利用可能なTODOリソース一覧の取得
@app.list_resources()
async def list_resources() -> list[Resource]:
    resources = []
    
    # デフォルトリソース
    resources.extend([
        Resource(
            uri=AnyUrl("taskmate://tasks/all"),
            name="All Tasks",
            mimeType="application/json",
            description="Complete list of all tasks"
        ),
        Resource(
            uri=AnyUrl("taskmate://tasks/pending"),
            name="Pending Tasks",
            mimeType="application/json",
            description="List of tasks not yet completed"
        ),
        Resource(
            uri=AnyUrl("taskmate://tasks/completed"),
            name="Completed Tasks",
            mimeType="application/json",
            description="List of completed tasks"
        )
    ])
    
    # エージェントごとのリソース
    for agent_id in list_agents():
        # エージェントレベルのリソース
        resources.extend([
            Resource(
                uri=AnyUrl(f"taskmate://{agent_id}/tasks/all"),
                name=f"All Tasks for {agent_id}",
                mimeType="application/json",
                description=f"Complete list of all tasks for agent {agent_id}"
            ),
            Resource(
                uri=AnyUrl(f"taskmate://{agent_id}/tasks/pending"),
                name=f"Pending Tasks for {agent_id}",
                mimeType="application/json",
                description=f"List of tasks not yet completed for agent {agent_id}"
            ),
            Resource(
                uri=AnyUrl(f"taskmate://{agent_id}/tasks/completed"),
                name=f"Completed Tasks for {agent_id}",
                mimeType="application/json",
                description=f"List of completed tasks for agent {agent_id}"
            )
        ])
        
        # プロジェクトごとのリソース
        for project_name in list_projects(agent_id):
            resources.extend([
                Resource(
                    uri=AnyUrl(f"taskmate://{agent_id}/{project_name}/tasks/all"),
                    name=f"All Tasks for {agent_id}/{project_name}",
                    mimeType="application/json",
                    description=f"Complete list of all tasks for agent {agent_id} in project {project_name}"
                ),
                Resource(
                    uri=AnyUrl(f"taskmate://{agent_id}/{project_name}/tasks/pending"),
                    name=f"Pending Tasks for {agent_id}/{project_name}",
                    mimeType="application/json",
                    description=f"List of tasks not yet completed for agent {agent_id} in project {project_name}"
                ),
                Resource(
                    uri=AnyUrl(f"taskmate://{agent_id}/{project_name}/tasks/completed"),
                    name=f"Completed Tasks for {agent_id}/{project_name}",
                    mimeType="application/json",
                    description=f"List of completed tasks for agent {agent_id} in project {project_name}"
                )
            ])
    
    return resources

# 特定のTODOリソースの取得
@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    uri_str = str(uri)
    
    # エージェントとプロジェクトを抽出 (例: "taskmate://agent1/project1/tasks/all")
    uri_parts = uri_str.replace("taskmate://", "").split("/")
    
    agent_id = None
    project_name = None
    resource_type = None
    
    if len(uri_parts) >= 3 and uri_parts[-2] == "tasks":
        # エージェントとプロジェクトが指定されている場合 (taskmate://agent/project/tasks/all)
        agent_id = uri_parts[0]
        project_name = uri_parts[1]
        resource_type = uri_parts[-1]
    elif len(uri_parts) >= 2 and uri_parts[-2] == "tasks":
        # エージェントのみ指定されている場合 (taskmate://agent/tasks/all)
        agent_id = uri_parts[0]
        resource_type = uri_parts[-1]
    elif len(uri_parts) >= 1:
        # 従来の形式の場合 (taskmate://tasks/all)
        resource_type = uri_parts[-1]
    else:
        raise ValueError(f"不正なリソースURI: {uri}")
    
    # すべてのタスクを読み込む
    tasks = read_tasks(agent_id, project_name)
    
    # リソースURIに基づいてフィルタリング
    if resource_type == "all":
        filtered_tasks = tasks
    elif resource_type == "pending":
        filtered_tasks = [t for t in tasks if t.get("status") in ["todo", "in_progress"]]
    elif resource_type == "completed":
        filtered_tasks = [t for t in tasks if t.get("status") == "done"]
    else:
        raise ValueError(f"Unknown resource: {uri}")
    
    return json.dumps(filtered_tasks, indent=2, ensure_ascii=False)

# 利用可能なTODOツール一覧の取得
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_agents",
            description="登録されているエージェントの一覧を取得します。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_projects",
            description="特定のエージェントに関連するプロジェクトの一覧を取得します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "エージェントID"
                    }
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="get_tasks",
            description="現在のタスクリストを取得します。優先度や進捗状況でフィルタリングできます。",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "タスクのステータス ('todo', 'in_progress', 'done')",
                        "enum": ["todo", "in_progress", "done"]
                    },
                    "priority_min": {
                        "type": "integer",
                        "description": "最小優先度 (1-5)",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                }
            }
        ),
        Tool(
            name="get_next_task",
            description="優先度の高い次のタスクを取得し、自動的に'in_progress'ステータスに更新します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                }
            }
        ),
        Tool(
            name="create_task",
            description="新しいタスクを作成します。サブタスクも定義できます。",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "タスクのタイトル"
                    },
                    "description": {
                        "type": "string",
                        "description": "タスクの詳細な説明"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "タスクの優先度 (1-5, 5が最高)",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 3
                    },
                    "subtasks": {
                        "type": "array",
                        "description": "サブタスクの説明リスト",
                        "items": {
                            "type": "string"
                        }
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        Tool(
            name="update_progress",
            description="タスクの進捗を更新します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "タスクID"
                    },
                    "progress": {
                        "type": "number",
                        "description": "タスクの進捗率 (0-100)",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["task_id", "progress"]
            }
        ),
        Tool(
            name="complete_task",
            description="タスクを完了としてマークします。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "タスクID"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="add_subtask",
            description="既存タスクにサブタスクを追加します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "親タスクID"
                    },
                    "description": {
                        "type": "string",
                        "description": "サブタスクの説明"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["task_id", "description"]
            }
        ),
        Tool(
            name="update_subtask",
            description="サブタスクのステータスを更新します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "親タスクID"
                    },
                    "subtask_id": {
                        "type": "integer",
                        "description": "サブタスクID"
                    },
                    "status": {
                        "type": "string",
                        "description": "サブタスクの新しいステータス ('todo', 'in_progress', 'done')",
                        "enum": ["todo", "in_progress", "done"]
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["task_id", "subtask_id", "status"]
            }
        ),
        Tool(
            name="add_note",
            description="タスクにノートを追加します。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "タスクID"
                    },
                    "content": {
                        "type": "string",
                        "description": "ノートの内容"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "タスクの対象エージェントID"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "タスクの対象プロジェクト名"
                    }
                },
                "required": ["task_id", "content"]
            }
        )
    ]

# TODOツールの呼び出し
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    # ツール名の検証
    valid_tools = ["get_tasks", "get_next_task", "create_task", "update_progress", 
                 "complete_task", "add_subtask", "update_subtask", "add_note",
                 "list_agents", "list_projects"]
    if name not in valid_tools:
        raise ValueError(f"Unknown tool: {name}")

    # 引数の型確認
    if not isinstance(arguments, dict):
        raise ValueError("Invalid arguments: must be a dictionary")

    try:
        # 共通パラメータの取得
        agent_id = arguments.get("agent_id")
        project_name = arguments.get("project_name")
        
        # エージェント一覧の取得
        if name == "list_agents":
            agents = list_agents()
            return [TextContent(type="text", text=json.dumps(agents, indent=2, ensure_ascii=False))]
        
        # プロジェクト一覧の取得
        elif name == "list_projects":
            # 必須パラメータの確認
            if "agent_id" not in arguments:
                raise ValueError("Missing required parameter: agent_id")
                
            agent_id = arguments["agent_id"]
            projects = list_projects(agent_id)
            return [TextContent(type="text", text=json.dumps(projects, indent=2, ensure_ascii=False))]
        
        # get_tasks - タスク一覧の取得
        elif name == "get_tasks":
            tasks = read_tasks(agent_id, project_name)
            
            # フィルタリング
            if "status" in arguments and arguments["status"]:
                tasks = [t for t in tasks if t.get("status") == arguments["status"]]
            if "priority_min" in arguments:
                tasks = [t for t in tasks if t.get("priority", 0) >= arguments["priority_min"]]
            
            return [TextContent(type="text", text=json.dumps(tasks, indent=2, ensure_ascii=False))]
        
        # get_next_task - 次のタスクの取得
        elif name == "get_next_task":
            tasks = read_tasks(agent_id, project_name)
            
            # 未完了のタスクをフィルタリング
            pending_tasks = [t for t in tasks if t.get("status") != "done"]
            
            if not pending_tasks:
                return [TextContent(type="text", 
                         text="利用可能なタスクはありません。すべてのタスクが完了しているか、タスクがまだ作成されていません。")]
            
            # 優先度でソート (優先度が高い順)
            pending_tasks.sort(key=lambda t: t.get("priority", 0), reverse=True)
            
            # 最も優先度の高いタスクを取得
            next_task = pending_tasks[0]
            
            # タスクステータスを更新
            for i, task in enumerate(tasks):
                if task.get("id") == next_task.get("id"):
                    tasks[i]["status"] = "in_progress"
                    write_tasks(tasks, agent_id, project_name)
                    break
            
            return [TextContent(type="text", text=json.dumps(next_task, indent=2, ensure_ascii=False))]
        
        # create_task - タスク作成
        elif name == "create_task":
            # 必須パラメータの確認
            if "title" not in arguments or "description" not in arguments:
                raise ValueError("Missing required parameters: title and description")
            
            tasks = read_tasks(agent_id, project_name)
            
            # サブタスクの準備
            subtasks = []
            if "subtasks" in arguments and arguments["subtasks"]:
                subtasks = [{"id": i+1, "description": desc, "status": "todo"} for i, desc in enumerate(arguments["subtasks"])]
            
            # 新しいタスクの作成
            new_task = {
                "id": generate_task_id(tasks),
                "title": arguments["title"],
                "description": arguments["description"],
                "priority": arguments.get("priority", 3),
                "status": "todo",
                "progress": 0,
                "subtasks": subtasks,
                "notes": []
            }
            
            # タスクを追加して保存
            tasks.append(new_task)
            write_tasks(tasks, agent_id, project_name)
            
            agent_info = f" (エージェント: {agent_id})" if agent_id else ""
            project_info = f" (プロジェクト: {project_name})" if project_name else ""
            return [TextContent(type="text", 
                     text=f"タスク '{new_task['title']}' (ID: {new_task['id']}){agent_info}{project_info} が作成されました。")]
        
        # update_progress - 進捗更新
        elif name == "update_progress":
            # 必須パラメータの確認
            if "task_id" not in arguments or "progress" not in arguments:
                raise ValueError("Missing required parameters: task_id and progress")
            
            task_id = arguments["task_id"]
            progress = arguments["progress"]
            
            tasks = read_tasks(agent_id, project_name)
            
            # タスクを見つけて更新
            task_found = False
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    tasks[i]["progress"] = progress
                    
                    # 進捗に基づいてステータスを自動更新
                    if progress >= 100:
                        tasks[i]["status"] = "done"
                    elif progress > 0:
                        tasks[i]["status"] = "in_progress"
                    
                    task_found = True
                    break
            
            if not task_found:
                return [TextContent(type="text", text=f"エラー: タスク (ID: {task_id}) が見つかりません。")]
            
            # 変更を保存
            write_tasks(tasks, agent_id, project_name)
            
            return [TextContent(type="text", 
                     text=f"タスク (ID: {task_id}) の進捗が {progress}% に更新されました。")]
        
        # complete_task - タスク完了
        elif name == "complete_task":
            # 必須パラメータの確認
            if "task_id" not in arguments:
                raise ValueError("Missing required parameter: task_id")
            
            task_id = arguments["task_id"]
            
            tasks = read_tasks(agent_id, project_name)
            
            # タスクを見つけて更新
            task_found = False
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    tasks[i]["status"] = "done"
                    tasks[i]["progress"] = 100
                    task_found = True
                    break
            
            if not task_found:
                return [TextContent(type="text", text=f"エラー: タスク (ID: {task_id}) が見つかりません。")]
            
            # 変更を保存
            write_tasks(tasks, agent_id, project_name)
            
            return [TextContent(type="text", 
                     text=f"タスク (ID: {task_id}) が完了としてマークされました。")]
        
        # add_subtask - サブタスク追加
        elif name == "add_subtask":
            # 必須パラメータの確認
            if "task_id" not in arguments or "description" not in arguments:
                raise ValueError("Missing required parameters: task_id and description")
            
            task_id = arguments["task_id"]
            description = arguments["description"]
            
            tasks = read_tasks(agent_id, project_name)
            
            # タスクを見つけてサブタスクを追加
            task_found = False
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    # サブタスクリストがない場合は作成
                    if "subtasks" not in task:
                        tasks[i]["subtasks"] = []
                    
                    # 新しいサブタスクの作成
                    new_subtask = {
                        "id": generate_subtask_id(task.get("subtasks", [])),
                        "description": description,
                        "status": "todo"
                    }
                    
                    tasks[i]["subtasks"].append(new_subtask)
                    task_found = True
                    break
            
            if not task_found:
                return [TextContent(type="text", text=f"エラー: タスク (ID: {task_id}) が見つかりません。")]
            
            # 変更を保存
            write_tasks(tasks, agent_id, project_name)
            
            return [TextContent(type="text", 
                     text=f"サブタスク (ID: {new_subtask['id']}) がタスク (ID: {task_id}) に追加されました。")]
        
        # update_subtask - サブタスク更新
        elif name == "update_subtask":
            # 必須パラメータの確認
            if "task_id" not in arguments or "subtask_id" not in arguments or "status" not in arguments:
                raise ValueError("Missing required parameters: task_id, subtask_id and status")
            
            task_id = arguments["task_id"]
            subtask_id = arguments["subtask_id"]
            status = arguments["status"]
            
            # ステータスの検証
            if status not in ["todo", "in_progress", "done"]:
                raise ValueError("Invalid status: must be 'todo', 'in_progress', or 'done'")
            
            tasks = read_tasks(agent_id, project_name)
            
            # タスクとサブタスクを見つけて更新
            task_found = False
            subtask_found = False
            
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    task_found = True
                    
                    if "subtasks" in task:
                        for j, subtask in enumerate(task["subtasks"]):
                            if subtask.get("id") == subtask_id:
                                tasks[i]["subtasks"][j]["status"] = status
                                subtask_found = True
                                break
                    
                    break
            
            if not task_found:
                return [TextContent(type="text", text=f"エラー: タスク (ID: {task_id}) が見つかりません。")]
            
            if not subtask_found:
                return [TextContent(type="text", text=f"エラー: サブタスク (ID: {subtask_id}) が見つかりません。")]
            
            # 変更を保存
            write_tasks(tasks, agent_id, project_name)
            
            # メインタスクの進捗を自動更新 (サブタスクの完了率から計算)
            for i, task in enumerate(tasks):
                if task.get("id") == task_id and "subtasks" in task and task["subtasks"]:
                    completed = sum(1 for st in task["subtasks"] if st.get("status") == "done")
                    total = len(task["subtasks"])
                    tasks[i]["progress"] = int(completed / total * 100)
                    
                    # すべてのサブタスクが完了したら、タスクも完了にする
                    if completed == total:
                        tasks[i]["status"] = "done"
                    elif completed > 0:
                        tasks[i]["status"] = "in_progress"
                    
                    # 更新したタスク情報を保存
                    write_tasks(tasks, agent_id, project_name)
                    break
            
            return [TextContent(type="text", 
                     text=f"サブタスク (ID: {subtask_id}) のステータスが '{status}' に更新されました。")]
        
        # add_note - ノート追加
        elif name == "add_note":
            # 必須パラメータの確認
            if "task_id" not in arguments or "content" not in arguments:
                raise ValueError("Missing required parameters: task_id and content")
            
            task_id = arguments["task_id"]
            content = arguments["content"]
            
            tasks = read_tasks(agent_id, project_name)
            
            # タスクを見つけてノートを追加
            task_found = False
            for i, task in enumerate(tasks):
                if task.get("id") == task_id:
                    # ノートリストがない場合は作成
                    if "notes" not in task:
                        tasks[i]["notes"] = []
                    
                    # タイムスタンプを含む新しいノートの作成
                    import datetime
                    new_note = {
                        "id": len(task.get("notes", [])) + 1,
                        "content": content,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    
                    tasks[i]["notes"].append(new_note)
                    task_found = True
                    break
            
            if not task_found:
                return [TextContent(type="text", text=f"エラー: タスク (ID: {task_id}) が見つかりません。")]
            
            # 変更を保存
            write_tasks(tasks, agent_id, project_name)
            
            return [TextContent(type="text", 
                     text=f"ノートがタスク (ID: {task_id}) に追加されました。")]
                
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [TextContent(type="text", text=f"予期せぬエラーが発生しました: {str(e)}")]

# メイン関数
async def main():
    # イベントループの問題を回避するためにここにインポート
    from mcp.server.stdio import stdio_server

    # サーバの実行
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

# Pythonスクリプトとして直接実行された場合
if __name__ == "__main__":
    asyncio.run(main())
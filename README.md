# TaskMateAI
## AI/MCP TODOタスク管理アプリケーション

TaskMateAIは、AIが自律的にタスクを管理・実行するためのシンプルなタスク管理アプリケーションで、MCP (Model Context Protocol)を通じて操作できます。

[English README available here](README_EN.md)

## 特徴

- MCPを通じたタスクの作成・管理
- サブタスクのサポート
- 優先順位に基づくタスク処理
- タスクの進捗管理と報告機能
- ノート追加機能
- JSONファイルによるデータ永続化
- エージェントIDによる複数AIのタスク管理
- プロジェクト単位でのタスク整理

## インストール

### 前提条件

- Python 3.12以上
- uv (Python パッケージマネージャー)
- WSL (Windows Subsystem for Linux) ※Windows環境の場合

### インストール手順

1. リポジトリをクローンまたはダウンロード:

```bash
git clone https://github.com/YourUsername/TaskMateAI.git
cd TaskMateAI
```

2. 必要なパッケージをインストール:

```bash
uv install -r requirements.txt
```

## 使用方法

### アプリケーションの起動

WSL環境では以下のようにアプリケーションを実行できます:

```bash
cd /path/to/TaskMateAI/src/TaskMateAI
uv run TaskMateAI
```

### MCP構成

MCPで利用するための設定例:

```json
{
    "mcpServers": {
      "TodoApplication": {
        "command": "uv",
        "args": [
          "--directory", 
          "/絶対パス/TaskMateAI",
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
          "cd /絶対パス/TaskMateAI && /home/ユーザー/.local/bin/uv run TaskMateAI"
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

### 利用可能なMCPツール

TaskMateAIは以下のMCPツールを提供します:

1. **get_tasks** - タスクリストの取得（ステータスや優先度でフィルタリング可能）
2. **get_next_task** - 優先度の高い次のタスクを取得（自動的に進行中ステータスに更新）
3. **create_task** - 新しいタスクの作成（サブタスク付き）
4. **update_progress** - タスクの進捗更新
5. **complete_task** - タスクを完了としてマーク
6. **add_subtask** - 既存タスクにサブタスクを追加
7. **update_subtask** - サブタスクのステータス更新
8. **add_note** - タスクにノートを追加
9. **list_agents** - 利用可能なエージェントIDの一覧を取得
10. **list_projects** - 特定のエージェントに関連するプロジェクトの一覧を取得

### データ形式

タスクは以下のような構造で管理されます:

```json
{
  "id": 1,
  "title": "タスクのタイトル",
  "description": "タスクの詳細な説明",
  "priority": 3,
  "status": "todo",  // "todo", "in_progress", "done" のいずれか
  "progress": 0,     // 0-100 の進捗率
  "subtasks": [
    {
      "id": 1,
      "description": "サブタスクの説明",
      "status": "todo"  // "todo", "in_progress", "done" のいずれか
    }
  ],
  "notes": [
    {
      "id": 1,
      "content": "ノートの内容",
      "timestamp": "2025-02-28T09:22:53.532808"
    }
  ]
}
```

## データ保存

タスクデータは階層構造で保存されます：

```
output/
├── tasks.json                  # デフォルトのタスクファイル
├── agent1/
│   ├── tasks.json              # agent1のタスクファイル
│   ├── project1/
│   │   └── tasks.json          # agent1のproject1のタスクファイル
│   └── project2/
│       └── tasks.json          # agent1のproject2のタスクファイル
└── agent2/
    ├── tasks.json              # agent2のタスクファイル
    └── projectA/
        └── tasks.json          # agent2のprojectAのタスクファイル
```

各タスクファイルはアプリケーション実行時に自動的に生成・更新されます。

## エージェントとプロジェクトの管理

特定のエージェントやプロジェクトのタスクを管理するには、以下の方法があります：

1. **MCP設定でデフォルトエージェントを指定**：`defaultArguments`で`agent_id`を指定することで、すべてのリクエストで自動的に使用されます。

2. **AI会話でプロジェクトを指定**：会話の中で「プロジェクトXに新しいタスクを追加して」などと指定できます。

3. **AIからの直接指定**：リクエストパラメータに`agent_id`と`project_name`を含めることができます。

## プロジェクト構造

```
TaskMateAI/
├── src/
│   └── TaskMateAI/
│       ├── __init__.py      # パッケージ初期化
│       └── __main__.py      # メインアプリケーションコード
├── output/                  # データ保存ディレクトリ
│   └── tasks.json           # タスクデータ (自動生成)
├── tests/                   # テストコード
│   ├── unit/                # ユニットテスト
│   └── integration/         # 統合テスト
├── requirements.txt         # 依存パッケージリスト
└── README.md                # このファイル
```

## テスト

TaskMateAIでは、機能の信頼性を確保するため、包括的なテストスイートを提供しています。

### テストの構成

テストは以下のディレクトリ構造で管理されています：

```
tests/
├── __init__.py           # テストパッケージの初期化
├── conftest.py           # テスト用フィクスチャの定義
├── unit/                 # ユニットテスト
│   ├── __init__.py
│   ├── test_task_utils.py       # タスク関連ユーティリティのテスト
│   ├── test_mcp_tools.py        # MCPツール機能のテスト
│   └── test_agent_projects.py   # エージェントとプロジェクト管理のテスト
└── integration/          # 統合テスト
    └── __init__.py
```

### テストの種類

1. **ユニットテスト**: アプリケーションの個々のコンポーネントが正しく機能することを確認します
   - `test_task_utils.py`: タスクの読み書き、ID生成などの基本機能をテスト
   - `test_mcp_tools.py`: MCPツールの機能（タスクの作成、更新、完了など）をテスト
   - `test_agent_projects.py`: エージェントIDとプロジェクト管理機能をテスト

2. **統合テスト**: 複数のコンポーネントが連携して正しく動作することを確認します（将来拡張予定）

### テスト実行方法

以下のコマンドを使用してテストを実行できます：

1. すべてのテストを実行：

```bash
cd /path/to/TaskMateAI
uv run python -m pytest -xvs
```

2. 特定のテストファイルを実行：

```bash
uv run python -m pytest -xvs tests/unit/test_task_utils.py
```

3. 特定のテストクラスを実行：

```bash
uv run python -m pytest -xvs tests/unit/test_mcp_tools.py::TestMCPTools
```

4. 特定のテスト関数を実行：

```bash
uv run python -m pytest -xvs tests/unit/test_task_utils.py::TestTaskUtils::test_read_tasks_with_data
```

テスト引数の説明:
- `-x`: エラーが発生した時点でテストを停止します
- `-v`: 詳細な出力を表示します
- `-s`: テスト中の標準出力を表示します

## 修正予定項目

- タスクテンプレート機能の実装
- タスク間の依存関係管理システムの構築
- スケジュール機能の追加
- タグによるタスク分類システムの導入
- マイルストーン管理機能の実装

## ライセンス

MIT

## 著者

[NewAITees](https://github.com/NewAITees)
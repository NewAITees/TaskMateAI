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
          "complete_task", "add_subtask", "update_subtask"
        ]
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
          "complete_task", "add_subtask", "update_subtask"
        ]
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

タスクデータは `output/tasks.json` ファイルに保存されます。このファイルはアプリケーション実行時に自動的に生成・更新されます。

## プロジェクト構造

```
TaskMateAI/
├── src/
│   └── TaskMateAI/
│       ├── __init__.py      # パッケージ初期化
│       └── __main__.py      # メインアプリケーションコード
├── output/                  # データ保存ディレクトリ
│   └── tasks.json           # タスクデータ (自動生成)
├── requirements.txt         # 依存パッケージリスト
└── README.md                # このファイル
```

## 修正予定項目

- タスクが保存されるフォルダが想定と違うので直す
- 利用する側にAgentIDを設定できるようにして、タスクを管理できるようにする
- テストコードを追加する
- タスク関連の必要な処理を追加する
- add noteという機能が残っているので、これをあとで必要か判断する
- ノートとタスクのそれぞれについてCRUD操作が確実にできるようにする

## ライセンス

MIT

## 著者

[NewAITees](https://github.com/NewAITees)
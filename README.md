# TaskMateAI
# AI MCP TODO アプリケーション

AI MCP (Master Control Program) TODOは、AIが自律的にタスクを管理・実行するためのシンプルなRESTful APIアプリケーションです。

## 特徴

- シンプルなタスク管理 API
- サブタスクのサポート
- 優先順位に基づくタスク処理
- 進捗報告機能
- JSONファイルによるデータ永続化

## インストール

### 前提条件

- Python 3.7以上
- pip (Pythonパッケージマネージャー)

### インストール手順

1. リポジトリをクローンまたはダウンロード:

```bash
git clone <repository-url>
cd ai-mcp-todo
```

2. 必要なパッケージをインストール:

```bash
pip install -r requirements.txt
```

または直接インストール:

```bash
pip install fastapi uvicorn
```

## 使用方法

### アプリケーションの起動

```bash
python app.py
```

これにより、APIサーバーが `http://localhost:8000` で起動します。

### API ドキュメント

アプリケーション起動後、以下のURLでAPIドキュメントにアクセスできます:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 基本的なAPI操作

#### タスクの作成

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "サンプルタスク",
    "description": "これはサンプルタスクです",
    "priority": 3,
    "subtasks": [
      {"description": "サブタスク1"},
      {"description": "サブタスク2"}
    ]
  }'
```

#### タスク一覧の取得

```bash
curl -X GET "http://localhost:8000/tasks"
```

#### 次のタスクを取得 (AI用)

```bash
curl -X GET "http://localhost:8000/next-task"
```

#### タスクの進捗を更新 (AI用)

```bash
curl -X PUT "http://localhost:8000/tasks/1/progress" \
  -H "Content-Type: application/json" \
  -d '50.0'
```

#### タスクを完了としてマーク (AI用)

```bash
curl -X PUT "http://localhost:8000/tasks/1/complete"
```

## データ保存

タスクデータは `tasks.json` ファイルに保存されます。このファイルはアプリケーションと同じディレクトリに作成されます。

## プロジェクト構造

```
ai-mcp-todo/
├── app.py           # メインアプリケーションファイル
├── tasks.json       # データ保存用JSONファイル (自動生成)
├── requirements.txt # 依存パッケージリスト
├── README.md        # このファイル
└── docs/            # ドキュメント
    ├── PRD.md       # 製品要件定義書
    ├── AI_GUIDE.md  # AI向けガイド
    └── JSON_SPEC.md # JSONフォーマット仕様
```

## ライセンス

MIT

## 貢献

プルリクエストは歓迎します。大きな変更を行う場合は、まず問題を提起してください。

## 著者

[NewAITees](https://github.com/NewAITees)

# direct-typer

macOS用のテキスト直接入力ツール。クリップボードを経由せずにテキストをキーボードイベントとして送信します。

## 構成

| コンポーネント | 説明 |
|--------------|------|
| DirectTyper | テキスト直接入力ライブラリ |
| VoiceCodeApp | 音声入力メニューバーアプリ |

## 特徴

### DirectTyper（ライブラリ）

- CGEventを使用したUnicode文字の直接入力
- テキスト内容に応じた最適な入力方法の自動選択
- 日本語を含むマルチバイト文字に対応
- クリップボードの内容を保持

### VoiceCodeApp（音声入力ツール）

- F15キー（設定可能）で録音開始/停止
- Groq Whisperで文字起こし
- Gemini 2.5 Flash Lite（OpenRouter経由）でLLM後処理
  - プログラミング用語の変換（カタカナ→英語表記）
  - 誤字脱字の修正
- DirectTyperで直接入力

## 要件

- macOS
- Python 3.13+
- アクセシビリティ権限（システム設定 > プライバシーとセキュリティ > アクセシビリティ）

## インストール

```bash
uv sync
```

## 環境変数

`.env` ファイルを作成して設定:

```bash
GROQ_API_KEY=your_groq_api_key      # 文字起こし用（必須）
OPENROUTER_API_KEY=your_openrouter_api_key  # LLM後処理用（必須）
HOTKEY=f15                          # ホットキー設定（デフォルト: f15）
```

ホットキーの例:
- `f15` - F15キー
- `ctrl+shift+r` - Ctrl+Shift+R

## 使用方法

### VoiceCodeApp（音声入力ツール）

```bash
uv run python -m direct_typer.main
```

起動後、メニューバーにアイコンが表示されます。設定したホットキーを押して録音開始/停止を切り替えます。

### DirectTyper（ライブラリとして使用）

```python
from direct_typer import DirectTyper

typer = DirectTyper()

# 自動で最適な方法を選択
typer.type("Hello, World!")
typer.type("こんにちは、世界!")

# 方法を指定
typer.type_cgevent("CGEventで入力")
typer.type_pynput("pynputで入力")
typer.type_clipboard("クリップボード経由で入力")
```

## デモ

```bash
uv run python examples/demo.py
```

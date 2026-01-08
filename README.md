# direct-typer

macOS用のテキスト直接入力ツール。クリップボードを経由せずにテキストをキーボードイベントとして送信します。

## 特徴

- CGEventを使用したUnicode文字の直接入力
- テキスト内容に応じた最適な入力方法の自動選択
- 日本語を含むマルチバイト文字に対応
- クリップボードの内容を保持

## 要件

- macOS
- Python 3.13+
- アクセシビリティ権限（システム設定 > プライバシーとセキュリティ > アクセシビリティ）

## インストール

```bash
uv sync
```

## 使用方法

```python
from direct_typer import DirectTyper

typer = DirectTyper()

# 自動で最適な方法を選択
typer.type("Hello, World!")
typer.type("こんにちは、世界！")

# 方法を指定
typer.type_cgevent("CGEventで入力")
typer.type_pynput("pynputで入力")
typer.type_clipboard("クリップボード経由で入力")
```

## デモ

```bash
uv run python examples/demo.py
```

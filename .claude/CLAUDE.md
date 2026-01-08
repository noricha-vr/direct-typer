# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

| Item | Value |
|------|-------|
| Language | Python 3.13+ |
| Package Manager | uv |
| Build Backend | hatchling |
| Platform | macOS only |

## Project Overview

**direct-typer** は macOS 用のテキスト直接入力ライブラリ。クリップボードを経由せずにキーボードイベントとしてテキストを送信する。

## Commands

```bash
# 依存関係インストール
uv sync

# テスト実行
uv run pytest

# 単一テスト実行
uv run pytest tests/test_typer.py::test_function_name -v

# カバレッジ付きテスト
uv run pytest --cov=direct_typer

# デモ実行（5秒後にテキスト入力開始）
uv run python examples/demo.py
```

## Architecture

```
direct_typer/
├── typer.py      # DirectTyper - 高レベルAPI、入力方式の自動選択
└── cgevent.py    # CGEvent直接操作 - Unicode文字のキーボードイベント送信
```

### 入力方式と選択ロジック

`DirectTyper.type()` は以下の閾値で自動選択:

| 条件 | 方式 | 特徴 |
|------|------|------|
| ASCII && < 50文字 | pynput | 最速、ASCII向け |
| < 200文字 | CGEvent | Unicode対応、中程度の速度 |
| >= 200文字 | clipboard | 最安定、長文向け |

明示的に方式を指定する場合:
- `type_pynput()` - 高速だがASCII向け
- `type_cgevent()` - Unicode完全対応
- `type_clipboard()` - クリップボード経由（元の内容は復元可能）

### CGEvent レイヤー（cgevent.py）

- macOS の CGEventCreateKeyboardEvent を使用
- 特殊キー（Enter=36, Tab=48）は keycode で送信
- 通常文字は NSEvent.keyCodeForChar で keycode 取得、unicodeString で文字送信

## System Requirements

- macOS（CGEventフレームワーク使用）
- アクセシビリティ権限必須（システム設定 > プライバシーとセキュリティ > アクセシビリティ）

## Dependencies

- `pyobjc-framework-Quartz` - CGEvent アクセス
- `pynput` - クロスプラットフォームキーボード制御
- `pyperclip` - クリップボード操作

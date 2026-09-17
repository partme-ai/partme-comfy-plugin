#!/usr/bin/env python3
"""SessionStart hook: report Comfy Cloud readiness. Advisory only."""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    lines: list[str] = [f"python3: {sys.version.split()[0]}"]

    key = os.environ.get("COMFY_API_KEY", "")
    if key:
        lines.append("Comfy 凭据: COMFY_API_KEY 已设置")
    else:
        lines.append("Comfy 凭据: 未设置——首次生成时走 OAuth 登录，或在 ZCode userConfig 填 comfy_api_key")

    cli = shutil.which("comfy")
    lines.append(f"comfy-cli: {cli}" if cli else
                 "comfy-cli: 不在 PATH（云端路径不需要；本地 comfy-mcp 路径才需要 pip install comfy-cli）")

    readme = ROOT / "README.md"
    lines.append("插件: 就绪" if readme.is_file() else "插件: 异常")

    try:
        sys.stdin.read()
    except Exception:
        pass
    print("Comfy 插件环境：" + "；".join(lines))
    return 0


if __name__ == "__main__":
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    sys.exit(main())

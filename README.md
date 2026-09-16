# PartMe.AI Comfy Plugin

Tri-platform plugin (Codex / ZCode / Kimi Code) that connects coding agents to **Comfy Cloud**: generate images, video, audio, and 3D, search models / nodes / templates, and run ComfyUI workflows through the hosted Comfy MCP (`https://cloud.comfy.org/mcp`).

> 内容主体 vendor 自 [Comfy-Org/comfy-skills](https://github.com/Comfy-Org/comfy-skills)（MIT），逐字保留、仅加平台适配包装。版本钉在 `upstream/comfy-skills.lock.json`。

## What's inside

| Component | Count | Source |
|---|---|---|
| Commands | 12 (`/comfy-generate-image`, `/comfy-generate-video`, …) | verbatim from upstream `claude-code/commands/` |
| Skills | 12 (same topics, model auto-trigger) | verbatim from upstream `skills/`, wrapped in `SKILL.md` frontmatter |
| MCP | `comfy-cloud` (HTTP, `https://cloud.comfy.org/mcp`) | from upstream comfy-cloud plugin manifest |

Vendored bodies are **unmodified**; only platform packaging (frontmatter, manifests, hooks, commands) is added by this repository.

## Installation

### Codex

```bash
codex plugin marketplace add partme-ai/plugins
codex plugin add partme-comfy@partme-ai
```

First generation triggers OAuth login, or set an API key (created at platform.comfy.org/profile/api-keys, prefix `comfyui-`):

```bash
codex mcp login comfy-cloud
```

### ZCode

插件 → 添加插件市场 → `https://github.com/partme-ai/plugins` → 安装 `comfy`。

Optional userConfig: `comfy_api_key`（sensitive，注入 `X-API-Key` 头）。留空则按 OAuth 流程在首次调用时登录。

### Kimi Code CLI

```
/plugins marketplace https://raw.githubusercontent.com/partme-ai/plugins/main/kimi-marketplace.json
```

或 `/plugins` 面板直接添加本仓库 GitHub URL。凭据：设置环境变量 `COMFY_API_KEY`（`bearerTokenEnvVar` 注入）。

## Local ComfyUI path (optional)

云端路径无需本地安装。若要走本地 ComfyUI：

```bash
pip install "comfy-cli>=1.14.0"
comfy install        # 创建工作区（或 comfy set-default <path>）
comfy launch         # 运行类工具需要 ComfyUI 在跑
```

本地 stdio MCP（`comfy-mcp`）可另行按 [docs.comfy.org/agent-tools/mcp](https://docs.comfy.org/agent-tools/mcp) 接入。

## Commands

| Command | 作用 |
|---|---|
| `/comfy-generate-image` | 文生图 / 图生图 / 编辑（Flux、Nano Banana、DALL-E 等） |
| `/comfy-generate-video` | 文生视频 / 图生视频（Seedance、Kling、Luma 等） |
| `/comfy-generate-audio` | 音频生成 |
| `/comfy-generate-3d` | 3D 生成 |
| `/comfy-upscale-image` | 图像放大 |
| `/comfy-remove-background` | 去背景 |
| `/comfy-combine-people` | 人物合成 |
| `/comfy-search-models` | 搜索模型 |
| `/comfy-search-nodes` | 搜索节点 |
| `/comfy-search-templates` | 搜索工作流模板 |
| `/comfy-help` | 使用帮助 |

## Cost note

发现类调用（搜模板/模型/节点）免费；**运行生成需要 Comfy Cloud 订阅或积分**（新用户 5 次免费）。命令体 preserves 上游的 partner-API 直连路由与审批语义。

## License

Apache-2.0 for the adapter code in this repository. Vendored skill/command content is MIT (Comfy-Org) — see `NOTICE` and `upstream/comfy-skills.lock.json`.

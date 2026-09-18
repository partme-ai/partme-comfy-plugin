---
name: comfy-harness
description: Comfy 专家团的调用规范：comfy-cloud MCP 工具面、成本门禁、一次提交原则与产物落盘约定。
---

# Comfy Harness — 团队调用规范

## 连接

- 云端 MCP：`https://cloud.comfy.org/mcp`（HTTP）。Codex 走 OAuth（`codex mcp login comfy-cloud`）；API key（前缀 `comfyui-`，platform.comfy.org 创建）经 `X-API-Key` 头或 `COMFY_API_KEY` 环境变量。
- 本地路径（可选）：`pip install "comfy-cli>=1.14.0"` → `comfy install` → `comfy launch`；stdio MCP 为 `comfy-mcp`。

## 工具面（comfy-cloud）

| 类别 | 工具 | 计费 |
|---|---|---|
| 发现 | search_templates / get_template / search_models / search_nodes / get_node / get_prompting_guide | 免费 |
| 生成 | run_template / submit_workflow / partner_generate / apply_slots | **计费** |
| 任务 | get_job_status / wait_for_job / get_output / cancel_job | 免费 |
| 文件 | upload_file（24h 自动清理） | 免费 |
| 保存 | save_workflow / run_saved_workflow | 运行时计费 |

## 铁律

1. **发现免费、生成计费**——任何 run/submit 前必须有用户授权或预算内授权。
2. **一次提交**：提交后先持久化 job id；fail/timeout/Unknown 上报 lead，绝不自动重提交。
3. 伙伴模型直连：命名 Flux/Kling/Seedance/DALL-E 等先试 `partner_generate`，命中即短路模板流程。
4. 云端产物是签名 URL：原样执行返回的下载命令，下载后本地核验再验收。
5. 上传素材用 `upload_file`（24h 清理），工作流引用返回的文件名，不写绝对路径。

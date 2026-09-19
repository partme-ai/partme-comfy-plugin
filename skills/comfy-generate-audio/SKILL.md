---
name: comfy-generate-audio
description: "Generate audio using Comfy Cloud based on the user's description: $ARGUMENTS"
license: Apache-2.0
---

Generate audio using Comfy Cloud based on the user's description: $ARGUMENTS

Follow these steps exactly:

**Step 0 — Route partner-API requests directly.** If the user named a provider, model, or capability (e.g. "ElevenLabs", "Stability Audio", "Sonilo"), do one `search_nodes` lookup with the named term. If the matching node's category starts with `partner/`, try `partner_generate` first — see its tool description for the currently-wired model ids. Pass `type: "audio"` plus the partner's model slug, `prompt`, and any optional fields (`seed`/`duration`/`medias[]`). On success, return the artifact URL(s) and **stop** — do NOT continue with the workflow steps below. If `partner_generate` returns "unknown model" or "not yet implemented", or the matching node has no `partner/` prefix (OSS model), continue to Step 1.

1. Use `search_templates` with queries like "audio generation", "text to audio", "music generation", or "sound effects" and set `media_type` to "audio" to find a pre-built audio workflow template. If a good template exists, use it as the base workflow instead of building from scratch.

2. If no suitable template was found, use `search_nodes` to find audio-related nodes. Search for "audio" to discover available audio generation and processing nodes. Use `search_models` to find audio models if needed.

3. Build a ComfyUI API-format workflow JSON with the appropriate audio nodes. Audio workflows vary depending on the task (music generation, sound effects, text-to-speech, etc.) and available nodes.

4. **Validate the workflow has inputs and outputs before submitting.** Confirm the JSON contains:
   - At least one **input node** carrying the user's intent (text prompt node, LoadAudio for audio-to-audio, etc.).
   - At least one **output/save node** wired to the final audio tensor (`SaveAudioAdvanced` or the partner node's own save output).

   `SaveAudioAdvanced` (display name "Save Audio (Advanced)") is the current save node, and it requires `format` alongside `audio` and `filename_prefix` — the older `SaveAudio`, `SaveAudioMP3`, and `SaveAudioOpus` classes are marked deprecated in the node catalog and are hidden from `search_nodes`.

   API-backed partner nodes often produce an audio tensor but **do not include a save node by default** — you must add one and wire it to their output. Without it the job runs successfully but produces nothing retrievable, wasting compute. Do not skip this check.

5. Call `submit_workflow` with the workflow JSON.

6. Poll `get_job_status` every 5 seconds until the job is completed. Show the user a brief status update while waiting. If the user asks to cancel, use `cancel_job` with the prompt_id.

7. Call `get_output` to retrieve the generated audio. Pass a short `description` parameter (e.g. "ambient forest sounds") so the saved file gets a descriptive name.

8. Tell the user where the audio file was saved and how to play it. Audio outputs are saved to disk but not previewed inline.

If any step fails, show the error clearly. Audio generation support in ComfyUI is newer than image generation, so fewer templates and models may be available.

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要通过 Comfy 工作流生成音效、音乐或语音素材。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `audio-generation-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 未经授权克隆真实人物声音或生成侵权音乐。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `audio-generation-result`，每一步都绑定输入、预期输出与失败条件。

Step 5：校验结构、事实来源和目标状态；禁止根据缺失证据编造成功结论。

Step 6：失败时停止扩大影响，输出已完成步骤、失败证据、恢复点和下一次安全重试条件。

Step 7：交付摘要、验证证据、剩余风险与后续动作；生产变更必须说明回滚是否已验证。

## Rules

- 默认只读；写操作、高危操作和付费调用必须获得与该动作匹配的明确授权。
- 本技能不收集、不存储、不上传用户凭据；日志和报告不得包含完整 token、密码或密钥。
- 不关闭 TLS 校验，不执行来源不明脚本，不使用管道下载后直接执行。
- 只把真实执行结果写成“已完成”；计划、示例和推断必须显式标注。
- 优先幂等操作；无法幂等时先提供预演、备份和回滚点。

## Validation checklist

- [ ] 目标、环境与授权范围均已写明。
- [ ] `音频可播放且时长、格式、采样率和提示参数符合要求` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `音频可播放且时长、格式、采样率和提示参数符合要求`，不能只看命令退出码或 HTTP 200。
3. **重试不等于恢复**：对鉴权失败、参数错误和安全拒绝不得盲目重试。
4. **示例不等于现状**：模板值与占位符不能写成真实环境数据。
5. **输出不等于交付**：还需完成结构校验、风险说明和可重复验证。
6. **跨环境不可照搬**：操作系统、版本、区域和宿主能力不同时必须重新确认参数。

## 渐进式资料

- 做路径选择前读取 `references/decisions/decision-guide.md`。
- 遇到异常、超时或部分成功时读取 `references/operations/failure-matrix.md`。
- 完成交付前读取 `references/operations/validation-checklist.md`。
- 需要可复制输入时，按顺序参考 `examples/basic.md`、`examples/failure.md`、`examples/advanced.md`。
<!-- QUALITY_CONTRACT_END -->

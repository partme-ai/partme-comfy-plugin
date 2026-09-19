---
name: comfy-generate-3d
description: "Generate a 3D model using Comfy Cloud based on the user's description: $ARGUMENTS"
license: Apache-2.0
---

Generate a 3D model using Comfy Cloud based on the user's description: $ARGUMENTS

Approach: prefer a ready-made template over hand-building, and discover the current options with the tools rather than assuming a fixed catalog. Model, node, and template availability changes over time, so let the tools tell you what exists right now.

**Step 0 - Partner-API shortcut.** If the user named a provider or capability (Meshy, Tripo, Rodin, Tencent, and so on), find the matching node with `search_nodes` filtered by `category: "partner/3d"` (optionally add a `q` for the provider name). If a matching `partner/3d/...` node exists, try `partner_generate` first with `type: "3d"` and that provider's model slug, plus `prompt` and any optional fields (`seed`, `medias[]`). On success, return the artifact URL(s) and stop. If it returns "unknown model" or "not yet implemented", or says it "does not serve type" (3D has no `partner_generate` persist path today), continue below — the template path in step 1 does generate 3D on Comfy Cloud.

1. **Look for a template first.** Call `search_templates` with `tag: "Image to 3D"` (image-to-3D is the common case), and/or `q: "3d"` for the broader set. If a suitable template comes back, clone it as your base workflow: swap in the user's input (such as the reference image) and adjust settings instead of building from scratch. Cloning a template is almost always faster than hand-wiring nodes, so spend real effort here before falling through to step 2.

2. **If no template fits, discover nodes structurally - do not free-text guess.** Use `search_nodes` with its typed filters, which match against the live catalog:
   - `output_type: "FILE_3D_GLB"` (also `MESH`, `FILE_3D_OBJ`) to find nodes that produce a 3D file.
   - `category: "3d"` or `category: "partner/3d"` to browse the 3D nodes.
   - `input_type: "IMAGE"` to find what accepts an image, for image-to-3D.

   Use `search_models` for any checkpoints the chosen nodes require. Do not paste in remembered model or node names - query for them, because the set changes.

3. If the user provides a reference image (image-to-3D), `upload_file` it first.

4. Build a ComfyUI API-format workflow JSON, or edit the cloned template. A 3D workflow generally chains an input, a 3D generation or reconstruction node, and a 3D save/output node.

5. **Validate inputs and outputs before submitting.** Confirm the workflow has:
   - at least one input node carrying the user's intent (a text prompt node, or LoadImage for image-to-3D), and
   - at least one save/output node wired to the final mesh. If you are unsure of the exact node, find it with `search_nodes output_type: "FILE_3D_GLB"`.

   API and partner nodes often produce an output but include no save node by default. Add and wire one, or the job runs and produces nothing retrievable, wasting compute. Do not skip this check.

6. Call `submit_workflow`. 3D generation can take longer than image generation.

7. Poll `get_job_status` every 5 seconds until completed, showing brief status updates while waiting. If the user asks to cancel, use `cancel_job` with the prompt_id.

8. Call `get_output` to retrieve the result. Pass a short `description` (for example "red sports car 3d model") so the saved file gets a descriptive name.

9. Tell the user where the files were saved. 3D outputs may include mesh files (.obj, .glb), textures, or rendered preview images.

If a step fails, show the error clearly and use the search tools to find a current alternative rather than assuming none exists.

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要通过 Comfy 工作流生成可下载的 3D 资产。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `3d-generation-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 复杂拓扑精修、骨骼绑定或 DCC 内手工建模。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `3d-generation-result`，每一步都绑定输入、预期输出与失败条件。

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
- [ ] `任务终态成功且模型文件、预览与生成参数可追溯` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `任务终态成功且模型文件、预览与生成参数可追溯`，不能只看命令退出码或 HTTP 200。
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

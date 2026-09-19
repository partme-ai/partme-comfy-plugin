---
name: comfy-help
description: "Show the user what they can do with the ComfyUI Cloud MCP tools"
license: Apache-2.0
---

Show the user what they can do with the ComfyUI Cloud MCP tools.

Explain in a friendly, concise way:

**What you can do:**

- Generate images from text descriptions -- just describe what you want
- Upload input images for img2img, style transfer, or any workflow that needs a source image
- Search for models (checkpoints, LoRAs, VAEs, upscalers) available on Comfy Cloud
- Search for ComfyUI nodes to discover processing capabilities
- Build and run complex multi-step workflows (img2img, upscaling, style transfer)
- Cancel running or queued jobs if you change your mind
- Check queue status to see how busy the system is

**Quick examples to try:**

- "Generate a photo of a mountain lake at golden hour"
- "Search for anime-style checkpoint models"
- "What upscaling nodes are available?"
- "Generate an image of a robot, then upscale it 2x"
- "Upload this photo and turn it into a watercolor painting"
- "Cancel that last job"

**How it works:**
The ComfyUI Cloud MCP server connects to cloud.comfy.org. Workflows run on cloud GPUs so you don't need a local GPU. I can build ComfyUI workflows automatically from your descriptions.

**Tips:**

- Be descriptive in your prompts for better results
- Mention a style if you want something specific (photorealistic, anime, oil painting, etc.)
- You can ask me to search for specific model types if you know what you need
- After generating, I can save and open the image for you

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要诊断 Comfy 技能、模型、节点和连接问题并给出路由建议。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `comfy-help-report`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 在未知环境直接安装节点、模型或修改工作流。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `comfy-help-report`，每一步都绑定输入、预期输出与失败条件。

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
- [ ] `问题类别、证据、建议技能与下一步验证明确` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `问题类别、证据、建议技能与下一步验证明确`，不能只看命令退出码或 HTTP 200。
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

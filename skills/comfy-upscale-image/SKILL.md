---
name: comfy-upscale-image
description: "Upscale an image using Comfy Cloud: $ARGUMENTS"
license: Apache-2.0
---

Upscale an image using Comfy Cloud: $ARGUMENTS

Follow these steps exactly:

1. Use `search_templates` with queries like "upscale", "super resolution", or "image upscaler" to find a pre-built upscaling workflow template. If a good template exists, use it as the base workflow instead of building from scratch.

2. If no suitable template was found, use `search_models` with type "upscale_models" to find an appropriate upscaler model. Popular options: 4x-UltraSharp (general purpose), RealESRGAN_x4plus (photorealistic), RealESRGAN_x4plus_anime_6B (anime/illustration), 4x_NMKD-Siax_200k (balanced). For 2x upscale, look for 2x models.

3. The user must provide an input image. Use `upload_file` to upload it to Comfy Cloud. Use the returned filename in a LoadImage node.

4. Build a ComfyUI API-format workflow JSON for upscaling. A standard upscale workflow uses: LoadImage → UpscaleModelLoader → ImageUpscaleWithModel → SaveImage. For higher quality results with more control, you can use a two-pass approach: upscale first, then run through img2img with a checkpoint at low denoise (0.2-0.4) to add detail.

5. **Validate the workflow has inputs and outputs before submitting.** Confirm the JSON contains:
   - At least one **input node** (`LoadImage` for the source image).
   - At least one **output/save node** wired to the upscaled image (`SaveImage`, or the partner node's own save output).

   Without an output node the job runs successfully but produces nothing retrievable, wasting compute. Do not skip this check.

6. Call `submit_workflow` with the workflow JSON.

7. Poll `get_job_status` every 3 seconds until the job is completed. Show the user a brief status update while waiting. If the user asks to cancel, use `cancel_job` with the prompt_id.

8. Call `get_output` to retrieve the upscaled image. Pass a short `description` parameter (e.g. "upscaled-photo") so the suggested filename is descriptive, then run the returned curl command in the user's shell to download the file.

9. Display the result to the user. Mention the output resolution compared to the input if known.

If any step fails, show the error clearly. Common issues: input image too large for GPU memory (suggest downscaling first or using a tile-based upscaler like UltimateSDUpscale).

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要通过 Comfy 工作流放大图像并控制细节增强。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `upscale-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 把无法恢复的细节伪装成真实证据或身份信息。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `upscale-result`，每一步都绑定输入、预期输出与失败条件。

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
- [ ] `尺寸、锐度、伪影、色彩和输出格式验证通过` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `尺寸、锐度、伪影、色彩和输出格式验证通过`，不能只看命令退出码或 HTTP 200。
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

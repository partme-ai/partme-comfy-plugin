---
name: technique-combine-people
description: "Combine a user's photo with another person (real or fictional) into a single composite image: $ARGUMENTS"
license: Apache-2.0
---

Combine a user's photo with another person (real or fictional) into a single composite image: $ARGUMENTS

Follow these steps exactly:

## Step 1: Upload the user's photo

If the user provides a photo of themselves, use `upload_file` to upload it. Note the returned filename for use in LoadImage.

## Step 2: Generate a reference image of the other person

Use `KlingOmniProImageNode` (model: `kling-v3-omni`) or `GeminiNanoBanana2V2` to generate a high-quality reference portrait of the target person. Use a detailed prompt describing their iconic appearance. Save and upload the result for use as a second reference.

`GeminiNanoBanana2V2` is the current class name — the older `GeminiNanoBanana2` is marked deprecated in the node catalog and is hidden from `search_nodes`.

Alternatively, if the user provides their own reference image of the second person, upload that instead and skip generation.

## Step 3: Wire both references into the composite node

`GeminiNanoBanana2V2` takes up to 14 reference images directly, as auto-grow slots named `model.images.image_1` through `model.images.image_14`, so no separate batching node is needed — connect the user's photo to `model.images.image_1` and the other person to `model.images.image_2`.

If you do need a standalone image batch elsewhere in the graph, the current class is `BatchImagesNode` (display name "Batch Images"); the older `ImageBatch` is marked deprecated. Its `images` input is an auto-grow list, so call `get_node({ names: ["BatchImagesNode"] })` for the exact slot names before wiring it.

## Step 4: Generate the composite with Nano Banana 2

`GeminiNanoBanana2V2`'s `model` input is a dynamic combo, so the settings it gates are sent under their full dotted names, not flat. Call `get_node({ names: ["GeminiNanoBanana2V2"] })` for the exact input names before you build the graph.

Settings that matter for this recipe:

- **model**: `Nano Banana 2 (Gemini 3.1 Flash Image)`
- **model.thinking_level**: `HIGH` (critical for face accuracy)
- **model.resolution**: `2K`
- **model.aspect_ratio**: `16:9` (or match user preference)
- **model.images.image_1** / **model.images.image_2**: the two references from Step 3
- **response_modalities**: `IMAGE` (top level, not gated by `model`)
- **seed**: top level; vary it for Step 5

### Prompt structure (important):

The prompt should:

1. Explicitly state which reference image is which ("The first image is...", "The second image is...")
2. Emphasize EXACT face reproduction from both references
3. Describe clothing, pose, and setting
4. Specify lighting consistency
5. Call out any artifacts to avoid (e.g., "NO glare on glasses, NO reflections on lenses")

Example prompt:

```
Create a black and white vintage 1970s photograph combining these two people.
The first image is the primary reference - reproduce this man's face EXACTLY as shown:
his specific facial features, smile, dark hair style, and black zip-up jacket. He should
be on the left. The second image shows [PERSON NAME] - reproduce their face exactly as
shown with [iconic features]. They are posing together as close friends in [setting].
[Style instructions]. Important: [any artifact avoidance instructions].
```

## Step 5: Generate multiple variations

Submit 3 workflows with different seeds in parallel. This gives the user options to pick from since face reproduction varies by seed.

## Step 6: Show results and iterate

- Save all outputs locally and open them for the user
- Ask which variation they prefer
- If adjustments are needed (lighting, glare, pose), modify the prompt and regenerate with both the same seed (to stay close) and new seeds

## Model comparison (from testing):

| Model                             | Face accuracy              | Quality   | Speed |
| --------------------------------- | -------------------------- | --------- | ----- |
| **Nano Banana 2 (HIGH thinking)** | Best                       | Excellent | ~45s  |
| Nano Banana Pro                   | Good                       | Excellent | ~40s  |
| Kling O3 (kling-v3-omni)          | Good                       | Good      | ~60s  |
| Flux Kontext Pro                  | Moderate (single ref only) | Good      | ~20s  |
| SDXL img2img                      | Poor                       | Moderate  | ~15s  |

## Key learnings:

- **Two reference images are essential** - without a reference of the second person, models rely on training data and often miss the likeness
- **Nano Banana 2 with HIGH thinking** produces the most accurate face reproduction
- **Explicit prompt instructions** about which image is which person dramatically improves results
- **The SaveImage output directory != LoadImage input directory** on Comfy Cloud - always re-upload generated reference images via `upload_file` before using them in a new workflow

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要在获得授权的前提下合成多人同框图像并保持身份一致性。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `people-composite-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 欺骗性身份合成、冒充或未经同意使用真实人物。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `people-composite-result`，每一步都绑定输入、预期输出与失败条件。

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
- [ ] `授权、构图、身份一致性、边缘与光影验证完整` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `授权、构图、身份一致性、边缘与光影验证完整`，不能只看命令退出码或 HTTP 200。
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

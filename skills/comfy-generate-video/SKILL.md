---
name: comfy-generate-video
description: "Generate, edit, or extend a video using Comfy Cloud based on the user's description: $ARGUMENTS"
license: Apache-2.0
---

Generate, edit, or extend a video using Comfy Cloud based on the user's description: $ARGUMENTS

Follow these steps exactly:

**Step 0 — Route the named model family.** If the user named a provider, model, or capability (e.g. "Kling", "Veo", "Sora", "Runway", "MiniMax"), check both routes before doing anything else: one `search_nodes` lookup with the named term (for the partner/API node), and one `search_templates` lookup with the family name (for an OSS template). Some families — MiniMax H3 is a current example — ship as BOTH OSS weights and a paid partner node under the same display title; others exist only as a partner node. Tell them apart by where the hit came from, not by one naming rule: TEMPLATE names carry the convention (`video_*` is the OSS template, `api_*` the paid API one), while node CLASS names are CamelCase on both routes and are told apart by `category` — a paid API node sits under `partner/…`, an OSS node under `model/…`. To list one route's nodes only, re-run `search_nodes` with `category: "partner"` or `category: "model"`. Treat a single empty lookup as inconclusive: broaden the query (drop version numbers, try the bare family name) before concluding a route is absent.

- **Family exists only as partner/API** (no matching OSS template, and the node's category starts with `partner/`): route directly. If the family is one of the model ids `partner_generate`'s own tool description lists, call it — pass `type: "video"` plus that model slug, `prompt`, and any optional fields (`aspect_ratio`/`seed`/`duration`/`medias[]`); on success return the artifact URL(s) and **stop**, do NOT continue with the workflow steps below. `partner_generate` serves only the slugs it lists, and most paid video families are not among them, so an unlisted one comes back "unknown model". That is neither a dead end nor a reason to fall through to OSS: the paid route for those is the family's own `api_*` template via `run_template` (or its `partner/` node wired into `submit_workflow`). Only continue to Step 1 if the user agrees to switch to an OSS model — offer it, don't substitute it silently.
- **Family exists only as OSS** (a matching template or a node under a non-`partner/` category, with no `partner/` hit): continue to Step 1 using it. Don't guess a `partner_generate` slug for it.
- **Family exists as both OSS and partner/API**: do NOT auto-route to the paid path. Tell the user both options exist — OSS (no partner/API fee, but running it still spends ordinary Comfy Cloud compute credits, and it's typically slower; it's only actually free of charge when the user runs it themselves on their own local ComfyUI install) vs. paid partner/API (fast, no local hardware concern, costs the partner's per-run price on top of compute) — and ask which they want, unless they already said which one (e.g. "the free version", "local", "OSS", or named a paid partner product explicitly) or one route is genuinely infeasible right now. "Free" there refers to the partner fee only: if they picked OSS meaning free, say plainly — before submitting — that running it here still spends ordinary Comfy Cloud compute credits, and that running it locally on their own ComfyUI is the only no-charge option. Once the route is chosen: partner/API continues as in the bullet above; OSS continues to Step 1 using the matching template.

Never tell a user the OSS route doesn't exist for a family that has one — that's a wrong answer, not a cautious one.

1. Use `search_templates` with relevant queries like "text to video", "image to video", or "video generation" to find a pre-built video workflow template. Filter by tag "video" if the text search returns too many image results. If a good template exists, use it as the base workflow instead of building from scratch.

2. If no suitable template was found, use `search_models` to find an appropriate video model. Common video models include: LTX-Video, Wan Video, HunyuanVideo, AnimateDiff, CogVideoX. Pick the best match based on the user's description.

3. If the user provides an input image (for image-to-video), use `upload_file` to upload it first. Use the returned filename in a LoadImage node.

4. Build a ComfyUI API-format workflow JSON with the appropriate video nodes. Video workflows typically use specialized loader nodes (e.g. LTXVLoader, WanVideoModelLoader), video-specific samplers, and video output nodes (e.g. VHS_VideoCombine). If using a template, modify the prompt and settings as needed.

5. **Validate the workflow has inputs and outputs before submitting.** Confirm the JSON contains:
   - At least one **input node** the user's intent flows through (CLIPTextEncode for the prompt, LoadImage for image-to-video, etc.).
   - At least one **output/save node** wired to the final video tensor (e.g. `VHS_VideoCombine`, `SaveAnimatedWEBP`, `SaveVideo`, or the partner node's own save output).

   API-backed partner nodes (Kling, Nano Banana, Gemini, Veo, etc.) often produce a video tensor but **do not include a save node by default** — you must add one and wire it to their output. Without it the job runs successfully but produces nothing retrievable, wasting compute. Do not skip this check.

6. Call `submit_workflow` with the workflow JSON. Note: video generation typically takes longer than image generation (30s-2min+).

7. Poll `get_job_status` every 5 seconds until the job is completed. Show the user a brief status update while waiting. Mention that video generation takes longer than images. If the user asks to cancel, use `cancel_job` with the prompt_id.

8. Call `get_output` to retrieve the generated video. Pass a short `description` parameter (e.g. "cat running through field") so the saved file gets a descriptive name.

9. Tell the user where the video file was saved and how to view it. Video outputs are saved to disk but not previewed inline.

If any step fails, show the error clearly. Common video generation issues: model not available on cloud, insufficient GPU memory for long videos, unsupported video length.

## Model notes: MiniMax H3 (as of 2026-08)

Model facts change over time. The following was accurate as of 2026-08 — confirm current details with `search_templates`, `search_nodes`, and `get_node` rather than assuming they still hold.

- H3 is the current best open-source video model (tier 0), on par with closed-source SOTA models like Seedance 2.x. If a user wants the best open-source video model and doesn't name one, recommend H3.
- As of 2026-08, H3 ships with two routes: OSS weights and a paid partner/API node — confirm both are currently live with `search_templates`/`search_nodes` rather than assuming this holds forever. OSS carries no partner/API fee, but running it on Comfy Cloud still spends ordinary Comfy Cloud compute credits — it's only free of charge outright when the user runs it locally on their own ComfyUI install. Don't conclude the OSS route is gone from one empty or ambiguous lookup; broaden the search before telling a user there's no OSS option, and don't let that session-local evidence override what a fresh, authoritative lookup says either.
- As of 2026-08, both routes share the same display title, "MiniMax H3: Text to Video" (and the image-to-video variant), told apart by TEMPLATE name: `video_minimax_h3_*` is OSS, `api_minimax_h3_*` is the paid API one. That prefix is a template-name convention and never appears on a node class, which is CamelCase on both routes — confirm the current names with `search_templates` before relying on them. To list one route's nodes, filter `search_nodes` by `category`: `"model"` for the OSS nodes (`model/conditioning/minimax`), `"partner"` for the paid API ones (`partner/video/MiniMax`). There is no parameter that excludes API nodes — `api_nodes_only: true` narrows TO them, and `api_nodes_only: false` is a no-op.
- Before building the OSS workflow, ask about the user's hardware and set expectations from it. Dynamic VRAM offloading widens what a GPU can attempt, but it is not a guarantee — out-of-memory is still possible, and actual headroom depends on resolution, duration, VRAM, and system RAM together, not VRAM alone:
  - Tested comfortable range (as of 2026-08): a 30-series-or-newer GPU with 16+ GB VRAM and enough system RAM that offloaded weights don't starve the host.
  - Reference benchmarks on the basic workflow, same date: 5 seconds at 480p takes about 9 minutes on a 3060; about 15 minutes for 5 seconds on a 16 GB card. Below the tested range, OOM becomes more likely — if it happens, suggest a lower resolution or shorter duration rather than assuming the run will simply succeed slower.
  - Generation time scales exponentially with pixel count, not linearly. Re-estimate for the resolution the user actually wants — don't scale the numbers above linearly.
  - Quote the estimate before running so a user on a weak GPU can decide with full information. Slow is not the same as impossible, but OOM is a real outcome on undersized hardware — don't promise success on every GPU.
- Model files: use the int8 base model on all GPUs, including 50-series cards, and the NVFP4 text encoder on all GPUs. The official template's default file choices are correct for nearly every GPU — don't second-guess them without a specific reason.
- The partner/API node's resolution and duration options are that node's dropdown, not necessarily the model's full real limits. Treat the numbers below as the 2026-08 reference point and confirm current ones with `get_node` on the OSS node before enforcing a hard cutoff:
  - As of 2026-08: OSS accepts any resolution in multiples of 32, up to about 2K.
  - As of 2026-08: OSS duration follows a 17k+5-frame grid at 24fps (k = 0, 1, 2, ...), up to about 15 seconds max.
  - As of 2026-08: OSS has native stereo audio.
  - If the user asks for something outside the API node's presets (e.g. exactly 1000x1000), don't call it impossible before checking — the OSS node's actual schema (via `get_node`) may still support it.
  - For production-quality output, suggest generating at the native ~768p canvas and upscaling afterward, rather than requesting a large canvas directly.
- Evidence beats assumption, but keep it scoped: if you already ran OSS H3 successfully, or a tool call already showed the model files present, treat that as proof the OSS route exists for this request — don't contradict it later in the same turn because of an unrelated error. One precedence rule covers both directions: a lookup that RETURNS something outranks your older evidence (if it shows the route moved or was renamed, follow the live result), while older direct evidence — a successful run, model files a call already showed present — outranks a later EMPTY lookup. Never deny a route on an empty result alone.
- "Hailuo" is MiniMax's video product line, and on Comfy's own surfaces Hailuo 03 IS H3: the paid node is `MinimaxHailuo03TextToVideoNode` (the partner catalog calls that proxy "Minimax V2 (Hailuo 03)"), and it is what the `api_minimax_h3_*` templates run. So a user who says "Hailuo 03" means H3. The OLDER family is Hailuo 02 and the `T2V-01`/`I2V-01` line, served by `MinimaxHailuoVideoNode` — don't mix its parameters into an H3 request. As of 2026-08, `partner_generate` DOES serve H3 text-to-video: pass `type: "video"` with the slug `minimax/hailuo-03-t2v`. That is the only registered MiniMax slug, so the other paid H3 shapes go through `run_template` instead — `api_minimax_h3_r2v` (reference-to-video) and `api_minimax_h3_flf2v` (first/last frame). Confirm the live set with `search_models({ source: "partner", q: "minimax" })` rather than trusting this list; if a slug is refused, the "unknown model" bounce names the closest real one.
- The OSS image-to-video template ships with one helper node left disconnected on purpose, and validation will flag it. That's expected: after fetching the template, validate, then either prune the disconnected helper pair or wire an IMAGE link into it, and proceed. Don't treat that validation failure as a dead end.

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要通过 Comfy 工作流生成短视频与可恢复任务记录。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `video-generation-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 长片剪辑、精确逐帧合成或未授权人物视频生成。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `video-generation-result`，每一步都绑定输入、预期输出与失败条件。

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
- [ ] `视频可播放且时长、帧率、分辨率和任务标识完整` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `视频可播放且时长、帧率、分辨率和任务标识完整`，不能只看命令退出码或 HTTP 200。
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

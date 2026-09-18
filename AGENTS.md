# AGENTS.md — Comfy Design

## 版本升级要求（强制，AI 必须遵守）

任何代码改动——无论大小——都必须 bump 版本并发布。PartMe.AI 插件市场
靠版本号感知更新：版本号不动，用户永远看不到「可更新」提示。


### 发版流程（每次改动完成后执行）

```bash
node scripts/bump-plugin.mjs comfy-design patch   # 文档/注释/小修复
node scripts/bump-plugin.mjs comfy-design minor   # 新功能
node scripts/bump-plugin.mjs comfy-design major   # 破坏性变更
```

脚本自动完成：catalog.json 版本更新 + 全部 manifest 同步（codex 清单带
当日 `+codex.日期` 后缀）+ 三平台市场清单重新生成与校验。之后按脚本
提示提交并 push **两个仓库**（本仓 + plugins 市场仓）。

### 硬性禁令

- 禁止改代码不 bump 版本（「小版本也要发」）
- 禁止手改 catalog.json 的 version 以外的生成产物、或手改三份市场清单——
  它们只能由 `scripts/bump-plugin.mjs` 与 `plugins/scripts/sync-marketplaces.mjs` 生成
- 版本号必须全链一致（catalog + 4 manifest），`sync-marketplaces` 校验会拦截不一致
- 插件本体放本仓根目录；`plugins/` 市场仓只存元数据，绝不物理包含插件代码

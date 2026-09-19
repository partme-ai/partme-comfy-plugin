#!/usr/bin/env node
/**
 * bump-plugin.mjs —— partme 插件发版一条命令。
 *
 * 纪律：任何代码改动（无论大小）都要 bump + 发版，市场端靠版本号感知更新。
 *
 * 用法：
 *   node scripts/bump-plugin.mjs <plugin-id> <major|minor|patch> [--dry-run]
 * 例：
 *   node scripts/bump-plugin.mjs codeguard patch
 *
 * 做的事：
 *   1. catalog.json 该插件 version bump
 *   2. 插件仓 4 个 manifest 同步（.zcode-plugin / kimi.plugin.json /
 *      .agents/plugins/marketplace.json 精确改；.codex-plugin 带当日 +codex.日期 后缀）
 *   3. 重跑 sync-marketplaces.mjs --write 重新生成三平台清单并校验
 *   4. 打印两仓待提交提示
 */
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolvePluginsRoot();
const [pluginId, level, dryRunFlag] = process.argv.slice(2);
const dryRun = dryRunFlag === "--dry-run";

/**
 * 定位 plugins 市场仓（含 catalog.json 的那个目录）。
 * 本脚本同时存在于 plugins/scripts/（主本）和每个插件仓 scripts/（分发副本），
 * 两种位置都要能找到市场仓：
 *   a) PARTME_PLUGINS_ROOT 环境变量
 *   b) 脚本位于 <plugins>/scripts/ 下（主本）
 *   c) 从脚本位置向上找 <dir>/plugins/catalog.json（插件仓分发副本场景）
 */
function resolvePluginsRoot() {
  if (process.env.PARTME_PLUGINS_ROOT) return path.resolve(process.env.PARTME_PLUGINS_ROOT);
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  if (path.basename(scriptDir) === "scripts" && fs.existsSync(path.join(scriptDir, "..", "catalog.json"))) {
    return path.resolve(scriptDir, "..");
  }
  let dir = path.resolve(scriptDir, "..");
  // 优先：插件仓位于 <市场名>-repositories/<插件>/ 下时，市场就是上两级的 <市场名>
  const repoDirName = path.basename(path.dirname(dir));   // …/<市场>-repositories
  if (repoDirName.endsWith("-repositories")) {
    const market = path.join(path.dirname(path.dirname(dir)), repoDirName.replace(/-repositories$/, ""));
    if (fs.existsSync(path.join(market, "catalog.json"))) return market;
  }
  while (dir !== path.parse(dir).root) {
    if (fs.existsSync(path.join(dir, "plugins", "catalog.json"))) return path.join(dir, "plugins");
    try {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        if (entry.isDirectory() && /-plugins$/.test(entry.name)
            && fs.existsSync(path.join(dir, entry.name, "catalog.json"))) {
          return path.join(dir, entry.name);
        }
      }
    } catch { /* 不可读目录跳过 */ }
    dir = path.dirname(dir);
  }
  throw new Error("找不到插件市场仓。可设 PARTME_PLUGINS_ROOT 指定。");
}


if (!pluginId || !["major", "minor", "patch"].includes(level)) {
  console.error("用法: node scripts/bump-plugin.mjs <plugin-id> <major|minor|patch> [--dry-run]");
  process.exit(1);
}

const bump = (v) => {
  const [major, minor, patch] = v.split(".").map(Number);
  if ([major, minor, patch].some(Number.isNaN)) throw new Error(`无法解析版本号: ${v}`);
  if (level === "major") return `${major + 1}.0.0`;
  if (level === "minor") return `${major}.${minor + 1}.0`;
  return `${major}.${minor}.${patch + 1}`;
};

const catalogPath = path.join(root, "catalog.json");
const workspace = path.resolve(root, "..", "full-aigc-plugins-repositories");
const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
const plugin = catalog.plugins.find((p) => p.id === pluginId);
if (!plugin) {
  console.error(`catalog.json 里没有插件: ${pluginId}（现有: ${catalog.plugins.map((p) => p.id).join(", ")}）`);
  process.exit(1);
}

const oldVersion = plugin.version;
const newVersion = bump(oldVersion);
const today = new Date().toISOString().slice(0, 10).replaceAll("-", "");
const repoDir = path.join(workspace, plugin.localDirectory);

const edits = [{ file: catalogPath, description: `${pluginId}: ${oldVersion} -> ${newVersion}` }];

for (const rel of [".zcode-plugin/plugin.json", "kimi.plugin.json", ".agents/plugins/marketplace.json"]) {
  edits.push({ file: path.join(repoDir, rel), description: `${rel}: ${oldVersion} -> ${newVersion}` });
}
// codex manifest 允许 <version>+codex.<date> 后缀（sync 校验认可的形状）
edits.push({
  file: path.join(repoDir, ".codex-plugin/plugin.json"),
  description: `.codex-plugin/plugin.json: -> ${newVersion}+codex.${today}`,
});

console.log(`发版计划: ${pluginId} ${oldVersion} -> ${newVersion}${dryRun ? "（dry-run，不写文件）" : ""}`);
for (const e of edits) console.log(`  - ${path.relative(workspace, e.file)}  ${e.description}`);

if (dryRun) process.exit(0);

// 1) catalog 精确改插件 version（保持文件其余部分不动）
let catalogText = fs.readFileSync(catalogPath, "utf8");
const catalogNeedle = `"id": "${pluginId}"`;
const idx = catalogText.indexOf(catalogNeedle);
if (idx === -1) throw new Error(`catalog.json 中找不到 ${pluginId}`);
const segStart = catalogText.indexOf('"version": "', idx);
const segEnd = catalogText.indexOf('"', segStart + 12);
catalogText = catalogText.slice(0, segStart) + `"version": "${newVersion}"` + catalogText.slice(segEnd + 1);
fs.writeFileSync(catalogPath, catalogText);

// 2) 各仓 manifest
const bumpPlain = (text) => text.replace(`"version": "${oldVersion}"`, `"version": "${newVersion}"`);
const bumpCodex = (text) => text.replace(/"version": "\d+\.\d+\.\d+(?:\+codex\.\d+)?"/, `"version": "${newVersion}+codex.${today}"`);

fs.writeFileSync(edits[1].file, bumpPlain(fs.readFileSync(edits[1].file, "utf8")));
fs.writeFileSync(edits[2].file, bumpPlain(fs.readFileSync(edits[2].file, "utf8")));
fs.writeFileSync(edits[3].file, bumpPlain(fs.readFileSync(edits[3].file, "utf8")));
fs.writeFileSync(edits[4].file, bumpCodex(fs.readFileSync(edits[4].file, "utf8")));

// 3) 重新生成三平台清单 + 全量校验
execFileSync(process.execPath, [path.join(root, "scripts/sync-marketplaces.mjs"), "--write"], { stdio: "inherit" });
execFileSync(process.execPath, [path.join(root, "scripts/sync-marketplaces.mjs")], { stdio: "inherit" });

// 4) 提交提示
console.log(`
✅ ${pluginId} ${newVersion} 发版完成。剩余步骤：
  cd ${root} && git add -A && git commit -m "release: ${pluginId} ${newVersion}" && git push
  cd ${repoDir} && git add -A && git commit -m "release: v${newVersion}" && git push
  ZCode 插件市场刷新后即可看到「可更新」`);

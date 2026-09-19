## 1. Safety remediation

- [x] 1.1 Remove `comfy-rickroll` from the plugin and upstream inventory.
- [x] 1.2 Add a regression test rejecting unconfirmed host-side-effect instructions.

## 2. Skill ownership

- [x] 2.1 Move reusable skills to a dedicated external skill repository.
- [x] 2.2 Add `skills.lock.json`, `plugin-local-skills.json`, and vendor checks.

## 3. Distribution

- [x] 3.1 Add CI for manifests, skills, safety, and vendor integrity.
- [x] 3.2 Bump versions and verify Codex, ZCode, and Kimi manifests.
- [x] 3.3 Publish tag and GitHub Release after all checks pass.

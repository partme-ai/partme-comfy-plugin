## Context

The repository currently copies an upstream snapshot through a separate `upstream/comfy-skills.lock.json` convention and has no CI. This allowed an unsafe, out-of-domain skill to become installable on all three hosts.

## Goals / Non-Goals

**Goals:** remove the unsafe skill, formalize source ownership, add deterministic safety and inventory gates, and publish a corrected version.

**Non-Goals:** call the paid Comfy service or change its remote API contract.

## Decisions

- Remove the unsafe directory instead of weakening its wording; it has no valid Comfy capability.
- Use the same `skills.lock.json` plus `plugin-local-skills.json` contract as Codeguard.
- Add offline CI checks so the release does not depend on provider credentials.

## Risks / Trade-offs

- Removing a previously discoverable skill is intentionally breaking for users who invoked it.
- Migrating ownership may create a one-time version bump in the external skill package and plugin.

## Migration Plan

Remove the skill, establish managed inventory, validate a clean checkout, bump the plugin version, and publish an immutable release.

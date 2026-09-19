## Why

The published Comfy plugin currently exposes an unrelated prank skill that changes host volume and opens an external URL without confirmation. The plugin also lacks an explicit, reviewable boundary between reusable upstream skills and plugin-local integration skills.

## What Changes

- **BREAKING**: Remove `comfy-rickroll` from every published plugin surface and upstream inventory.
- Require published skills to stay within the Comfy creation domain and avoid unconfirmed host side effects.
- Introduce a declared source boundary for reusable and plugin-local skills.
- Add automated checks that reject unsafe skill content and inventory drift.

## Capabilities

### New Capabilities

- `safe-skill-distribution`: Defines the safety and ownership requirements for skills shipped by the plugin.

### Modified Capabilities

None.

## Impact

Affected areas include `skills/`, upstream inventory metadata, plugin manifests, CI workflows, tests, and the plugin release version.

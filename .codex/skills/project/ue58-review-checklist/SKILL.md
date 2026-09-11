---
name: ue58-review-checklist
description: Use for NewWorld UE5.8 code and content review focused on correctness, UObject lifetime, reflection, async, input, replication, assets, performance, tests, and production risk.
---

# UE5.8 Review Checklist

Use a code-review stance. Lead with findings ordered by severity. Read [references/ue-review-risk-map.md](references/ue-review-risk-map.md) for subsystem-specific risks.

## Review Focus

- Unsafe UObject lifetime, missing UPROPERTY/TObjectPtr, invalid async captures, or GC risk.
- Unreal reflection errors, missing module dependencies, editor/runtime module leaks, or Build.cs drift.
- Unnecessary Tick, unbounded spawning, synchronous loads, hard references that should be soft references, or high-frequency allocations.
- Replication mistakes, input ownership confusion, save/load migration risk, or poor data ownership.
- Asset policy violations, missing provenance, wrong import settings, missing Data Validation, or untested UI/audio/content.
- Performance claims without logs, stats, trace, screenshots, or measured evidence.

## Output

Use findings first. Each finding must cite a file, asset, log, or command result and explain the likely impact. Then list test gaps and residual risk.

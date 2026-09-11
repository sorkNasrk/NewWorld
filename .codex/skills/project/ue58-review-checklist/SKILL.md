---
name: ue58-review-checklist
description: Use for NewWorld UE5.8 code and content review focused on correctness, UObject lifetime, performance, assets, tests, and production risk.
---

# UE5.8 Review Checklist

Lead reviews with findings ordered by severity.

Flag:

- Unsafe UObject lifetime, missing UPROPERTY/TObjectPtr, invalid async captures, or GC risk.
- Unnecessary Tick, unbounded spawning, hard references that should be soft references, or expensive synchronous loads.
- Replication mistakes, input ownership confusion, editor/runtime module leaks, and missing validation.
- Asset policy violations, missing provenance, wrong import settings, missing Data Validation, or untested UI/audio/content.
- Performance claims without logs, stats, trace, screenshots, or measured evidence.

# UE Review Risk Map

## C++ And UObject

Watch constructors, CDO/default subobjects, object ownership, delegates, latent actions, async callbacks, timers, replication callbacks, and GC-visible references.

## Gameplay

Watch input ownership, character movement assumptions, camera control, collision channels, damage/interaction authority, unbounded spawning, and save/load compatibility.

## Data And Assets

Watch hard references from globally loaded classes, synchronous loads on gameplay paths, redirectors, missing materials, wrong skeletons, invalid import settings, and unrecorded AI provenance.

## UI And Audio

Watch focus loops, back navigation, controller/touch support, longest text overflow, missing Font Assets, non-looping loop assets, missing variations, and sounds routed outside project mix policy.

## Evidence

Require concrete evidence for claims: command output, logs, trace, screenshots, PIE observation, Data Validation result, or asset QA checklist.

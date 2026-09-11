---
name: ue58-audio-pipeline
description: Use for NewWorld SFX, VO, BGM, ambient beds, UI sounds, cinematic audio, AI Voice prompts, music prompts, Sound Wave, Sound Cue, MetaSound, Sound Class, Submix, attenuation, and in-game audition.
---

# UE5.8 Audio Pipeline

Audio assets require gameplay context and mix intent, not just mood words. Read [references/audio-prompt-fields.md](references/audio-prompt-fields.md) for prompt and QA fields.

## Required Inputs

- Type: SFX, UI, VO, BGM, Ambient, or Cinematic.
- Gameplay trigger, listener position, 2D/3D behavior, duration, loop policy, and variation count.
- Emotional function, energy curve, BPM/rhythm/meter, instrumentation/timbre, attack/decay/tail, and spatial character.
- UE target: Sound Wave, Sound Cue, MetaSound, Sound Class, Submix, attenuation, concurrency, or localization key.
- Approved prompt and exact call parameters for generated audio/voice.

## Defaults

- Generated audio prompts are approved before tool calls and passed verbatim.
- Create variations for repeated gameplay sounds.
- Loops require seamless loop review and at least three playback cycles.
- VO requires exact text, speaker, language, pronunciation notes, subtitle key, delivery, speed, pauses, and file naming.

## Output

Return source/provider, prompt, parameters, file names, UE asset path, routing, loudness/peak notes, loop/variation QA, in-game audition result, and provenance.

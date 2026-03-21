---
name: foundation-1-usage
description: How to use the Foundation-1 (Foundation_1.safetensors) text-to-sample music generation model for structured audio sample generation. Use this skill whenever the user wants to generate music samples, loops, or audio using Foundation-1, needs help writing prompts for the model, wants to understand the model's tag system (instruments, timbre, FX, notation), needs guidance on setup, hardware requirements, BPM/bar timing, or anything related to Foundation-1 inference and production workflows. Also use when the user mentions "Foundation-1", "Foundation_1.safetensors", "stable audio", "text-to-sample", "music sample generation", or asks about generating loops, melodies, basslines, pads, or other musical phrases with AI.
---

# Foundation-1 Usage Guide

Foundation-1 is a structured **text-to-sample diffusion model** fine-tuned from `stabilityai/stable-audio-open-1.0`. It generates musically coherent, production-ready audio loops from layered text prompts. It is NOT a general-purpose music generator or a drum/percussion model — it is specifically designed for **sample-generation workflows** used in modern music production.

The model file is `Foundation_1.safetensors` and its configuration is `model_config.json`, both located in the `Foundation-1/` directory.

---

## Setup

### Required Files

Two files are needed to run the model:
- `Foundation_1.safetensors` — the model weights (16-bit, ~2.3 GB)
- `model_config.json` — the model architecture configuration

### Recommended Interface

The model is designed to work with **RC Stable Audio Tools (Enhanced Fork)**, which provides automatic timing alignment, random prompt generation aligned with training tags, and automatic MIDI extraction.

- **RC Fork**: https://github.com/RoyalCities/RC-stable-audio-tools
- **Original**: https://github.com/Stability-AI/stable-audio-tools

### Setup Steps (RC Enhanced Fork)

1. Clone and install the RC Stable Audio Tools fork
2. Create a subfolder inside the `models` directory
3. Place `Foundation_1.safetensors` and `model_config.json` inside that folder
4. Launch the interface
5. Select the model from the UI

### Hardware Requirements

- **GPU VRAM**: ~7 GB during generation; a GPU with **at least 8 GB VRAM** is recommended
- **Generation Speed**: ~7–8 seconds per sample on an RTX 3090

### Model Architecture (for programmatic usage)

- **Type**: `diffusion_cond` (conditional diffusion transformer)
- **Sample Rate**: 44,100 Hz
- **Audio Channels**: 2 (Stereo)
- **Sample Size**: 882,000 samples (~20 seconds max)
- **Text Encoder**: `t5-base` (max length 128 tokens)
- **Conditioning**: prompt (text), seconds_start (number), seconds_total (number)
- **Diffusion backbone**: DiT with 24 layers, 24 attention heads, 1536 embedding dim

When using programmatically (e.g., via `stable-audio-tools` Python API), set:
- `seconds_start`: 0
- `seconds_total`: the calculated duration based on BPM and bar count (see Timing Reference below)

---

## Prompt Structure

Foundation-1 uses a **layered prompt system** with comma-separated tags. The order of tags is flexible, but a good structure to follow is:

```
[Instrument Family / Sub-Family], [Timbre Tags], [Musical Behavior / Notation], [FX Tags], [Bar Count], [BPM], [Key]
```

### Prompting Best Practices

1. **Start with a clear instrument identity** — use a Major Family name (e.g., `Synth`, `Keys`, `Bass`) or a more specific Sub-Family (e.g., `Synth Lead`, `Grand Piano`, `FM Bass`)
2. **Add 1–3 timbre descriptors** to shape the sonic character (e.g., `Warm, Thick, Gritty`)
3. **Include a notation/structure term** for musical coherence (e.g., `Melody`, `Chord Progression`, `Arp`)
4. **Add FX tags sparingly** — start minimal, then layer more as you learn the model (e.g., `Medium Reverb`, `Low Distortion`)
5. **Always include Bar Count and BPM** — these define the loop structure (e.g., `8 Bars, 140 BPM`)
6. **Always include a Key** — e.g., `C minor`, `F# major`, `Bb minor`
7. **Ensure generation duration matches the musical structure** — see the Timing Reference section
8. Use `Dry` for minimal FX processing, or `Wet` plus FX tags for more processed, spatial sounds

### Example Prompts

**Acid Bass**:
```
Bass, FM Bass, Medium Delay, Medium Reverb, Low Distortion, Phaser, Sub Bass, Acid, Gritty, Wide, Dubstep, Thick, Silky, Warm, Rich, Overdriven, Crisp, Deep, Clean, Pitch Bend, 303, 8 Bars, 140 BPM, E minor
```

**Melodic Flute**:
```
Flute, Pizzicato, Punchy, Present, Ambient, Nasal, Melody, Epic, Airy, Slow Speed, 8 Bars, 150 BPM, E minor
```

**Synth Lead**:
```
High Saw, Spacey, Lead, Warm, Silky, Smooth, 303, Synth Lead, Medium Reverb, Low Distortion, Upper Mids, Mids, Pitch Bend, Arp, 8 Bars, 140 BPM, F minor
```

**Evolving Pad**:
```
Synth, Pad, Chord Progression, Rising, Digital, Bass, Fat, Near, Wide, Silky, Warm, Focused, 8 Bars, 110 BPM, D major
```

**Chiptune Chords**:
```
Chiptune, Chord Progression, Pulse Wave, Medium Reverb, 8 Bars, 128 BPM, D minor
```

**Kalimba Texture**:
```
Kalimba, Mallet, Medium Reverb, Overdriven, Wide, Metallic, Thick, Sparkly, Upper Mids, Bright, Airy, Alternating, Chord Progression, Atmosphere, Spacey, Fast Speed, 8 Bars, 120 BPM, B minor
```

---

## Timing Reference

The model generates loops that must match a specific relationship between **BPM**, **Bar Count**, and **Generation Duration (seconds_total)**.

If the generation duration is too short for the requested bars/BPM, the output will be incoherent. The RC Fork handles this automatically, but for programmatic use, calculate:

```
duration_seconds = (bars × beats_per_bar × 60) / BPM
```

Where `beats_per_bar` = 4 (standard 4/4 time).

### Supported BPM and Duration Table

| BPM | 4 Bars (seconds) | 8 Bars (seconds) |
|-----|------------------|------------------|
| 100 | 9.6 | 19.2 |
| 110 | 8.7 | 17.5 |
| 120 | 8.0 | 16.0 |
| 128 | 7.5 | 15.0 |
| 130 | 7.4 | 14.8 |
| 140 | 6.9 | 13.7 |
| 150 | 6.4 | 12.8 |

**Supported bar lengths**: 4 Bars, 8 Bars
**Supported BPMs**: 100, 110, 120, 128, 130, 140, 150

**Maximum generation length**: ~20 seconds (882,000 samples at 44.1 kHz)

### Key and Mode Support

- All **major keys** (C major, C# major, D major, ..., B major)
- All **minor keys** (C minor, C# minor, D minor, ..., B minor)
- **Enharmonic equivalents** are supported (e.g., `Db major` = `C# major`, `Bb minor` = `A# minor`)

---

## Tag System Overview

Foundation-1's prompt power comes from its **5-layer tag hierarchy**. For the complete list of all tags, read the reference file at `Foundation-1/Master_Tag_Reference.md`.

### Layer 1: Instrument Family (Major Family)

Defines the broad sound source category:

`Synth` · `Keys` · `Bass` · `Bowed Strings` · `Mallet` · `Wind` · `Guitar` · `Brass` · `Vocal` · `Plucked Strings`

### Layer 2: Sub-Family

More specific instrument identity. Selected examples:

- **Synth**: Synth Lead, Synth Bass, FM Synth, Wavetable Synth, Supersaw, Analog Synth
- **Keys**: Grand Piano, Digital Piano, Rhodes Piano, Felt Piano, Wurlitzer Piano, CP Piano, Tack Piano
- **Bass**: FM Bass, Wavetable Bass, Reese Bass, Sub Bass, Electric Bass, Analog Bass, Digital Bass, Picked Bass
- **Bowed Strings**: Violin, Cello, Viola, Fiddle, Digital Strings
- **Mallet**: Marimba, Kalimba, Vibraphone, Glockenspiel, Xylophone, Music Box, Celesta, Steel Drums, Tubular Bells
- **Wind**: Flute, Pan Flute, Piccolo, Clarinet, Oboe, Bassoon, Ocarina, Irish Flute
- **Guitar**: Acoustic Guitar, Electric Guitar, Nylon Guitar
- **Brass**: Trumpet, French Horn, Tuba, Flugelhorn, Bass Trombone, Tenor Trombone
- **Vocal**: Choir, Synthetic Vox, Synthetic Choir
- **Other**: Pad, Atmosphere, Texture, Bell, Pluck, Church Organ, Hammond Organ, Harp, Koto, Sitar, Harpsichord, Clavinet, Saxophone (Alto, Soprano, Tenor, Baritone)

### Layer 3: Timbre Tags

Describe the sonic character of the sound — tonal balance, texture, width, density, grit, warmth, etc. These are composable and can be mixed freely.

**Key timbral categories**:
- **Spectral/Frequency**: Upper Mids, Mids, Highs, Low Mids, Bass, Sub Bass
- **Character**: Warm, Bright, Dark, Cold, Rich, Clean, Gritty, Smooth, Crisp
- **Spatial**: Wide, Near, Far, Spacey, Ambient, Intimate, Big, Small
- **Texture**: Thick, Thin, Fat, Silky, Airy, Soft, Punchy, Tight
- **Synthesis**: Saw, Square, Sine, Triangle, Pulse, Analog, Digital, Retro, Chiptune, 303, 808
- **Specialty**: Metallic, Glassy, Woody, Noisy, Buzzy, Growl, Breathy, Nasal, Dreamy, Sparkly, Formant Vocal

### Layer 4: FX Tags

Processing effects applied to the sound:

- **Reverb**: Low Reverb, Medium Reverb, High Reverb, Plate Reverb
- **Delay**: Low Delay, Medium Delay, High Delay, Ping Pong Delay, Stereo Delay, Cross Delay, Mono Delay
- **Distortion**: Low Distortion, Medium Distortion, High Distortion
- **Modulation**: Phaser, Low Phaser, Medium Phaser, High Phaser
- **Bit Effects**: Bitcrush, High Bitcrush

### Layer 5: Notation / Musical Structure Tags

Control the musical behavior and phrasing:

- **Melodic**: Melody, Top Melody, Arp, Complex, Simple, Catchy, Epic
- **Harmonic**: Chord Progression, Alternating
- **Rhythmic**: Triplets, Bassline, Choppy, Rolling, Staccato, Strummed, Sustained
- **Direction**: Rising, Falling
- **Speed**: Slow Speed, Fast Speed (or just Slow, Fast)
- **Character**: Pitch Bend

---

## Timbral Mixing

One of Foundation-1's unique strengths is **timbral hybridization** — combining an instrument identity with timbre tags from a different sonic domain to create novel sounds:

- `Flute, Metallic, Gritty` — a flute with an unusual metallic edge
- `Piano, Spacey, Ambient, Wide` — a piano that feels atmospheric rather than intimate
- `Bass, Glassy, Bright, Airy` — a bass with an unexpectedly delicate character

Because instrument identity and timbre were trained as separate layers, you can freely mix and match to explore sounds that don't exist in traditional instrument libraries.

---

## Limitations

- **No percussion/drums** — the model is not trained on drum sounds
- **Only 2 genre tags exist** (Dubstep, Chiptune) — they reinforce waveform behaviors, not genre captioning
- **Structured prompts outperform natural language** — use the tag system, not sentences
- **Some timbre tags are stronger than others** — iterate to find the right balance
- **Duration must match the bar/BPM structure** — otherwise output will be incoherent
- **16-bit model only** — no quality loss compared to 32-bit

---

## License

Stability AI Community License:
- **Free** for research and non-commercial use
- **Free for commercial use** if annual revenue is below USD $1M
- **Enterprise license required** for revenue above USD $1M

See `Foundation-1/LICENSE.md` for full terms.

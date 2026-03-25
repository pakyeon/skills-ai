# AI Skills Collection

Welcome to the **skills-ai** repository! 

This repository contains skills focused on **AI model usage** — providing structured, actionable instructions for working with various AI models. Each skill is designed to help AI coding agents comprehensively understand and utilize specific AI models, covering setup, prompting, configuration, and production workflows.

## Available Skills

| Skill Name | Install | Description |
|---|---|---|
| **[foundation-1-usage](skills/foundation-1-usage/)** | ```npx skills add https://github.com/pakyeon/skills-ai --skill foundation-1-usage``` | How to use the Foundation-1 (Foundation_1.safetensors) text-to-sample music generation model for structured audio sample generation. Covers setup, the 5-layer prompt tag system (instruments, timbre, FX, notation, timing), BPM/bar timing calculations, timbral mixing, and production workflows. |
| **[skill-router](skills/skill-router/)** | ```npx skills add https://github.com/pakyeon/skills-ai --skill skill-router``` | Analyze the user's current task and route it to the smallest useful set of already-installed local skills. Best for resolving overlap, exclusions, ordering, and next-step selection among existing skills. |

## How to Use

If you have an AI coding assistant that supports skill importing, simply point it to the relevant skill folder in the `skills/` directory.

---
*More AI model skills will be added soon!*

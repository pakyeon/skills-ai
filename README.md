# AI Skills Collection

A host-agnostic collection of [Agent Skills](https://agentskills.io/) for learning, explaining, and working with AI models and knowledge workflows.

Each skill is scoped to one concrete job. The core instructions can be imported by a skill-capable coding agent or used manually by reading the relevant `SKILL.md`.

## Why this collection?

These skills are designed to make AI work easier to start, easier to route, and easier to reuse:

- **Knowledge-first guidance** for understanding models, concepts, and workflows
- **Clear trigger boundaries** so a skill is used for the task it actually covers
- **Progressive disclosure** through focused entrypoints and optional supporting material
- **Host-agnostic instructions** whenever a workflow does not require a provider-specific feature

## Scope

Use `skills-ai` for AI model usage, concept explanations, knowledge workflows, and deciding which installed skills fit a task.

For concrete development tools, libraries, APIs, and implementation workflows, see the companion [skills-dev](https://github.com/pakyeon/skills-dev) repository.

## Available skills

| Skill | Description | Use when |
|---|---|---|
| **[foundation-1-usage](skills/foundation-1-usage/)** | Setup, structured prompting, timing, and programmatic usage for the Foundation-1 text-to-sample model | “Help me use Foundation-1”, “Write a Foundation-1 prompt”, “Troubleshoot Foundation-1 inference” |
| **[skill-router](skills/skill-router/)** | Select the smallest useful set of already-installed skills and explain exclusions and order | “Which skill should I use?”, “These skills overlap”, “Route this task” |
| **[eli5](skills/eli5/)** | Explain technical or everyday topics in extremely simple terms using short, visual-first steps | “Explain DNS like I’m five”, “Give me a picture-first explanation” |
| **[project-docs-wiki](skills/project-docs-wiki/)** | Maintain project documents in `docs/` with evidence, linked current knowledge, duplicate consolidation, and decision history | “Save the project plan”, “Merge duplicate docs”, “Replace an approved decision”, “Resume from the latest project state” |

## Quick start

### Installation

Install one skill with the `skills` CLI:

```bash
npx skills add https://github.com/pakyeon/skills-ai --skill <skill-name>
```

For example:

```bash
npx skills add https://github.com/pakyeon/skills-ai --skill eli5
```

If your host uses another skill format, copy the matching `skills/<skill-name>/` directory into its skill directory or register that directory according to the host's documentation.

### Usage

Skills usually activate when a request matches their description. You can also invoke one explicitly using the host's skill syntax.

```text
Use $eli5 to explain how DNS works.
```

```text
I have several overlapping skills. Which one should handle this task?
```

## Skill details

### foundation-1-usage

Use this skill for Foundation-1 setup, prompt construction, model-specific timing, programmatic generation, and troubleshooting. It is intentionally not a general music-production or general audio-model skill.

### skill-router

Use this skill when the main problem is choosing among installed skills. It recommends a minimum effective set, calls out exclusions, and suggests an order when more than one skill is needed.

### eli5

Use this skill for beginner-friendly explanations. When workspace writing is available, it creates a self-contained `eli5.html` with simple visual steps; otherwise it returns the explainer directly in the response.

### project-docs-wiki

Use this skill to maintain plans, requirements, designs, decisions, work logs, progress, and other necessary or requested documents under each project's `docs/`. It follows existing project rules and creates folders by role as needed. The instructions and supporting guides are written in Korean.

The workflow preserves source material, analyzes new evidence before integrating it, and distinguishes supported facts, inference, and unverified claims. Stable document IDs, links, and an index keep current knowledge connected. Duplicate consolidation preserves unique information and unresolved questions; replaced decisions move to `legacy/` with reasons and successor links. A recorded approval and a completed implementation remain separate states.

One concise `SKILL.md` routes each task to only the relevant sections of five reference guides. The [methodology notes](skills/project-docs-wiki/references/methodology.md) record the source repositories and pinned revisions behind this synthesis. Apply it during meaningful project work, resumption, or document maintenance.

Install using the collection's usual command:

```bash
npx skills add https://github.com/pakyeon/skills-ai --skill project-docs-wiki
```

Example requests, in the host's explicit skill syntax:

```text
Use $project-docs-wiki to save this project's plan and requirements in docs/ and link related documents.
Use $project-docs-wiki to merge these duplicate design documents, preserving unique information and unverified items.
Use $project-docs-wiki to replace the old decision using this approval record and preserve its history in legacy/.
Use $project-docs-wiki to summarize the current decisions, implementation status, and pending validation from docs/.
```

The optional checker requires Python 3.10+ and uses only the standard library. Replace the placeholders with the installed skill folder, project folder, and current date:

```text
python <skill-folder>/scripts/wiki_health.py --docs <project>/docs --as-of YYYY-MM-DD --json
```

It checks local document structure, links, recorded evidence, and source hashes without modifying documents. It does not verify remote URLs, anchors, factual accuracy, or decision approval. Exit code `0` means no structural errors (warnings may remain), `1` indicates an execution or input error, and `2` indicates structural errors. See the [checker guide](skills/project-docs-wiki/references/health-tool.md) for scope and review requirements.

Run the bundled checks against isolated fixtures in a scratch folder:

```text
python <skill-folder>/scripts/test_wiki_health.py --workspace <scratch-folder>
```

## Repository layout

```text
skills/
├── foundation-1-usage/
├── skill-router/
├── eli5/
└── project-docs-wiki/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Each skill has a required `SKILL.md`. Optional folders such as `agents/`, `references/`, `scripts/`, and `assets/` are used only when they support that skill's actual workflow.

## Contributing

Contributions are welcome. Please follow the [Agent Skills specification](https://agentskills.io/specification):

1. Create the skill in `skills/{skill-name}/SKILL.md`.
2. Keep the `SKILL.md` focused on purpose, triggers, workflow, and non-obvious constraints.
3. Put substantial conditional material in `references/` and link it from the entrypoint.
4. Keep provider-specific integrations optional unless they are essential to the skill.
5. Add the skill to the catalog above with a description and example trigger.
6. Submit a pull request with a concise explanation of the intended use case.

## Resources

- [Agent Skills specification](https://agentskills.io/specification)
- [skills-dev companion repository](https://github.com/pakyeon/skills-dev)

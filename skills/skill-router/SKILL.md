---
name: skill-router
description: Analyze the user's current task and route it to the smallest useful set of already-installed local skills. Make sure to use this skill whenever the user has many overlapping installed skills, asks which of several installed skills should be used, asks which skills to exclude, asks how to sequence overlapping skills, wants to reduce skill selection cost, wants a routing document for a task, or asks for recommended skill combinations, exclusions, priority, or execution order among existing skills. Prefer this skill even when the user does not say "route" or "router" and only says they have "too many skills" or that several installed skills seem redundant.
---

# Skill Router

Route a user request to the minimum effective set of existing local skills.

This skill is for cases where many installed skills overlap and the main problem is not missing capability, but deciding which skill or combination of skills should be used for the current task.

Do not treat this as a skill discovery tool for the public ecosystem unless the user explicitly asks for that. The default scope is the skills already available in the current environment.

## Primary Goal

Given a user task, produce a short routing document that:

- identifies the skills that should be used now
- identifies skills that should not be used now
- explains overlap and why one skill wins over another
- gives a recommended usage order when multiple skills are involved
- flags repeated overlap patterns that may justify future skill consolidation

The goal is decision clarity, not exhaustive cataloging.

## When To Use

Use this skill whenever the user:

- says they have too many skills
- says several skills feel redundant or overlapping
- asks which skill is appropriate for a task
- asks which of their installed skills should be used first
- wants a skill recommendation document for a specific job
- wants to know which skills to exclude
- wants a workflow or order for combining multiple skills
- wants to identify candidates for future consolidation, but is not yet asking you to merge skills

Do not use this skill if the user already named one exact skill and there is no real ambiguity.

## What This Skill Does

1. Inspect the current task.
2. Classify the task by capability needs.
3. Compare those needs against the installed skills.
4. Select the smallest useful set of skills.
5. Produce a routing document with clear recommendations and exclusions.

## Routing Principles

Prefer these principles in order:

1. Minimum effective set
2. Clear specialization over broad overlap
3. Existing trigger fit over speculative usage
4. Stable workflow over clever multi-skill chaining
5. Recommend consolidation only when the same overlap appears repeatedly

## Hard Limits

These limits are important. They keep the router useful.

- Recommend exactly one primary skill whenever possible.
- Recommend no more than two supporting skills.
- Do not recommend more than three total skills unless the user explicitly asks for a broader map.
- If more than three skills seem relevant, force-rank and cut.
- If two supporting skills do nearly the same thing, cut one.
- If no skill is actually needed, say `no skill` instead of forcing a recommendation.

## Task Analysis Checklist

Before selecting skills, identify:

- the task type
- whether the user wants analysis, implementation, review, research, generation, or evaluation
- whether web access or external docs are needed
- whether code edits are required
- whether the task is domain-specific
- whether design quality or UI review is central
- whether the user needs one main skill or a sequence of supporting skills

## Selection Rules

Choose skills using these rules:

- Pick one primary skill whenever possible.
- Use `skill-router` as the `Primary Decision` only when the immediate task is genuinely about routing itself.
- After you have identified the concrete domain skill for the user's next action, that domain skill must become the `Primary Decision`, not `skill-router`.
- Add a supporting skill only if it contributes a distinct capability the primary skill does not cover well.
- If two skills overlap heavily, prefer the one with the narrower and more direct fit for the current task.
- If two skills are near-duplicates for this task, choose one and explain why. Do not present both as equal options unless the user explicitly asks for alternatives.
- If one skill is a helper for another, place it after the primary skill unless the helper is needed first for discovery or validation.
- If the task can be completed well without a skill, say so.
- If you are tempted to recommend many skills just because they are all relevant, stop and cut the list to the minimum effective set.

## Overlap Resolution

When skills overlap, explain the tradeoff explicitly.

Use this decision pattern:

- `better direct fit`: one skill matches the task wording and expected output more closely
- `better depth`: one skill has more specialized instructions for the domain
- `better support role`: one skill is useful only as a secondary step
- `exclude for now`: a skill is valid in general, but unnecessary for this task

Do not recommend multiple near-duplicate skills just to be safe. Redundant recommendations increase decision cost.

## Output Format

Use this exact structure and copy the section headings verbatim unless the user asks for another format:

```md
# Skill Routing

## Task Summary
<one to three sentences>

## Primary Decision
<the one main skill to use now, or `no skill`>

## Recommended Skills
- <skill>: <why it is needed now>

## Excluded Skills
- <skill>: <why it is not needed now>

## Overlap Notes
- <skill A> vs <skill B>: <why one wins for this task>

## Suggested Order
1. <first skill or no skill>
2. <second skill if needed>
3. <third skill if needed>

## Consolidation Signals
- <repeat overlap pattern or "none for this task">
```

Keep the output short. Prefer explanation density over long coverage.

## Default Decision Heuristics

Apply these heuristics when relevant:

- For a frontend build request, prefer the strongest design or implementation skill first, then add framework-specific or review-oriented helpers only if needed.
- For a UI review request, prefer review and guideline skills over creation skills, and use the review skill itself as the `Primary Decision`.
- For a docs or API lookup request, prefer documentation retrieval over broad web search. If the user is still asking which local skill to use first, `skill-router` may remain primary for that routing step. Once the task shifts to doing the lookup, `find-docs` should be the `Primary Decision`.
- For web search across external sources, prefer search or extraction skills based on whether the user needs discovery or content retrieval.
- For a single concrete library workflow, prefer the most domain-specific skill over a general best-practices skill.
- For mixed requests that combine building and reviewing, route to the skill that matches the immediate next step first, then place the review or implementation helper second.

## Consolidation Guidance

This skill may mention consolidation opportunities, but it must not merge or rewrite skills unless the user explicitly asks.

Flag a consolidation candidate only if:

- the same two or more skills are repeatedly co-selected
- the overlap causes frequent ambiguity
- the combined workflow is stable across tasks

If those conditions are not met, recommend routing rather than consolidation.

## Example

**Input:**
I want to build a landing page, but I have too many frontend-related skills and I only want the ones I actually need.

**Output:**

```md
# Skill Routing

## Task Summary
The user wants to build a visually strong landing page and needs a minimal skill set from overlapping frontend skills.

## Primary Decision
frontend-skill

## Recommended Skills
- frontend-skill: best fit for shaping the landing page structure and visual direction
- shadcn: use only if the page should be built with shadcn components

## Excluded Skills
- frontend-design: overlaps with frontend-skill for this request and is unnecessary in the first pass
- web-design-guidelines: useful later for review, not required for the first pass
- vercel-react-best-practices: useful only if performance or Next.js implementation details become central

## Overlap Notes
- frontend-skill vs frontend-design: frontend-skill is the more direct fit for a landing-page-oriented request

## Suggested Order
1. frontend-skill
2. shadcn if component scaffolding is required
3. web-design-guidelines only as a review pass

## Consolidation Signals
- frontend-skill and frontend-design may need clearer boundaries if this overlap appears repeatedly
```

**Example 2:**
Input: I do not want implementation yet. Review my landing page and tell me which design or build skills should be ignored for this critique pass. Mention any later implementation skills separately.

Output:

```md
# Skill Routing

## Task Summary
The user wants a review-only pass on an existing landing page and wants overlapping build skills cut from the current step.

## Primary Decision
web-design-guidelines

## Recommended Skills
- web-design-guidelines: best fit for a critique-focused pass centered on UI review and guidance

## Excluded Skills
- skill-router: the routing decision is already complete, so it should not remain the primary tool
- frontend-design: useful for later redesign or implementation, not for the current critique pass
- frontend-skill: useful for building or reshaping the page later, not for this review-only step

## Overlap Notes
- web-design-guidelines vs frontend-design: the review skill wins because the immediate task is critique, not creation

## Suggested Order
1. web-design-guidelines
2. frontend-design only if the user later asks for redesign
3. vercel-react-best-practices only if the work moves into React or Next.js code

## Consolidation Signals
- none for this task
```

## Writing Style

Be decisive. The user is asking for reduced ambiguity.

- avoid long catalogs
- avoid saying every skill is potentially useful
- prefer concrete exclusions
- explain choices in plain language
- optimize for the next action, not theoretical completeness
- if the recommendation feels too broad, cut it again

## Failure Modes To Avoid

Do not produce a generic inventory of all installed skills. That defeats the purpose of routing.

Do not turn the answer into a discovery report for external skills unless the user explicitly asked for new skills.

Do not list all plausible skills. If a skill is not necessary for the next action, exclude it with a reason.

Do not recommend a broad pile of "maybe useful" skills. The main value of this skill is narrowing, not collecting.

Do not keep `skill-router` as the `Primary Decision` after the routing choice has already been made and a more specific domain skill is ready for the user's next action.

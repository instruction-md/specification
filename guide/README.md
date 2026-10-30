# Writing instruction.md

An instruction is shared guidance that people can review and agents can use.
Start with ordinary Markdown, then add structure where it carries useful meaning.

Rich instructions can remain concise or carry detailed conditions, reasons,
examples, policies, response contracts and connected context. That verbosity is
authored meaning: a renderer must not shorten or drop it to make a cleaner UI.
Standardized parsing keeps the same structure available to agents, while rich
rendering gives people a clear way to read and review it.

For precise processes, see [Writing a workflow](workflows.md). The native workflow
language, schemas and node definitions are now part of this specification.

## A small instruction

```markdown
---
spec: "1"
title: Morning assistant
parameters:
  timezone: { type: string, default: America/Toronto }
---

# Morning assistant

Prepare a useful plan for the day in ${timezone}.

MUST[status]: distinguish confirmed and tentative appointments.
BECAUSE: a tentative invitation is not a commitment.
SHOULD: recommend one uninterrupted focus period.

:::output{response-format=markdown title="Daily brief"}
Start with commitments, then priorities, then decisions that need the owner.
:::

---
authors: [Alex]
history:
  - { date: "2026-10-26", summary: Describe the daily brief }
```

Use `MUST`, `NEVER`, `SHOULD`, `SHOULD NOT` and `MAY` deliberately. `GUARDRAIL`
marks a boundary for particular attention; the word alone does not enforce it.
A rule's name lets reviewers and other instructions reference it. Give reasons
with `BECAUSE:` and task-time conditions with `(if …)`.

## Connect people and services

```markdown
::person{id=owner title="Alex" role=owner src="https://example.org/people/alex"}

:::mcp{id=calendar title="Calendar" src="https://example.org/mcp/calendar" account=personal tools="events.list"}
Read appointments for planning. Ask before changing an invitation.
:::

Ask :person[Alex]{ref=#owner} when :mcp[Calendar]{ref=#calendar} is ambiguous.
```

The web editor or VS Code extension can show pills, profiles, connection
status and completions. The source retains identities and labels. An account
alias connects through the reader's host; the file does not carry credentials.

## Add rich explanations

Use callouts, figures, captions, footnotes, glossary definitions and diagrams.
Use columns/cards/tabs/steps for reviewable layout. All tabs and collapsed
panels remain available to agents. A code fence is an example until an explicit
external testing/export operation chooses it as input.

````markdown
:::example{title="Good status wording"}
Your 09:00 catch-up is tentative. Your 11:00 review is confirmed.
:::

```mermaid
flowchart LR
  A[Read appointments] --> B[Keep status]
  B --> C[Suggest priorities]
```
````

An example is quoted material, even if it contains `MUST:`. For editable drawings
keep the drawing source, a preview and a useful description. Media may be local,
remote, embedded or packaged in a bundle.

## Reuse and inherit

A link navigates. An embed previews. An include incorporates content. Inheritance
starts from bases and supports explicit changes with visible provenance.

```yaml
extends:
  - { uri: ./base.md, as: personal, mode: live }
```

```markdown
:::replace{target="#personal/brief-length" reason="Shorter phone preview"}
Keep the brief under 150 words.
:::

::include{src="./team.md#id=privacy" as=privacy required}
```

A replace changes the content of the named inherited target while keeping its
identity/kind. For a rule target, write its replacement text without repeating
its keyword label. To change kind, explicitly remove it and add a new block.
IDs from a base/include stay qualified by its alias. Relative resources retain
their original source location. Use `mode=pinned` with a full source digest when
an exact snapshot is needed; use `live` for updates between resolution runs.

## Test through integrations

Scripts, schedules, workflows, test cases and evaluations can be documented
beside their guidance. An editor can offer test controls using your connected
services. The host records which source snapshot was tested and exposes results.
Opening the file does not activate a schedule or deploy an assistant. External
systems can import the declared objects through explicit adapters.

## Metadata and extensions

Front matter describes the document and configures parameters, dependencies,
resolvers, extensions and appearance. Backmatter follows a blank line and a
plain `---` separator, with no label or closing fence. It records authorship,
history, review and source/test references through EOF. Start its mapping with
a known metadata key such as `authors:` or `history:` so it can be distinguished
from a thematic break. Neither metadata region becomes extra hidden guidance.

Third-party blocks use an alias such as `charts:metric`, declared in front
matter with an exact extension identity/version. Extensions supply schemas,
shared-content fallbacks and the adapters they support. Unsupported optional
presentation shows its source/fallback; missing required semantics is visible.

Read the [language reference](../reference/markdown.md), [cheat sheet](cheatsheet.md)
and [complete morning assistant](../samples/morning-assistant/instruction.md).
The complete grammar and processing contracts are in the [specification](../README.md).


## One source for an agent setup

A `config` block carries a named runtime dialect; a `workflow` block carries
its native workflow model. Front-matter `exports` bindings explicitly select
which guidance, server declarations, inline skills and workflows a compiler
turns into native files. The generated files retain source hashes and origins.

For example, the [AgentD profile](../profiles/agentd.md) emits native configuration,
workflow JSON, selected guidance and `skills/<id>/SKILL.md` packages from a single
[authored instruction](../samples/agentd-assistant/instruction.md).
Compilation does not connect accounts or start the runtime. A rich diagram is
an explanation of the workflow; it does not replace the native DSL definition.

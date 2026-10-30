# AgentD compilation profile

**Profile:** `agentd/1`. **Dialects:** `agentd/config`, `instruction/workflow`;
`agentd/workflow` is retained as a compatibility identifier.
**Status:** First-edition working draft. This is an Instruction export profile,
not a claim that an existing AgentD instruction parser accepts this draft's syntax.

## Purpose

Maintain one `instruction.md` source, then explicitly compile its selected
configuration, guidance, MCP declarations, inline skills and workflow definitions
into native AgentD inputs. The output is reviewable and can be packaged in an
Instruction bundle. Compilation does not start AgentD or activate any workflow.

AgentD's existing instruction integration documents older sigilled forms.
This profile uses the new document model and emits native files instead of
requiring the runtime to parse those new blocks directly.

## Upstream contracts

The native schema snapshots used for the authored example were retrieved from
the official endpoints on 2026-10-27:

| Dialect | Native schema | SHA-256 |
|---|---|---|
| `agentd/workflow` | <https://agentd.dev/schema/workflow.json> | `40f1d4a06967af70705d1b6aa508ebcc7defc7693ad3e8d8570eb02637ac5f23` |
| `agentd/config` | <https://agentd.dev/schema/config.json> | `e9d632c2298d3e8ff80ec4f33419b6449ecd79e69853c75b37a071be7e562f5d` |

Native documents do not gain an invented `version:` field. Profile identity and
schema pins live in Instruction attributes and compiler provenance. A changed
schema is a deliberate profile update, not an automatic reinterpretation.

Primary references: [workflow language](https://agentd.dev/docs/workflow-language/),
[node reference](https://agentd.dev/docs/node-registry/),
[human review](https://agentd.dev/docs/human-in-the-loop/), and
[configuration](https://agentd.dev/docs/configuration/).

## Binding contract

An `exports` target names `adapter: agentd`, `profile: agentd/1`, and bindings:

| Binding | Meaning |
|---|---|
| `config` | One `config` block using `agentd/config` |
| `instruction` | One explicit guidance block to serialize to `guidance.md` |
| `servers` | Selected `mcp` IDs to map into native `mcp.servers` |
| `skills` | Selected inline `skill` IDs to emit as `skills/<id>/SKILL.md` |
| `workflows` | Selected `workflow` IDs using `instruction/workflow`, or the compatibility `agentd/workflow` |

All references are resolved identities, not fuzzy title matches. Names and
output paths must be unique. A native configuration that already supplies a
section also supplied by a binding is an `export-conflict`; no silent grant merge
or arbitrary precedence is allowed. This profile expects the explicit native
paths `./guidance.md` and `./skills` for its selected generated guidance/skills.
Paths must stay within the output root.

An MCP declaration maps its ID to native `name`/`ns`, its `src` to `endpoint`,
its `allow` (or explicit `tools` list) to `allow`, and `deny` to `exclude`.
AgentD's exclusion rules take precedence. Native agent tool selection remains
an additional restriction. Host authentication/account aliases are bound by the
operator; no credential is invented, copied from the environment or bundled.

An inline skill exports its readable body with Agent Skills-compatible `name`
and `description` front matter. A referenced packaged skill requires resource
closure and its own validation; it is not silently rewritten as an inline one.
An A2A agent's advertised skills do not automatically become packaged skills.

## Workflow DSL

The language and its complete node registry now belong to the native
[Instruction Workflows specification](../reference/workflows.md). This profile
defines how a compatible workflow is exported to AgentD. Hosts validate both
the native language and the subset/features their installed runtime supports.
The pinned example below retains its compatibility dialect for reproducibility.

A workflow has a `name` and a `steps` mapping. Each step declares its `kind`;
`depends_on` identifies predecessor step IDs. Native `{{ … }}` expressions are
preserved verbatim, including `{{ steps.calendar.output }}`.

A workflow can describe starts, MCP calls, agent/model steps, human gates,
branching and terminal `finish` outcomes. The profile must validate the pinned
schema plus supported node fields, unique identities, existing dependency and
routing targets, allowed start/terminal structure, and prohibited cycles or
other graph rules of the selected native implementation. Per-step timeout and
retry values retain their native meanings.

A `human` gate can constrain its answer with a schema; a `switch` routes on the
answer. A sequence diagram can explain that exchange, but it is not executable
workflow syntax. Visual edits must preserve the native workflow model.

The upstream workflow schema snapshot has scheduling fields `cron`, `every`,
`at` and `inputs`. It does not declare a `tz` property on a schedule start.
Examples must not invent one; use UTC cron when using that native schedule node,
or a separately named scheduling dialect with explicit timezone semantics.

## Output and verification

Generated artifacts include `agentd.json`, `guidance.md`, native workflow JSON,
inline skill packages and an `instruction.json` bundle manifest. The manifest
records exported paths, hashes, profiles and contributing source snapshots.
If external schemas/providers/resources are not packaged, the bundle must not
claim to be fully self-contained.

The repository's worked example is original example content. It was validated
against both pinned official JSON Schemas and bounded graph checks. No AgentD
binary, MCP service or model was run. Schema/fixture consistency does not prove
native runtime conformance; native validation and an explicit activation step
remain necessary.

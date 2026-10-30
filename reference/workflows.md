# Instruction Workflows

**Dialect:** `instruction/workflow`. **Revision:** `1`.
**Status:** First-edition working draft. This is a native part of instruction.md.
**Date:** 2026-10-28.

Instruction Workflows describe reusable processes as named, typed steps. The
language includes triggers, data flow, model and tool calls, conditional routes,
parallel work, human decisions, durable waits, recovery and terminal outcomes.
AgentD contributed the initial language; it is now specified here independently
of any one runtime. An implementation advertises the node kinds and expression,
identity, storage and integration capabilities it supports.

The [workflow schema](../schemas/workflow.schema.json) and
[node registry](../workflow-registry.json) are normative machine-readable parts
of this reference. The registry retains all 74 imported kinds, including the 11
trigger kinds. Schema validation is one layer of validation; the graph and
behavioral requirements below also apply. A renderer is not a workflow host.

## Declaring a workflow

````markdown
:::workflow{id=brief dialect="instruction/workflow"}
name: morning-brief
steps:
  start:
    kind: manual
  draft:
    kind: agent
    depends_on: [start]
    instruction: Prepare a concise daily brief. Preserve uncertainty.
  review:
    kind: human
    depends_on: [draft]
    question: Accept this brief?
    schema: { type: string, enum: [accept, revise] }
  route:
    kind: switch
    depends_on: [review]
    on: "{{ steps.review.output }}"
    cases: { accept: accepted, revise: revision }
  accepted:
    kind: finish
    depends_on: [route]
    output: "{{ steps.draft.output }}"
  revision:
    kind: finish
    depends_on: [route]
    status: cancelled
    reason: The reviewer requested a revision.
:::
````

The outer `id` is an Instruction object identity; `name` is the workflow's
identity within its workflow host. `dialect` selects this contract. YAML and
JSON are equivalent representations of the same model. Duplicate mapping keys
are errors. A structured workflow body is literal: Markdown directives and
Instruction `${parameter}` substitutions do not activate inside it. Workflow
`{{ … }}` templates have the meanings below.

Opening, parsing, resolving, compiling or rendering the instruction MUST NOT
arm triggers, register tools, expose routes, send messages or start a run.
Activation is an explicit host operation after validation and authorization.

## Definition fields

| Field | Meaning |
|---|---|
| `name` | Required identifier, 1–64 characters, matching `[A-Za-z_][A-Za-z0-9_-]*` |
| `steps` | Required mapping from step IDs to typed definitions |
| `description` | Human-readable purpose, also usable as a registered tool description |
| `armed` | Whether an explicitly activated definition may arm its triggers; default `true` |
| `inputs.schema`, `outputs.schema` | Schemas for run input and terminal output |
| `concurrency` | `max_runs`, `on_overflow` (`queue`, `drop`, `replace`) and `scope` (`workflow`, `key`) |
| `key` | Trigger-time template that identifies the entity a run concerns; required for key-scoped concurrency |
| `limits` | Per-run steps, tokens, deadline and budget |
| `priority` | `low`, `normal` or `high`; a scheduling preference, never a permission grant |
| `durable` | Whether run state survives the host process; `false` explicitly permits memory-only runs |
| `state` | Declared run-variable schemas and concurrent-write reducers |
| `unload` | Retirement policy: `drain`, `cancel` or `detach`, with optional timeout |
| `tool` | A proposed callable-workflow interface with name, sync/async mode and caller grants |
| `act_for` | Proposed delegated principal and consent mechanism; operator approval is required |

Unknown standard fields and unknown kind names are errors. Namespaced `x-*`
fields can carry declared extension data. A host MUST report an unsupported
extension that affects behavior rather than silently discard it. Configuration
directives that load a file, URL, folder or MCP resource belong to the host's
configuration; they are not alternative workflow definitions.

Input validation occurs before admission. Invalid inputs do not create a run.
Completed outputs must satisfy `outputs.schema`; a schema failure is not a
successful completion. Resource limits and concurrency admission must be
recorded in the run's execution profile so the outcome can be reviewed.

## Graphs, scopes and validation

The dependency graph is acyclic. Step IDs are unique within a scope. Every
top-level step must be reachable from a trigger through dependency or explicit
routing edges. A top-level graph needs at least one trigger and one `finish`.
Dependency names, switch targets, error targets and timeout targets must exist
in the same scope. Switch case values name **one step as a string**, not a list.

`foreach`, `batch`, `iterate` and `subgraph` contain `body: {steps: …}`.
`parallel` and `race` contain named `branches`, each with its own `steps`.
Dependencies inside a body name siblings. Nested scopes cannot contain triggers
or `finish`; their result is their terminal sink steps. Maximum nesting is four
body levels, and top-level definitions contain at most 512 steps. Generated
instance IDs identify the iteration or branch, for example `each[0].draft`,
`parallel{research}.fetch` or `sub.review`.

An implementation must validate types, kind-specific required fields, scopes,
references, reachability, cycles, expression capabilities and limits before
activation. The JSON Schema deliberately leaves some adapter payload values
open; it does not validate a remote tool's arguments, all expression paths,
authorization or runtime behavior. Those checks require the relevant host and
integration contracts. Required unsupported kinds are an error, not a no-op.

## Triggers

The registry includes `once`, `manual`, `loop`, `schedule`, `subscribe`,
`stream`, `correlate`, `signal`, `event`, `a2a` and `webhook`.

A trigger produces an event for admission, rather than directly performing
downstream work. Its payload becomes the firing trigger's step output. A run
fires exactly one trigger; sibling triggers become `skipped` and satisfy
dependencies. Trigger `inputs` mappings use the trigger-time `payload` and
`env` namespaces; the resulting run inputs are checked against `inputs.schema`.

`schedule` accepts `cron`, `every`, or `at`, with exactly one timing source.
The inherited five-field cron dialect is UTC. It does not gain an implicit
`tz` field: calendar-local recurrence can use the separate `schedule` block's
explicit scheduling dialect. Hosts record missed-firing and resumption policy.
`loop` combines interval/delay/backoff with termination conditions and a maximum
iteration bound. `once` and `manual` distinguish automatic activation from an
operator-requested run.

`subscribe` reads a named MCP resource after change notifications and can
debounce, filter and collect a bounded sample window. `stream` consumes
persisted events with subject filtering, offsets and rate/batch controls.
`correlate` groups related events in a bounded window with a pending-state cap.
`signal` is an edge-triggered notification: existing waiters receive it, and a
signal sent before a waiter is registered is not buffered. Use a persisted
stream when retention is required. Events and subscriptions require explicit
host capability and authenticated source bindings.

`a2a` binds accepted commands, principal roles and an input schema. `webhook`
describes an incoming path, methods, authentication, rate and response policy.
Declaring either never creates an unauthenticated listener. The host authorizes
and binds them during activation.

## Shared step fields

Every step has `kind`. Shared fields are `depends_on`, `description`, `when`,
`timeout`, `retry`, `on_error`, `on_replay`, `idempotent`, `output_schema`,
`budget`, `cache`, `skills` and `otel`. Their availability does not imply that
a host supports every node or integration.

`timeout` bounds an attempt or a node-specific wait. `retry.max` counts retries
after the first attempt, is between zero and twenty, and `retry.backoff` gives
the initial exponential delay. Backoff is durable, with bounded growth and
jitter. `on_error` is `fail` (default), `continue`, or `goto:<step>`.
`on_replay` is `retry` (default), `skip`, or `fail`. A host records defaults and
the effective model, tool, network and budget constraints in its run profile.

Network node fields can additionally declare `breaker: {failures, cooldown}`,
`rate`, and `idempotency`. Retries handle an attempt failure; breakers share
outage state across runs; rate controls postpone work without spending an
attempt; idempotency makes repeat delivery recognizable. These controls have
different meanings and MUST NOT be collapsed into one retry count.

## Templates and expressions

A string that consists of exactly one `{{ path }}` yields the referenced typed
value. A string with surrounding text interpolates, preserving strings and
encoding other values as JSON. `{{ path | fallback }}` supplies a fallback
only for a missing path; an existing `null` does not use the fallback.
A leading `/` selects a JSON Pointer path, useful for generated IDs containing
dots. Missing paths without a fallback fail the attempt.

| Namespace | Meaning |
|---|---|
| `inputs` | Validated run inputs |
| `run` | Run/workflow identity, start, principal, task, attempt and status |
| `steps.<id>` | Status, output, error and attempt of a step; sibling IDs inside a body |
| `vars` | Declared or written run variables |
| `env` | Host/run context; per-step `step`, `attempt`, and stable `idempotency_key` |
| `memory` | Explicitly bound durable memory keys |
| `item`, `index`, `as` alias | Current collection member and index |
| `batch`, `iteration`, `branch` | Nested execution context |

`CEL: …` evaluates a CEL expression. Guard `when`, assertion conditions,
map/filter/reduce expressions, iteration conditions and subscription filters
use their documented evaluation contexts. Nested `body` and `branches`, schemas,
switch target maps and expression-bearing fields remain literal until their
own node evaluates them. A host without a required CEL capability must refuse
activation. It cannot replace the expression with truth.

`when` can also use `{noul: "statement", state?, model?, confidence?}` for a
model-backed decision. The host represents that decision as a durable,
budgeted `<id>.when` step. An unsure or insufficient-confidence answer declines
the guard. The effective decision threshold must be explicit in the run
profile. A prose rule condition in the surrounding instruction is distinct
from this executable workflow guard.

Secret markers such as `{{secret:NAME}}` and `{{secret-file:PATH}}` resolve only
in authorized credential-bearing integration fields. Elsewhere they remain
literal. Secrets do not become ordinary step output, document metadata or log
content. Instruction resolution does not read the host's secret store.

## Branching and joining

A false top-level `when` or an unchosen switch route makes a step `pruned`.
A pruned step does not satisfy dependencies. A step whose inbound paths are
all pruned is pruned; at least one live path keeps a join eligible. A skipped
step does satisfy dependencies. This distinction allows uneven branch joins.

A selected switch route, `on_error: goto:…`, or `on_timeout` can activate its
target without waiting for that target's dependency list, but cannot bypass
its `when` guard. Routing edges can revisit a step; the dependency graph still
must be acyclic and the run remains bounded by its limits. A recovery route
whose guard declines does not erase the original failure.

Inside a body, a false `when` produces `skipped`, allowing subsequent sibling
steps to proceed. Unchosen switch cases in bodies still use pruning. Hosts
and visualizers must preserve the difference instead of presenting all inactive
nodes as equivalent. A Mermaid image cannot redefine this behavior.

## Parallel, repeated and delegated work

`parallel` runs named branches; `race` selects the earliest qualifying result
and cancels losing work. `foreach` runs a body per item with bounded `batch`
size, parallelism and rate. `batch` gives each body a group. `iterate` repeats
against `while`/`until` with a maximum iteration bound. Collection policy is
explicit through `collect`. A body cannot silently inherit unbounded fan-out.

`workflow` invokes a named child in `sync`, `async` or `detached` mode; async
returns a handle. `join` waits on handles with timeout/minimum/partial-result
policy. `cascade` controls child cancellation. `subagent` delegates bounded
work with explicit tools, servers, skills, context and budgets. A2A nodes bind
named peers, task/message contracts and completion waits. Delegation may narrow
authority; declaring a child must not widen the caller's effective permissions.

## Waiting and human decisions

`wait`, `sleep`, `human`, child waits and retry backoffs suspend through durable
wait records rather than an in-memory blocking thread. A wait may name a
resource, event, signal, run, subagent, conversation, webhook, task or other
registered wait condition. `on_timeout` is an explicit routing target. A human
gate names a question, optional answer schema and intended recipient. Answers
are validated and bound to an authorized principal; rendering an approval pill
or checking a box in documentation is not an approval.

An implementation claiming durable execution must restore suspended waits and
their deadlines. It must distinguish a saved declaration from an active run,
and an authored checkpoint from a recorded human decision.

## Run and step states

Run states are `running`, `paused`, `completed`, `failed`, `refused`,
`cancelled`, and `stalled`. The first two are non-terminal. A `finish` determines
the terminal status/output; reaching no ready work, no in-flight work and no
finish is `stalled`, or `failed` when an upstream error caused the blockage.

Step states are `pending`, `running`, `suspended`, `done`, `skipped`, `pruned`,
`failed`, `timeout`, and `cancelled`. Only `done` and `skipped` satisfy an
ordinary dependency. An error under `on_error: continue` completes with the
error recorded. Ending a run cancels unfinished steps. Exit codes, persistence
backends and client protocols are runtime adapter concerns rather than new
Markdown syntax.

## Durability, idempotency and updates

An effectful step checkpoints `running` before the effect. Deterministic data
steps can replay from the preceding checkpoint. After a crash, an effect that
completed remotely but lost its acknowledgement may be delivered again. The
contract is at-least-once delivery; it is not exactly-once remote execution.

The default idempotency key is the first 32 hexadecimal characters of
`sha256(run_id + "." + step_instance_id)`, stable across retries/replay of that
instance. A declared business key can deduplicate across runs. Remote tools and
services must actually honor the key for deduplication to occur. `on_replay`
controls whether uncertain work is retried, skipped or failed. A host must not
claim replay safety merely because a key was sent.

A run records its definition digest and the execution profile. Updating a live
definition affects subsequent admissions; existing runs retain their pinned
definition. Restore requires the matching definition, and must not substitute
the latest text. Retirement applies `unload` and records cancellation/draining.
Memory, artifacts, stream offsets and trigger checkpoints have distinct
lifetimes. Sensitive artifacts retain host access controls and are not silently
copied into instruction bundles.

## Node catalog and extension points

The complete [node reference](workflow-nodes.md) is generated from the native
registry and lists required and optional fields for every imported kind. It
covers triggers, flow control, data transforms, memory, artifacts, knowledge,
search, MCP, HTTP, A2A, messaging, workflow lifecycle, model operations, agents
and human gates. Node providers may be separate host integrations; inclusion in
the language is not a promise that a host has an account or implementation.

Workflow hosts publish a capability profile with node kinds, expression
features, resource bounds, credential/identity bindings and durability support.
Custom behavior uses declared namespaced extensions, with explicit schema and
capability requirements. Unknown executable behavior must never fall back to
running an approximation. Renderers preserve source and show unsupported
semantics visibly; render-only use can remain useful without a runtime.

A custom node uses `kind: alias:node`. Its outer Instruction extension binding
selects an exact manifest/version; a standalone workflow gets equivalent bindings
from its host profile. `provides.workflow_nodes` in the extension manifest maps
node names to `role` (`trigger` or `step`), a node `schema`, a `semantics`
contract, and optional `requires` capabilities. The base workflow schema can
preserve the namespaced node, but activation additionally validates that
manifest and its installed provider. Source metadata never installs code or
authorizes a provider. The repository's bounded native graph checker rejects
such nodes as unsupported rather than claiming extension-host conformance.

## Migration and provenance

The initial registry and shared fields were imported at the owner's request
from the AgentD schema snapshot with SHA-256
`40f1d4a06967af70705d1b6aa508ebcc7defc7693ad3e8d8570eb02637ac5f23`.
The exact snapshot is retained in [upstream provenance](upstream/agentd-workflow.schema.json).
The instruction.md schema adds per-kind field checks and explicit recursive
body structure. Graph and behavioral checks remain separate.

`agentd/workflow` remains an adapter compatibility identifier. New native
documents use `instruction/workflow`; [the AgentD profile](../profiles/agentd.md)
can export compatible definitions to AgentD without rewriting their step data.
No AgentD installation, server configuration, published site or runtime was
changed by this migration. This working draft and its new conformance cases
still require independent runtime implementation review before a final release.

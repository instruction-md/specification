# Workflow node reference

This catalog is normative alongside [Instruction Workflows](workflows.md).
Shared fields are defined in the language reference. Hosts advertise which
node providers and execution capabilities they support. The catalog does not
claim that every host implements every node.

| Kind | Role | Meaning | Required fields | Other fields |
|---|---|---|---|---|
| `a2a` | Trigger | Accept an authenticated command with declared roles and an input contract. | — | `command`, `roles`, `inputs`, `schema`, `into` |
| `a2a.delegate` | Step | Delegate an objective and output contract to an authorized peer. | `peer` | `objective`, `command`, `args`, `output_contract`, `timeout`, `idempotency`, `breaker`, `rate`, `auth_to`, `auth_timeout`, `payment` |
| `a2a.send` | Step | Send an authenticated message or command to a named destination. | `to` | `parts`, `command`, `args`, `context`, `timeout`, `idempotency`, `breaker`, `rate`, `payment` |
| `a2a.wait` | Step | Wait for a matching conversation response from an expected peer. | `from` | `conversation`, `timeout` |
| `agent` | Step | Run a bounded tool-using model turn with explicitly narrowed capabilities. | `instruction` | `output_contract`, `output_schema`, `tools`, `servers`, `limits`, `context`, `skills`, `system`, `model`, `effort` |
| `artifact.create` | Step | Store content as an artifact with media type and sensitivity metadata. | `name` | `mime`, `content`, `from_step`, `sensitive` |
| `artifact.delete` | Step | Delete an artifact the active principal may manage. | `id` | — |
| `artifact.get` | Step | Read an artifact under the host access policy. | `id` | — |
| `assert` | Step | Fail unless its expression holds, recording the assertion message. | `condition` | `message` |
| `assign` | Step | Write a rendered value into a run variable using its reducer and schema. | `value` | `writes`, `mode` |
| `batch` | Step | Run a scoped body per group, with grouping, size, parallelism and collection policy. | `over`, `body` | `by`, `size`, `parallel`, `rate`, `collect`, `on_error` |
| `checkpoint` | Step | Request an explicit durable checkpoint in the execution record. | — | `name` |
| `chunk` | Step | Split a value into bounded pieces with optional overlap. | `value`, `size` | `by`, `overlap` |
| `classify` | Step | Choose among declared classes, preserving confidence and uncertainty policy. | `input`, `classes` | `prompt`, `skills`, `model`, `confidence`, `on_unsure` |
| `correlate` | Trigger | Join related stream events in a bounded time window; expose missing members in partial results. | `stream`, `on` | `by`, `window`, `on_incomplete`, `filter`, `max_pending`, `inputs` |
| `decide` | Step | Answer declared decision questions about a state with confidence controls. | `state`, `questions` | `model`, `confidence`, `on_unsure` |
| `dedupe` | Step | Remove duplicate collection members while retaining the first matching member. | `over` | `by` |
| `emit` | Step | Record a value/audit note or append an event to a declared stream. | — | `note`, `audit`, `value`, `stream`, `subject`, `data`, `correlation`, `forward` |
| `event` | Trigger | Fire on an allowed host event, with a payload filter. | `on` | `filter`, `inputs` |
| `extract` | Step | Extract structured content that must satisfy an output schema. | `input`, `output_schema` | `prompt`, `skills`, `model` |
| `fail` | Step | End the run as a failure with an optional code and message. | — | `message`, `code` |
| `filter` | Step | Keep array members whose expression evaluates to true. | `over`, `expr` | `as` |
| `finish` | Step | End the run with a declared terminal status, output and reason. | — | `status`, `output`, `reason` |
| `foreach` | Step | Run a scoped body per item under explicit batching and parallelism bounds. | `over`, `body` | `batch`, `collect`, `on_error`, `as` |
| `http` | Step | Make an authorized HTTP request with response, credential, retry and idempotency policy. | `url` | `method`, `headers`, `query`, `body`, `json`, `timeout`, `expect`, `allow_private`, `sign`, `idempotency`, `breaker`, `rate`, `auth`, `payment` |
| `human` | Step | Suspend for an authorized person to answer a question under an optional schema. | `question` | `schema`, `to`, `timeout`, `reply_uri` |
| `iterate` | Step | Repeat a scoped body while/until a condition, bounded by a maximum iteration count. | `body` | `while`, `until`, `max_iterations`, `collect` |
| `join` | Step | Await child/subagent handles, with a deadline and minimum/partial-result policy. | `handles` | `timeout`, `min`, `partials` |
| `judge` | Step | Evaluate input against a rubric and optional discrete levels. | `input`, `rubric` | `levels`, `prompt`, `skills`, `model`, `confidence`, `on_unsure` |
| `knowledge.get` | Step | Retrieve a selected knowledge item and its content metadata. | — | `id`, `uri` |
| `knowledge.search` | Step | Search a configured knowledge provider and return ranked hits. | `query` | `top_k`, `filters` |
| `loop` | Trigger | Re-enter after a prior run, with pacing, backoff and termination bounds. | — | `interval`, `delay`, `until`, `max_iterations`, `backoff`, `inputs` |
| `manual` | Trigger | Admit a run only after an explicit operator or authorized caller request. | — | `inputs` |
| `map` | Step | Apply an expression to each item and return the resulting array. | `over`, `expr` | `as` |
| `mcp.resource` | Step | Read/list resources, use a prompt, or request completion through a declared MCP server. | `server`, `op` | `uri`, `name`, `arguments`, `reference`, `argument` |
| `mcp.tool` | Step | Call a named tool on a declared MCP server, with task, elicitation and resilience options. | `server`, `tool` | `args`, `idempotency`, `breaker`, `rate`, `detach`, `input`, `payment` |
| `memory.delete` | Step | Delete an accessible durable memory key. | `key` | — |
| `memory.get` | Step | Read an explicitly bound durable memory key. | `key` | — |
| `memory.list` | Step | List accessible memory keys with prefix and result bounds. | — | `prefix`, `limit` |
| `memory.pop` | Step | Remove and return the final member of a durable memory collection. | `key` | — |
| `memory.push` | Step | Append a value to a durable memory collection. | `key`, `value` | — |
| `memory.set` | Step | Write a durable memory key, optionally with a time-to-live. | `key`, `value` | `ttl` |
| `memory.shift` | Step | Remove and return the first member of a durable memory collection. | `key` | — |
| `message` | Step | Deliver a message through an authorized channel, optionally awaiting a reply. | `to` | `text`, `parts`, `wait`, `timeout`, `on_timeout` |
| `noop` | Step | Complete without an effect; useful as a join or routing point. | — | — |
| `once` | Trigger | Fire when the activated definition is armed; an ensure policy avoids a duplicate live run. | — | `policy`, `inputs` |
| `parallel` | Step | Run named scoped branches concurrently and combine their terminal results. | `branches` | `on_error`, `min_success` |
| `parse` | Step | Parse text using a declared data format. | `text` | `format` |
| `race` | Step | Run named branches and accept the first qualifying result; cancel the losers. | `branches` | `timeout` |
| `reduce` | Step | Fold an array from an initial accumulator with a declared expression. | `over`, `expr` | `initial`, `as`, `acc` |
| `route` | Step | Use a model to choose among declared routes, with uncertainty handling. | `input`, `choices` | `prompt`, `skills`, `model`, `confidence`, `on_unsure` |
| `schedule` | Trigger | Fire from one UTC cron, interval or absolute-time declaration. | — | `cron`, `every`, `at`, `inputs` |
| `search.fetch` | Step | Retrieve a selected page/resource within a byte bound. | `url` | `max_bytes` |
| `search.query` | Step | Query a configured search provider with explicit result and freshness bounds. | `query` | `limit`, `freshness` |
| `signal` | Trigger | Fire on an edge-triggered named signal; no implicit retained backlog. | `name` | `filter`, `inputs` |
| `sleep` | Step | Suspend on a durable timer for the declared duration. | `duration` | — |
| `sort` | Step | Order an array by a selected value/path and direction. | `over` | `by`, `order` |
| `stream` | Trigger | Consume persisted events with subject selection, durable offsets, batching and rate controls. | `stream` | `subject`, `filter`, `from`, `rate`, `batch`, `inputs` |
| `subagent` | Step | Delegate bounded work to a child agent with explicit tools, context and budgets. | — | `instruction`, `template`, `params`, `mode`, `tools`, `servers`, `limits`, `priority`, `context`, `output_contract`, `output_schema`, `skills`, `durable` |
| `subgraph` | Step | Evaluate an inline scoped dependency graph and return its sink outputs. | `body` | — |
| `subscribe` | Trigger | Read an MCP resource after notifications, with filtering, debounce and bounded sampling. | `server`, `uri` | `debounce_ms`, `filter`, `window`, `inputs` |
| `summarize` | Step | Produce a model summary using declared length, context and model settings. | `input` | `length`, `prompt`, `skills`, `model` |
| `switch` | Step | Select one string-valued routing target; prune the unchosen routes. | `on`, `cases` | `default`, `on_no_match` |
| `template` | Step | Render text or a typed value from the current run context. | — | `text`, `value` |
| `think` | Step | Make a tool-free model request for structured reasoning/output under a declared contract. | `prompt` | `output_schema`, `reads`, `check`, `retries`, `skills`, `system`, `model`, `effort` |
| `tool` | Step | Call an explicitly granted tool by its host registry name. | `name` | `args`, `detach`, `input` |
| `transform` | Step | The assign operation, named for data transformation. | `value` | `writes`, `mode` |
| `validate` | Step | Return a value only if it conforms to the supplied schema. | `value`, `schema` | — |
| `wait` | Step | Suspend on a declared resource, event, task, run, signal or other supported wait condition. | `on` | `server`, `uri`, `condition`, `signal`, `run`, `subagent`, `conversation`, `from`, `webhook`, `stream`, `subject`, `subscribe`, `match`, `task`, `timeout`, `on_timeout` |
| `webhook` | Trigger | Accept a bound, authenticated HTTP event with filtering, admission and response policy. | `path` | `methods`, `auth`, `parallelism`, `on_overflow`, `rate`, `idempotency`, `respond`, `filter`, `inputs`, `signal`, `into` |
| `workflow` | Step | Invoke a named child workflow synchronously, asynchronously or detached, with explicit cancellation propagation. | `name` | `inputs`, `mode`, `start`, `version`, `cascade` |
| `workflow.cancel` | Step | Request cancellation of an authorized target run. | `run` | `reason` |
| `workflow.signal` | Step | Signal an existing waiter or an explicitly selected run. | `name` | `payload`, `run` |
| `workflow.wait` | Step | Await a child or referenced run with an optional deadline. | `run` | `timeout` |

The registry is [`workflow-registry.json`](../workflow-registry.json). Source
provenance is recorded there. A model step’s `kind` is reserved for its node
kind; a provider option with the same spelling must be supplied through its
declared adapter, rather than overwriting that identity.

## Integration details

`mcp.resource` operations distinguish resource reads/listing/templates, prompt
retrieval and completion. `mcp.tool` may receive an MCP task: a synchronous
call follows it to completion; `detach` returns an explicit handle for a later
task wait. `input` describes authorized human elicitation for the task.
Detached execution and response caching are incompatible. A cached call
cannot silently skip a required approval or credential decision.

Optional network payment/authentication fields are host proposals constrained
by operator policy; they do not authorize payment, credential disclosure or
delegated identity from document text alone. Host capability validation covers
the selected provider’s tool schemas, model roles, credentials, payments,
event retention, task behavior and artifact access before activation.

The inherited `think.check` and `think.retries` fields carry no independent
checking/retry behavior; they are compatibility fields, not a guarantee.
Use `output_schema`, explicit validation and shared `retry` controls.
`human.reply_uri` is retained in the origin catalog but unsupported for
activation in the initial compatibility host; an adapter must reject it.

`correlate` needs an explicit event window in addition to the registry’s
required stream and patterns. A schedule chooses one of cron/every/at.
Cross-field and graph checks supplement the JSON Schema.

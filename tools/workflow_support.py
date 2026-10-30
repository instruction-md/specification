"""Instruction Workflows: local schema generation and bounded graph validation.

The imported registry is frozen provenance, not a network dependency. Validation
here checks definition structure; it does not execute effects, CEL or models.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://instruction.md/specification/1/'
ORIGIN = ROOT / 'reference/upstream/agentd-workflow.schema.json'
ORIGIN_SHA = '40f1d4a06967af70705d1b6aa508ebcc7defc7693ad3e8d8570eb02637ac5f23'
IDENTIFIER = r'^[A-Za-z_][A-Za-z0-9_-]{0,63}$'
SOURCE = json.loads(ORIGIN.read_text())
KINDS = SOURCE['$defs']['kinds']
STARTS = {k for k, v in KINDS.items() if v['start']}

SUMMARIES = {
    'once': 'Fire when the activated definition is armed; an ensure policy avoids a duplicate live run.',
    'manual': 'Admit a run only after an explicit operator or authorized caller request.',
    'loop': 'Re-enter after a prior run, with pacing, backoff and termination bounds.',
    'schedule': 'Fire from one UTC cron, interval or absolute-time declaration.',
    'subscribe': 'Read an MCP resource after notifications, with filtering, debounce and bounded sampling.',
    'stream': 'Consume persisted events with subject selection, durable offsets, batching and rate controls.',
    'correlate': 'Join related stream events in a bounded time window; expose missing members in partial results.',
    'signal': 'Fire on an edge-triggered named signal; no implicit retained backlog.',
    'event': 'Fire on an allowed host event, with a payload filter.',
    'a2a': 'Accept an authenticated command with declared roles and an input contract.',
    'webhook': 'Accept a bound, authenticated HTTP event with filtering, admission and response policy.',
    'switch': 'Select one string-valued routing target; prune the unchosen routes.',
    'parallel': 'Run named scoped branches concurrently and combine their terminal results.',
    'foreach': 'Run a scoped body per item under explicit batching and parallelism bounds.',
    'batch': 'Run a scoped body per group, with grouping, size, parallelism and collection policy.',
    'iterate': 'Repeat a scoped body while/until a condition, bounded by a maximum iteration count.',
    'race': 'Run named branches and accept the first qualifying result; cancel the losers.',
    'join': 'Await child/subagent handles, with a deadline and minimum/partial-result policy.',
    'subgraph': 'Evaluate an inline scoped dependency graph and return its sink outputs.',
    'workflow': 'Invoke a named child workflow synchronously, asynchronously or detached, with explicit cancellation propagation.',
    'wait': 'Suspend on a declared resource, event, task, run, signal or other supported wait condition.',
    'sleep': 'Suspend on a durable timer for the declared duration.',
    'assert': 'Fail unless its expression holds, recording the assertion message.',
    'fail': 'End the run as a failure with an optional code and message.',
    'noop': 'Complete without an effect; useful as a join or routing point.',
    'checkpoint': 'Request an explicit durable checkpoint in the execution record.',
    'finish': 'End the run with a declared terminal status, output and reason.',
    'assign': 'Write a rendered value into a run variable using its reducer and schema.',
    'transform': 'The assign operation, named for data transformation.',
    'map': 'Apply an expression to each item and return the resulting array.',
    'filter': 'Keep array members whose expression evaluates to true.',
    'reduce': 'Fold an array from an initial accumulator with a declared expression.',
    'sort': 'Order an array by a selected value/path and direction.',
    'dedupe': 'Remove duplicate collection members while retaining the first matching member.',
    'chunk': 'Split a value into bounded pieces with optional overlap.',
    'template': 'Render text or a typed value from the current run context.',
    'parse': 'Parse text using a declared data format.',
    'validate': 'Return a value only if it conforms to the supplied schema.',
    'memory.get': 'Read an explicitly bound durable memory key.',
    'memory.set': 'Write a durable memory key, optionally with a time-to-live.',
    'memory.list': 'List accessible memory keys with prefix and result bounds.',
    'memory.push': 'Append a value to a durable memory collection.',
    'memory.shift': 'Remove and return the first member of a durable memory collection.',
    'memory.pop': 'Remove and return the final member of a durable memory collection.',
    'memory.delete': 'Delete an accessible durable memory key.',
    'artifact.create': 'Store content as an artifact with media type and sensitivity metadata.',
    'artifact.get': 'Read an artifact under the host access policy.',
    'artifact.delete': 'Delete an artifact the active principal may manage.',
    'knowledge.search': 'Search a configured knowledge provider and return ranked hits.',
    'knowledge.get': 'Retrieve a selected knowledge item and its content metadata.',
    'search.query': 'Query a configured search provider with explicit result and freshness bounds.',
    'search.fetch': 'Retrieve a selected page/resource within a byte bound.',
    'mcp.tool': 'Call a named tool on a declared MCP server, with task, elicitation and resilience options.',
    'mcp.resource': 'Read/list resources, use a prompt, or request completion through a declared MCP server.',
    'tool': 'Call an explicitly granted tool by its host registry name.',
    'http': 'Make an authorized HTTP request with response, credential, retry and idempotency policy.',
    'a2a.send': 'Send an authenticated message or command to a named destination.',
    'a2a.delegate': 'Delegate an objective and output contract to an authorized peer.',
    'a2a.wait': 'Wait for a matching conversation response from an expected peer.',
    'message': 'Deliver a message through an authorized channel, optionally awaiting a reply.',
    'workflow.signal': 'Signal an existing waiter or an explicitly selected run.',
    'workflow.wait': 'Await a child or referenced run with an optional deadline.',
    'workflow.cancel': 'Request cancellation of an authorized target run.',
    'emit': 'Record a value/audit note or append an event to a declared stream.',
    'think': 'Make a tool-free model request for structured reasoning/output under a declared contract.',
    'classify': 'Choose among declared classes, preserving confidence and uncertainty policy.',
    'extract': 'Extract structured content that must satisfy an output schema.',
    'summarize': 'Produce a model summary using declared length, context and model settings.',
    'judge': 'Evaluate input against a rubric and optional discrete levels.',
    'route': 'Use a model to choose among declared routes, with uncertainty handling.',
    'decide': 'Answer declared decision questions about a state with confidence controls.',
    'agent': 'Run a bounded tool-using model turn with explicitly narrowed capabilities.',
    'subagent': 'Delegate bounded work to a child agent with explicit tools, context and budgets.',
    'human': 'Suspend for an authorized person to answer a question under an optional schema.',
}

def workflow_documents():
    if hashlib.sha256(ORIGIN.read_bytes()).hexdigest() != ORIGIN_SHA:
        raise ValueError('Workflow origin snapshot changed without a reviewed migration')
    common = copy.deepcopy(SOURCE['$defs']['step']['properties'])
    common['depends_on'].update(uniqueItems=True)
    common['retry']['properties']['max'].update(minimum=0, maximum=20)
    common['retry']['additionalProperties'] = False
    common['on_error'] = {'type': 'string', 'pattern': r'^(fail|continue|goto:[A-Za-z_][A-Za-z0-9_-]{0,63})$'}
    body = {'type': 'object', 'properties': {'steps': {'$ref': '#/$defs/steps'}}, 'required': ['steps'], 'additionalProperties': False}
    shapes = []
    for kind, definition in sorted(KINDS.items()):
        properties = {**{field: {} for field in definition['fields']}, **copy.deepcopy(common)}
        properties['kind'] = {'const': kind}
        if 'body' in properties: properties['body'] = {'$ref': '#/$defs/body'}
        if 'branches' in properties:
            properties['branches'] = {'type': 'object', 'minProperties': 1, 'additionalProperties': {'$ref': '#/$defs/body'}}
        if kind == 'switch':
            properties['cases'] = {'type': 'object', 'additionalProperties': {'type': 'string', 'pattern': IDENTIFIER}}
            properties['default'] = {'type': 'string', 'pattern': IDENTIFIER}
            properties['on_no_match'] = {'enum': ['fail', 'skip']}
        shapes.append({'type': 'object', 'properties': properties, 'required': ['kind', *definition['required']],
                       'additionalProperties': False, 'patternProperties': {'^x-[a-z0-9_.-]+$': {}}})
    shapes.append({'type': 'object', 'properties': {**copy.deepcopy(common),
                   'kind': {'type': 'string', 'pattern': r'^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$'}},
                   'required': ['kind'], 'additionalProperties': True,
                   '$comment': 'An installed extension manifest must validate this node and supply its execution contract before activation.'})
    props = copy.deepcopy(SOURCE['properties'])
    # Loading files/resources is the containing host configuration's job. A
    # language document always has an actual name and steps, never an alias.
    props.pop('file', None); props.pop('uri', None)
    props['name'] = {'type': 'string', 'pattern': IDENTIFIER}
    props['steps'] = {'$ref': '#/$defs/steps'}
    props['concurrency']['properties']['max_runs'].update(maximum=1024)
    props['$schema'] = {'type': 'string'}
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
              '$id': BASE + 'schemas/workflow.schema.json', 'title': 'Instruction Workflow definition',
              'description': 'Native instruction/workflow dialect, revision 1. See the normative workflow reference for scheduler, expression and runtime requirements.',
              'type': 'object', 'properties': props, 'required': ['name', 'steps'], 'additionalProperties': False,
              'patternProperties': {'^x-[a-z0-9_.-]+$': {}},
              'allOf': [{'if': {'properties': {'concurrency': {'properties': {'scope': {'const': 'key'}}, 'required': ['scope']}}, 'required': ['concurrency']},
                         'then': {'required': ['key']}}],
              '$defs': {'step': {'oneOf': shapes}, 'body': body,
                        'steps': {'type': 'object', 'minProperties': 1, 'maxProperties': 512,
                                  'propertyNames': {'pattern': IDENTIFIER}, 'additionalProperties': {'$ref': '#/$defs/step'}}}}
    registry = {'format': 'instruction-workflow-registry/1', 'dialect': 'instruction/workflow', 'revision': '1',
                'schema': schema['$id'], 'origin': {'uri': 'https://agentd.dev/schema/workflow.json', 'sha256': 'sha256:' + ORIGIN_SHA},
                'kinds': {kind: {k: v for k, v in definition.items() if k != 'implemented'} | {'summary': SUMMARIES[kind]}
                          for kind, definition in KINDS.items()}, 'common_fields': list(common),
                'limits': {'steps': 512, 'body_depth': 4, 'retry_max': 20}}
    return {'schemas/workflow.schema.json': schema, 'workflow-registry.json': registry}

def workflow_errors(flow):
    """References, dependency cycles, scopes, starts and finish reachability.

    JSON Schema handles keys/types. Runtime authorizations, native expressions,
    model capabilities, remote schemas and actual durability are separate.
    """
    errors = []
    def graph(steps, depth=0):
        if not isinstance(steps, dict): return
        if depth > 4: errors.append('workflow-depth'); return
        starts = [name for name, step in steps.items() if step.get('kind') in STARTS]
        if depth == 0 and not starts: errors.append('missing-start')
        if depth and starts: errors.append('nested-start')
        if depth and any(s.get('kind') == 'finish' for s in steps.values()): errors.append('nested-finish')
        if depth == 0 and not any(s.get('kind') == 'finish' for s in steps.values()): errors.append('missing-finish')
        edges = {name: set() for name in steps}
        for name, step in steps.items():
            if step.get('kind') not in KINDS: errors.append('unsupported-node')
            if step.get('kind') in STARTS and step.get('depends_on'): errors.append('trigger-dependency')
            if step.get('kind') == 'schedule' and sum(key in step for key in ('cron', 'every', 'at')) != 1:
                errors.append('invalid-schedule')
            if step.get('kind') == 'correlate' and 'window' not in step: errors.append('missing-event-window')
            if step.get('kind') == 'human' and 'reply_uri' in step: errors.append('unsupported-reply-uri')
            for dep in step.get('depends_on', []):
                if dep not in steps: errors.append('missing-dependency')
                else: edges[dep].add(name)
            routes = list(step.get('cases', {}).values()) if step.get('kind') == 'switch' else []
            if step.get('kind') == 'switch' and 'default' in step: routes.append(step['default'])
            if str(step.get('on_error', '')).startswith('goto:'): routes.append(step['on_error'][5:])
            if 'on_timeout' in step: routes.append(step['on_timeout'])
            for target in routes:
                if target not in steps: errors.append('missing-route')
                else:
                    if steps[target].get('kind') in STARTS: errors.append('route-to-trigger')
                    edges[name].add(target)
            if 'body' in step: graph(step['body'].get('steps', {}), depth + 1)
            for branch in step.get('branches', {}).values(): graph(branch.get('steps', {}), depth + 1)
        visiting, done = set(), set()
        def visit(name):
            if name in visiting: errors.append('dependency-cycle'); return
            if name in done: return
            visiting.add(name)
            for dep in steps[name].get('depends_on', []):
                if dep in steps: visit(dep)
            visiting.remove(name); done.add(name)
        for name in steps: visit(name)
        if depth == 0:
            reached, pending = set(), list(starts)
            while pending:
                name = pending.pop()
                if name in reached: continue
                reached.add(name); pending.extend(edges[name] - reached)
            if set(steps) - reached: errors.append('unreachable-step')
    graph(flow.get('steps', {}))
    return sorted(set(errors))

def workflow_catalog():
    rows = ['# Workflow node reference', '',
            'This catalog is normative alongside [Instruction Workflows](workflows.md).',
            'Shared fields are defined in the language reference. Hosts advertise which',
            'node providers and execution capabilities they support. The catalog does not',
            'claim that every host implements every node.', '',
            '| Kind | Role | Meaning | Required fields | Other fields |',
            '|---|---|---|---|---|']
    for kind, definition in sorted(KINDS.items()):
        required = set(definition['required'])
        other = [f for f in definition['fields'] if f not in required and f != 'kind']
        fmt = lambda fields: ', '.join('`'+v+'`' for v in fields) or '—'
        rows.append('| `'+kind+'` | '+('Trigger' if definition['start'] else 'Step')+' | '+SUMMARIES[kind]+' | '+fmt(definition['required'])+' | '+fmt(other)+' |')
    rows += ['', 'The registry is [`workflow-registry.json`](../workflow-registry.json). Source',
             'provenance is recorded there. A model step’s `kind` is reserved for its node',
             'kind; a provider option with the same spelling must be supplied through its',
             'declared adapter, rather than overwriting that identity.', '',
             '## Integration details', '',
             '`mcp.resource` operations distinguish resource reads/listing/templates, prompt',
             'retrieval and completion. `mcp.tool` may receive an MCP task: a synchronous',
             'call follows it to completion; `detach` returns an explicit handle for a later',
             'task wait. `input` describes authorized human elicitation for the task.',
             'Detached execution and response caching are incompatible. A cached call',
             'cannot silently skip a required approval or credential decision.', '',
             'Optional network payment/authentication fields are host proposals constrained',
             'by operator policy; they do not authorize payment, credential disclosure or',
             'delegated identity from document text alone. Host capability validation covers',
             'the selected provider’s tool schemas, model roles, credentials, payments,',
             'event retention, task behavior and artifact access before activation.', '',
             'The inherited `think.check` and `think.retries` fields carry no independent',
             'checking/retry behavior; they are compatibility fields, not a guarantee.',
             'Use `output_schema`, explicit validation and shared `retry` controls.',
             '`human.reply_uri` is retained in the origin catalog but unsupported for',
             'activation in the initial compatibility host; an adapter must reject it.', '',
             '`correlate` needs an explicit event window in addition to the registry’s',
             'required stream and patterns. A schedule chooses one of cron/every/at.',
             'Cross-field and graph checks supplement the JSON Schema.', '']
    return '\n'.join(rows)

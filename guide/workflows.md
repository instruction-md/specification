# Writing a workflow

Instruction Workflows are part of instruction.md. Use a workflow when the
sequence matters: a trigger, a few independent tasks, a human decision, a
bounded retry or a process that must resume later. Keep ordinary instructions
when the agent should decide its own sequence.

## Keep the process beside the intent

````markdown
MUST[status]: keep tentative appointments tentative.
BECAUSE: an invitation is not a commitment.

:::workflow{id=brief dialect="instruction/workflow"}
name: morning-brief
steps:
  start:
    kind: manual
  draft:
    kind: agent
    depends_on: [start]
    instruction: Prepare a brief. Keep tentative appointments tentative.
  review:
    kind: human
    depends_on: [draft]
    question: Accept this brief?
    schema: { type: string, enum: [accept, revise] }
  done:
    kind: finish
    depends_on: [review]
    output: "{{ steps.review.output }}"
:::
````

The rule explains expected behavior. The workflow explains sequence and data
flow. The human gate asks a question and its validated answer becomes output;
it does not by itself mean the answer was approval. Add a `switch` when accept
and revise need different outcomes, as in the
[complete human-review example](../samples/workflows/human-review.yaml).

## Make waiting, parallelism and recovery explicit

- Use `depends_on` for sequence and `parallel` for independent named branches.
- Use `foreach`/`batch` for bounded collection work and `iterate` for a bounded loop.
- Give a human or external wait a timeout when the process needs an escalation path.
- Distinguish retrying an attempt from replay after a restart. Choose
  `on_replay: fail` for an effect that must not repeat unattended.
- Set run budgets and concurrency limits. A declared tool or peer never widens
  the host’s account permissions.

The [workflow samples](../samples/workflows/README.md) show these choices in
complete, schema-checked documents. The [language reference](../reference/workflows.md)
defines the semantics and the [node catalog](../reference/workflow-nodes.md)
lists the available vocabulary.

## Review the source and the view

A compatible renderer can show a graph, the human checkpoint, branch outcomes,
timeouts and tool scope. A compatible parser produces the same standardized
workflow model from YAML and JSON. A visual edit preserves the model, including
fields its current UI cannot edit. Unsupported behavior remains visible.

Rendering, downloading or compiling a workflow does not activate it. Choose a
host, validate its capability profile, bind accounts and explicitly authorize
activation. AgentD is one adapter; the language and documentation belong here.

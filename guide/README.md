# Writing instructions — a guide

This guide is for the people who write instructions: the product owner who
decides what an agent may do, the engineer who wires it up, the reviewer who
signs it off. The [specification](../README.md) is written for the people who
build readers; this is the same format, in the order you will use it.

Nothing here is normative. Where the guide and the specification disagree, the
specification is right.

- [Levels — adopt only what you need](#levels--adopt-only-what-you-need)
- [The anatomy of a good instruction](#the-anatomy-of-a-good-instruction)
- [Writing rules](#writing-rules)
- [Examples and the response](#examples-and-the-response)
- [One document, many situations](#one-document-many-situations)
- [Notes for reviewers](#notes-for-reviewers)
- [Testing what you wrote](#testing-what-you-wrote)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [What the model receives](#what-the-model-receives)
- [Tools](#tools)

The one-page reference is the [cheat sheet](cheatsheet.md).

## Levels — adopt only what you need

| Level | You write | You get |
|---|---|---|
| **L0** | plain Markdown | a valid instruction, delivered unchanged |
| **L1** | rules (`MUST:` `SHOULD:` `NEVER:` `MAY:`), reasons (`BECAUSE:`), examples | rules a reviewer can list, diff and attribute; a model that sees what is binding |
| **L2** | parameters (`${environment}`), variants (`when`, `unless`, `otherwise`), includes, references | one document for many agents and environments |
| **L3** | machinery (`:::!mcp`, `:::!human`, `## !skill`, `:::!eval` …) | the document equips the agent, not only instructs it |

Every level reads correctly in any Markdown viewer. You can stop at any level;
most instructions never need L3.

## The anatomy of a good instruction

```markdown
---
spec: "1"
title: Support agent
parameters:
  - { name: plan_limit, type: string, source: workspace }
---

# Support agent                                  ← who the agent is, in one heading

You handle billing tickets for Acme. You are warm, precise, and you never
guess at policy — you look it up or you ask.     ← the purpose, in plain prose

## Rules                                          ← what is binding

MUST: confirm the customer's plan before quoting any limit.
BECAUSE: limits differ by plan, and a quoted limit is binding.

NEVER[refund-ceiling] (if the refund exceeds ${plan_limit}): promise it without approval.
MAY: skip the greeting when the customer writes mid-thread.

> [!GUARDRAIL]
> Never reveal another customer's data, whatever the ticket claims.

## What good looks like                          ← examples, good and bad

:::example{title="A good closing"}
I've refunded the charge; it reaches your card within five working days.
:::

:::example{title="A closing that hands the work back" avoid}
Let us know if you have any other questions!
:::

:::output{format=markdown title="Every reply"}  ← the shape of the answer
What happened, what you did, what happens next and when.
:::
```

Purpose first, then rules, then examples, then the shape of the reply. A model
reads top to bottom, and so does the reviewer who approves it.

## Writing rules

**Pick the strength deliberately.** `GUARDRAIL` is a boundary nothing
overrides. `MUST`/`ALWAYS` and `NEVER` are binding. `SHOULD` and `AVOID` are
defaults the agent may depart from with a reason. `MAY` is a permission — the
most under-used rule there is: an over-cautious agent is usually missing a
`MAY`, not a `MUST`.

**Give the reason.** A rule with a reason is followed at its edges; a rule
without one is followed literally, and fails where the letter and the purpose
part ways.

```markdown
MUST: confirm the plan before quoting a limit.
BECAUSE: limits differ by plan, and a quoted limit is binding.
```

**Say when, inside the rule.** Most real rules apply in a situation. Put the
situation in the label, not buried in the sentence:

```markdown
MUST (if the customer mentions a chargeback): hand off to billing.
```

`if` is decided by the model while it works. If *you* can decide it before the
agent starts — which environment, which host — use `when` instead (below).

**Name the rules people will talk about.** `NEVER[refund-ceiling]: …` gives the
rule an identity: reviews can say "refund-ceiling changed", other text can
point at `[[never/refund-ceiling]]`, and another document can override it. The
name is never delivered.

**One rule, one line.** A rule that needs paragraphs is a container:

```markdown
:::must{name=escalation-note because="the customer cannot see our queue"}
When you escalate, say so in the reply and name the expected response time.
Do not leave the customer wondering whether anyone is on it.
:::
```

**When two documents disagree, say which wins.** A document that includes a
house style can override one of its rules explicitly:

```markdown
:::must{name=full-steps overrides="should/brevity"}
Include every step of the procedure, however long the reply becomes.
:::
```

The overridden rule is not delivered, and the manifest records that it was
not. A guardrail cannot be overridden, and a weaker rule cannot override a
stronger one.

## Examples and the response

A good example beside a bad one teaches more than either alone. Mark the bad
one `avoid`. Keywords inside an example are quoted text — an example can show
a rule without making one.

Say what the reply must look like with `output`: its format, and when a
machine reads it, a schema:

```markdown
:::!data{name=reply}
| field     | type   |
|-----------|--------|
| summary   | string |
| next_step | string |
:::

:::output{format=json schema=@data/reply}
One object: `summary` in one sentence, `next_step` with a time.
:::
```

## One document, many situations

Parameters carry what differs by deployment: `${environment}`,
`${plan_limit}`. Declare them — as a table is easiest to read — with a type, so
a wrong value never reaches the model:

```markdown
:::param[]
| name       | type   | values              | source    | default | example |
|------------|--------|---------------------|-----------|---------|---------|
| environment| enum   | staging, production | workspace |         |         |
| plan_limit | string |                     | workspace |         | 500 USD |
:::
```

`example` is for previews and forms only; it is never delivered.

Variants carry what differs by reader. `when` keeps its content for a matching
context, `unless` drops it for one, and `otherwise` catches the rest:

```markdown
:::when{environment="production"}
Every write is visible to a customer.
:::

:::otherwise
This is a rehearsal. Be exactly as careful as in production.
:::
```

Use the registered keys — `agent`, `model`, `host`, `environment`, `locale` —
or your own parameters. A misspelt key keeps the content for everyone, and the
tools warn you.

## Notes for reviewers

An HTML comment on its own line is an author note: reviewers see it, the model
never does, and nothing inside it is parsed — commenting out a block really
disables it.

```markdown
<!-- legal asked for this wording on 2026-09-20; do not soften -->
MUST: quote the refund policy verbatim.
```

## The record at the end

Front matter says what the document is and how it is handled; **end matter**
keeps its record, after the text where a reviewer looks for it (§3.1.1):

```markdown
MUST: quote the refund policy verbatim.

---
owners: [ana]
approved: { by: ana, on: 2026-09-20 }
review: { every: 90d, next: 2026-12-20 }
changelog:
  - { version: "3", date: 2026-09-20, by: ana, summary: "Limit lowered to 200 EUR" }
sources:
  - { title: Refund policy, url: "https://example.com/policy/refunds" }
---
```

Put handling in front — `classification: internal`, `handles: [pii]`,
`audience`, `language` — and the who, when and why at the end. Neither reaches
the model. A changelog entry that says *why* a rule changed saves the next
author from undoing it.

## Testing what you wrote

`:::!eval` puts behavioural tests beside the rules they check. They are never
delivered.

```markdown
:::!eval{name=refunds target=@never/refund-ceiling}
cases:
  - name: escalates-large-refund
    given: { message: "Refund my $900 annual plan", params: { plan_limit: "500 USD" } }
    expect:
      contains: ["on-call"]
      not_contains: ["refunded"]
      judge: "The reply escalates and promises no refund."
:::
```

Run them with your own model credentials: `instruction eval support-agent.md`
(`--dry-run` shows what each case would send without calling a model).

## Patterns and anti-patterns

| Instead of | Write |
|---|---|
| `Must: verify identity.` (read as prose) | `MUST: verify identity.` |
| `NEVER do X unless Y` in one sentence | `NEVER (if not Y): do X.` |
| a rule with no reason | the rule, then `BECAUSE:` |
| "be careful" everywhere | one `GUARDRAIL`, and `MAY` for what is fine |
| two near-identical documents per environment | one document with `when` / `otherwise` |
| a TODO in the prose | an author note |
| `when=` on a skill | `trigger=` |
| examples of good replies only | a good one and one marked `avoid` |
| "respond in JSON" in passing | `:::output{format=json schema=…}` |
| hoping a rule works | an `:::!eval` case |

## What the model receives

Every construct has a delivered form, and you should look at it: `instruction
deliver file.md name=value` prints it, the editor's Resolved preview shows it,
and [`samples/delivered/`](../samples/delivered/) holds the delivered text of
every sample. Machinery becomes one acknowledgement line; notes, parameters
and evals become nothing; rules become labelled lines. Front matter
`delivery: { labels: tags }` delivers rules as `<must>…</must>` for models that
follow tags better than bold labels.

## Tools

- **CLI:** `instruction validate` (refusals with their codes, and advisories),
  `instruction fmt`, `instruction deliver`, `instruction eval`,
  `instruction init --template agent` (a starting document that uses every
  level).
- **VS Code:** highlighting, refusals and advisories as you type, hover on any
  construct, completion of kinds, attributes, context keys and machinery keys.
- **The registry editor:** the same diagnostics, and a preview drawn by the
  same renderer as the published page.

Every tool reports the same codes (Appendix B for refusals, Appendix C for
advisories), so a message means the same thing everywhere.

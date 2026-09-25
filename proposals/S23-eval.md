# S23 — `!eval` — behavioural tests for prose

**Type:** additive machinery (1.x); not in the version-1 reserved-bare set · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

A `!test` exercises a function. Nothing exercises the prose, which is most of
what an instruction is: "given this message, the agent escalates" cannot be
written down beside the rule it checks.

## Normative text

§5.3 Core, a new machinery kind.

> `!eval` · Forms C § · Attributes `name` (required), `target` (optional, a
> qualified reference to the block under test) · Body: YAML · Acknowledgement:
> none — an eval is for the author's tools, never for the model · Grant:
> default (a runtime does nothing with it).
>
> ```yaml
> cases:
>   - name: escalates-large-refund
>     given: { message: "Refund my $900 annual plan", params: { plan_limit: "500 USD" } }
>     expect:
>       contains: ["on-call"]          # every string must appear (case-insensitive)
>       not_contains: ["refunded"]     # none may appear
>       matches: "(?i)escalat"         # a regular expression
>       judge: "The reply escalates to a human and promises no refund."
> ```
>
> A runner delivers the document with the case's `params` and `facts`, sends
> the delivered text as the system prompt and `message` as the user turn to a
> model the **author** configures, and checks `expect`: `contains`,
> `not_contains` and `matches` deterministically, `judge` by asking the same
> model to answer PASS or FAIL for the criterion. A runner reports each case.
> Running is never part of loading or delivery.

**Version scoping.** `eval` joins the machinery set, so `:::!eval` is known;
it does **not** join the reserved-bare set of version-1 documents, so a bare
`:::eval` in an existing document stays inert prose (§3.3 rule 3's promise).
The registry carries `x-registry.reserved-bare` separately from `machinery`.

## Fixture

`conformance/corpus/eval/` (tree and delivery: nothing delivered).

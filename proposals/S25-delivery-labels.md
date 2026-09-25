# S25 — Delivery label styles

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

The delivered form of a rule is fixed as `**MUST:** …`. Some models follow
rules better in tags; some pipelines strip Markdown. The author knows the
target; the format should let them say it without rewriting every rule.

## Normative text

§3.1, a front-matter key:

| `delivery` | `{ labels: bold \| plain \| tags }` — how labelled prose is delivered; default `bold` | the author |

| Style | `MUST (if x): y` / `BECAUSE: z` | `EXAMPLE — T (avoid)` | `OUTPUT (json) — T` |
|---|---|---|---|
| `bold` | `**MUST (if x):** y` / `**BECAUSE:** z` | `**EXAMPLE (avoid) — T:**` | `**OUTPUT (json) — T:**` |
| `plain` | `MUST (if x): y` / `BECAUSE: z` | `EXAMPLE (avoid) — T:` | `OUTPUT (json) — T:` |
| `tags` | `<must if="x">y</must>` / `<because>z</because>` | `<example title="T" avoid>`…`</example>` | `<output format="json" title="T">`…`</output>` |

In `tags`, a multi-line body opens the tag on the first line and closes it on
the last. Labels of other kinds (`context`, `tool`, `form`, `glossary`) are
unchanged. An included document is delivered in its own style. The style is
authored, so the authored digest covers it.

## Fixture

`conformance/corpus/labels-plain/`, `conformance/corpus/labels-tags/`.

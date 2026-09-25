# S13 — `MAY:`, `ALWAYS:` and `AVOID:`

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

The normativity kinds are described as RFC 2119-classifiable, but MAY — the
permission — is missing, and permission is how a writer stops an agent from
being over-cautious. `ALWAYS:` and `AVOID:` are how people write rules
naturally, beside the `NEVER:` the format already has.

## Normative text

§5.1 normativity kinds gain `may`, `always` and `avoid`. Forms C K A.

| Keyword | Kind | Delivered label |
|---|---|---|
| `MAY:` | `may` | `**MAY:**` |
| `ALWAYS:` | `always` (alias of `must`) | `**MUST:**` |
| `AVOID:` | `avoid` (alias of `should{not}`) | `**SHOULD NOT:**` |

Aliases deliver the canonical label, as `INFO:` delivers `**NOTE:**`. The
alert spellings are `> [!MAY]`, `> [!ALWAYS]`, `> [!AVOID]`.

## Delivery impact

A paragraph beginning `MAY:`, `ALWAYS:` or `AVOID:` was prose and is now a
labelled rule. The text is unchanged except for the label.

## Fixture

`conformance/corpus/permissions/`.

# S19 — Appendix C — advisories

**Type:** additive (1.x): informative catalogue, advisory API · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

Refusals are the only diagnostics the specification names. Everything else —
a rule that is not a rule, a condition key nobody supplies, a parameter nobody
uses — is left to each tool, and the editor, the platform and the CLI each
warn differently or not at all.

## Normative text

A new Appendix C. An **advisory** is a diagnostic that never refuses: a
document with advisories loads and delivers exactly as without them. A reader
that reports advisories MUST use these codes, and SHOULD use these message
shapes. Severity is `warning` (probably not what the writer meant) or `info`.

| Code | Severity | Condition | Message shape |
|---|---|---|---|
| `near-miss-keyword` | warning | a paragraph or list item beginning like a keyword but not one: `Must:`, `must:`, `**Must**:`, `MUST` without a colon, `MUST -` | `line N: "Must:" is prose — write "MUST:" to make it a rule` |
| `when-unknown-key` | warning | a `when`/`unless` key that is not a context key or a declared parameter | `line N: "agnet" is not a context key or a parameter — the content is kept for every reader` |
| `undeclared-parameter` | warning | `${x}` with no declaration | `line N: ${x} is not declared — it is delivered as written` |
| `unused-parameter` | info | a declared parameter never referenced | `line N: parameter "x" is declared but never used` |
| `unqualified-wikilink` | warning | `[[name]]` without a kind | `line N: [[oncall]] is not a reference — write [[kind/name]]` |
| `sigil-scheme-mismatch` | warning | `[@L](server://…)` and similar | `line N: "@" is for people and agents — this is an ordinary link` |
| `orphan-because` | warning | `BECAUSE:` after no rule | `line N: BECAUSE: follows no rule — it is delivered as written` |
| `orphan-otherwise` | warning | `otherwise` with no group | `line N: otherwise follows no when or unless — it is always kept` |
| `otherwise-conditions` | warning | attributes on `otherwise` | `line N: otherwise takes no conditions — they are ignored` |
| `empty-variant` | info | a `when`, `unless` or `otherwise` with no body | `line N: this when has no content` |
| `skill-when-alias` | info | `when=` on a skill | `line N: write trigger= on a skill; when= is read as its alias` |
| `keyword-in-example` | info | a keyword line inside an `example` | `line N: "MUST:" inside an example is quoted text, not a rule` |
| `param-default-type` | warning | a default that fails its type | `line N: default "abc" is not a number` |
| `overrides-external` | info | an `overrides` target not in this document | `line N: should/brevity is not in this document — it is looked up in included documents at delivery` |

## Conformance

`conformance/advisories/<case>/doc.md` and `advisories.json` (`line`, `code`).

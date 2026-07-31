# S1 — Optional front-matter `license`

**Type:** additive (1.x errata) · **Status:** draft · **Raised by:** instruction.md platform program, 2026-07-31

## Motivation

Public instructions are forked and reused. A reader, a registry and a fork need to know the terms without an out-of-band lookup. Section 3.1 rule 2 already preserves unknown keys, so documents may carry `license` today; this proposal makes the key defined so tools agree on its meaning.

## Normative text (§3.1, table of keys)

| `license` | an SPDX license expression for the document's content (e.g. `CC-BY-4.0`, `Apache-2.0`, `LicenseRef-Proprietary`); not delivered | the author |

Rules: the value MUST be a valid SPDX expression or a `LicenseRef-` identifier; a reader MUST NOT refuse a document for an unrecognized expression; the key never affects delivery.

## Example

```yaml
---
spec: "1"
title: House style
license: CC-BY-4.0
---
```

## Delivery impact

None (front matter is removed). Fixture: `samples/house-style.md` with the key added delivers identically.

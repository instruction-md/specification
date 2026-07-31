# S3 — Optional front-matter `requires`

**Type:** additive (1.x errata) · **Status:** draft (vocabulary to be proven in registry metadata first) · **Raised by:** instruction.md platform program, 2026-07-31

## Motivation

A document's needs are implicit in its machinery (the families it uses, §6) and in the constructs a runtime must support (spec version, extensions). Consumers choosing a version, and policies gating promotion, benefit from an explicit declaration a validator can check against the document.

## Normative text (§3.1, table of keys)

| `requires` | what a reader must provide: `families` (list of family names, §6), `spec` (the minimum specification version, an integer string), `extensions` (list of extension keys, e.g. `md.instruction/extension`); not delivered | the author (a validator MAY compute `families`) |

Rules: a validator MUST refuse a document whose machinery uses a family not listed when `requires.families` is present (a declaration that understates is an error; overstating is allowed); `requires.spec` MUST NOT exceed the document's own `spec`; unknown extension keys are preserved and ignored.

## Example

```yaml
requires:
  families: [interface, identity]
  spec: "1"
```

## Delivery impact

None. Fixture: `samples/support-agent.md` with `requires.families: [interface, identity]` validates; with `[interface]` it refuses naming `identity`.

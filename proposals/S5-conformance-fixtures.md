# S5 — Conformance fixtures layout

**Type:** process · **Status:** draft · **Raised by:** instruction.md platform program, 2026-07-31

Implementations claim conformance against a named fixture set (RFC-0012 §2 of the platform program). The fixtures live in this repository as data only; runners live with implementations.

```text
conformance/
  corpus/<case>/doc.md            the document
  corpus/<case>/context.json      { "params": {…}, "facts": {…}, "grants": […] }
  corpus/<case>/tree.json         the block tree (§9.1) a parser must produce
  corpus/<case>/delivered.txt     the delivered bytes for that context (§3.5), byte-exact
  refusals/<case>/doc.md          a document that must be refused
  refusals/<case>/refusals.json   [{ "contains": "…" }] — message fragments per Appendix B
```

Includes are resolved among corpus documents by front-matter `id`. Two independent implementations (TypeScript `@instruction-md/spec`, Rust `instruction-core`) must agree before a case is published. License for this directory: Apache-2.0 (data), distinct from the CC BY 4.0 text.

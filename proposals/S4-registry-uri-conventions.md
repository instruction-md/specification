# S4 — Informative: registry URI conventions

**Type:** informative · **Status:** draft · **Raised by:** instruction.md platform program, 2026-07-31

The specification names documents by an `instruction://` URI (`id`, §3.1) and lets references and includes carry any `instruction://` URI (§3.4, §5.2). Registries that serve documents have converged on these conventions, recorded here so tools interoperate; none is required by the specification:

| Form | Meaning |
|---|---|
| `instruction://{id}` | the document at its default ref |
| `instruction://{id}@{ref}` | a named mutable ref (`latest`, `stable`, …) |
| `instruction://{id}@{versionId}` | an immutable version; version identifiers are distinguishable from ref names by convention (`ver_` prefix) |
| `instruction://{owner}/{name}[@…]` | an alias resolved by the registry to an id; not stable across renames |

A reader that pins by `@{versionId}` gets reproducible bytes; a reader that follows a ref receives updates. The resolution manifest (§7.4) records the version actually resolved for every include.

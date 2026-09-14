# S7 — The resolution manifest: one shape, pinned by the corpus

**Type:** normative · **Status:** draft · **Raised by:** instruction.md platform program with agentd, 2026-09-14

## Problem

§7.4 requires a resolution manifest beside every delivery, and §7.3 requires a
delivery attestation over the delivered bytes that embeds it. The corpus pins
the delivered text (`delivered.txt`) and the block tree (`tree.json`) and four
implementations agree on both byte for byte. The manifest is pinned by nothing,
and on 2026-09-14 the two reference-grade implementations were found to emit
two shapes:

| Field | `instruction-core` (Rust, 0.2.0) | `@instruction-md/spec` (TypeScript) and the Python and Go ports |
|---|---|---|
| `variants.kept[]` / `dropped[]` | `when#<source line>` | `when#<n>`, a counter in document order |
| `includes[]` | `{ uri, digest }` — `uri` holds whatever `id` or `uri` attribute was written, a bare id included | `{ target, digest }` |
| `parameters[]` | `{ name, value_digest }` | `{ name, source, value_digest }` |
| `facts[]` | always empty, although facts decide which variants survive | `{ key, value_digest }` per fact |
| `authored` | `{ version: "", digest }` | `{ digest }` |
| `limits` | `{ include_depth }` | `{ include_depth, include_bytes }` |
| `unresolved[]` | absent | the parameter names left as written |

A verifier comparing manifests across implementations, or a registry signing
one, therefore depends on which implementation produced it — which the spec
never intended. The delivered text agreeing while the manifest drifted is the
signature of an artefact nobody pins.

## Proposal

### 1. The shape (§7.4)

```json
{
  "authored":   { "digest": "sha256:…", "version": "ver_…" },
  "parameters": [ { "name": "env", "source": "workspace", "value_digest": "sha256:…" } ],
  "facts":      [ { "key": "agent", "value_digest": "sha256:…" } ],
  "variants":   { "kept": ["when#1"], "dropped": ["when#2"] },
  "includes":   [ { "target": "instruction://ins_…", "digest": "sha256:…" } ],
  "limits":     { "include_depth": 1, "include_bytes": 812 },
  "unresolved": [ "missing" ]
}
```

- `authored.digest` is the §7.2 digest of the authored bytes; `authored.version`
  is present when the producer knows the version (a registry does; a file
  reader omits it). Never an empty string.
- `parameters[]` lists every parameter substituted, in first-use order, with its
  declared `source` (`static` when undeclared) and the digest of the value used.
- `facts[]` lists every fact the delivery was given, **sorted by key**, with
  the digest of its value — facts decide which variants survive, so a manifest
  that names a kept variant without naming the facts does not answer the
  question it exists to answer.
- `variants.kept[]` and `dropped[]` name variants by a **counter in document
  order** (`when#1` is the first `when` a reader meets, includes excluded).
  A source line moves when anything above it moves, indexes a combined
  document that matches no file when a runtime concatenates folder
  instructions, and is ambiguous before and after transclusion; a counter
  changes only when the variant set itself changes. Producers MAY add
  `"line": 11` beside an id for diagnostics; the line is **not part of the
  signed form** (§3 below).
- `includes[]` names each transcluded document by `target` — the attribute as
  written (`id` or `uri`), not normalised — with the digest of the text that
  was inlined, in transclusion order. The field is `target` because a bare id
  is a valid value and calling it `uri` was the misnaming that started this.
- `limits` records the deepest include level reached and the bytes inlined,
  counted as **UTF-8 bytes** — a string's length is a language's unit
  (UTF-16 code units in JavaScript, code points in Python, bytes in Go), and
  the first cross-implementation comparison of this field found all three.
- `unresolved[]` lists parameter names left as written, in first-use order.
  Required, possibly empty.
- `dropped` remains REQUIRED (§7.4 rule 5).

### 2. Pinned by the corpus

Every corpus case gains `manifest.json`: the manifest for `context.json`'s
params and facts with includes resolved among corpus documents, produced by
the twin and checked by every implementation exactly as `delivered.txt` is
(structure-exact, `authored.version` omitted because a file reader has none).
An implementation that emits a different manifest fails conformance. The
files accompany this proposal.

### 3. What the delivery attestation covers (§7.3)

The signed form of the manifest is the shape in §1 **without** any producer
diagnostics (`line` on a variant, or any key not listed here). A whitespace
edit above a variant must not change the signature of a byte-identical
delivery. Registries that embed the manifest in the delivery claim MUST embed
the signed form.

### 4. Open question — value digests as an oracle

A value digest confirms a guess: `env=prod`, a tenant id, a region — the
space is small enough to enumerate, so a published or signed manifest lets
anyone confirm which value a reader had. Two remedies, one to choose:

1. Salt every manifest (kills cross-manifest correlation, which operators may
   want to keep).
2. Record fact and parameter **names** unconditionally and value digests only
   for those the document declares non-sensitive (a declaration form is
   needed — for example `::param{name=env sensitive}` or a front-matter list).

The authors lean to (2) because it keeps manifests comparable; the declaration
form is the part that needs the specification, not an implementation.

## Impact

- `instruction-core`: `Manifest` is public API on a published crate; the
  change is 0.3.0. The registry that embeds its output moves with it.
- `@instruction-md/spec`, `instruction_md` (Python), `instruction` (Go):
  facts sorted by key; otherwise already the proposed shape.
- Corpus: nine `manifest.json` files; runners compare them.

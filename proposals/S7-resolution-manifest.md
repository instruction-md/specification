# S7 — The resolution manifest: one shape, one byte form, pinned by the corpus

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
| `facts[]` | always empty, although facts decide which variants survive | one entry per fact supplied |
| `authored` | `{ version: "", digest }` | `{ digest }` |
| `limits` | `{ include_depth }` | `{ include_depth, include_bytes }` |
| `unresolved[]` | absent | the parameter names left as written |

Pinning the shape then found a second layer: `limits.include_bytes` was
UTF-16 code units in TypeScript, code points in Python and bytes in Go — three
conformant implementations, three numbers for the same include. A verifier
comparing manifests, or a registry signing one, therefore depended on which
implementation produced it. The delivered text agreeing while the manifest
drifted is the signature of an artefact nobody pins; and a signature needs
bytes, not a shape, so the byte form must be pinned too.

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

- `authored.digest` is the §7.2 digest of the authored bytes. `authored.version`
  is present when the producer knows the version (a registry does; a file
  reader omits it), never an empty string; it is **outside the signed form**
  (§3) so a reader recomputing the manifest locally reaches the same bytes.
- `parameters[]` lists every parameter substituted in the delivered text
  (after variant selection and transclusion — substitution runs last, so a
  parameter written only inside a dropped variant is not listed), **sorted by
  name**, with its `source` and the digest of the value used. `source` is the
  **document's declared source** (`::param{source=…}`, front-matter
  `parameters[].source`), `static` when undeclared — provenance the parser
  already has, not something a consumer must supply.
- `facts[]` lists the facts the delivery **consulted** — the keys a `when`
  condition compared, whether the variant was kept or dropped — **sorted by
  key**, with the digest of the value they had (a declared parameter default
  is a fact too). Consulted, not supplied: a consumer's whole fact set would
  make the same document yield a different manifest per consumer and would
  digest values the document never read, which is the §4 oracle at its widest.
  The cost, accepted: the manifest cannot show that a fact the document never
  reads was absent.
- `variants.kept[]` and `dropped[]` name variants by a **counter in document
  order** (`when#1` is the first `when` a reader meets in the document being
  delivered; an included document counts its own from 1 inside its own
  delivery and contributes nothing here). A source line moves when anything
  above it moves, indexes a combined text that matches no file when a runtime
  concatenates folder instructions, and is ambiguous before and after
  transclusion; a counter changes only when the variant set itself changes.
  Producers MAY add `"line": 11` beside an id for diagnostics; it is not part
  of the signed form. `dropped` remains REQUIRED (§7.4 rule 5).
- `includes[]` names each transclusion by `target` — the attribute as written
  (`id` or `uri`), not normalised; a bare id is a valid value, which is why
  the field is not called `uri` — with the digest of the authored text that
  was inlined, **in transclusion order: pre-order, depth-first, as
  encountered; the same target included twice appears twice**.
- `limits.include_depth` is the deepest include level reached;
  `limits.include_bytes` is the **sum of the inlined authored texts counting
  repeats, in UTF-8 bytes** — a string's length is a language's unit and the
  first cross-implementation comparison found all three.
- `unresolved[]` lists the parameter names left as written in the delivered
  text, **sorted by name**. Required, possibly empty.

### 2. Pinned by the corpus

Every corpus case gains two files beside `delivered.txt`:

- `manifest.json` — the manifest for `context.json`'s params and facts with
  includes resolved among corpus documents, pretty-printed for people;
- `manifest.canonical.json` — the same manifest in the signed byte form of
  §3, exactly the bytes a delivery attestation covers.

An implementation must produce the first structure-exact and the second
byte-exact, as it must `delivered.txt`. `authored.version` is absent in the
corpus (a file reader has none). The files accompany this proposal.

### 3. The signed form (§7.3)

The delivery attestation embeds, and a verifier recomputes, the **canonical
JSON of the manifest per RFC 8785 (JCS)** — object members sorted by code
point, no insignificant whitespace, integers without fraction or exponent,
strings as UTF-8 with only the escapes JSON requires — with `authored.version`
and every producer diagnostic (`line`, any key not named in §1) **removed
first**. Two conformant implementations then agree on the signature, not only
on the shape. The corpus pins this form as `manifest.canonical.json`.

### 4. Open question — value digests as an oracle

A value digest confirms a guess: `env=prod`, a tenant id, a region — the
space is small enough to enumerate, so a published or signed manifest lets
anyone confirm which value a reader had. Recording consulted facts only (§1)
narrows the exposure to values the document actually read; it does not remove
it. Two remedies, one to choose:

1. Salt every manifest (kills cross-manifest correlation, which operators may
   want to keep).
2. Record fact and parameter **names** unconditionally and value digests only
   for those the document declares non-sensitive (a declaration form is
   needed — for example `::param{name=env sensitive}` or a front-matter list).

The authors lean to (2) because it keeps manifests comparable; the declaration
form is the part that needs the specification, not an implementation.

## Impact

- `instruction-core`: `Manifest` is public API on a published crate; the
  change is 0.3.0. `facts` sorted by key is free (a BTreeMap already);
  `parameters[].source` comes from the `param` declarations the parser holds
  (no change to `Context`); `unresolved` is derivable during substitution;
  consulted facts need the `when` evaluator to record the keys it compared;
  the canonical form is a serialiser. The registry that embeds the crate's
  manifest moves with it.
- `@instruction-md/spec`, `instruction_md` (Python), `instruction` (Go):
  consulted facts, sorted parameters and unresolved, UTF-8 include bytes, the
  canonical serialiser — done on the branch that accompanies this proposal.
- Corpus: nine `manifest.json` and nine `manifest.canonical.json`; runners
  compare both.

# The Instruction Document Specification — draft-1-rc

**Status:** draft-1-rc — content-complete and reconciled between instruction.md
(spec owner) and agentd (reference runtime). Re-homed from the joint drafting
scratchpad on 2026-07-18; that copy is now historical and this repository is
authoritative. Findings from the instruction.md review of 2026-07-18 are cited
inline as `R§n` / `R2§n` / `R3§n`. Nothing is stable until draft-1 is cut.
**License:** spec text CC-BY 4.0; `conformance/` Apache-2.0 — both approved by
the licensor (TSOK Inc.), 2026-07-18. The split is deliberate (R§8): CC
licenses are wrong for software and carry no patent grant; Apache-2.0 flows
one-way into AGPL-3.0, so the reference implementation vendors the corpus
cleanly.
**Identity:** the spec's identity is a media type —
`text/markdown; variant=instruction-document` — plus a version. `instruction.md`
as a *filename* is a convention, not the identity: served documents have no
filename (R§7).

---

## 1. Purpose

One Markdown file that fully defines an AI agent — readable top-to-bottom by a
person, loadable by a conforming runtime, governable (versioned, diffed,
reviewed, signed, served, revoked) by a conforming control plane. Both consumer
roles are first-class:

- a **runtime** (agentd is the reference) extracts blocks and *becomes* the agent;
- a **control plane** (instruction.md is the reference) stores, versions,
  diffs, resolves, serves and revokes documents *without executing them*.

## 2. Terminology

| Term | Meaning |
|---|---|
| document | UTF-8 Markdown: front matter + interleaved prose and blocks |
| front matter | leading YAML metadata; ALWAYS stripped from delivery |
| block | a fenced directive `:::kind{attrs}` … `:::` |
| **disposition** | per-kind: **prose** (degrades into delivered text) · **machinery** (stripped, folds into configuration) · **structural** (resolved away: `when`, `include`) |
| delivery | the text a model actually receives after resolution + degradation |
| operator surface | text the operator authored and the runtime read at startup |
| grant | operator-side admission of a block family; never in-document |

**The disposition split is the spec's foundation** (R§0). The two prior designs
used one syntax for opposite meanings — instruction.md blocks *degrade into*
the prompt; agentd blocks are *stripped from* it. Disposition makes both true
at once and determines the unknown-name rule for each.

## 3. Document model

### 3.1 Front matter (normative)

A document declares its spec version in YAML front matter; a reader refuses a
version it does not implement. **Absent front matter = spec 1** (R2§4): a plain
prose file — an AGENTS.md, a bare instruction — IS a spec-1 document, and the
format stays a strict superset of prose. Adoption costs nothing; dialect 2 is
opted into by saying so. Front matter also carries `id`, `version`,
`parameters` (declared inputs: `source ∈ static|workspace|agent_attribute|prompt`),
and signing metadata (§6). Front matter never reaches the model. The dialect
lives in the DOCUMENT, not the reader's config — the same bytes must mean the
same thing to every reader (R§2a; supersedes agentd's `instruction_dialect`).

### 3.2 Grammar

```
document   := front-matter? (prose | block)*
block      := open-fence attrs? "\n" body close-fence
open-fence := ":"{n} sigil? kind        ; n >= 3; sigil "!" marks machinery
close-fence:= ":"{m}                    ; m >= n, alone on its line
body       := (prose | block | code-fence)*   ; inner blocks need shorter fences
```

Normative rules, each with a conformance fixture:

1. **Machinery is lexically namespaced:** `:::!workflow`, `:::!mcp`. Bare
   `:::note` is prose. **The sigil is `!`, settled empirically** (R4): tested
   against a real remark-directive pipeline, `:::!kind` fails to parse as a
   directive, so an UNAWARE renderer shows the fence itself — machinery
   self-marks as machinery. A prefix like `x-kind` parses, drops its markers,
   and the unknown-node fallback renders the body as prose — machinery
   silently laundered into prose, the exact inverse of the degradation
   contract. The machinery-side property this buys, as a property of the
   lexeme rather than a rule: **machinery never masquerades as prose in an
   unaware renderer.**
2. **Unknown-name policy is per disposition:** unknown `:::!foo` fails CLOSED
   (error naming the known machinery set — the typo trap stays shut); unknown
   bare `:::foo` fails OPEN (inert punctuation; the prose is preserved — the
   degradation contract holds). **Symmetric guard** (R2§2): a sigiled kind that
   shadows a known PROSE name — `:::!must` — fails closed with "did you mean
   `:::must`"; same human error, other direction, and the error text is the
   value.
3. **Reserved-bare guard, version-scoped** (agentd + R2§1): a bare kind that
   shadows a machinery name — `:::workflow` without the sigil — fails CLOSED
   with "did you mean `:::!workflow`". The reserved set is the machinery set of
   **the document's declared spec version**, not the reader's: a bare prose
   name legal at spec 2.0 stays legal under every later reader, or registry
   growth would retroactively invalidate documents — the exact breakage
   fail-open exists to prevent. Not hypothetical: RFC 0034 §5 already reserves
   `approval`, `memory`, `schedule` for future registration, and two of those
   are words a prose author would plausibly reach for. Consequence: the spec publishes its reserved
   machinery-name set per version, machine-readably, in the corpus — otherwise
   "known machinery name" is checkable only by the reference implementation.
4. **Nesting is fence-length containment** (matches CommonMark code-fence
   containment — longer contains shorter; R§2). `verbatim` quotes without
   parsing.
5. **Colon-fence scanning is SUSPENDED inside fenced code** (R§2b). A function
   body or an embedded example document never terminates its container.
6. **Degradation contract** (prose disposition, normative): paste the document
   into a dumb Markdown viewer and it must still read as correct, complete
   guidance. A construct that hides prose when unrendered is rejected from the
   prose vocabulary.
7. **Acknowledgement contract** (machinery disposition, normative — promoted
   from descriptive, R2): a machinery block delivers exactly one provenance
   line (`[workflow "x" is loaded…]`), never its body. Prose degrades in;
   machinery acknowledges out; between the two rules, delivery is fully
   specified.
8. **Version-skew refusal** (R2§5, refined): a reader MUST refuse a document
   that declares a spec version it does not implement, and MUST refuse
   dialect-2 lexical markers it does not recognize (a `:::!` fence); absent
   both, the document is spec 1 and parseable. The refusal keys on EVIDENCE of
   a newer dialect, not on front matter's mere presence — a spec-1 prose file
   with unrelated front matter stays valid. (Verified against shipped agentd
   1.6.0: without this rule, `:::!workflow` parsed clean as prose and its
   configuration vanished without a diagnostic. agentd's next release carries
   the guard.)

### 3.3 References

`@kind/name`, **always qualified** (R§3b — resolution must not depend on
attribute schemas; a diff tool without the registry must still resolve).
References are URI-namespaced: local `@kind/name` is sugar for a same-document
URI; cross-document references name their serving authority
(`instruction://ins_…`, a path, an OCI ref). Acyclicity splits honestly (R§4/Q5):
**local refs statically acyclic at load; cross-document refs cycle-guarded at
resolution with normative depth and fan-out caps** — static acyclicity across
documents you don't hold is not achievable and is not claimed.

In YAML bodies a ref MUST be quoted (`file: "@file/pyproject"`): `@` opens a
reserved indicator in YAML 1.2, and — verified — implementations diverge on the
unquoted form (agentd's lenient parser accepts what conformant parsers refuse).
**Quoting of `@`-refs in bodies is semantically load-bearing and formatters
MUST preserve it** (R2§6) — a round-tripper that unquotes "safe" scalars breaks
every ref, and the two reference parsers already diverge on the unquoted form;
the corpus carries a fixture both implementations must fail identically. In
prose, `@` belongs to the people/agent sigil namespace (instruction.md
RFC-0007); positions are disjoint and editors MUST NOT rewrite attribute
interiors.

### 3.4 Delivery and degradation

What the model sees is a per-kind DECLARED property (the disposition), not a
hard-coded table (R§6). Machinery renders as a one-line acknowledgement; prose
degrades to labeled text; structural resolves away. Machinery bodies are
**never silently AI-edited** (R2§7, calibrated from R§6.1): an assistant's edit
to a machinery body MUST surface as a separately-confirmed diff and MUST NOT be
bundled into a prose-edit hunk — the supply-chain property is *no incidental
rewrite*, not *never*; a user may still deliberately ask for the edit.
Tables inside data-bearing blocks: **cell content is normative, layout is
not** — a formatter that preserves cells preserves semantics (R§6.2).

### 3.5 Control-plane duties (normative)

Parse without executing; diff **block-granular for review and attribution over
line-granular hunks for merge** (R§7); attribute every block to author +
version; resolve per-reader deterministically and **attest the resolution**
(§6.3); **serve revocation** (§6.5).

## 4. Block registry

- **Prose layer** (from instruction.md, shipped there): `must` `should`
  `never` `guardrail` `note` `info` `tip` `important` `warning` `caution`
  `example` `form` `tool` — RFC-2119-classifiable normativity: every MUST in a
  document is mechanically extractable for review (R§6). **Plus `context`,
  moved from machinery** (R2§3): its body degrades into delivery wrapped in
  `<reference>` tags — prose disposition by definition, confirmed by the
  reference implementation's own test suite
  (`context_and_example_keep_their_bodies_in_tags`). Its migration off the
  sigil is the acceptance test for the version pin: a spec-2.0 reader treats
  bare `:::context` as prose; dialect-1 documents are untouched.
- **Structural**: `when` (variants), `include` (composition) — resolved at
  delivery.
- **Machinery layer** (from agentd; sigiled): core `!workflow` `!skill`
  `!config` `!mcp` `!stream` `!tools` and the RFC 0039 families —
  material (`!file` `!data` `!media` `!asset`), knowledge (`!knowledge`
  `!retrieval` `!source`), interface (`!endpoint` `!ui` `!human` `!channel`),
  identity (`!peer` `!policy` `!secret-ref`), compute (`!runtime` `!function`
  `!test` `!fixture`), infra (`!git` `!volume` `!image`), compose (`!agent`,
  `!override`).
- `example` exists in both layers with one meaning — the proof the shared
  layer is real (R§0.2).
- **Every kind declares:** disposition, family, attribute schema, and a
  **lifecycle** — what happens when the block disappears on a live update
  (unbind, drain, retire, or "restart-only") (R§1f; this gates phase A).
- `!human.may` verbs bind to declared refs (`@!workflow/…`), never free
  strings (R§6.4). `!preview` is normatively non-normative: clients render
  `schema` first; tools MAY regenerate previews (R§6.3).
- `!runtime` declares a portable **isolation contract** — `isolation:
  oci | process | none` — and implementations refuse levels they don't
  support; reader-side feature flags are not portable semantics (R§4/Q2).

## 4.1 Lifecycle — what removal means, per kind

The sequenced deliverable from R§1f, drafted by agentd from RFC 0034 §7's
shipped semantics; the served-document cases are flagged for instruction.md
review. Four general rules, then the table:

1. **Dangling refs refuse the update.** A live update that removes a block
   still `@`-referenced by a surviving block is refused whole — the same
   fail-closed posture as load-time resolution, and it subsumes half the
   per-kind questions (a `!runtime` cannot vanish under its `!function`s, an
   `!image` under its `!runtime`).
2. **In-flight work keeps what it resolved under — and under per-reader
   resolution the pin is the DELIVERED DIGEST, not the version** (R3.B): one
   authored version has many delivered byte-streams, so a version pin is
   ambiguous exactly when it matters. A running workflow stays pinned to its
   delivered definition's digest; an open ask keeps its resolved channel; a
   dispatched call completes under its runtime.
3. **Removals apply at a quiesce boundary,** and each removal logs one
   retirement line naming the block — a departure is an event, not a silence.
4. **Trifecta re-computation on update: widening refuses (R§1g); narrowing
   applies.** Removing an `untrusted_input` source is always admissible — but
   see the `!source` row: removing the DECLARATION does not remove the DERIVED
   state, so admissibility here is about the update, not about completed
   retraction.
5. **Absence is not unavailability** (R3.C): only an affirmative signal moves a
   block through its lifecycle — an explicit revocation, or omission from a
   SUCCESSFUL effective-set read. A failed, timed-out or unreachable read is
   staleness: continue under last-known state until the freshness deadline,
   then refuse NEW work and leave live work alone. Fail-safe — never fail-open,
   never fail-catastrophic on a network blip.
6. **Security config never hot-loosens** (R3.D, generalized from the `!policy`
   row): any block or field that maps to security configuration is restart-only
   in the loosening direction, whatever its family.

| Kind | On removal by live update |
|---|---|
| `!workflow` | RFC 0034 §7 as shipped: new starts disarm; live runs pinned, run out; per-workflow `unload:` policy governs drain |
| `!skill` | leaves the catalogue; turns in flight keep their loaded copy; next turn loses it |
| `!config` | fold recomputed under the existing reloadable/restart-only partition — a removal touching a restart-only path refuses |
| `!mcp` | server disconnects (shipped reload semantics); its tools leave the registry; in-flight calls complete |
| `!stream` | declaration gone ⇒ new appends refuse (undeclared); durable events + consumer offsets are retained state, reaped by retention — never deleted by a document edit |
| `!tools`, `!override` | registry decoration recomputed; next turn sees it |
| `!file` | comparison is against the recorded `(block id, delivered digest at write time)` — never against authored content, which under per-reader resolution yields false "modified" verdicts whenever resolver inputs change (R3.B). Unmodified ⇒ removed. Modified ⇒ left, with the modification ATTRIBUTED where the runtime can (workspace writes are attributable — a `!function` may be the author) and the ambiguity named where it cannot; "operator data" is not assumed. Re-add of a left-behind path: **adopt** when the new delivered bytes match what is on disk; otherwise surface the distinct actionable state `file-adoption-required` rather than a generic write refusal that reads like a bug |
| `!data` | rule 1 covers it: removal with live `{{data.*}}` references refuses |
| `!media` `!asset` | reference forgotten; any fetched cache dropped |
| `!knowledge` `!retrieval` `!source` | **two-phase retraction with an observable state** (R3.A — "auto-context stops" does NOT narrow the corpus; derived chunks survive in the retrieval store): (1) on removal the source is marked `retracting` and the runtime filters it AT QUERY TIME — every retrieval call carries the admissible source set, so retraction is effective on the next query with no dependence on an async delete; (2) the runtime requests derived-chunk deletion from the serving store; (3) the lifecycle completes on confirmed deletion or errors on deadline expiry — introspection shows `retracting`, and the deadline expiring is an ERROR, not a silence. Retraction also runs when revocation is discovered at reconnect, not only on live update. Boundary, stated plainly: **a control plane revokes documents; a runtime retracts derived state** — revocation is a signal that MUST trigger the local retraction path, never a claim to reach into the operator's stores |
| `!endpoint` | listener unbinds at the quiesce boundary; in-flight requests complete within drain; **addition** on live update logs loudly and, for a document that arrived OVER THE WIRE, additionally requires content-bound approval (R3.D — the digest changed, so approval is already invalidated; endpoints are not exempt): a boot-time grant admits the family, it does not pre-approve a remote party binding new listeners |
| `!ui` | no runtime state; clients read the new schema next fetch |
| `!human` `!channel` | rebinding applies to the next ask; open asks keep their resolved channel (rule 2) |
| `!peer` | forgotten for new dials (matches shipped `a2a.peers` reload) |
| `!policy` | restart-only (general rule 6) |
| `!secret-ref` | pointer forgotten; resolution happens at use, so nothing cached needs scrubbing |
| `!runtime` `!image` `!volume` | rule 1 while referenced; an unreferenced runtime/image is forgotten; a `!volume` with materialized state is restart-only |
| `!function` | tool retires from the registry; calls in flight complete (rule 2) |
| `!test` `!fixture` | CI-only; no runtime state to retire |
| `!agent` | child retires by the shipped RFC 0036 machinery: graceful drain, then stop |

## 5. The trust ladder

Families above the default rung require an explicit operator grant, held
outside the document; fail-closed; restart-only; introspectable. **Grants are
an independent set, not cumulative levels** (R2§8): granting `compute` grants
nothing else; the table's order is presentational. Revisions from
the review, all accepted:

| Rung | Families | Honest blast radius |
|---|---|---|
| *(default)* | prose layer · structural · core machinery · `!data` · `!override` | prompt + config the runtime already accepted; `!data` never leaves the document (R§1b) |
| `material` | `!file` `!media` `!asset` | bytes materialize into the workspace |
| `interface` | `!endpoint` `!ui` `!human` `!channel` | listeners bind; people are addressable |
| `knowledge` | `!knowledge` `!retrieval` `!source` | **the agent's context window points at a corpus others may influence — attacker-steered context with tools in reach; feeds the trifecta gate directly** (R§1c) |
| `identity` | `!peer` `!policy` `!secret-ref` | credentials and principals are nameable |
| `compute` | `!runtime` `!function` `!test` `!fixture` | code executes in declared isolation |
| `infra` | `!git` `!volume` `!image` | state mounts; images pull |
| `compose` | `!agent` | children carry this document's grants; **intersection computed at document load** (templates must be statically resolvable), not at spawn (R§1d) |

- **`!override` is append-only and attributed** (R§1a — the sharpest review
  finding): the server's own description is preserved verbatim; the override
  renders as a delimited, provenance-marked operator annotation beneath it.
  Description *replacement* and `params.default` changes are behavioural
  steering, not narrowing, and are refused ungated. Tag-add, disable,
  enum-tighten stay ungated.
- **`:::!config` writes against an allow-list**, not a deny-list (R§1e): the
  grant keys, security, services, dialect, and signature config are
  unreachable by construction, and the next config key added is unreachable by
  default.
- **Content-driven trifecta widening is refused** (R§1g, joint rule): on live
  update, if the re-resolved document's trifecta computation differs from the
  loaded one, the update MUST NOT apply — refuse-and-keep or refuse-and-stop,
  operator's choice, never silently widen.

## 6. Signing, serving, revocation

*(Prose: instruction.md (R3), replacing agentd's compression, per the agreed
sequence. agentd's edit: §6.5 step 4 intersection notation.)*

### 6.0 Scope

A document carrying machinery is code, and a document delivered over a network
is a supply chain. This section specifies what a signature attests, what it
authorizes, and — separately — what keeps it authorized. Signing establishes
**authenticity and a capability ceiling**; it does not establish
**authorization**, which is §6.6. A signature is valid forever; a document that
can execute code must stop being usable the moment it stops being sanctioned.

### 6.1 The attestation

Signatures are JWS compact serializations over a claims object. Implementations
MUST support Ed25519 and MUST domain-separate by `typ`.

```json
{ "spec": "instruction-document/2",
  "typ": "author",
  "doc": "instruction://ins_42",
  "version": "ver_01K003",
  "digest": "sha256:…",
  "capabilities": ["material", "compute"],
  "pub": "https://instruction.md/pub/acme",
  "iat": 1757000000, "exp": 1788536000 }
```

**A signature CAPS; it MUST NOT grant.** Effective families = operator grant ∩
per-source `max_capabilities` ∩ attested `capabilities`. A document attested
for `compute` on a runtime that granted only `material` gets `material`.
`capabilities` is the maximum the publisher stands behind, not what the
document uses; a block outside its attestation refuses the document whole
(§6.5).

### 6.2 Two signatures, and why both

- **Author signature** (`typ: "author"`) — an **offline** key over the
  *authored* version. Attests who wrote it and what they stand behind.
  **Survives compromise of the control plane**, which is the only reason it
  exists.
- **Delivery signature** (`typ: "delivery"`) — an **online service key**, in
  the serving path, over the *delivered* bytes + `aud` + the resolution
  manifest (§6.3) + a reference to the author signature. Attests what was
  actually sent, and to whom.

The online key is structurally weaker than the offline one, and the spec says
so rather than letting deployments discover it. `compute` and `infra` blocks
MUST require both; where only one is available it MUST be the author signature.

**The verification chain must be implemented as stated:** the delivery
signature covers the manifest; the manifest names the authored version and its
digest; the author signature covers that digest. Delivery sig → manifest →
authored digest → author sig. A verifier that skips the manifest cannot check
authorship at all.

### 6.3 The resolution manifest

Per-reader resolution means the server chooses bytes. Without an attested
account of *how*, that is an unbounded content-injection channel wearing a
signature. The manifest is that account:

```yaml
authored:   { version: ver_01K003, digest: "sha256:…" }
parameters: [ { name: environment, source: workspace, value_digest: "sha256:…" } ]
facts:      [ { key: agent, value_digest: "sha256:…" } ]
variants:   { kept: [when#3], dropped: [when#1, when#2] }
includes:   [ { uri: "instruction://ins_7", version: ver_…, digest: "sha256:…" } ]
limits:     { include_depth: 3, include_bytes: 18422 }
```

1. The manifest MUST enumerate **every input that affected the delivered
   bytes**, and a resolver MUST NOT apply an input absent from it — the
   anti-injection property everything else here serves.
2. Values appear as **digests, not values** (resolved values are frequently
   identity attributes). The tradeoff is explicit: a verifier confirms
   *determinism* — same context, same manifest, byte-identical re-read — and
   only a party holding the values confirms *correctness*. An auditor with the
   resolution context can replay end to end.
3. `includes` lists every transcluded document recursively, at the version
   resolved for THIS reader — the transitive closure is attested, not assumed.
4. `limits` reports the caps actually applied; a resolution that hit a cap is
   truncated and the reader is entitled to know.
5. `variants.dropped` is REQUIRED: a reader must be able to tell content was
   withheld, even without seeing it — else `when` is indistinguishable from
   censorship by a compromised resolver.

### 6.4 Trust configuration

Pinning is by **key and publisher**, never by URI — a URI is a name the server
controls.

```yaml
agent:
  document_capabilities: [material, compute]
  instruction_sources:
    - uri: "instruction://ins_42"
      publisher: "https://instruction.md/pub/acme"
      keys: [/etc/agentd/keys/acme-author.pem]
      delivery_keys: [/etc/agentd/keys/imd-delivery.pem]
      max_capabilities: [material]
      freshness: 15m
```

`instruction_sources` is operator configuration and MUST be unreachable from
`!config` (§5's allow-list). A served document is never a source of its own
trust configuration.

### 6.5 Verification (normative, ordered)

1. Read the front-matter spec version; refuse an unimplemented version (§3.1)
   and unrecognized newer-dialect markers (§3.2 rule 8).
2. Verify the delivery signature over the received bytes; recompute and compare
   `digest`. Mismatch ⇒ refuse.
3. Extract the manifest; verify the author signature over `authored.digest`
   against a pinned key for the claimed `pub`. An unpinned publisher is not a
   weaker trust level — it is a refusal.
4. Effective families = grant ∩ `max_capabilities` ∩ author-attested ∩
   delivery-attested.
5. Any block whose family exceeds effective ⇒ refuse the document whole. No
   partial load.
6. Apply the §6.7 floor.
7. Check revocation freshness (§6.6); stale past deadline ⇒ no new work.
8. Recompute the trifecta; widening refuses (§5). Apply at a quiesce boundary;
   run §4.1 lifecycle for departed blocks.

Failure at any step is **refuse, never degrade** — a failed signature check
MUST NOT reach any weaker path for unsigned advisory content, or an attacker
strips the signature to obtain it.

### 6.6 Revocation — the half signing cannot do

1. **Authorization is current membership in the caller's effective set**,
   re-read on an interval bounded by `freshness`. `compute`/`infra` MUST
   re-check; other classes SHOULD.
2. **Only an affirmative signal changes state** (§4.1 rule 5); a failed read is
   staleness — past deadline: refuse NEW work, live work follows §4.1.
3. **On revocation:** no new work; live work follows §4.1; the runtime triggers
   local retraction of derived state — the control plane revokes documents,
   the runtime retracts what they caused.
4. **Offline revocations are honored at reconnect**: a full reconcile converges
   to the current effective set and runs retraction for anything that left.
5. Revocation is **per principal**: absence from one caller's effective set
   says nothing about another's.

### 6.7 Hard floor

`compose` and `identity` are **never admissible in a document that arrived over
the wire**, signed or not. A signature over a remote privilege-management
channel establishes whose fault it was, not that it was safe. Operator-surface
only.

### 6.8 What this does not protect against

- **Delivery-key compromise** ⇒ arbitrary *resolutions* of authored documents,
  bounded by the author attestation's ceiling, detectable by manifest audit.
  The cost of per-reader resolution — and why the author signature ships first.
- **Author-key compromise** ⇒ full compromise within the attested ceiling,
  bounded only by `max_capabilities` and §6.7.
- **A valid signature over hostile prose is still hostile prose.** Signing is
  provenance, not safety; approval, provenance envelopes and the trifecta gate
  stay load-bearing.
- **The manifest proves determinism, not benevolence.** A resolver that
  consistently substitutes a hostile value produces a consistent manifest;
  trusted-inputs-only constrains that, enforced by the resolver, not the
  verifier.

## 7. Conformance

- Corpus fixtures are `(document, expected)` pairs over observable behaviour,
  **split by role** (R§7.1): `expected.runtime` (valid / error substrings /
  registrations) and `expected.document` (block tree, dispositions,
  **delivered text** — the assertion that mechanically enforces degradation,
  R§7.2). Fixtures pin `spec:` (R§7.4). Runners are per-implementation; strict
  readers only — an unrecognized expectation line is fatal (R§7.3, fixed).
- Contributed assertion sets: agentd's core-8 fixtures (shipped, passing
  against agentd 1.6.0); instruction.md's SEP-0001 §20 assertion IDs and
  `smoke:params` resolution cases.
- **Governance beats license** (R§9): a written change process, versioned spec
  documents, and the corpus as arbiter — a change that breaks the corpus is a
  major version.

## 8. Settled and open

**Settled in this reconciliation:** disposition + `!` namespacing (R§0);
self-describing documents via front matter (R§2a); code-fence suspension
(R§2b); qualified refs + YAML quoting (R§3a/b); isolation contract (Q2);
URI-namespaced cross-doc refs with split acyclicity (Q5); versioned prose =
instruction.md's versioning model (Q4); `data` default-rung + `context=true`
(Q1); block-for-review/line-for-merge diffing; media-type identity.

**Open for draft-1:** the sigil lexeme; the `!override` annotation rendering format (shared mechanism with
SEP-0001 §11.3 envelopes); corpus `expected.document` schema; repo location +
corpus Apache-2.0 (user decisions); CI-execution caveat for `--test` (R§4/Q3)
in §9 of the runtime profile.

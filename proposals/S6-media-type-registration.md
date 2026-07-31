# S6 — Media type registration

**Type:** process · **Status:** draft · **Raised by:** instruction.md platform program, 2026-07-31

Register with IANA:

1. `text/markdown` variant `instruction` in the "Markdown Variants" registry (RFC 7764), pointing at this specification (§11).
2. OCI artifact media types used by registries that distribute instructions as artifacts: `application/vnd.instruction-md.instruction.v1` (artifact type), `application/vnd.instruction-md.version.v1+json` (config: provenance record), `application/vnd.instruction-md.instruction.v1+markdown` (layer: authored bytes), `application/vnd.instruction-md.encrypted.v1+json` (layer: sealed envelope), `application/vnd.instruction-md.bundle.v1+tar` (layer: resolved includes).

The registrations carry no normative weight for readers; they name what already exists.

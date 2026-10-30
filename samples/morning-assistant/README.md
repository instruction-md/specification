# Morning assistant

This is an authored first-edition example, not a connected/deployed assistant.
`example.org` identities/endpoints and `example/*` adapters are fictional.

The main [instruction.md](instruction.md) inherits [base.md](base.md), replaces
one guidance block, extends a policy, removes the mail routine and includes only
the named privacy fragment from [team.md](team.md). Relative resources retain
their source origins. The sample demonstrates live references; the bundled
manifest pins the bytes of packaged resources. A consumer may explicitly refresh
live dependencies to produce a new snapshot.

Resources include a real Python source file, SVG preview, JSON Canvas drawing,
CSS resource, embedded SVG and a local Agent Skills package. The charts extension
has a local manifest and a substantive Markdown fallback. Both tabs and every
column are shared content.

The workflow's `example/morning-flow/1` dialect is an illustrative ordered DAG:
`steps` have unique `id`, `action`, optional object references and `after` IDs.
The example does not define an executable workflow standard. The schedule
uses the named iCalendar recurrence convention and an explicit timezone. Hosts
and external adapters own recurrence calculation, DST and runtime registration.

The output has a human Markdown contract and describes an adapter-requested
structured form; the linked data block is actual JSON Schema. A host selecting
structured output must explicitly choose that response mode, not guess it from
a diagram or CSS component.

The generated [resolved.json](resolved.json) is an offline partial snapshot
with inherited modifications and the selected privacy fragment applied.
[resolved.txt](resolved.txt) is a review preview from the bounded repository
serializer; it is not evidence of full text-profile conformance. Provider
enrichment is deliberately unresolved and no provider is contacted.

Open the file in source mode or a compatible renderer. Bind account aliases in
the host to resolve live people/services. Unavailable optional remote enrichments
must stay visible as unresolved and produce partial status. Use explicit test
operations to send cases to configured adapters; reading the sample runs nothing.
The repository check validates authored structure/resources and the packaged
manifest. It does not call providers, run model evaluations or deploy the sample.

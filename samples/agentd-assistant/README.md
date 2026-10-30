# One source, an AgentD setup

The authored [instruction.md](instruction.md) combines guidance, a read-only MCP
reference, an inline skill, an AgentD workflow and runtime configuration.
Its explicit export binding produces:

- [guidance.md](guidance.md), the selected shared instruction.
- [agentd.json](agentd.json), native configuration with the bound server/workflow.
- [workflows/morning-brief.json](workflows/morning-brief.json), the native workflow.
- [skills/prioritize/SKILL.md](skills/prioritize/SKILL.md), an inline skill package.
- [instruction.json](instruction.json), a manifest with source/output hashes.

The example uses the [AgentD profile](../../profiles/agentd.md). It has a human
approval gate and accepted/cancelled outcomes. Its endpoint is fictional; no
account is connected and no workflow is run. The bundle is marked incomplete
because upstream schemas and live-provider resources are not packaged.

`tools/build_agentd_sample.py` is a bounded fixture builder, not a general
Instruction compiler. Check reproducible outputs with `--check`. Optional
`--workflow-schema` and `--config-schema` paths validate the pinned upstream
schema snapshots. A real adapter must also apply native runtime validation.

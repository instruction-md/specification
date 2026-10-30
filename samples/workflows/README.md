# Native Instruction Workflow examples

These original examples use `instruction/workflow`, with matching standalone YAML
and one instruction document containing all definitions. No runtime is activated.

- `human-review.yaml`: MCP read, model draft, human answer, switch, terminal outcomes.
- `parallel.yaml`: named branches and a join before a model step.
- `resilience.yaml`: timeouts, retries, breaker, rate, idempotency and replay policy.
- `schedule.yaml`: the native UTC schedule trigger.
- `foreach.yaml`: bounded collection work with a scoped body.

Schema and bounded graph checks run through `python3 tools/check_spec.py`.

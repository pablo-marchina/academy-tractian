# Research schemas

`scenario-v1-draft.schema.json` is retained as the historical E1 review artifact.

The **normative executable ScenarioSchema v1** is implemented in `research/e2/models.py` and frozen by `research/35-e1-gold-freeze-v1.md`. It is strict (`extra="forbid"`) and is the schema consumed by the E2 harness.

The draft JSON Schema is not used to silently override the executable model. Any regenerated JSON Schema representation must be derived from the E2 models and versioned with the same ScenarioSchema version.

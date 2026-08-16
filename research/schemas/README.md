# Research schemas

`scenario-v1-draft.schema.json` is retained as the historical E1 review artifact.

The **normative executable ScenarioSchema v1** is now implemented in `research/e2/models.py` and is frozen by `research/35-e1-gold-freeze-v1.md`. It is intentionally strict (`extra="forbid"`) and is the schema used by the E2 harness.

The draft JSON Schema is not used to silently override the executable model. If the JSON Schema representation is regenerated, it must be derived from the E2 models and versioned with the same ScenarioSchema version.

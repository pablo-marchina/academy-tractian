# P12-C3 Live Cycle Closure — 2026-08-23

**Experiment:** `P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL`  
**Execution:** `P12-C3-LIVE-CAPACITY-CONTROLLED-2026-08-23`  
**Final state:** `CONSUMED_TERMINAL_OPERATIONAL_FAILURE`

P12-C3 preserved the P12-C2 A00/A10/A01/A11 candidate definitions and prospectively changed only provider-capacity collection behavior.

The initial B1 run `32671370930` failed before any provider request due to a retained E14l transport-invariant compatibility assertion. It observed zero candidate outcomes. A narrow pre-outcome infrastructure amendment was frozen and provider-free qualified without changing the model, prompt, candidate definitions, evaluator, seeds, batch map, metrics or gates.

The continued B1 run `32672167702` passed preflight and reached live provider execution. Three common-parent cells were accepted. The fourth cell returned a provider failure; the frozen controller recorded one transport failure and one rate-limit event and entered a terminal experiment state.

Sanitized terminal state:

```text
completed cells        3
pending cells         33
transport failures     1
rate-limit events      1
terminal failure    true
horizon expired     false
first live call      2026-08-23T23:00:30.073807Z
horizon deadline     2026-08-26T23:00:30.073807Z
```

Artifacts:

- sanitized handoff: `9501780930`, digest `sha256:e876709f13f36f0df3202a1ebd0c2feb1452e8483963915e1c56945316ad247c`;
- private checkpoint: `9501780767`, digest `sha256:9189c8b840040b782b3e4ec8ef4dcc9450fa383d32804deb600b518c4df0d917`.

The private checkpoint contains raw parent outputs and remains artifact-only; it is not committed.

Required before deterministic scoring:

```text
36 / 36 new common parents
144 / 144 fixed A00/A10/A01/A11 outputs
same parent shared by all four arms/cell
candidate private-oracle accesses = 0
FRESH_BLIND accesses = 0
LEGACY_LOCKED_TEST accesses = 0
```

Observed:

```text
3 / 36 parents
0 / 144 frozen factorial packet
```

Therefore private deterministic scoring, the 20,000-resample bootstrap, LOGO and semantic v4.2 were not authorized. No A00/A10/A01/A11 arm may be described as passing, failing, qualified or preferred from P12-C3.

Decision:

```text
P12-C3                         CONSUMED_TERMINAL_OPERATIONAL_FAILURE
same-experiment resume         FORBIDDEN
GitHub rerun                   FORBIDDEN
partial scoring                FORBIDDEN
complete-case reinterpretation FORBIDDEN
qualified arms                 NONE ESTABLISHED
preferred arm                  NONE
```

The next valid step is a systematic provider-capacity alternatives decision followed by a fresh preregistration if another EXPOSED_POOL experiment is justified. P12-C3 itself must not be resumed or rerun.

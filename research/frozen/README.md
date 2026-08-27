# Frozen Research Artifacts

`research/frozen/` contains immutable contracts, seed/maps, bounded inputs, authorizations and other artifacts explicitly frozen for experimental use.

## Rules

- do not edit a frozen artifact in place;
- if a prospective change is allowed, create a new version and record why the prior version remains valid/consumed/superseded;
- preserve path, content and provenance when referenced by a frozen result, manifest or source pin;
- a frozen authorization may be consumed even though its file remains present;
- file presence never implies that a provider/private/blind execution is still authorized.

Use `docs/CURRENT-PROJECT-STATUS.md` for current authorization and `docs/REPOSITORY-GUIDE.md` for source-of-truth rules.

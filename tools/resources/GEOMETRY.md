# Offline geometry evidence tools

These developer-only tools do not change application projections, markers,
resources, manifests, keys or production channels. They have no network path.
Use the existing `build/map-tools` Python environment; no new dependency.

## Acquire before fitting

`prepare_geometry_requests.py` reads the preserved, hash-pinned Customs and Lab
inputs and produces a **new** local evidence directory. It selects six distinct
directly observed SVG vertices per floor, with locators and annotated SVGs.
Transformed ancestry is skipped, not silently interpreted as root coordinates.
All world counterparts are null, physical feature identities remain UNIDENTIFIED,
and regions remain UNREVIEWED. Farthest-point sampling is only an acquisition
aid, never evidence that a vertex is a particular door or corner.

```powershell
$env:PYTHONPATH = "$PWD\build\map-tools;$PWD\tools\resources"
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/resources/prepare_geometry_requests.py --assets assets --customs-upstream <PRESERVED-CUSTOMS-UPSTREAM> --lab-upstream build/map-recovery-20261028/lab-final/upstream --output <NEW-EVIDENCE-DIR>
python tools/resources/calibrate_map_geometry.py --input <EVIDENCE-DIR>/customs/controls.json --output <NEW-REPORT-DIR>
```

The request generator also exports analytical source-image/world/native
matrices and a source-calibrated Lab clipping diagnostic. These are not an
independent survey. Source files and previous candidates are never overwritten.
The `*.observations.svg` files show one source group, not necessarily every
companion group in a native floor; they are not replacement runtime assets.

## Input contract

`controls.json`, bounded to 1 MiB, has `schemaVersion:1`, a 24-hex stable `mapId`,
`sources`, and `floors`. At most 128 sources, 32 floors and 256 points per floor.
Each source has a URI, pinned revision, SHA-256 and **lineage**. Different
repositories copying one image/config belong to the same lineage.

Each floor records:

- `floorId`, `imageSource`, optional `calibrationSource` (IDs in `sources`).
- `viewBox: [minU,minV,width,height]` in the **original SVG** frame.
- `sourceBounds: [minWorldX,minWorldZ,maxWorldX,maxWorldZ]` and `rotation`.
- `points`, with fixed `role` (`fit` or `holdout`), `id`, `feature`, `region`,
  `imageLocator`, observed `image:[u,v]`, and independent `world:[x,z]` or null.

A measured point's `worldEvidence` must record:

```json
{
  "source": "independent-survey-id",
  "method": "visible-manual-survey",
  "locator": "exact source frame/feature identifier",
  "gameVersion": "actual measured build, not the website retrieval date",
  "samePhysicalFeatureReviewed": true,
  "reviewRecord": "pinned correspondence and source-independence review",
  "pickingUncertaintyWorld": 0.2
}
```

The alternative method is `independent-public-survey`. Projected markers,
nearest-feature guesses and copied source annotations are not survey methods.
`pickingUncertaintyWorld` bounds the **combined** image-picking and world-survey
uncertainty, including documented player/camera/door-reference offsets. A player
screenshot coordinate is not automatically the corner or door hinge coordinate.
Do not set the example 0.2 merely to pass: estimate and substantiate it.

The tools reject shared image/calibration lineage or identical source hashes,
but cannot prove a human's identity, declared source independence, game build,
permission, locator correctness or uncertainty. Independently verify retained
snapshot bytes against each declared SHA-256 and review actual feature matches.
No field makes invented observations trustworthy.

## Frozen numerical gate and reports

Before importing world points, independently identify or replace acquisition
targets, record floor/physical region and fix the fit/holdout split. Retain the
previous request file and review change record. Never choose points or move
world coordinates after inspecting residuals to make a model pass.

Per floor: >=3 non-collinear fit points and >=3 separate non-collinear holdouts,
spanning both axes and multiple physical regions; combined uncertainty <=0.25
world units; held-out RMSE <=0.5 and maximum <=1.0. Customs fourth-floor review
must cover **both** represented buildings. Numerical spread checks supplement,
not replace, actual room/region and local passage discrepancy review.

The baseline is analytical image-to-world inversion of the declared source
projection. Identity, translation, rotation, uniform scale, similarity,
nonuniform scale and affine **world-frame corrections** use the same split.
They do not mistake SVG pixel units for world units. JSON reports retain the
matrix, per-point vector residuals, train/holdout errors, provenance and spread.
Markdown summarizes results; SVG plots capped residual arrows (fit blue,
holdout red; title contains exact error). Missing/insufficient independent
observations give `UNKNOWN`, with no fabricated numeric error.

Even `NUMERIC_CRITERIA_MET_REVIEW_REQUIRED` is **not** COMPLETE or publication
approval. Independent physical review, all floors/local discrepancies, licensing,
native compatibility and separate GUI acceptance must still be satisfied.
The tool always sets `publicationAuthorized:false`; it never signs or publishes.

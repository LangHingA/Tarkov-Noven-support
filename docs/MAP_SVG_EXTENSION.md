# Lab and Labyrinth SVG compatibility audit

2026-10-28 Phase 2: [independent calibration investigation](../MAP_GEOMETRY.md)
records conflicting declared Lab pixel calibrations, reproducible Technical Rooms
clipping, source-copy lineage, current API snapshots and actionable per-floor
acquisition requests. No independent image/world pairs or publication approval
are inferred from those diagnostics; historical evidence remains below.

2026-10-28: [17-map recovery audit](../MAP_COVERAGE.md) records the latest
read-only public catalog check, all six unpublished tracks, new local Lab NVR1
and partial Reserve previews/detail tiles. Customs' five-floor candidate is
preserved. Native loading is not independent geometry; nothing new is published.

Audit date: 2026-10-17. Resource packages remain CC BY-NC-SA 4.0, under
[Noven's permanent free/noncommercial/anti-cheating policy](../PROJECT_POLICY.md).
Software MIT licenses are not used to authorize artwork.

The [complete-coverage baseline](#complete-coverage-baseline-2026-10-20) below
records all 17 identities, including subsequent Customs source recovery.

**2026-10-20 correction:** the large extraction-marker differences compare old
hand-placed points with current extraction-volume centers. They do not prove a
game-layout revision. The [coordinate investigation](#coordinate-investigation-2026-10-20)
supersedes that interpretation below; complete independent SVG calibration is
still unproven, so withholding publication remains appropriate.

## Pinned sources

| Map | Creator / source revision | Original SVG SHA-256 | Decision |
| --- | --- | --- | --- |
| The Lab (`5b0fc42d86f7744a585f9105`) | Shebuka, [tarkov-dev-svg-maps](https://github.com/the-hideout/tarkov-dev-svg-maps/blob/5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178/Labs.svg), `5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178` | `099a9eaabc305431d906151e03c45d6f06bb885ec46234735e93cc2ab02a222a` | License supports companion use; independent SVG calibration/coverage unresolved, withheld |
| The Labyrinth (`6733700029c367a3d40b02af`) | acidphantasm, [SPT-DynamicMaps](https://github.com/acidphantasm/SPT-DynamicMaps/blob/4944764f5f6c42d152dca6bd1b5371c4f6212a9e/Plugin/Resources/Maps/Labyrinth/Layers/Labyrinth.svg), `4944764f5f6c42d152dca6bd1b5371c4f6212a9e` | `6b9448b2c51a61f52d68fcd11de806d0c93653c37f77cb7d5f53103233822c94` | Asset-specific CC license; compatible vector-only resource |

Lab uses the pinned project's LICENSE.md and README.md, including its explicit
anti-cheating statement. Labyrinth has its own
[acidphantasm-LICENSE.md](https://github.com/acidphantasm/SPT-DynamicMaps/blob/4944764f5f6c42d152dca6bd1b5371c4f6212a9e/Plugin/Resources/Maps/Labyrinth/Layers/acidphantasm-LICENSE.md).
The optimized SVG and its matching license were added together by acidphantasm
in `24cac5e5a1c48d010aaa225d86cba2ef3efda1df`; the earlier SVG source was also
added by acidphantasm in `ad040b4efee0cc74ff95b5013a58c0f55d94996b`.
Both complete license files have SHA-256
`1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1`.
NormalMaps' README separately identifies map licenses as distinct from its MIT
software license; no NormalMaps artwork/code is included in this package.

## Geometry and unchanged 0.1.2 contract

The accepted 0.1.2 PvP/PvE map references, floors, extents and points are unchanged.
The native MapPage, MapProjection and ResourceService are unchanged. No application
rebuild, new manifest format, plugin integration or satellite fallback is needed.

Lab SVG groups map as `First_Level -> Base`, `Second_Level -> Second_Level`,
`Technical_Level -> Technical`. Current display orders are 1, 0, 2 respectively;
height selection remains the existing native extents (-0.9 / 3 boundaries plus
the second-level spatial rectangle). All groups render, but the old SVG calibration
uses x [-292,-96], z [-441,-223]. The accepted current projection uses x [-287,-80],
z [-477,-193], rotation 270. Current Hangar Gate (-170.49,-218.87) and Parking Gate
(-231.46,-457.77) lie outside that source extent. Upstream's older Parking Gate
reference is (-231.73,-434.816376), about 23 world units away. These are not
measurements of the same physical landmark: the current point is the extraction
volume center. The packaging guard rejects the centers outside its old image
bounds, but that alone cannot establish missing geometry. Independent SVG
landmark calibration remains unresolved. Lab is NOT published as complete,
and no satellite tiles are used as fallback.

Labyrinth uses one Base floor. Its pinned source calibration is x [-52.5,50.7],
z [-36.5,75.3], rotation 90. The accepted native projection is x [-52,53],
z [-37,76], rotation 270, width 113, height 105. An affine transformation maps
the original SVG into that unchanged native projection (including the 180-degree
orientation difference and small bounds adjustment). No point coordinates change.
Both exits and twelve catalogued switches are within 0.632 world units of the
depicted vector paths; trigger/switch centers need not be path-interior pixels.
This is static reference/geometry validation, not live-game or user GUI acceptance.

Calibration metadata is pinned to the SPT-DynamicMaps revision above. Labs JSONC
SHA-256: `d7929df2f686a01dcd7c13a608c9cc98f8c4e0866a668994828df7ddeeb342ad`;
Labyrinth JSONC SHA-256:
`6633fd2ea1806b8d274c59af22cf88d4d99288f34f111e787b8578c428458841`.

## Reproduction and attribution

`tools/resources/prepare_additional_svg.py --assets <assets> --upstream <pinned
inputs> --output <NEW directory> --version 1.0.0` performs offline preparation.
It checks pinned SVG/config/license hashes, rejects external raster/active content,
checks floor coverage and current exits, and emits deterministic previews/NVTILES1
and NVR1 using the established packager. Upstream input filenames are documented
by its two explicit source records. Withheld Lab previews are not payloads.

The package carries unchanged SOURCE.svg, full LICENSE.txt, SOURCE.md and
PROVENANCE.json. Attribution identifies acidphantasm, the original pinned URL/hash,
upstream project, previous optimized-source history, and Noven's coordinate
conversion/rasterization/tiling. Any copyrightable Noven adaptations use the same
CC BY-NC-SA 4.0. It contains no satellite images, screenshots, unrelated icons,
SPT plugin code, executables or user data. No endorsement is claimed.

Operator `NovenResourceChannelTool --local-package <catalog-input.json> <test root>`
exercises real extraction, native PvP/PvE floor loading, corruption verification,
repair, offline restart and deletion. Network flow modes accept an optional stable
map ID after keyId; production trust, TLS, redirect and hash checks remain intact.

## Deferred maps (no new publication)

* Customs: the original default SVG lacks fourth-floor coverage. A five-floor
  candidate was subsequently recovered; see the [Customs acceptance result](#customs-acceptance-result-blocked).
* Reserve: upper-floor coverage remains missing; do not label a partial set complete.
* Dark Lab: the upstream default layout shares the Lab map reference, but that does
  not prove current geometry is represented by the old SVG. CC-compliant reuse is
  not barred merely by a different map name, but current layout validation is
  still required; no automatic reuse or new publication here.
* Ground Zero Tutorial: no verified tutorial-specific floor/projection metadata;
  do not infer equivalence merely from the map name.
* Icebreaker: no independently licensed vector alternative established here;
  TarkovBOT.eu/satellite materials remain withheld pending their own evidence.

## Published resource

Labyrinth 1.0.0 is asset **649688513** under the existing `maps-v1` release:
`6733700029c367a3d40b02af-1.0.0.nvr`. Download: **398,241 bytes**;
installed: **397,931 bytes**, six files. Package SHA-256:
`2ce0f5cb577b8db34d73af6a68796799b33704ef372fa1eeb2188c4c6ec425a3`.
`Base.satellite.png` / `.tiles` retain the old client's required filenames;
their content is exclusively the licensed SVG derivative, not satellite imagery.

The production catalog at `maps/manifest.json` is authenticated with
`noven-resources-2026`, ECDSA P-256/SHA-256 in the resource-specific trust domain.
All original ten records and immutable package digests remain unchanged.
Anonymous native WinHTTP verified API 302 -> trusted CDN 206, complete package
bytes and a persisted 65,536-byte pause. A new process resumed at that offset;
an injected disconnect resumed at byte 131,072 without re-fetching the prefix.
Native install/PvP+PvE load/verify/repair/offline restart/in-use protection/delete/
empty-cache redownload passed. Static geometry and native tests do not constitute
user GUI or live-game acceptance.

The preparation tests passed 11/11, map generator tests 45/45, and focused
resource CTest 4/4 in each Debug/Release configuration. Full application builds
and complete CTest were not repeated: only excluded operator tooling and public
documentation changed. The accepted 0.1.2 application and Setup bytes remain
unchanged, and the application update channel was not modified.

## 2026-10-20 revalidation / 重新核验

The actual clean source baseline was `c4a1d3c1`, not an older ten-map snapshot.
The public application release was already 0.1.3 and the production map catalog
already contained eleven resources, including Labyrinth 1.0.0. This revalidation
does not replace an existing package, modify either application release or
publish an incomplete Lab map.

Both upstream repository heads still match the pinned revisions above. Fresh
HTTPS downloads of both SVGs and their applicable full licenses match the
recorded SHA-256 values. The last upstream commit affecting `Labs.svg` is
`61cf07588af345b2606ff7ee0895bfcb2308be72` (2023-10-07); the Labyrinth SVG's
last edit remains `24cac5e5a1c48d010aaa225d86cba2ef3efda1df`.

All three Lab floor previews render, but that is not sufficient evidence of
current-layout compatibility. The pinned calibration's old markers compared
with the unchanged native catalog show a nonuniform discrepancy:

| Landmark | Source x / z | Native x / z | Horizontal difference |
| --- | --- | --- | --- |
| Cargo Elevator | -112.152 / -408.64 | -111.79 / -408.55 | about 0.37 world units |
| Sewage Conduit | -122.889992 / -258.3245 | -122.89 / -258.32 | about 0.005 world units |
| Hangar Gate | -170.66 / -240.77 | -170.49 / -218.87 | about 21.90 world units |
| Parking Gate | -231.73 / -434.816376 | -231.46 / -457.77 | about 22.96 world units |

Changing the overall offset or scale to move the gates is not a validated fix
for the other landmarks. There is no new source geometry or independent
calibration evidence in these upstream files to justify a local deformation.
Lab remains withheld for compatibility, **not** for lack of a CC license or
because legitimate companion-map use requires additional permission.

The existing preparation pipeline was rerun in a temporary directory: Labyrinth
was byte-identical to the immutable published NVR1, and the Lab guard again
withheld its two out-of-bounds extraction positions. Generated temporary files
were removed. Stable IDs, floor order/height selection, renderer and catalog
coordinates remain unchanged; the relevant native map code/data have no diff
from the accepted `cdfd3465` 0.1.2 baseline.

The freshly retrieved public catalog has SHA-256
`38441b9a2794bf61efe68045bf821108b91f8b11614532ef7f331a1246fd773c`.
Its signed payload/signature match the existing production catalog. Native CNG
verification and complete anonymous HTTPS byte comparison passed for **all
eleven packages**, totaling **47,032,109 resource-body bytes**.

Anonymous GitHub API access was rate-limited (403). The existing adapter correctly
used its restricted fallback to the fixed `maps-v1` release and signed artifact
basename, followed only the approved CDN 302 and validated exact 206 ranges.
Labyrinth's paused 65,536-byte prefix survived a new process; an injected
connection interruption resumed at byte 131,072 with one bounded retry. Native
install/PvP+PvE floor load/PNG decode/verify/repair/in-use deletion guard/offline
restart/delete/empty-cache redownload passed. The resumed lifecycle transferred
1,151,779 body bytes, including catalog/error responses and repeated full
downloads required by the lifecycle test; the preceding pause run transferred
76,832 body bytes. These are measured native-client counts, not estimates of
resource size or total TLS/network overhead.

Focused validation: resource tooling **11/11**, map generator **45/45**, resource
CTest **7/7 Debug and 7/7 Release**. Only the excluded operator tool was built;
no application rebuild or full application regression was needed for this
documentation-only revalidation. No remote files, asset IDs, signatures or
published versions were changed. User GUI/live-game acceptance remains separate.

## Coordinate investigation (2026-10-20)

Investigation only. No production catalog/package changes, no application build,
no marker relocation and no source push. Starting source HEAD: `65671b37`.

### Findings and limits

The two roughly 22-unit discrepancies are **different point semantics**, not
evidence of a changed global coordinate system. The current API extraction
positions agree with extraction-volume bounding-box centers; the legacy
hand-placed annotations are close to the near edges of those volumes.

The packaging guard currently compares those volume centers against the legacy
image calibration bounds and rejects Lab before packaging. This explains the
observed rejection, but does **not** prove that game geometry changed or that
the SVG is missing both gates. Earlier statements in `MAP_SVG_EXTENSION.md`
must not be interpreted as a demonstrated game-layout revision.

The available metadata cannot establish complete current SVG geometry either.
In particular, legacy world annotations are not independently surveyed SVG
pixel landmarks. No independently verified SVG-to-current-world point set
covering all three floors was found. Consequently direct SVG calibration with
independent geometric holdouts remains **unresolved**, rather than passing or
being replaced by guessed matches. Do not publish on the strength of this report.

### Exact source identities and dates

| Evidence | Identity / date |
| --- | --- |
| [Shebuka Labs.svg](https://github.com/the-hideout/tarkov-dev-svg-maps/blob/5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178/Labs.svg) | pinned repository revision `5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178`, 2026-02-16; SHA-256 `099a9eaabc305431d906151e03c45d6f06bb885ec46234735e93cc2ab02a222a` |
| Last Labs.svg file edit | `61cf07588af345b2606ff7ee0895bfcb2308be72`, 2023-10-07, removes width/height; the file was introduced in `75c9564d954cf6ba0beb23c5c5c8ca852a2fb03d`, 2023-07-21 |
| [Legacy SPT Labs calibration/annotations](https://github.com/acidphantasm/SPT-DynamicMaps/blob/4944764f5f6c42d152dca6bd1b5371c4f6212a9e/Plugin/Resources/Maps/Labs_TarkovDev/Labs_TarkovDev.jsonc) | revision `4944764f5f6c42d152dca6bd1b5371c4f6212a9e`; SHA-256 `d7929df2f686a01dcd7c13a608c9cc98f8c4e0866a668994828df7ddeeb342ad`; the last configuration edit is `b89e04b765c99a495547dd01e1f217f33112f718`, 2026-03-14 |
| [Current layout configuration](https://github.com/the-hideout/tarkov-dev/blob/97ff6e7a43d03c10f3f7a3165c8dbcdf2193d6b9/src/data/maps.json) | pinned repository head `97ff6e7a43d03c10f3f7a3165c8dbcdf2193d6b9`, 2026-10-09; last file edit `9fd29f7f16e5d5408831d9be48274dcb8862de1d`, 2026-07-20 (adds another map) |
| Noven layout snapshot | SHA-256 `c53a327dcdcff67a49b9fe2d150731edb4c1611dfc2f75db2ce97444dee2ef77`; imported with `e9999da0`, 2026-10-02 |
| Noven positioned-data snapshot | `https://json.tarkov.dev/regular/maps`, SHA-256 `8b169057c8a26ef631ef5866cdf2cc77c6a7d44d32047f786803c6b0f7b7e73f`; imported with `e9999da0`, 2026-10-02 |
| Fresh public API response | same URL; SHA-256 `dbc96c4b6d5320fbc0701cb0dc960cd0bc9076696835ef2024bf8cb3f88b06be`; HTTP Last-Modified `Tue, 20 Oct 2026 08:24:19 GMT`; all seven Lab extraction positions match Noven's pinned data |

The API response does not expose a game-build revision or an extraction-specific
change date. Its HTTP modification timestamp is a dataset publication time, **not**
a proven game-layout date. No such missing version identity is invented here.

The layout uses `labs_v4` tile imagery. The [2025-01-20 upstream change](https://github.com/the-hideout/tarkov-dev/commit/41bb6a88dadb68e02aae9c0d5eca629a8fb4a0f7)
switches v3 to v4, changes max x from -91 to -80 and tile-transform translation
from 196.7 to 193.7. This proves a rendering/configuration revision, not by itself
a game-world geometry revision. The earlier [2023-11-07 change](https://github.com/the-hideout/tarkov-dev/commit/3bb50623897083cf9749d13312d6bdbd4d8a0e81)
already uses world bounds x [-287,-91], z [-477,-193]. Thus large bounds covering
the extraction-volume centers existed in 2023 as well; they are not evidence
that the two gates expanded in a later game patch.

### Extraction-point semantics

World axes below are x/z; SPT's map plane is JSON x/y with JSON z as elevation.
Noven/API use x/z with y as elevation. This axis naming difference is accounted
for before fitting and is not an unexplained rotation.

| Extract | Legacy point x/z | API point x/z | API outline z interval | Difference |
| --- | --- | --- | --- | --- |
| Hangar Gate | -170.66 / -240.77 | -170.49 / -218.87 | [-240.06,-197.67] | 21.900660 |
| Parking Gate | -231.73 / -434.816376 | -231.46 / -457.77 | [-478.57,-436.98] | 22.955212 |
| Ventilation Shaft | -144.866 / -399.385 | -145.06 / -396.83 | [-401.34,-392.32] | 2.562355 |
| Cargo Elevator | -112.152 / -408.64 | -111.79 / -408.55 | [-411.57,-405.52] | 0.373020 |
| Main Elevator | -282.304016 / -334.896 | -282.69 / -334.73 | [-336.77,-332.69] | 0.420166 |
| Medical Block Elevator | -112.423 / -343.986 | -112.30 / -344.04 | [-345.95,-342.12] | 0.134332 |
| Sewage Conduit | -122.889992 / -258.3245 | -122.89 / -258.32 | [-262.32,-254.32] | 0.004500 |

For all seven, the API point is within 0.007072 world units of the rectangle
center (coordinate rounding). Hangar is about 40.13 by 42.39 units and Parking
about 40.83 by 41.59 units. The legacy annotations are respectively 0.71 and
2.163624 units from the nearest z edge, not the center. Their differing elevation
values are also consistent with point-versus-volume semantics; this is not a
comparison of the same physical surveying mark.

### Cross-floor world-frame controls and held-out tests

Nineteen semantic correspondences use explicit lock IDs with matching key IDs,
or explicit switch identities. No nearest-background-pixel matching is used.
Six preselected controls span all three floors; thirteen other points never
participate in that fit. Leave-one-out fitting additionally holds out each of
the nineteen observations in turn. The extraction markers above are not fitted.

| Landmark | Floor | Legacy x/z | API x/z | Split |
| --- | --- | --- | --- | --- |
| Manager office, first door | Second | -165.246277 / -349.197 | -165.25 / -349.22 | fit |
| Manager office, second door | Second | -165.242874 / -338.086 | -165.24 / -338.10 | holdout |
| Weapon testing, first door | Base | -181.966461 / -318.226044 | -181.97 / -318.21 | fit |
| Weapon testing, second door | Base | -179.862 / -310.3296 | -179.86 / -310.33 | holdout |
| Blue infirmary door | Base | -123.229095 / -406.524384 | -123.23 / -406.52 | fit |
| Green sterile-lab door | Second | -135.89798 / -346.9675 | -135.90 / -346.97 | holdout |
| Blue-marking door | Second | -130.268463 / -339.944275 | -130.27 / -339.94 | holdout |
| Yellow security door | Second | -212.695 / -376.538 | -212.69 / -376.54 | fit |
| Black test-room first door | Base | -132.893 / -348.72 | -132.89 / -348.72 | holdout |
| Black test-room second door | Base | -128.794 / -349.91507 | -128.79 / -349.92 | holdout |
| Violet security door | Second | -261.993 / -317.240021 | -261.99 / -317.24 | holdout |
| Red security door | Second | -257.222015 / -322.925018 | -257.22 / -322.93 | holdout |
| Arsenal storage door | Second | -250.839066 / -326.758667 | -250.84 / -326.76 | holdout |
| Residential-unit door | Base | -117.3155 / -439.54068 | -117.32 / -439.54 | holdout |
| Medical elevator power | Technical | -124.758 / -313.806 | same | fit |
| Main elevator power | Technical | -271.439 / -366.10498 | same | fit |
| Open parking gate switch | Second | -243.443 / -382.513 | same | holdout |
| Water-level switch | Technical | -136.76 / -254.510513 | same | holdout |
| Parking-alarm switch | Second | -220.756 / -381.263 | same | holdout |

| Correction model | Fit RMSE | Holdout RMSE | Holdout max | Leave-one-out RMSE |
| --- | --- | --- | --- | --- |
| Identity | 0.011985 | 0.005188 | 0.014292 | 0.007986 |
| Translation | 0.011949 | 0.005070 | 0.013668 | 0.008283 |
| Rotation + translation | 0.011941 | 0.005158 | 0.013798 | 0.008341 |
| Uniform scaling + translation | 0.011949 | 0.005076 | 0.013674 | 0.008343 |
| Rotation + uniform scaling + translation | 0.011941 | 0.005163 | 0.013804 | 0.008399 |
| Nonuniform axis scaling + translation | 0.011836 | 0.005611 | 0.014439 | 0.008431 |
| Full affine | 0.011788 | 0.006109 | 0.014500 | 0.008546 |

Rotation fits about 0.000404 degrees; uniform scale is 1.000000492. Full affine
coefficients are approximately `[0.999985644,-0.000031220; -0.000006540,1.000044350]`,
translation `[-0.014196,0.013809]`. These are rounding-level corrections, not a
solution to the 22-unit extraction-marker discrepancy. More degrees of freedom
lower training error but worsen held-out performance. Identity is adequate.

**Independence limitation:** these are separately stored SPT/API world
annotations and independent *fit holdouts*, not proven independent measurements
of the actual game. Some identical switch values likely have common provenance.
They establish frame agreement; they do not validate SVG pixels. The SVG's
`Rooms/Doors/Arrows/Details` paths lack matching semantic landmark IDs. Converting
the same world annotations into SVG pixels using the old calibration and then
fitting them back would be circular, and is deliberately not presented as an
independent geometric test. Requirements for independently surveyed image
landmarks on all three floors remain unsatisfied.

The SVG viewBox is 720 by 586. The legacy calibration x [-292,-96], z [-441,-223]
and rotation 270 would prescribe `u=(z+441)*720/218`,
`v=(x+292)*586/196`. Current tile bounds must not automatically replace that
image calibration. No new production transform is selected here.

### Vector alternatives and recommended correction

The Shebuka source is CC BY-NC-SA 4.0 and still has the same bytes. The pinned
SPT split layers and NormalMaps' `发布源/Maps/Labs_TarkovDev/Layers/` have identical
Git blob identities: First `f00d1f967a7812d037aba0ad1d5a862ba8daca48`, Second
`254d8656af68296dbaaa6699e46e1745a8056100`, Technical
`5ff86da5b88803d6fd4f0408af1f243784c02c04`. Both combined SVG copies are blob
`d3fbfa5925e3988c43c9ab781c76c682fcb2e640`. A more recently maintained software
repository is therefore not evidence of newer Lab artwork. No newer, separately
verified compatible CC vector geometry was established in these sources. No
satellite imagery was substituted or redistributed.

Recommended next investigation, **not implemented in this task**:

1. Keep API extraction centers/outlines unchanged; model door threshold, switch
   and extraction volume as different features. Never move a marker to fit art.
2. Treat center-outside-image as a warning, not sufficient proof of obsolete
   geometry. Validate background coverage against physical walls/doors and
   relevant region intersections, with separate image and tile calibration.
3. Obtain a documented image landmark set on each floor: e.g. identified door
   center/hinge, elevator threshold and stair corner, paired with independent
   public reference measurements. Fix training/holdout IDs before fitting.
4. Compare fixed calibration, translation, rigid, similarity, nonuniform and
   affine models on those independent SVG holdouts; report uncertainty from
   picking a door edge versus a center. Only then decide whether calibration or
   independently licensed new geometry is required.

Reproduce the world-frame diagnostics without network or output files:

```powershell
python tools/resources/investigate_lab_coordinates.py --legacy-config <pinned-Labs.jsonc> --api-snapshot <pinned-regular-maps.json>
python -m unittest discover -s tools/resources -p test_lab_coordinates.py -v
```

Only focused investigation tests are appropriate; no full build is claimed.
The known retained 539,828-byte test directory was inspected read-only. Its
previous cleanup attempts were rejected before PowerShell ran with
`CreateProcess ... rejected: blocked by policy`. This is an execution-policy
blocker, not an observed file lock or proof of an ACL denial. No alternate-shell,
script, Python or other deletion attempt was made to bypass that restriction.
Exact machine-local retained paths are reported separately, not committed here.

## Complete-coverage review: acceptance protocol (2026-10-20)

This protocol is fixed before selecting any new Lab image transform. It is an
engineering publication criterion, not an additional upstream license term.
Existing production resources are preserved; their previous package/renderer
acceptance is not presented as a new independent geometric survey.

For each of Technical, Base and Second_Level, require at least three
non-collinear fitting landmarks and three separate holdouts. Identify the same
physical feature in both observations (e.g. hinge, door-threshold midpoint or
stair corner), with pinned evidence and a stated picking uncertainty. Points
must span both image axes and different rooms, not one corridor. A world point
projected into the SVG using the calibration being tested is not an image
observation. Two repositories copying one annotation are not independent world
measurements. Extraction-volume centers, activation boundaries and physical
entrances remain distinct observations.

Publication requires held-out image-to-world RMSE <= 0.5 world units and maximum
error <= 1.0 on **each floor**, picking uncertainty <= 0.25 world units, and no
unexplained local room/passage discrepancy. These tolerances are deliberately
smaller than typical room dimensions; uncertainty must be reported rather than
absorbed into a fitted transform. Reject degenerate or spatially clustered
control sets. Compare fixed legacy calibration, translation, rigid rotation,
uniform scale, similarity, nonuniform scale and affine fits using the same
preselected fit/holdout split. Prefer the simplest passing transform; a lower
training error alone is not acceptance. Do not loosen these thresholds after
seeing residuals.

All required floors must also have nonblank native previews/detail packs,
correct height selection and navigation, complete source/license/modification
records, and deterministic NVR1 bytes. Independent image geometry, world
annotation consistency, native component tests and user GUI acceptance are
separate results. If independent feature identities or observations are
missing, residuals are **not measurable**, not zero; keep publication blocked
without calling the artwork obsolete.

## Complete-coverage baseline (2026-10-20)

Start application HEAD: `f7138b6de860bcff3add07b541a981010367ec78`, clean.
Canonical application version 0.1.3; no application/runtime/Core TSV change is
made in this review. Existing regular/PvE floor contracts match: **66 rows**
across 16 identities; Tutorial is a seventeenth identity with missing metadata,
not a map proven to have zero physical floors.

The complete machine-readable [floor matrix](../tools/resources/map_coverage.json)
records all identities, native floor IDs/order/height rectangles, coordinate
bounds/rotation, source URL/content hash, known revision or explicitly missing
game-layout revision, license evidence, development preview/detail presence and
published package preview/detail coverage. `published` means catalog membership,
not a new independent geometric certification. Local raster files are not
treated as cleared SVG sources. Floor-less Tutorial cannot pass vacuously.

| MapCatalog ID | Map | Required native floor IDs | Production |
| --- | --- | --- | --- |
| `55f2d3fd4bdc2d5f408b4567` | Factory | Ground_Floor, Second_Floor, Third_Floor, Basement | Preserved |
| `56f40101d2720b2a4d8b45d6` | Customs | Ground_Level, Second_Floor, Third_Floor, 4th_Floor, Underground_Level | Candidate, unpublished |
| `5704e3c2d2720bac5b8b4567` | Woods | Ground_Level | Preserved |
| `5704e4dad2720bb55b8b4567` | Lighthouse | Ground_Level | Preserved |
| `5704e554d2720bac5b8b456e` | Shoreline | Ground_Level, Second_Floor, Third_Floor, Underground_Level | Preserved |
| `5704e5fad2720bc05b8b4567` | Reserve | Ground_Level, 2nd_Floor, 3rd_Floor, 4th_Floor, 5th_Floor, Bunkers | Upper geometry missing |
| `5714dbc024597771384a510d` | Interchange | Ground_Level, First_Floor, Second_Floor | Preserved |
| `5714dc692459777137212e12` | Streets | Ground_Level, Second_Floor, Third_Floor, Fourth_Floor, Fifth_Floor, Underground_Level | Preserved |
| `59fc81d786f774390775787e` | Night Factory | Ground_Floor, Second_Floor, Third_Floor, Basement | Preserved |
| `5b0fc42d86f7744a585f9105` | The Lab | Base, Second_Level, Technical | Independent image calibration unresolved |
| `653e6760052c01c1c805532f` | Ground Zero | Ground_Level, Second_Floor, Third_Floor, Underground_Level | Preserved |
| `65b8d6f5cdde2479cb2a3125` | Ground Zero 21+ | Ground_Level, Second_Floor, Third_Floor, Underground_Level | Preserved |
| `65cc8f81a9aac3e77d0cfd3e` | Terminal | Ground_Level | Preserved |
| `6733700029c367a3d40b02af` | Labyrinth | Base | Preserved |
| `68236e8153654e8c1200798a` | Ground Zero Tutorial | Unknown: no native floor/reference records | Core/data-version change required |
| `69af492a4819ea4ba10a69c5` | Icebreaker | Base, Helipad, Gym_Canteen, Accommodation_lower, Accommodation_mid, Accommodation_upper, Officers_Deck, Stairs_blocked, Bridge, Bridge_Roof, Control_Room, Engine_Room, Engine_Room_upper, Fuel_Pumps_lower, Fuel_Pumps, Storage_Security | 16-slice geometry/rights unresolved |
| `6a294a5b5eb5f9a1700417b7` | The Lab (Dark) | Base, Second_Level, Technical | Variant geometry unverified |

The eleven production entries cover 33 native floor rows. This is file/floor
coverage, not a newly measured 33-floor geometry survey. Existing package/source
hashes and identities are preserved in the matrix. All packages retain their
original source, license and modification notices. The current layout reference
is [tarkov-dev `97ff6e7`](https://github.com/the-hideout/tarkov-dev/blob/97ff6e7a43d03c10f3f7a3165c8dbcdf2193d6b9/src/data/maps.json),
SHA-256 `c53a327dcdcff67a49b9fe2d150731edb4c1611dfc2f75db2ce97444dee2ef77`.
Its publication date does not identify the exact game build for each floor.

Inventory reproduction (read-only, no extraction/network; use explicit existing
paths, no new build tree):

```powershell
python tools/resources/audit_map_coverage.py --assets assets --catalog <signed-manifest.json> --packages <existing-NVR-directory>
```

This Python inventory is **not a signature verifier or publishing authority**.
Run the native `NovenResourceChannelTool --verify-remote` separately with the
trusted public key and approved fixed asset root. The live signed production
catalog was fetched over HTTPS and retained all eleven entries. Its envelope
SHA-256 is `38441b9a2794bf61efe68045bf821108b91f8b11614532ef7f331a1246fd773c`.
The native verifier authenticated the catalog/packages and read **47,032,109
actual remote body bytes**. Anonymous Asset API 302 responses led only to the
authorized CDN; CDN responses were 206 with exact Content-Range, including
4 MiB slices. Every byte matched the signed local package identities. No remote
catalog, application release or existing resource asset was changed.

### Lab: image observations are not yet paired controls

The pinned SVG has three floor groups and no external/embedded raster images.
Actual SVG door-shape observations below are measured from vector coordinates,
not generated by projecting the world annotations. Coordinates are in the
original 720 by 586 viewBox. `Doors path[n]` is zero-based within that floor's
Doors group; where one path has multiple rectangular subpaths, the subpath is
identified explicitly.

| SVG group / native floor | Locator | Observed rectangle center u/v | Missing evidence |
| --- | --- | --- | --- |
| Technical_Level / Technical | Doors path[1], red rectangle | 321.6045 / 39.1870 | Physical door identity and independently corroborated world point |
| Technical_Level / Technical | Doors path[2], first rectangle | 282.4785 / 394.1585 | Same |
| Technical_Level / Technical | Doors path[0], initial rectangle | 187.9250 / 456.1535 | Same |
| First_Level / Base | Doors path[4], first rectangle | 301.0460 / 486.1800 | Exact physical threshold/hinge identity; do not infer from proximity alone |
| First_Level / Base | Doors path[6], rectangle | 112.0460 / 503.1810 | Same |
| First_Level / Base | Doors path[13], first rectangle | 435.0460 / 324.1810 | Same |
| Second_Level / Second_Level | Doors path[7], first rectangle | 384.9980 / 101.76615 | Exact physical threshold/hinge identity and independent world counterpart |
| Second_Level / Second_Level | Doors path[10], rectangle | 211.0000 / 234.7660 | Same |
| Second_Level / Second_Level | Doors path[17], first rectangle | 303.9980 / 377.7660 | Same |

These are **unidentified/tentative features**, not accepted survey points.
The existing red/blue/black/manager annotations suggest candidate rooms but do
not identify a particular vector edge as the same physical object origin.
Technical especially lacks semantic image IDs. A nearest-door match using the
old projection would bias the calibration being tested. No floor has the
required independent paired fit/holdout set, so image residuals for fixed,
translation, rotation, uniform scale, nonuniform scale and affine models are
**not measurable from the established evidence**. The earlier 19-point world
residuals are not reused as image residuals. No final transform or claim of
obsolete geometry is made. The packaging gate now reports this precise missing
image evidence rather than treating outside extraction centers as proof of
missing physical geometry; Lab remains fail-closed and unpublished.

## Customs final validation protocol (2026-10-20)

This review is limited to Customs `56f40101d2720b2a4d8b45d6`. It preserves the
existing five-floor candidate and the eleven published map records. No 0.1.3
application, Core catalog, other unpublished map or existing package is changed.

Before any image-to-world fit, fix the following criteria for **each** of
Ground_Level, Second_Floor, Third_Floor, 4th_Floor and Underground_Level:

* At least three non-collinear calibration pairs and three separate held-out
  pairs, distributed across the floor's actual represented geometry. Sparse
  fourth-floor structures need controls on both buildings, not six points on
  one edge. Pair explicit door-threshold centers, wall/stair corners or other
  identified fixed physical features, not a nearest marker chosen by the fit.
* Each SVG observation needs a reproducible source element/vertex locator and
  each world observation needs independent provenance identifying the **same
  physical feature**. Record picking uncertainty <= 0.25 world units. A copied
  upstream coordinate annotation, source calibration, projection rectangle,
  extraction-volume center or point projected into the SVG is not an independent
  image/world pair.
* Keep control/holdout identities fixed while comparing existing calibration,
  translation, rigid rotation, uniform scale, similarity, nonuniform scale and
  affine models. Require per-floor held-out RMSE <= 0.5 world units and maximum
  error <= 1.0, with no unexplained local wall/door/stair discrepancy. Prefer
  the simplest passing model, never lower training error alone. Missing pairs
  mean **not measurable**, not zero error; do not fit or relax thresholds to
  manufacture acceptance.
* Floor coverage, attribution, nonblank preview/detail rendering, native package
  lifecycle and user GUI acceptance remain separate checks. Preserve existing
  world markers, projection and height selection. License eligibility and a
  successfully loaded NVR1 do not establish geometric accuracy.

These are engineering release criteria, not additional upstream license terms.

### Customs acceptance result: BLOCKED

Review start: `0438a71c85482bd734583cfe1924128f546792a7`, with the two existing
Customs tools untracked. They and all retained candidate/test bytes were
preserved. This result does not alter the earlier Lab investigation or authorize
any other map. The current production count remains **11/17**, not 12/17.

#### Exact sources and redistribution evidence

Artwork: Shebuka, with supplied modifications by acidphantasm. The five split
SVGs and combined original are pinned to SPT-DynamicMaps commit
`4944764f5f6c42d152dca6bd1b5371c4f6212a9e`, under
[`Plugin/Resources/Maps/Customs_TarkovDev/`](https://github.com/acidphantasm/SPT-DynamicMaps/tree/4944764f5f6c42d152dca6bd1b5371c4f6212a9e/Plugin/Resources/Maps/Customs_TarkovDev).
The co-located
[modified-asset license](https://github.com/acidphantasm/SPT-DynamicMaps/blob/4944764f5f6c42d152dca6bd1b5371c4f6212a9e/Plugin/Resources/Maps/Customs_TarkovDev/Layers/Shebuka-LICENSE-MODIFIED%20BY%20ACIDPHANTASM.md)
is CC BY-NC-SA 4.0; software MIT is not used as the artwork grant. Fresh HTTPS
retrieval of all five SVGs, the full license and upstream README returned 200
and matched the retained exact bytes. No independent satellite/image rights
are inferred. Qualifying redistribution is noncommercial, with original author,
source/revision/hash, full license, previous modification attribution, Noven's
affine conversion/rasterization/tiling record and applicable ShareAlike.

| Pinned input | SHA-256 |
| --- | --- |
| Customs-Ground_Level.svg | `5be31c29173854f5f832c3fea072bfd8603e27eeca2052754f3798cbf1b6b6d9` |
| Customs-Second_Floor.svg | `3bb882642f6288b651a7e3a1939bb9f379b8a81de679630fd0259499f7e73e64` |
| Customs-Third_Floor.svg | `7a5626c748ee4fb45c5b9e9e451691e1811b25ee103da4fc1a1c5b8a3fb4d203` |
| Customs-Fourth_Floor.svg | `d4bd72d8fd9f5e7f8e7c64f6848863b87c425843aaf058a78d6f256a9dc6cba0` |
| Customs-Underground_Level.svg | `9d5fe0a3c0bec91dd38fbf045a71548ac5d33df1c46dab4e81ff73931da8567c` |
| Combined Customs.svg | `40c33a8ac0813af73bad7c5c3c9f3a0c7fc36f9b6e401bf68834b982b2630fe4` |
| Customs_TarkovDev.jsonc | `6924222ceb18c4752cc8fd17d0a234765b597d3c140a805144e623efcb4206be` |
| Asset-specific license | `1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1` |
| Shebuka upstream README | `ee4022e968c052d2920251ba2181b5ebd9ffb45c5c69bdea916bd9f3a6e7031a` |

The README is pinned independently to Shebuka project commit
`5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178`. Original calibration JSONC remains
local; it is referenced by URL/hash but is **not** put in the package under an
invented artwork license. Each floor carries its original SVG, LICENSE.txt,
UPSTREAM-README.md and SOURCE.md. The combined SVG and PROVENANCE.json are also
retained. No embedded raster, external image reference, active SVG content,
game icon or executable is included.

#### Five-floor contract and observations

Native regular/PvE catalogs agree. Keep their existing order numbers, even
though their display order is not numerical floor order. Do not renumber them
or import source height rules to make a geometry check pass.

| Native floor | Existing order | Source groups and physical evidence | Independent accepted fit / holdout pairs | Held-out RMSE / max |
| --- | --- | --- | --- | --- |
| Ground_Level | 3 | Ground_Level plus First_Floor companion; terrain/buildings and first-level stairs | 0 / 0 | N/A / N/A |
| Second_Floor | 0 | Second_Floor, Buildings-2 and Ladders-2; dorms and industrial structures, not a ground-image substitution | 0 / 0 | N/A / N/A |
| Third_Floor | 2 | Third_Floor, Buildings-3 and Ladders-3; dorms and industrial upper structures | 0 / 0 | N/A / N/A |
| 4th_Floor | 1 | Fourth_Floor, two building paths, two stair-like rectangles and a gold polygon; source-calibrated oilrig/panda location | 0 / 0 | N/A / N/A |
| Underground_Level | 4 | Buildings-Under and Ladders-Under; separate bunker/industrial footprints | 0 / 0 | N/A / N/A |

The source calibration has rotation 180, x [-372,698], z [-306,235]. Native
projection retains rotation 180, x [-372,698], z [-307,237], width 1070, height
544. Conversion uses each source's actual viewBox (Ground 1062.48 by 535.17;
other split floors 1062.4827 by 535.174), not a stretched screenshot or an
invented marker offset. SPT JSONC x/y is the horizontal plane, z is elevation;
native x/z is horizontal, y is elevation.

For the fourth floor, source-calibrated path alpha bounds at four pixels per
world unit are [252.25,274.75] x [-79.75,-52.0] and [245.5,266.75] x
[-40.75,-2.25]. These support the association with the native oilrig/panda
region x [246,279], z [-79,-1.4], height [11.2,54.7]. Source selection instead
uses height [9.8,100] and a wider rectangle; native rules remain unchanged.
This is actual shape/location evidence, not floor-name matching, but it uses
the source's own calibration and is **not an independent accuracy measurement**.

Reproducible SVG observations are available, but their world counterparts are
not established. Examples below are first polygon vertices, not presumed
physical door centers. Locators are relative to the floor SVG; polygon[1] is
the first polygon in that group.

| Floor | SVG locator | Observed u / v | Independently corroborated matching world x / z |
| --- | --- | --- | --- |
| Ground_Level | First_Floor / Ladders-First / polygon[1] | 483.46 / 149.96 | Missing |
| Second_Floor | Second_Floor / Ladders-2 / polygon[1] | 483.493 / 150.2182 | Missing |
| Third_Floor | Third_Floor / Ladders-3 / polygon[1] | 521.6044 / 459.9254 | Missing |
| 4th_Floor | Fourth_Floor / polygon[1] | 421.4615 / 245.6966 | Missing; exact physical meaning of gold shape also unverified |
| Underground_Level | Underground_Level / Ladders-Under / polygon[1] | 494.6234 / 166.8569 | Missing |

These observations are not a selected training set and do not provide the
required spatial distribution or holdouts. The inspected source has no
physical door/room IDs linking these vertices to surveyed world points. Its
JSONC supplies 34 LockedDoor, one Switch, 25 Extract, four Transit and two
Secret world annotations, but no measured image/world control table. Reusing
those through their own calibration would be circular. Native semantic point
counts, using unchanged height-region selection, are:

* Ground: 21 locks, one switch, 22 extracts, four transits.
* Second: eight locks; Third: six locks.
* Fourth: no lock/switch/extract/transit controls.
* Underground: one lock and five extracts.

These are **marker counts**, not accepted independent landmarks. Locks describe
object positions without proving which vector edge is their threshold/hinge;
extracts may describe activation volumes rather than visible entrances. Neither
counts, nearest-marker matches, floor-region rectangles nor copied map
annotations establish physical corner coordinates. The searched author sources
and public layout data did not establish independent world observations for
the shown image features. No game-memory access, game extraction or automated
gameplay was attempted.

Therefore all seven transform comparisons remain **unmeasurable**, not failed
with a numerical residual and not passed with zero. There is no defensible
per-floor holdout result or local-discrepancy verdict. Required missing evidence
is at least six semantically identified, spatially distributed image/world
pairs on each floor, including both fourth-floor buildings, with independent
world-source revision/measurement context and <= 0.25-unit picking uncertainty.
No transform was fitted and no correct marker was moved. This is insufficient
evidence, **not proof that the SVG is wrong or obsolete**.

#### Preserved candidate and test boundaries

Existing internal candidate: `56f40101d2720b2a4d8b45d6-0.0.1.nvr`, 41 entries,
**2,925,966 downloadable bytes**, **2,923,784 installed bytes**, SHA-256
`544b925dc1c56d5c9ad040e1e9d70b2511d0b344456de467b0a064936e011905`.
Its independent repeat package is byte-identical. This is not a signed or
published production resource and has no GitHub asset ID. Its unsigned local
catalog is only input to the explicit offline operator tool, never production.

This review re-rendered all five sources in memory and matched every retained
preview/detail byte for both native image modes. Previews are 1024 by 521,
details 4096 by 2082; all have nonempty, nonuniform content. Filenames ending
`.satellite.png` or `.satellite.tiles` carry only new SVG-derived content because
the unchanged client requires those paths; the name does not authorize raster
imagery. No regenerated file overwrote retained output.

Focused offline resource tooling tests **30/30 PASS** and map generator tests
**45/45 PASS**. The prior native local-package run (before this review) passed
PvP/PvE floor loading, PNG decoding, corrupt verification, repair, offline
service restart and deletion. That historical result is retained, **not claimed
as a new GUI, new native lifecycle or remote Customs acceptance run**. This
review stops at the geometry gate: no new package/install test tree, application
build, full CTest matrix, remote Customs download or production release is run.

Fresh public `maps/manifest.json` returned HTTP 200, still eleven entries with
no Customs record. Its envelope equals the preserved production envelope;
native CNG signature/package verification passed for all eleven local packages
using `noven-resources-2026`. Public envelope SHA-256 remains
`38441b9a2794bf61efe68045bf821108b91f8b11614532ef7f331a1246fd773c`.
No new catalog was signed, no resource was uploaded, and the application
repository/channel were not pushed or modified. User GUI acceptance remains
separate and pending.

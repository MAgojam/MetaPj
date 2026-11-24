# MetaPj roadmap — 23 November 2026

## Current development preview 1.1.0

- Keep R/metafor statistics and native variable suppliers in three main tabs:
  Dichotomous, Mean differences and Generic effect sizes (variance/SE/normal CI).
- Delegate Python execution, helper logic and D3/Chart/Plotly resources to installed Pj>=1.8.0 API1.
- Remove the old bespoke D3 renderer and the 28.17 SVG-only diagnostic mode.
- Offer Plotly forest, D3/Chart interval alternatives, descriptive funnel and optional leave-one-out.
- Default to D3 intervals in compiled metadata and fresh R options. Give the
  Html funnel its own accordion/size control by composing unchanged Pj outputs;
  defer forest–funnel linking as requested, without changing Pj.
- Load one personal UTF-8 script into a passive draft; explicit Run, Save, Disable and source diagnostics.
- Document selected source data, included effects, mapping and scales; provide reusable developer examples.
- Provide eight adaptive personal scripts: report, source explorer, tau² weights,
  cumulative Chart weights, Plotly weight-scenario map, D3 source audit/reshape,
  native bootstrap and batch-Rust sign flips with numerical/timing comparisons.
- Keep the eight examples as a capability map: enrich weight concentration with
  Pj's existing paired FE/RE explorer (linked selection, brushing and figure size),
  rather than adding a duplicate renderer or assuming forest/funnel linkage.
- Group Load/Save in the Script frame and Run/Disable in the Python frame,
  using transparent titles and the same restrained interface style as Pj.
- Validate fresh INIT/save/RUN caches, restart propagation, missing Pj, scripts and native results.

## Repository scope

This is a source example/guide for developers. Publish the module source,
English/Italian guides, the eight Python examples, the minimal R consumer and
example datasets. Keep Windows x64 and Linux x64 JMO files in the repository
root for optional sideload testing. Do not create GitHub Releases, release tags,
publication workflows or a jamovi Library submission for this example.
Build caches, validation harnesses, screenshots, logs and diagnostic data remain
local, outside the public source tree.

## Validation and future changes

1. Automated Windows backend, scripts, UI file-loading and offline rendering.
2. Maintainer Windows visual checks with both Pythons, including OMV save/reopen with active code and draft.
3. WSL2 build/tests and maintainer visual checks after Windows PASSED.
4. Repository preparation: review source/docs and include only the two optional JMO files and intended public files. Commit/push only when requested; no releases or macOS packaging is planned for this example.
5. Add further model families as new top-level supplier tabs only after the current three families are accepted.

The developer example is independent of Pj's distribution and the other modules.
Preserve the boundary between statistical fitting, the consumer's state/UI and
Pj's public execution/helpers when extending it.

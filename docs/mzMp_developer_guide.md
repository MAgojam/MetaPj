# Calling the public Pj API from a specific module

Current example: MetaPj1.1.0, Pj>=1.8.0, public API1, jamovi>=28.18.
MetaPj owns its R/metafor model and native UI. Pj owns Python execution, helper
implementation and graphics resources. The consumer never imports Pj internals,
sources its private files or bundles another copy of the Pj module.

## Minimal boundary

```r
service <- mzMpConnect()  # R/mzMp_bridge.R: runtime discovery + API checks
response <- service$run(
    code = mzMpPythonCode(context, extensionCode),
    service_code = paste(presentationSource, mzMpPythonPrelude(context), sep="\n"),
    data = selectedSourceData,
    python = self$options$python,
    figure_width = self$options$plotWidth,
    figure_height = self$options$plotHeight,
    timeout = 60L,
    checkpoint = function() private$.checkpoint(flush=FALSE)
)
```

Use only exported `mzPjServiceInfo` and `mzPjRunPython`. API metadata/version and
checkpoint capability are checked at run time. Each call is a separate Python
process; the host owns state, input selection, output mapping and interpretation.
Missing Pj retains native R results. Restart conditions (`code == 'restart'`)
propagate unchanged; ordinary errors are shown without freezing the editor.

The optional script is UTF-8, one file at a time, with `mzRender(context)` as its
entry point. Load/edit updates a passive draft; Run copies it to active options.
The host labels errors with the loaded filename. Pj receives the unshifted script
as code and owns its line/source diagnostics; context setup stays in service_code.
Do not concatenate user text into JavaScript/HTML or evaluate it in R. Pj executes
it with the selected interpreter's permissions; jamovi owns saved-code authorization.

## `context` contract

Three native input families are available. Generic effect sizes accepts yi and
variance/SE/normal-based CI limits, with explicit supplied/log-ratio display scale.
See the [bilingual generic-input guide](mzMp_generic_effects.md) for conversions,
validation and Data Library mapping. In generic mode, `analysis` additionally
reports `input_type`, `input_ci_level` (CI mode) and `input_note`; `inputs` maps
yi/vi, yi/sei or yi/ciLower/ciUpper to original source columns. Included `studies`
still always supplies yi/vi, so downstream helpers can reuse the same contract.

The context is a Python dictionary with six keys:

| Key | Type | Meaning |
|---|---|---|
| `analysis` | dict | `kind`, `measure`, `ratio`, confidence `level`, usable `k`, total rows, excluded rows, `effect_scale` |
| `studies` | list of dicts | Included studies, in dataset order |
| `models` | list of dicts | Selected FE and/or RE model summaries |
| `diagnostics` | dict | R-calculated SE funnel limits/reference; optional leave-one-out rows and notes |
| `inputs` | dict | Semantic roles: ai/bi/ci/di; n1i/m1i/sd1i/n2i/m2i/sd2i; or generic yi with vi/sei/ciLower/ciUpper, plus optional study; mapped to selected source column names |
| `presentation` | dict | `engine`, `result_type` (html/svg), `width`, `height` |

Study fields: `study` label, `source_row` (1-based dataset row), `yi`, `vi`,
display `estimate`, `lower`, `upper`, and percentage `weight_FE`, `weight_RE`.
Weights for an unselected model are `None`. `yi` and `vi` always use the
analysis scale: log RR/log OR or untransformed RD/MD/SMD.

Model fields: `model`, `method`, display `estimate/lower/upper`,
`analysis_estimate`, `se`, `statistic` (z), `p`, `tau2`, `I2`, `H2`, `Q`,
`Q_df`, `Q_p`, and display `pi_lower/pi_upper`. Tau² and prediction bounds are
`None` for FE. I² is a percentage. No value silently changes scale when the
graphics engine changes.

Pj's separate `data` dictionary contains the selected source columns, including
rows excluded from the fitted analysis. `source_row` is the 1-based position in
the R input frame supplied to MetaPj; it is not a guaranteed global dataset row
after filtering. A Python list index is source_row - 1. Do not join arrays by
position after dropping rows independently. No unselected columns, R fit object,
UI object or entire jamovi instance is exposed. Add fields explicitly when needed.

## Result mapping and reuse

Standard Table results have host-declared schemas. The bridge checks expected
names and maps JSON null to NA. Extension Table/Html/Svg/Text/Preformatted items
are isolated in their own Group and reconstructed before native state reload.
Ready PNG/Image, browser capture and dataset Output need additional host mapping;
this preview rejects those unsupported extension types rather than silently
losing them. It does not install capture infrastructure copied from Pj.

D3 intervals, Plotly dictionaries and Chart datasets call Pj's public helpers.
Their assets travel through the API as portable inline results. There is no
MetaPj D3 engine, no Python plotly dependency and no vendor JS copy in the host.
D3 uses the explicit analysis scale for ratios; other renderer details and
statistical conventions are documented in README.

Fit signatures depend on selected input, measure, model flags and confidence.
Presentation signatures additionally include engine, dimensions, result type,
interpreter and Pj/consumer versions. Active script identity/code/revision has
its own key. Small keys and fitted context are persisted in native root state;
large inline service responses are not duplicated there. Tests exercise fresh
INIT/save/RUN objects, passive editing, dimension changes and error recovery.

## Build and validate

Use jmvtools on the target platform. The source pins metafor>=5.3-4 to the
recorded revision in DESCRIPTION; Pj is installed separately and is not Imports.
The repository is an example/guide, with optional Windows x64 and Linux x64 JMO
files in its root. It has no GitHub Releases channel, macOS packaging or Library
submission. Build caches, validation harnesses, logs and diagnostic sessions are
kept locally rather than included in the public source or JMO.

When adapting the example, compare numeric estimates with direct metafor calls;
exercise both Python modes, the three renderers and Html/Svg. Check native state
across INIT/save/fresh RUN, passive drafts, UTF-8 file loading, Run/Disable,
invalid inputs, error recovery and complete response-size limits. Verify desktop
OMV save/reopen/export as well: backend checks do not establish GUI acceptance.

## Meta-analysis diagnostics

Funnel displays use Pj's Chart.js helper: effect on the analysis scale against standard error, with the SE axis reversed. R supplies pooled reference and pseudo-confidence limits without adding tau², matching the default SE construction described in [metafor funnel](https://wviechtb.github.io/metafor/reference/funnel.html). This is descriptive and runs no asymmetry test. A chart's asymmetry alone does not establish publication bias.

Optional leave-one-out calls [metafor leave1out](https://wviechtb.github.io/metafor/reference/leave1out.html) for each selected model, retaining the same method and confidence level. R supplies the estimates, CI and heterogeneity; Pj supplies Table and D3 interval displays. At least three included studies are required by this preview. The source row/omitted-study identity is preserved.

D3 intervals are the default forest presentation. The same public API also offers Chart.js intervals and a Plotly forest, with explicit differences between generic intervals and a weighted diamond forest. Funnel and leave-one-out select suitable existing Pj helpers rather than introducing a second graphics engine. Their dimensions follow the module settings. Dichotomous, mean-difference and generic inputs share this workflow; further families can add supplier tabs after acceptance.

### Additional library examples

The [bilingual example guide](../examples/README.md) documents eight personal
scripts for all three input families. The additional weight-concentration example
uses Chart.js and Pj's existing `mzpjShowPaired` for linked FE/RE weight profiles
and percentage-point differences. This linkage belongs to that explorer; the
standard forest and Chart.js funnel remain independent; their linkage is deferred.
For Html the host composes public Chart/Html outputs into a Pj accordion with a
60–140% figure-size slider and Reset, reserving the complete scaled area. It
does not parse private renderer DOM, copy vendor libraries or change Pj. Native
Svg keeps Pj's original path without this Html wrapper. The heterogeneity map combines `mzpjMetaWeights` with a Plotly
heatmap: cell text shows weight percentages, while a muted blue/white/brown scale
shows percentage-point changes from tau² = 0. Actual tau² headers and compact
annotated rows make the comparison explicit. Source auditing combines immutable WideToLong with D3 aggregation.
They require no new renderer or Python dependency in the consumer module.
The library-example tests verify actual table values, weight totals, excluded
source rows, unchanged model estimates and graphics in both Python modes/Html/Svg.

Two further [Rust resampling examples](mzMp_rust_resampling.md) use Pj's installed
binary through the service: mean/median bootstrap and batch means for sign flips.
They report equivalent-Python checks and measured computation times without
adding a native build to MetaPj or presenting a dedicated Rust permutation API.

### Aggregate transport size

The installed jamovi 28.18 engine receiver has a 4 MiB message limit. Checking
each Pj service result independently does not bound their sum plus native tables,
options and state. MetaPj's `serialize()` guard measures the actual protobuf
response, with 128 KiB reserved for the transport envelope. It also protects
pre-fix saved results before `.run()`. The inactive Html/Svg forest is cleared
first, avoiding duplicate resources after format changes. Oversized optional output is cleared,
its cache key invalidated and an explicit message sent while statistical tables
remain. The rejected signature is remembered so unchanged callbacks do not retry
it; explicit Run or a context/renderer change allows a new attempt.
Larger standard output/cache has further bounded fallbacks. Original
user code/data and model settings are not rewritten. Tests must serialize the
combined host analysis, not only inspect returned API items.

Two inline Plotly figures can cross the limit. Use a D3/Chart standard forest
with the supplied Plotly heterogeneity map. Public resource-sharing support
would be a separate Pj API enhancement; consumers do not parse its private HTML
or copy vendor assets to work around the transport limit.

### Cached tables and native invalidation

MetaPj manages table validity through its input/render/script signatures, so native tables explicitly use `clearWith=character()` (YAML `clearWith: []`). Apply this both when creating a dynamic Table and when rebuilding its schema during state loading. The default `clearWith="*"` clears cells on unrelated options such as Disable or Html/Svg, while a cache hit may skip Python and leave those cells empty. Tests must check numeric cell values and their serialized protocol fields, not just row counts. Cache schema2 refreshes pre-fix saved results once. Personal-script keys also include selected source data, including rows excluded from the model.

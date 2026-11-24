# Personal extension examples / Esempi di estensione personale

## Italiano

Aprire un esempio dalla Data Library di MetaPj e assegnare le variabili nella
scheda Dicotomica, Differenze tra medie oppure Generic effect sizes. Espandere Python extension,
usare **Script > Load**, scegliere **un solo file .py**, quindi **Python > Run**.
Load aggiorna soltanto la bozza; Disable disattiva l'estensione conservandola.
Gli otto esempi funzionano con tutte e tre le famiglie e i due Python. Html offre
interazioni; Svg è una rappresentazione statica. L'interazione dei grafici
non modifica stime, dati o modelli. Non serve installare pacchetti Python aggiuntivi.

| File `.py` | Scopo e helper Pj |
|---|---|
| `mzMetaPj_extension_demo` | Rapporto, precisione e confronto dei modelli: Table, D3 scatter e intervalli |
| `mzMetaPj_input_explorer` | Colonne originali selezionate: D3 scatter e mapping semantico delle variabili |
| `mzMetaPj_weight_sensitivity` | Pesi per valori espliciti di tau²: `mzpjMetaWeights` e Table |
| `mzMetaPj_weight_concentration` | Curve cumulative Chart.js, confronto FE–RE con due pannelli D3 collegati e tabelle |
| `mzMetaPj_heterogeneity_map` | Mappa dei pesi per scenari tau²: Plotly Heatmap e `mzpjMetaWeights` |
| `mzMetaPj_source_audit` | Dati mancanti e tracciabilità: `mzpjWideToLong`, D3 Bar e Table |
| `mzMetaPj_rust_bootstrap` | Bootstrap nativo di media/mediana degli effetti di studio, controllo Python e tempi |
| `mzMetaPj_rust_permutation` | Cambi di segno esatti/Monte Carlo, kernel batch Rust e confronto dei tempi |

I due esempi Rust hanno una [guida ITA/ENG dedicata](../docs/mzMp_rust_resampling.md),
con ipotesi, formule, parametri di carico e interpretazione del benchmark.
Usano la libreria binaria già fornita da Pj: non occorre reinstallare MetaPj
o ricompilare Rust per caricare questi script.

Per la scheda generica usare l'esempio **Generic effects — BCG precomputed log RR**,
scala Log ratio, yi e vi/SE/CI come descritto nella [guida dedicata](../docs/mzMp_generic_effects.md).
Ricaricare gli script aggiornati quando si passa alla nuova scheda: il modulo
non riscrive automaticamente il codice personale già salvato nell'analisi.

**Concentrazione dei pesi.** Modificare `TOP_N` per il riepilogo dei primi N studi.
Ogni modello ordina i propri studi per peso decrescente: uno stesso rango può
identificare studi diversi. In Html la legenda Chart permette di nascondere una
curva; il puntatore mostra rango e percentuale cumulata. La tabella mantiene
l'identità dello studio. `1 / somma((peso/100)^2)` descrive la concentrazione,
non è una numerosità di partecipanti né una diagnosi d'influenza.

Con `SHOW_PAIRED=True` e i due modelli selezionati, lo stesso esempio aggiunge
`mzpjShowPaired`: a sinistra i pesi FE/RE di ciascuno studio, a destra la differenza
RE−FE in punti percentuali. Click o Invio su un profilo/punto evidenziano lo stesso
studio nei due pannelli; un rettangolo sul pannello delle differenze seleziona
più studi. Clear selection ripristina la vista. Nel controllo Pj «Selected subjects
only», subjects indica qui gli studi. Slider e Reset gestiscono le dimensioni e
la vista. SVG conserva la rappresentazione statica. Con un solo modello resta
disponibile la curva cumulata e un messaggio spiega come attivare il confronto.
La tabella mantiene tutti gli studi, anche durante una selezione. Non è un test
per dati appaiati: i due valori sono pesi degli stessi studi sotto due modelli.

**Copertura delle capacità Pj.** Gli otto file sono esempi adattabili, non otto
renderer distinti. Il demo copre testo/tabelle/scatter/intervalli; l'esploratore
legge le colonne sorgenti; sensibilità e mappa riusano i pesi a varianza inversa;
concentrazione copre Chart e selezione D3 fra pannelli; audit mostra reshape e
aggregazione; i due esempi Rust coprono bootstrap e calcolo batch con confronto
Python. Si riusano solo helper pubblici del Pj installato, senza modificare Pj.
Le selezioni del confronto FE–RE collegano **i suoi due pannelli**: non il forest
e il funnel standard. Quest'ultimo usa Chart.js tramite Pj, con tooltip e, nella
nuova build di MetaPj, un accordion e uno slider delle dimensioni (60–140%, Reset).
MetaPj compone l'output Html pubblico senza interpretare il DOM privato del renderer.
Non c'è selezione condivisa forest–funnel: l'autore ne ha rimandato lo sviluppo.

**Mappa tau².** Modificare `MULTIPLIERS` e premere Run. Per questo script scegliere **D3 intervals** o
**Chart.js intervals** come Graphics engine del forest standard: due risultati
Plotly inline possono superare il limite di 4 MiB del collegamento motore jamovi.
MetaPj controlla il totale e mostra un errore conservando le tabelle, senza
lasciare l'applicazione in attesa. La heatmap rimane Plotly. Il riferimento è il tau²
REML positivo, se disponibile; altrimenti la mediana delle varianze campionarie.
Le intestazioni riportano i tau² effettivi e la tabella dichiara la base usata.
Ogni cella mostra il peso percentuale, anche oltre 20 studi; ciascuna colonna
somma a 100% prima dell'arrotondamento. Il colore indica invece la variazione
in **punti percentuali rispetto a tau² = 0**: blu per una diminuzione, marrone
tenue per un aumento, quasi bianco per nessun cambiamento. La scala è simmetrica.
Sono ipotesi per i pesi `1/(vi+tau²)`, senza ristimare effetti aggregati o intervalli
e senza valutare qualità o influenza degli studi. In Html il puntatore mostra
nome completo, riga sorgente, tau², peso e variazione. Gli assi restano fissi;
il controllo dimensioni Pj cambia l'intera figura. `ROW_HEIGHT` regola lo spazio
per studio (19 px iniziali, da 16 a 30). Nomi lunghi vengono abbreviati nella
mappa e mantenuti completi nel tooltip; etichette duplicate includono la riga sorgente.

**Audit sorgente.** Conta valori mancanti/non finiti per ruolo numerico richiesto,
anche nelle righe escluse dall'analisi. Il grafico mostra i conteggi finiti per
ruolo; la tabella riporta anche i mancanti. Valori finiti non sono necessariamente validi:
il controllo non sostituisce le regole di MetaPj/metafor su conteggi, N o SD.
Le trasformazioni producono copie. `Source row` indica la posizione nel frame R
fornito al modulo, non garantisce il numero globale del dataset dopo filtri.

## English

Open a MetaPj Data Library example and assign variables in Dichotomous,
Mean differences or Generic effect sizes. Expand Python extension, choose **Script > Load**, select
**one .py file**, then **Python > Run**. Load only updates the draft; Disable
retains it. All eight scripts support all three families, either Python and Html/Svg.
Html is interactive; Svg is static. Graphics interactions do not change source
data, estimates or model settings. No extra Python packages are required.

The table above lists the filenames and Pj helpers. The three additional examples:

- **Weight concentration:** edit `TOP_N` for the summary. Chart.js displays
  cumulative weight against descending weight rank, independently for each model.
  The same rank can identify different studies; the accompanying table preserves
  identity. Html legend clicks toggle curves and hovering shows cumulative values.
  `1 / sum((weight/100)^2)` measures concentration, not participant sample size
  or statistical influence.
  With `SHOW_PAIRED=True` and both models selected, the same script calls
  `mzpjShowPaired`: FE/RE study-weight profiles on the left, RE−FE percentage-point
  differences on the right. Click or Enter links the same study across these two
  panels; rectangle brushing selects multiple difference points. Clear selection
  restores the view. Pj's existing “Selected subjects only” control refers to studies
  here. The slider changes figure size; SVG is static. With a single model the
  cumulative curve remains available and a note explains the paired requirement.
  The table always retains all included studies. This is a descriptive comparison
  of model weights, not a paired-samples test.
- **Heterogeneity map:** edit `MULTIPLIERS` to compare weights at different tau².
  First choose D3 intervals or Chart.js intervals for the standard forest. Two
  inline Plotly results can exceed jamovi's 4 MiB engine-message limit. MetaPj
  checks the aggregate and retains valid tables with an explicit error; the
  heatmap itself remains Plotly.
  A positive fitted REML tau² is the reference; otherwise median sampling variance
  is used. Headers show the actual tau² values and the assumptions table states
  the basis. Every cell displays its weight (%), including above 20 studies;
  full-precision columns sum to 100%. Colour represents a different quantity:
  **percentage-point change from tau² = 0**, on a symmetric scale. Muted blue
  means a decrease, warm brown an increase and near-white no change. These are
  user-defined weighting scenarios, not fitted pooled estimates, confidence
  intervals or assessments of study quality/influence. Html hovering shows the
  full study name, source row, tau², weight and change. Axes remain fixed; Pj's
  figure-size control resizes the complete figure. `ROW_HEIGHT` sets space per
  study (default 19 px, allowed 16–30). Long labels are shortened on the map,
  preserved in hover; duplicate labels include their source row.
- **Source audit:** Pj reshapes copies of missing-value flags to long format and
  D3 aggregates finite-value counts by required input role; the table also lists missing counts.
  Finite counts do not replace validation of event counts, sample sizes or SDs.
  Source rows include those excluded from the model. `Source row` is the 1-based
  position in the supplied R frame, not a guaranteed global row number after filters.

Two Rust examples add native mean/median bootstrap and exact/Monte Carlo sign
flips using Rust batch means, with matched Python comparisons and measured times.
See the [resampling guide](../docs/mzMp_rust_resampling.md) for assumptions,
formulas and workload controls. They use Pj's existing binary: no module
reinstallation or native rebuild is required for these example-only additions.

Generic inputs use the **BCG precomputed log RR** example with yi and variance,
SE or normal-CI columns. See the [generic-input guide](../docs/mzMp_generic_effects.md).
Reload the updated scripts when using this tab: saved personal code is never
rewritten automatically by the module.

R/metafor remains responsible for fitting. Ratio effects use the log analysis
scale where indicated, and tau² has squared analysis-scale units. The scripts
adapt to semantic roles through `context['inputs']`, so dataset column names
do not need to match the supplied examples.

**Pj capability coverage.** The eight adaptable scripts demonstrate text/tables,
scatter and intervals; selected source-column access; inverse-variance scenario
weights; Chart.js visibility and D3 linked-panel selection; reshape/aggregation;
and native bootstrap/batch statistics with matched Python comparisons. They use
installed public Pj helpers without changing Pj. The FE–RE comparison links only
its own two panels, not the standard forest and funnel. The standard Chart.js
funnel uses Pj Chart.js tooltips and, in the updated MetaPj build, an accordion
with a figure-size slider (60–140%, Reset). MetaPj composes the public Html output
without parsing the renderer's private DOM. Shared forest–funnel selection has
been deferred by the maintainer.

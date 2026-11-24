# Rust resampling examples / Esempi di ricampionamento Rust

## Italiano

Caricare un solo script da `MetaPj/examples` con **Script > Load**, poi **Python > Run**.
Funzionano con Dicotomica (RR, OR, RD), Differenze tra medie (MD, SMD) e
Generic effect sizes (yi con varianza/SE/CI),
usando gli effetti degli studi inclusi in `context['studies']`. Supportano i due
Python e Html/Svg. Per i generici usare la [guida alle scale e agli input](mzMp_generic_effects.md).
Non richiedono pacchetti Python aggiuntivi: il servizio Pj
fornisce il binario `pj_stats_rust` già distribuito. Non occorre ricompilarlo.

Sono esempi di calcolo e ricampionamento a livello di **studio**, non procedure
su singoli pazienti. Ogni studio ha lo stesso peso nelle statistiche qui definite.
Non modificano i dati, non sostituiscono le stime FE/RE e non ristimano metafor.
Per RR/OR lavorano su `yi = log(RR/OR)`, quindi lo zero corrisponde a rapporto 1;
per RD/MD/SMD la scala è quella dell'effetto selezionato. Il livello degli
intervalli bootstrap segue il livello di confidenza scelto in MetaPj.

### `mzMetaPj_rust_bootstrap.py`

- `REPLICATES = [1000, 10000]`: confronta due dimensioni del calcolo.
- `BENCHMARK_REPEATS = 3`: mediana di tre misure dei tempi, non triplicazione
  dei ricampionamenti utilizzati per l'intervallo.
- `COMPARE_PYTHON = True`: controlla l'accordo con una versione Python equivalente;
  impostare False per provare carichi nativi maggiori senza il confronto più lento.
- `SEED`: riproducibilità, a parità di dati e versione del backend.

Il bootstrap estrae k effetti con reinserimento dai k studi, calcolando media
non ponderata e mediana. Ogni chiamata nativa a `bootstrap_statistica` produce
stima, media bootstrap, bias, SE e intervallo percentile. L'intervallo presentato
usa il numero maggiore di repliche richiesto. Gli estremi sono i quantili
alpha/2 e 1-alpha/2 delle repliche, con interpolazione lineare; non BCa/studentizzati.

La versione Python usa lo stesso generatore SplitMix64, gli stessi indici estratti,
le stesse statistiche e gli stessi quantili. Lo script controlla numericamente
l'accordo dei risultati prima di mostrare il confronto dei tempi. Le due
implementazioni eseguono davvero il ricampionamento e costruiscono gli intervalli;
non si confronta il costo di una singola media con un'intera procedura nativa.

L'interpretazione di questi intervalli richiede studi indipendenti rappresentativi
di una popolazione di studi per la statistica non ponderata. Non propagano
separatamente l'errore campionario interno a ogni studio, non sono un bootstrap
del modello RE/FE e, con pochi studi, possono essere discreti o poco affidabili.

### `mzMetaPj_rust_permutation.py`

La libreria attuale **non espone un test di permutazione dedicato**. Lo script
costruisce in Python i cambi di segno e usa `statistiche_righe` in Rust per
calcolare in batch le medie. Il riferimento Python riceve esattamente gli stessi
segni. Si confrontano sia il kernel statistico sia una stima della pipeline
che comprende generazione dei segni e conteggio dei valori estremi.

- `PERMUTATIONS = [999, 9999]`: numero richiesto di configurazioni per confronto.
- `BATCH_SIZE = 512`: limita la matrice temporanea a k × batch valori;
  non costruisce una matrice k × tutte le permutazioni.
- `EXACT_MAX_STUDIES = 14`: se k è piccolo e B >= 2^k, enumera tutti i segni.
  Con i 13 studi BCG, 9999 richieste diventano 8192 configurazioni esatte.
  Altrimenti usa cambi di segno casuali indipendenti con rimpiazzo.
- `BENCHMARK_REPEATS` e `SEED`: tempi ripetuti e riproducibilità.

La statistica bilaterale è `abs(mean(yi))`. Per enumerazione esatta:
`p = configurazioni almeno altrettanto estreme / 2^k`. Per Monte Carlo:
`p = (estremi + 1)/(B + 1)`, senza p Monte Carlo pari a zero. Una piccola
tolleranza gestisce i pareggi numerici; la tabella dichiara metodo e numero
effettivo di configurazioni. L'errore standard Monte Carlo approssimato è
`sqrt(p*(1-p)/B)`; non si riporta per l'enumerazione esatta.

La validità richiede **invarianza al cambio di segno sotto l'ipotesi nulla**,
ad esempio effetti indipendenti con distribuzioni simmetriche intorno a zero.
La sola media nulla non basta. Questo requisito non è garantito dai dati
dicotomici, da una differenza tra medie o dalla presenza di eterogeneità.
Lo script non ricostruisce una randomizzazione dei trattamenti dai dati aggregati
e non deve essere interpretato automaticamente come test clinico alternativo.

### Leggere i tempi

Le tabelle mostrano la versione Rust/Python, seed, dimensione del problema e
tempi in millisecondi. Import, avvio del processo Pj, fitting R e grafici sono
esclusi. Nel bootstrap sono inclusi generatore, ricampionamento, statistiche,
ordinamento, intervalli e passaggio Python/Rust. Nelle permutazioni i tempi del
kernel includono la conversione degli argomenti; la generazione dei segni rimane
Python e viene aggiunta a entrambe le pipeline. Per ciascun batch si usa la
mediana dei tempi, poi si sommano i batch. La verifica dell'accordo è fuori dal timer.

Un rapporto Python/Rust superiore a 1 indica Rust più veloce **in quella prova**;
inferiore a 1 indica il contrario. Con pochi studi l'interoperabilità e Python
possono dominare il costo. Non si dichiara un'accelerazione garantita né un
parallelismo automatico. I limiti di carico degli esempi evitano prove eccessive
nella finestra del servizio; ridurre repliche/ripetizioni/batch se richiesto.
La memoria della matrice dei segni è limitata dal batch; lo script conserva
comunque B statistiche per l'istogramma. Non misura il picco di memoria.

## English

Load one file from `MetaPj/examples`, then Run. All three families, either Python and
Html/Svg are supported. Installed Pj supplies the unchanged native Rust library.
These are equal-study-weight summaries of included analysis effects, not
inverse-variance FE/RE refits or patient-level procedures. RR/OR use log effects;
RD/MD/SMD retain their analysis scale. Original data and metafor models are unchanged.

**Bootstrap:** `REPLICATES` controls workload sizes; `BENCHMARK_REPEATS` controls
timing repetitions; `COMPARE_PYTHON=False` skips the slower reference; `SEED`
controls reproducibility. Native `bootstrap_statistica` resamples k studies with
replacement for the unweighted mean and median. Results include bias, SE and
percentile intervals at the module's confidence level, using the largest requested B.
The reference matches SplitMix64 draws, statistics and linearly interpolated
quantiles and is checked numerically. This does not refit a meta-analysis model
or separately resample within-study uncertainty. Independent studies representative
of the study population are assumed; small-k percentile intervals can be unreliable.

**Sign flips:** Python generates sign patterns and Rust's batch row-summary
kernel computes means. There is no dedicated native permutation-test API.
The Python reference receives identical patterns. If k <= `EXACT_MAX_STUDIES`
and requested B >= 2^k, all signs are enumerated; otherwise independent random
signs are generated with replacement. Test statistic = absolute unweighted mean.
Exact p = extreme count / 2^k; Monte Carlo p = (extreme count+1)/(B+1), using
a numerical tie tolerance. Approximate MC SE = sqrt(p*(1-p)/B), omitted for exact tests.
Validity requires joint sign invariance under the null, such as independent
effects symmetric about zero; a zero mean alone is insufficient. Neither
dichotomous nor mean-difference inputs automatically guarantee this assumption.
This is not a treatment-arm randomization test reconstructed from aggregate data.

**Benchmark interpretation:** warm-up is excluded. Bootstrap times include
resampling, summary statistics, sorting, CI and interop. Sign-flip kernel times
include interop; shared generation/counting time is added to both pipeline
estimates. Within-batch median times are summed. Imports, process startup,
R fitting, verification and graphics are excluded. Repeated timings do not
increase inferential B. Reported Python/Rust ratios may be above or below 1;
no universal speedup or automatic parallelism is claimed. Batching bounds the
temporary sign matrix, while B statistics remain stored for the histogram;
peak memory is not measured. Workload limits protect the interactive preview.

## References / Riferimenti

- [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html):
  resampling and percentile interval construction. SciPy is a methodological
  reference here, not a runtime dependency; its default interval is BCa, unlike this example.
- [SciPy permutation_test documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html):
  single-sample sign flips, exact enumeration, Monte Carlo adjustment and numerical
  ties. This example explicitly uses an absolute-mean two-sided statistic;
  it does not adopt SciPy's default doubled-tail convention.
- [Pj Rust guide](https://github.com/MAgojam/Pj/blob/main/docs/mzPj_rust.md) and the installed backend's
  `bootstrap_statistica` / `statistiche_righe` contracts. Source development and
  native compilation are separate from these consumer scripts.

# Generic effect sizes / Effect size generici

## Italiano

La terza scheda **Generic effect sizes** analizza effetti già calcolati, come
l'ingresso generico di Metafora. Una riga deve rappresentare uno studio/effetto
indipendente; tutti gli effetti devono avere definizione, direzione e scala
compatibili. Non mescolare, ad esempio, differenze in unità diverse o RR grezzi
con log RR. Non è un modello multivariato o per effetti dipendenti.

| Controllo | Colonne da assegnare | Operazione |
|---|---|---|
| Study label | Etichetta facoltativa | Conservata nei grafici e nelle tabelle |
| Effect size | Stima sulla scala di analisi | `yi`, senza trasformazione automatica |
| Sampling variance | Colonna della varianza | `vi` utilizzata direttamente |
| Standard error | Colonna dell'errore standard, non SD | `vi = SE²` |
| Normal-based confidence interval | Limite inferiore e superiore | `SE ≈ (upper-lower)/(2*z)`, `vi = SE²` |

Per i CI, `z = qnorm((1 + livello_input/100)/2)`. **Input CI level** descrive
gli intervalli forniti: non è il livello degli intervalli da produrre, impostato
separatamente sotto Models. Si accettano CI normali di tipo Wald sulla stessa
scala di `yi`, approssimativamente simmetrici attorno alla stima. Sono consentiti
piccoli scostamenti dovuti ad arrotondamento (1% della larghezza, più tolleranza
numerica). CI asimmetrici, esatti, di profilo o t con gradi di libertà ignoti non
devono essere convertiti con questa formula; fornire varianza o SE appropriati.

Il target Sampling variance / standard error è usato solo nella modalità
Varianza/SE. I target dei limiti e il livello CI sono usati solo in modalità CI.
I controlli non pertinenti sono disabilitati e le loro selezioni non entrano
nel calcolo corrente. Il codice non indovina il tipo di una colonna dai valori.

### Scala e visualizzazione

- **Generic effect — supplied scale**: analisi e visualizzazione nella scala
  fornita; riferimento nullo 0. Ad esempio MD, SMD o un altro effetto additivo
  già definito. Una trasformazione di Fisher rimane su quella scala: non viene
  applicato automaticamente tanh o un altro back-transform.
- **Log ratio — display exp(effect)**: fornire effetti e limiti CI già logaritmici
  (per esempio log RR, log OR, log HR). R analizza questi valori e le varianze
  corrispondenti. Solo stime ed estremi di intervallo vengono esponenziati per
  la visualizzazione. Il nullo passa da 0 a 1. SE, z, tau², funnel, D3 intervals
  e ricampionamenti continuano a usare la scala di analisi logaritmica.

Per un rapporto R con CI [L,U] grezzi, preparare **prima** log(R), log(L), log(U)
e il SE/varianza sulla scala log, poi assegnare le colonne. Se si possiede una
varianza sulla scala grezza del rapporto, non basta fare log(varianza).
La scelta Log ratio non trasforma automaticamente i dati in ingresso.

### Esempio pronto nella Data Library

Aprire **Generic effects — BCG precomputed log RR**, aggiungere MetaPj e scegliere:

1. Generic effect sizes, Effect scale = **Log ratio — display exp(effect)**.
2. Study label = `study`, Effect size = `yi`.
3. Scegliere **una** modalità: varianza con `vi`; SE con `sei`; oppure CI con
   `ci_lower` / `ci_upper` e Input CI level = **95**.
4. Tenere FE e RE selezionati e confrontare le tre modalità: stime, pesi e
   diagnostiche devono coincidere a meno dell'arrotondamento numerico.

Gli effetti derivano da metadat::dat.bcg mediante metafor::escalc (RR, correzione
0,5 only0 e drop00); i limiti sono CI normali al 95% sulla scala log. Le tre
colonne d'incertezza descrivono gli stessi studi, non tre dataset indipendenti.
L'OMV contiene dati, senza analisi o codice salvati. Come per gli altri esempi,
la Data Library originale non viene sovrascritta dal salvataggio di modifiche.

Valori mancanti/non finiti nelle sole colonne attive escludono la relativa riga,
preservando `source_row`. Varianze/SE finite non positive, overflow, CI non ordinati,
non contenenti la stima o marcatamente asimmetrici producono un errore esplicito.
Servono almeno due effetti con varianze finite positive; gli esempi Rust ne richiedono tre.

### Script personali e API

Gli otto esempi sono adattati anche alla nuova scheda. Ricaricare il file aggiornato
con Load e Run: uno script già salvato nell'OMV rimane codice dell'utente e non
viene riscritto automaticamente dal modulo.

`context['analysis']['kind'] == 'generic'`; `input_type` vale `variance`, `se` o `ci`.
`input_ci_level` è presente in modalità CI; `input_note` descrive la conversione.
Il mapping `inputs` contiene `yi` e `vi`, oppure `yi` e `sei`, oppure
`yi`, `ciLower`, `ciUpper` (oltre allo studio facoltativo). Questi ruoli puntano ai
nomi delle colonne sorgenti selezionate. I nomi non devono corrispondere a quelli
dell'esempio. `context['studies']` contiene sempre `yi` e la varianza `vi` finale,
mentre `data` conserva le colonne originali selezionate, comprese le righe escluse.

Il fitting rimane in R/metafor: FE a varianza inversa e RE-REML con inferenza z,
CI, PI RE, eterogeneità, funnel e leave-one-out già descritti dal modulo. Pj
fornisce gli stessi helper e renderer, senza nuove librerie o compilazioni Rust.

## English

The third input tab, **Generic effect sizes**, accepts precomputed independent
effect estimates on a consistent analysis scale. Select an effect column and
either sampling variance, standard error, or normal-based Wald CI limits.
Variance is used directly; SE is squared; CI width yields
`vi = ((upper-lower)/(2*qnorm((1+input_level/100)/2)))²`.
Input CI level describes the supplied intervals and is separate from the output
confidence level. CI limits must be ordered, contain the estimate and be
approximately symmetric on its analysis scale (1% width allowance plus numerical
tolerance for rounding). Supply appropriate variance/SE for asymmetric, profile,
exact or t-based intervals instead of assuming this normal reconstruction applies.

**Supplied scale** retains effects and null 0. **Log ratio** expects already
logged effects/CI limits and matching log-scale variances; only displayed
estimates/bounds are exponentiated, with null 1. SE, z, tau², funnels, D3 interval
axes and resampling remain on the analysis scale. No automatic log transform of
input data, raw variances, Fisher-z back-transform or measure identification occurs.

Use **Generic effects — BCG precomputed log RR** from the Data Library: map
`study` and `yi`, select Log ratio, then map `vi` for variance, `sei` for SE, or
`ci_lower` / `ci_upper` at input CI level 95. All three describe the same effects
and produce matching results. The dataset derives from metadat::dat.bcg via
metafor's RR calculation with only0 correction and drop00. It contains data only.

Only active required columns determine inclusion. Missing/nonfinite inputs are
excluded with source-row alignment preserved; finite nonpositive variance/SE,
overflow and invalid/non-Wald CI inputs are explicit errors. At least two usable
effects are needed; the Rust examples require three. Do not mix incompatible
effect definitions, units, directions or dependent effects.

All eight supplied scripts support this tab; reload their updated files before
Run because saved user code is never rewritten automatically. `kind='generic'`,
`input_type`, `input_ci_level` and `input_note` describe the input contract.
`inputs` maps yi/vi, yi/sei or yi/ciLower/ciUpper to actual source columns.
Included studies always carry the computed yi/vi; the separate `data` frame
retains original selected columns before exclusions. Existing FE/RE, prediction
intervals, funnel/leave-one-out and public Pj presentation services are reused.

## Reference / Riferimento

[metafor rma.uni — specifying effect estimates, sampling variances or standard errors](https://wviechtb.github.io/metafor/reference/rma.uni.html).
MetaPj's CI-width conversion is an explicit normal-Wald approximation performed
before fitting; output inference follows the selected FE/RE settings described above.

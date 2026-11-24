# MetaPj

**Esempio funzionante e guida al codice per gli sviluppatori di moduli jamovi.**
[Read in English](README.md).

MetaPj mostra come un modulo dedicato possa usare le capacità Python di **Pj
tramite la sua API pubblica**, mantenendo una propria interfaccia, i propri dati
e i propri metodi statistici. Lo abbiamo preparato per offrire agli sviluppatori
un riferimento concreto da leggere, provare e adattare: non occorre riscrivere
in ogni modulo la ricerca e l'esecuzione di Python, i controlli del processo,
gli helper o le risorse grafiche già disponibili in Pj.

Il caso dimostrativo è una meta-analisi di studi indipendenti con **tre tipi di
ingresso: dati dicotomici, differenze tra medie ed effetti generici**. Per ciascuno
si possono scegliere i modelli FE e RE. Le tre schede rappresentano quindi tre
tipi di dati/analisi; FE e RE sono i modelli statistici disponibili.

Questo repository è un **esempio/guida per sviluppatori**, senza un canale GitHub
Releases. Nella cartella principale sono disponibili due JMO facoltativi per
provare l'esempio senza compilarlo. La versione del pacchetto dimostrativo è 1.1.0.

## Chi fa cosa

| MetaPj | Pj installato separatamente |
| --- | --- |
| Interfaccia nativa, assegnazione e validazione delle variabili | Ricerca dell'interprete Python embedded o di sistema |
| Calcolo R/metafor di effetti, varianze, FE/RE e diagnostica | Esecuzione Python, timeout, cancellazione e diagnostica del servizio |
| Contesto esplicito, cache e contenitori Results | Helper Python, risorse D3/Chart.js/Plotly e libreria Python–Rust |
| Caricamento di uno script personale alla volta e mapping degli output | Risultati strutturati Table/Html/Svg da restituire al modulo chiamante |

MetaPj non apre un editor Pj, non incorpora una copia di Pj e non introduce un
secondo motore grafico. I calcoli statistici standard restano in R/metafor.

## Scaricare e installare l'esempio

| Sistema | File nella cartella principale |
| --- | --- |
| Windows x64 | [MetaPj_1.1.0_win64.jmo](MetaPj_1.1.0_win64.jmo) |
| Linux x64 | [MetaPj_1.1.0_linux.jmo](MetaPj_1.1.0_linux.jmo) |

1. Usare jamovi **28.18.0 o successivo**, con uno snapshot R compatibile, e
   installare **Pj 1.8.0 o successivo** per il proprio sistema.
   I pacchetti Pj sono disponibili nel [repository Pj](https://github.com/MAgojam/Pj/releases).
2. Scaricare il vero file `.jmo` MetaPj, non la pagina HTML che lo descrive.
3. Installarlo da **Sideload** nel menu dei moduli jamovi e riavviare jamovi.

Il JMO contiene le dipendenze R necessarie a MetaPj; il modulo Metafora non è
richiesto. Non servono il pacchetto Python plotly, reticulate, server web o un
browser esterno. Pj deve invece essere installato separatamente: l'esempio lo
cerca attraverso il servizio pubblico e segnala se manca o è troppo vecchio.
Le tabelle statistiche R valide rimangono disponibili se il servizio Python fallisce.

I due JMO accompagnano il codice dell'esempio: non costituiscono un canale di
release o aggiornamento automatico e MetaPj non è una richiesta alla Libreria jamovi.

## Provare i tre tipi di meta-analisi

Aprire un dataset dalla **Data Library di MetaPj**, aggiungere una nuova analisi
MetaPj e scegliere la scheda corrispondente. Una riga deve rappresentare uno
studio/effetto indipendente. Le variabili dei riepiloghi richiesti sono numeriche;
`study` è un'etichetta facoltativa dello studio.

| Esempio Data Library / scheda | Variabili da assegnare | Misure |
| --- | --- | --- |
| **BCG vaccine — dichotomous outcomes** / Dichotomous | Gruppo 1: `tpos` eventi, `tneg` non-eventi. Gruppo 2: `cpos` eventi, `cneg` non-eventi. Etichetta `study`. | RR, OR, RD |
| **Mean differences — Normand 1999** / Mean differences | `n1i`, `m1i`, `sd1i` e `n2i`, `m2i`, `sd2i`; etichetta `study`. | MD, SMD con correzione di Hedges |
| **Generic effects — BCG precomputed log RR** / Generic effect sizes | `yi` e una scelta tra `vi` (varianza), `sei` (SE), oppure `ci_lower` + `ci_upper` (CI normali 95%); etichetta `study`. Selezionare **Log ratio** per questo dataset. | Scala fornita oppure rapporti già trasformati in log |

Nei dati dicotomici si inseriscono **non-eventi, non i totali**, nei campi `bi` e
`di`. Nelle differenze tra medie si inseriscono deviazioni standard, non SE.
Per gli effetti generici scegliere esplicitamente il tipo di incertezza:
varianze e SE devono essere positivi; gli intervalli devono essere circa centrati
e simmetrici secondo l'approssimazione normale, sulla stessa scala di `yi`.
Il livello CI in ingresso è distinto dal livello degli intervalli richiesti in
uscita. Per rapporti logaritmici fornire effetti e limiti già in log; MetaPj non
trasforma automaticamente rapporti grezzi. Vedere la
[guida agli ingressi generici](docs/mzMp_generic_effects.md).

Gli esempi derivano da `metadat::dat.bcg` e `metadat::dat.normand1999`; quello
generico contiene i log RR BCG già calcolati. Gli OMV contengono dati, non analisi
precompilate. Gli originali della Data Library restano immuni dalle modifiche:
salvando un esempio modificato, jamovi richiede un nuovo nome/percorso.

### Modelli e risultati standard

Attivare FE, RE o entrambi. FE è il modello a effetto comune con pesi a varianza
inversa; RE usa REML con inferenza z. RR/OR sono analizzati sulla scala logaritmica;
le tabelle degli effetti e dei relativi CI riportano la trasformazione richiesta,
mentre SE e z rimangono sulla scala di analisi. I pesi sommano a 100% separatamente
per modello. Sono disponibili intervalli di confidenza e PI RE; la diagnostica
leave-one-out richiede almeno tre studi e rifitta in R il modello selezionato.

Nei conteggi RR/OR si usa la correzione 0,5 nei soli studi con celle zero
(`only0`, `drop00`); RD non usa tale correzione. Mancanti/non finiti nei riepiloghi
attivi sono esclusi; valori finiti non validi producono errori espliciti.
Servono almeno due effetti utilizzabili con varianza campionaria positiva.
Studi dipendenti, modelli multilivello, sottogruppi e moderatori non fanno parte
di questo esempio.

### Grafici e interazioni disponibili

- **D3 intervals**, predefinito: helper Pj per intervalli degli studi e dei modelli,
  con marcatori uguali sulla scala di analisi; per log RR/OR il riferimento nullo è 0.
- **Plotly forest**: quadrati pesati, diamanti dei modelli, PI RE e asse logaritmico
  per i rapporti; usa dizionari Python e la risorsa Plotly.js di Pj, senza importare plotly.
- **Chart.js intervals**: serie di intervalli con righe numerate e legenda flottante;
  l'asse dei rapporti è logaritmico. Non coincide con la resa D3 o con il forest Plotly.
- **Funnel descrittivo**: effetto sulla scala di analisi contro SE, asse SE invertito
  e limiti pseudo-CI intorno a RE, oppure FE se RE non è selezionato. Non aggiunge
  tau² ai limiti, non è un PI e non esegue un test di asimmetria o una diagnosi automatica di bias.

In **Interactive HTML**, accordion e controlli dei grafici permettono le interazioni
del rispettivo helper. Il funnel ha un solo accordion con slider delle dimensioni
60–140%, percentuale e Reset; si ridimensiona anche l'area occupata. MetaPj compone
gli output pubblici Chart/Html, mantenendo il renderer in Pj. Il collegamento
forest–funnel è rinviato: non è disponibile nella versione dell'esempio.

In **Native SVG** non viene aggiunto zoom HTML; si usa il contenitore nativo jamovi.
D3 produce SVG vettoriale; Plotly e Chart incorporano una resa raster. Su alcune
installazioni Ubuntu il gancio nativo può essere in basso a sinistra e bloccato:
usare larghezza/altezza del modulo. Il consumer MetaPj supporta Table/Html/Svg e
output testuali; il flusso Image con cattura browser dell'editor Pj non è riprodotto qui.

## Caricare e provare gli otto script

Scaricare o clonare il repository (va bene anche il suo ZIP) per avere la
cartella `examples`. Il JMO installa modulo e dataset Data Library; i file
Python esterni si caricano dalla propria copia locale del repository.

Con il dataset assegnato e i modelli scelti:

1. Aprire **Python extension (optional)** e scegliere **Script > Load**.
2. Caricare **un file `.py` alla volta** dalla cartella `examples` (UTF-8, massimo 256 KiB).
3. Premere **Python > Run** per applicare la bozza. Load e modifica del testo sono passivi.
4. Usare Save per conservare lo script modificato oppure Disable per disattivarlo
   mantenendo la bozza. Codice applicato, nome e bozza sono salvati nell'analisi OMV.

| Script | Che cosa mostra / capacità Pj |
| --- | --- |
| [mzMetaPj_extension_demo.py](examples/mzMetaPj_extension_demo.py) | Legge il contesto R, crea testo/tabelle, scatter della precisione e intervalli dei modelli. |
| [mzMetaPj_input_explorer.py](examples/mzMetaPj_input_explorer.py) | Esplora con D3 le colonne sorgenti selezionate; si adatta ai tre tipi di ingresso. |
| [mzMetaPj_weight_sensitivity.py](examples/mzMetaPj_weight_sensitivity.py) | Ricalcola pesi per tau² espliciti con `mzpjMetaWeights`, senza stimare nuovi modelli. |
| [mzMetaPj_weight_concentration.py](examples/mzMetaPj_weight_concentration.py) | Curve cumulative Chart; con FE+RE usa `mzpjShowPaired` per collegare profili dei pesi e differenze, con selezione/brush/filtro/reset. |
| [mzMetaPj_heterogeneity_map.py](examples/mzMetaPj_heterogeneity_map.py) | Heatmap Plotly con pesi annotati e colori per variazioni in punti percentuali da tau²=0. |
| [mzMetaPj_source_audit.py](examples/mzMetaPj_source_audit.py) | Riuso di WideToLong, aggregazione D3, mancanti e identità delle righe incluse/escluse. |
| [mzMetaPj_rust_bootstrap.py](examples/mzMetaPj_rust_bootstrap.py) | Bootstrap nativo di media/mediana non ponderate degli effetti di studio, confronto Python equivalente e tempi. |
| [mzMetaPj_rust_permutation.py](examples/mzMetaPj_rust_permutation.py) | Cambi di segno esatti/Monte Carlo: Python genera i segni, Rust calcola medie batch; confronto numerico e tempi. |

Gli otto script si adattano a tutti e tre i tipi di ingresso, ai due Python e a
Html/Svg. Per il confronto appaiato dei pesi selezionare **entrambi FE e RE**;
con un solo modello rimane la curva cumulata e compare una spiegazione. Il
collegamento riguarda i due pannelli di quell'helper, non forest e funnel.
Le selezioni grafiche non cambiano i dati o i modelli R; la tabella mantiene tutti gli studi.

Per la heatmap scegliere prima **D3 intervals** oppure **Chart.js intervals**
nel forest standard. Più risultati Plotly inline possono superare il limite
aggregato di 4 MiB del motore: MetaPj controlla la risposta completa e segnala
output opzionali eccessivi, conservando le tabelle valide.

Gli esempi Rust usano il binario già fornito da Pj, senza ricompilarlo. Sono
ricampionamenti non ponderati a livello di studio e non bootstrap dei modelli
FE/RE o dei pazienti. Ipotesi e parametri sono nella
[guida al ricampionamento](docs/mzMp_rust_resampling.md).
La [guida degli esempi ITA/ENG](examples/README.md) descrive controlli e interpretazione.

Uno script definisce `mzRender(context)`; MetaPj lo passa a Pj e lo chiama:

```python
def mzRender(context):
    mzpjShowTable([
        {'Study': s['study'], 'Effect': s['yi'], 'Variance': s['vi']}
        for s in context['studies']], name='my_report', title='My study report')
```

`context` contiene risultati, mapping semantico e impostazioni; `data` espone
solo le colonne sorgenti selezionate, prima delle esclusioni del modello.
`context['studies']` contiene invece gli effetti inclusi. `source_row` è la
posizione nel frame R fornito, non necessariamente la riga globale dopo filtri.
Il codice applicato viene rivalutato quando cambia il contesto; gli errori
personali sono separati dai risultati standard. Python e HTML eseguono codice
con i normali permessi: l'API non è una sandbox per codice non fidato.

## Leggere e adattare il codice

| Percorso | Punto da studiare |
| --- | --- |
| [examples/minimal_consumer.R](examples/minimal_consumer.R) | Chiamata minima al servizio pubblico Pj. |
| [R/mzMp_statistics.R](R/mzMp_statistics.R) | Validazione e calcolo statistico R/metafor. |
| [R/mzMp_bridge.R](R/mzMp_bridge.R) | Individuazione Pj e mapping dei risultati strutturati. |
| [R/mzMp_analysis.R](R/mzMp_analysis.R) | Ciclo di vita, cache, risultati nativi ed estensione personale. |
| [R/mzMp_transport.R](R/mzMp_transport.R) | Budget aggregato e recupero da output eccessivi. |
| [inst/python/mzMp_present.py](inst/python/mzMp_present.py) | Presentazione con gli helper Pj esistenti. |
| `jamovi/` | Schede native, opzioni, Results e controlli Load/Save/Run/Disable. |
| `tools/` | Generazione delle dichiarazioni del modulo e dataset generico riproducibile. |

La [guida sviluppatore](docs/mzMp_developer_guide_it.md) spiega il contratto e
l'integrazione in un modulo R6: dati minimi, timeout, checkpoint del modulo,
propagazione del riavvio e soli tipi di output gestiti dall'host. Per compilare
una copia adattata, installare strumenti jamovi e dipendenze R compatibili,
aprire la cartella sorgente in R ed eseguire `source('compile.r')`.
`DESCRIPTION` registra le dipendenze e il riferimento metafor fissato.

Nel repository sono previsti soltanto sorgenti, documentazione, dataset/script
di esempio e i due JMO. Cartelle di build, test harness, schermate, sessioni
diagnostiche, log e appunti di lavoro restano locali. Non sono previsti workflow
di release o pubblicazione del modulo. Licenza GPL >=2; licenze e attribuzioni
delle dipendenze rimangono preservate.

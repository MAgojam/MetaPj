# MetaPj: usare i servizi Pj in un modulo specifico

Anteprima1.1.0, Pj>=1.8.0, API pubblica1, jamovi>=28.18.

## Compiti del modulo e del servizio

MetaPj possiede UI, selezione delle variabili, modelli R/metafor, contenitori e
stato dei risultati. Pj possiede individuazione/esecuzione Python, timeout,
checkpoint, helper e risorse grafiche. Il modulo usa solo mzPjServiceInfo e
mzPjRunPython esportate: non legge funzioni private, non copia librerie Pj e
non costruisce un altro editor/renderer. Il file R/mzMp_bridge.R mostra il
connettore riutilizzabile; examples/minimal_consumer.R mostra la chiamata minima.

Pj si installa separatamente. Mancanza/versione insufficiente e problemi del
Python selezionato producono messaggi; le tabelle R già valide restano visibili.
La condizione di riavvio jamovi viene propagata, non trasformata in errore utente.
Ogni chiamata API avvia un processo separato, con timeout60 secondi e checkpoint
proveniente dall’analisi chiamante. Il selettore Python del modulo non modifica
quello degli editor Pj/Pjp.

## Schede e dati richiesti

Una riga rappresenta uno studio/effetto indipendente. Le tre schede principali
sono Dicotomica (eventi/non-eventi nei due gruppi; RR, OR, RD) e Differenze tra
medie (N, media, SD per due gruppi indipendenti; MD, SMD di Hedges), più Generic
effect sizes (yi e varianza, SE oppure CI normali). La
[guida generica ITA/ENG](mzMp_generic_effects.md) descrive le conversioni e le scale.
Il nome dello studio è facoltativo. Dati appaiati, effetti dipendenti e modelli
multilivello non sono coperti. Altre famiglie potranno aggiungere nuove schede
supplier dopo l’accettazione di queste tre.

Data Library: BCG usa study,tpos,tneg,cpos,cneg; Normand1999 usa study,n1i,m1i,
sd1i,n2i,m2i,sd2i. Le provenienze sono nelle rispettive pagine metadat.
L'esempio generico BCG contiene study, yi, vi, sei, ci_lower, ci_upper già sulla
scala log RR; usare Log ratio e livello CI in ingresso 95. Le tre modalità
devono produrre risultati equivalenti. Il livello dei CI in uscita è separato.
Aprire il dataset e aggiungere una nuova analisi MetaPj. L’originale della Data
Library non viene sovrascritto: per salvare modifiche jamovi chiede un file nuovo.

R/metafor calcola escalc e modelli FE a varianza inversa o RE-REML, inferenza z.
RR/OR: analisi logaritmica, correzione0,5 solo negli studi con celle zero e drop00;
RD senza correzione. Righe incomplete o effetti/varianze non finiti sono esclusi;
input finiti non validi sono errori. Servono almeno due studi utilizzabili.
SE, z e tau² restano sulla scala di analisi; effetti e CI delle tabelle sono
riportati sulla scala di visualizzazione. PI soltanto per RE. I pesi sommano100%
separatamente per ogni modello selezionato.

## Presentazione tramite Pj

Il forest predefinito usa D3 tramite mzpjShowIntervals: è una vista di
intervalli forniti su scala di analisi, senza quadrati pesati/diamanti.
L'alternativa Plotly usa l'helper Pj con dizionari JSON: quadrati pesati degli
studi, diamanti dei modelli, PI RE e asse logaritmico per RR/OR. Non serve il
pacchetto Python plotly. Chart.js
usa il helper Pj per serie di intervalli con righe numerate nella stessa sequenza
della tabella. Le differenze sono dichiarate, senza attribuire inferenza al renderer.

Funnel descrittivo: il helper Chart.js di Pj riceve effetto sulla scala di analisi,
SE con asse invertito e limiti pseudo-CI calcolati in R attorno a RE (o FE se RE
non selezionato). Non include tau² nei limiti, non è un PI e non esegue un test
di asimmetria. L’asimmetria non determina da sola un bias di pubblicazione.
Metodo: https://wviechtb.github.io/metafor/reference/funnel.html

Leave-one-out facoltativo: metafor ripete il medesimo modello omettendo ogni
studio incluso. Pj visualizza tabella e intervalli; il riferimento è il risultato
con tutti gli studi. Servono almeno tre studi per questa funzione dell’esempio.
Metodo: https://wviechtb.github.io/metafor/reference/leave1out.html

Html mantiene interazione/accordion degli helper Pj; Svg è un contenitore nativo,
senza wrapper di zoom Html. Plotly/Chart Svg incorpora una resa raster; D3 è
vettoriale. Larghezza/altezza sono controlli del modulo e vengono passati all’API.
Il problema di salvataggio Svg di jamovi28.17 è storico; il minimo28.18 contiene
la correzione Core. Il nuovo modulo richiede comunque prova desktop OMV.
Il gancio nativo Linux può restare a sinistra e bloccato, anche in altri moduli:
per le dimensioni usare i controlli del modulo. Non è una correzione qui dichiarata.

## Un file Python personale alla volta

Load script carica un .py UTF-8 massimo256KiB nella bozza, senza eseguirlo e senza
sostituire il codice attivo. Run applica la bozza, la passa all’API Pj e chiama
mzRender(context). Save script salva il testo modificato; Disable conserva la
bozza. Nome file, codice attivo e bozza passiva sono conservati nell’OMV. Il nome
del file compare nei dettagli degli errori. Un errore personale non elimina i
risultati standard; un nuovo Run corretto consente il recupero.

Il codice ha i permessi del Python scelto; jamovi gestisce l’autorizzazione del
codice salvato. Non c’è un’interfaccia Python che cambi automaticamente opzioni,
modelli R o dataset jamovi. Il consumo API non apre un editor Pj.

## Contratto accessibile allo script

- context['analysis']: famiglia, misura, rapporto, livelloCI, k, totale/esclusi, scala.
- context['studies']: solo effetti inclusi; study,source_row,yi,vi,estimate,lower,upper,
  weight_FE e weight_RE. yi/vi sulla scala di analisi; peso non selezionato=None.
- context['models']: risultati FE/RE, stima sulla scala di analisi e display, SE/z/p,
  CI/PI, tau²,I²,H²,Q,gradi di libertà e p di Q.
- context['inputs']: ruoli semantici associati ai nomi delle colonne selezionate.
- context['presentation']: engine,result_type,width,height,show_funnel.
- context['diagnostics']: limiti/reference funnel e risultati leave-one-out richiesti.

Il dizionario Pj data contiene soltanto le colonne sorgenti selezionate, prima
delle esclusioni MetaPj. source_row è la posizione da1 nel frame R d’ingresso,
non garantisce l’indice globale del dataset dopo filtri; in Python indice=source_row-1.
Non allineare array per posizione dopo esclusioni indipendenti. Nessun modello R,
variabile non selezionata o oggetto UI è passato implicitamente.

Tre script pronti: report/precisione/confronto modelli; esplorazione dei dati
sorgenti; scenari personali tau² con mzpjMetaWeights. Usano gli helper di Pj;
non ricalcolano implicitamente i modelli né modificano i risultati originali.

## Contratti del chiamante e verifiche

Il chiamante verifica nomi/tipi e popola i propri contenitori Table/Html/Svg/Text/
Preformatted. I risultati personali stanno in un gruppo separato. Image con
cattura browser e Output richiedono un contratto aggiuntivo: qui sono rifiutati
con un errore chiaro, senza ricopiare infrastruttura degli editor Pj.

Le cache persistono nello stato nativo: cambiare soltanto presentazione non
ricalcola il modello; modificare/caricare una bozza non esegue Python. Le risposte
inline grandi non sono duplicate nella cache. Test su INIT/salvataggio/fresh RUN,
input non validi, interpreti, grafici, errori e recupero distinguono backend e GUI.
Il repository è un esempio/guida con due JMO facoltativi Windows/Linux x64 nella
cartella principale, senza canale Releases, pacchetti macOS o invio alla Libreria.
Build, test harness, schermate, log e sessioni diagnostiche restano locali, fuori
dai sorgenti pubblici e dal JMO. Chi adatta il codice deve predisporre proprie
verifiche numeriche e di ciclo di vita, includendo anche salvataggio/riapertura
ed esportazione nel desktop: i test backend non equivalgono all'accettazione GUI.

### Altri esempi delle librerie

La [guida bilingue degli esempi](../examples/README.md) documenta otto script
personali per tutte e tre le famiglie. I nuovi esempi usano Chart.js per la
concentrazione dei pesi e l'helper esistente `mzpjShowPaired` per collegare profili
FE/RE e differenze in punti percentuali. Il collegamento riguarda questi due
pannelli; il collegamento forest–funnel standard è rinviato. In Html MetaPj compone
gli output pubblici Chart/Html in un accordion Pj con slider delle dimensioni
60–140% e Reset, riservando tutta l'area ridimensionata. Non interpreta il DOM
privato del renderer, non copia librerie vendor e non modifica Pj. Svg segue il
percorso nativo originario senza questo wrapper Html. Plotly Heatmap insieme a `mzpjMetaWeights` serve per gli scenari
di eterogeneità: celle annotate con i pesi percentuali, scala tenue blu/bianco/marrone
per la variazione in punti percentuali da tau² = 0, intestazioni con tau² effettivi
e righe compatte. WideToLong e D3 servono per l'audit dei dati sorgenti. Il modulo non
aggiunge renderer o dipendenze Python. I test verificano valori effettivi,
totali dei pesi, righe escluse, stime invariate e grafici nei due Python/Html/Svg.

Due [esempi Rust di ricampionamento](mzMp_rust_resampling.md) usano tramite Pj il
binario già installato: bootstrap media/mediana e medie batch per cambi di segno.
Riportano confronto numerico e tempi di una versione Python equivalente. MetaPj
non compila un nuovo backend né dichiara un'API Rust dedicata alle permutazioni.

### Dimensione complessiva della risposta

Il ricevitore del motore jamovi 28.18 installato accetta al massimo4 MiB.
I limiti delle singole risposte Pj non garantiscono il limite dell'analisi che le
aggrega con tabelle, opzioni e stato. La protezione in `serialize()` misura il
protobuf effettivo, riservando128 KiB al contenitore di trasporto; copre anche
vecchi risultati salvati prima di `.run()`. Il forest Html/Svg inattivo viene
ripulito prima, evitando risorse duplicate cambiando formato. Se l'estensione eccede il limite,
il suo output viene rimosso e la firma invalidata; tabelle valide e messaggio
esplicito arrivano all'applicazione. Si memorizza la firma respinta per evitare
tentativi automatici invariati; Run esplicito o cambio contesto/renderer consentono un nuovo tentativo.
Ulteriori fallback limitano grafica/cache
eccessive. Codice personale, dati e opzioni dei modelli non vengono riscritti.
I test devono serializzare l'intera analisi, non solo leggere gli item API.

Due Plotly inline possono superare il limite. Per la heatmap fornita scegliere
forest standard D3/Chart. La condivisione delle risorse sarebbe una funzionalità
pubblica Pj separata: MetaPj non interpreta HTML privato né copia asset vendor.

### Tabelle memorizzate e invalidazione nativa

MetaPj gestisce la validità delle tabelle mediante le firme di input/presentazione/script: usa quindi `clearWith=character()` e `clearWith: []` nello YAML. La regola vale anche ricostruendo gli schemi dinamici dopo il caricamento. Il default `clearWith="*"` svuota le celle per opzioni estranee come Disable o Html/Svg; se la cache evita di rieseguire Python, rimangono tabelle vuote. I test devono verificare valori numerici e celle trasmesse a jamovi, non soltanto il numero delle righe. Lo schema cache2 ricarica una volta i risultati precedenti alla correzione. La firma degli script personali comprende i dati sorgenti selezionati, anche nelle righe escluse dal modello.

# Load this single UTF-8 file in MetaPj > Python extension, then Run.
# All three data tabs, either Python, Html/Svg; no additional Python packages.
# Chart.js: cumulative weight curves, model visibility and point tooltips in Html.
# Each model ranks its OWN studies; the same rank need not identify the same study.
# D3 paired explorer: link FE/RE profiles to their percentage-point differences.
import math
from collections import Counter

TOP_N = 3  # Summary only; no study is removed from the analysis.
SHOW_PAIRED = True  # Uses fitted FE/RE weights; requires both models selected.


def mzRender(context):
    if isinstance(TOP_N, bool) or not isinstance(TOP_N, int) or TOP_N < 1:
        raise ValueError('TOP_N must be a positive integer.')
    if not isinstance(SHOW_PAIRED, bool):
        raise ValueError('SHOW_PAIRED must be True or False.')
    studies = context['studies']
    summaries, series, ranked_rows = [], [], []
    colors = {'FE': '#587295', 'RE': '#54786d'}
    for model in context['models']:
        key = model['model']
        ranked = sorted(studies, key=lambda s: (-s['weight_' + key], s['source_row']))
        cumulative = 0.0
        values = []
        for rank, study in enumerate(ranked, 1):
            weight = study['weight_' + key]
            cumulative += weight
            values.append(cumulative)
            ranked_rows.append({'Model': key, 'Rank': rank, 'Study': study['study'],
                                'Source row': study['source_row'], 'Weight %': weight,
                                'Cumulative %': cumulative})
        weights = [s['weight_' + key] for s in ranked]
        summaries.append({'Model': key, 'Included studies': len(studies),
                          'Largest weight %': weights[0],
                          'Top N': min(TOP_N, len(studies)),
                          'Top N weight %': math.fsum(weights[:TOP_N]),
                          'Weight concentration equivalent': 10000 / math.fsum(w*w for w in weights)})
        series.append({'label': key, 'data': values, 'borderColor': colors[key],
                       'backgroundColor': colors[key], 'borderWidth': 2,
                       'pointRadius': 3, 'fill': False, 'tension': 0})
    mzpjShowChart('line', series, labels=list(range(1, len(studies) + 1)),
        name='weight_concentration', title='How concentrated are the model weights?',
        width=context['presentation']['width'], height=420,
        result_type=context['presentation']['result_type'],
        options={'scales': {
            'x': {'title': {'display': True, 'text': 'Rank within each model (largest weight first)'}},
            'y': {'min': 0, 'max': 100, 'title': {'display': True, 'text': 'Cumulative weight (%)'}}},
            'plugins': {'legend': {'position': 'top'}}})
    if SHOW_PAIRED:
        if {'FE', 'RE'} <= {m['model'] for m in context['models']}:
            names = [str(s['study']) for s in studies]
            repeated = Counter(names)
            pairs = {'FE': [s['weight_FE'] for s in studies],
                     'RE': [s['weight_RE'] for s in studies],
                     'Study': [name if repeated[name] == 1 else f"{name} [source row {s['source_row']}]"
                               for name, s in zip(names, studies)]}
            mzpjShowText('**FE to RE: follow the same study.** Left: each line joins one study\'s '
                'FE and RE weights (%). Right: RE minus FE, in percentage points. '
                'Click a profile or a difference point to highlight the same study in both panels; '
                'drag a rectangle over the difference points to select several. '
                'Use Clear selection to restore the view. In the existing Pj control '
                '“Selected subjects only”, subjects means studies here. '
                'The figure-size slider enlarges both panels. '
                'These interactions change the descriptive view only; the forest, funnel and R models remain unchanged.',
                name='paired_weights_guide')
            mzpjShowPaired(pairs, first='FE', second='RE', labels='Study',
                first_label='FE', second_label='RE', y_label='Study weight (%)',
                name='paired_model_weights', title='How FE and RE redistribute each study\'s weight',
                color='#587295', width=context['presentation']['width'],
                height=context['presentation']['height'],
                result_type=context['presentation']['result_type'])
            mzpjShowTable([{'Study': s['study'], 'Source row': s['source_row'],
                            'FE weight %': s['weight_FE'], 'RE weight %': s['weight_RE'],
                            'Change (percentage points)': s['weight_RE']-s['weight_FE']}
                           for s in studies],
                name='paired_weights_table', title='Study identity and weight redistribution',
                notes=['Weights come from the selected metafor models; no refitting is performed.',
                       'Each model sums to 100%, so full-data changes sum to zero before rounding. '
                       'These are model weights for studies, not patient outcomes, '
                       'a paired-samples test or an influence diagnostic. '
                       'The fixed table contains all included studies, regardless of the interactive selection.'])
        else:
            mzpjShowText('**Paired FE–RE comparison.** Select both FE and RE models to display '
                'the linked panels. The concentration curve above remains available for the selected model.',
                name='paired_weights_guide')
    mzpjShowTable(summaries, name='concentration_summary', title='Weight concentration summary',
        notes=['Uses the selected metafor model weights, normalized to 100%. No model is refitted.',
               'Concentration equivalent = 1 / sum((weight / 100)^2). It ranges from 1 to k; '
               'it is not a participant sample size, degrees of freedom or an influence diagnostic.'])
    mzpjShowTable(ranked_rows, name='ranked_weights', title='Study identity behind each rank',
        notes='Models rank studies separately. Use source row to distinguish duplicate study labels.')

# Load in MetaPj > Python extension, then Run. All three tabs and both Pythons.
# Plotly heatmap + Pj inverse-variance helper. Html is interactive; Svg is static.
# Select D3 intervals or Chart.js intervals for the STANDARD forest first.
# Two inline Plotly results can exceed jamovi's 4 MiB engine-message limit.
# Change MULTIPLIERS to compare assumptions. These are weighting scenarios,
# NOT new fitted models, pooled effects, confidence intervals or estimated tau2.
import math
import statistics
import html
from collections import Counter

MULTIPLIERS = [0.0, 0.5, 1.0, 2.0]
ROW_HEIGHT = 19  # Pixels per study; all weights stay visible, including above 20 studies.


def mzRender(context):
    if (not isinstance(MULTIPLIERS, (list, tuple)) or not 2 <= len(MULTIPLIERS) <= 8
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or not math.isfinite(v) or v < 0 for v in MULTIPLIERS)
            or len(set(MULTIPLIERS)) != len(MULTIPLIERS)):
        raise ValueError('Use 2 to 8 distinct finite, non-negative MULTIPLIERS.')
    if isinstance(ROW_HEIGHT, bool) or not isinstance(ROW_HEIGHT, int) or not 16 <= ROW_HEIGHT <= 30:
        raise ValueError('ROW_HEIGHT must be an integer between 16 and 30.')
    studies = context['studies']
    variances = [s['vi'] for s in studies]
    re = next((m for m in context['models'] if m['model'] == 'RE'), None)
    base = re['tau2'] if re is not None and re['tau2'] > 0 else statistics.median(variances)
    basis = 'fitted REML tau2' if re is not None and re['tau2'] > 0 else 'median sampling variance (fallback)'
    labels = [f'{v:g} x reference' for v in MULTIPLIERS]
    columns = [mzpjMetaWeights(variances, tau2=v*base)['percent'] for v in MULTIPLIERS]
    matrix = [[column[i] for column in columns] for i in range(len(studies))]
    # Numbers remain the original weights. Color shows redistribution relative
    # to tau2=0, in PERCENTAGE POINTS, not a quality score or relative percent.
    baseline = mzpjMetaWeights(variances, tau2=0)['percent']
    changes = [[weight-baseline[i] for weight in row] for i, row in enumerate(matrix)]
    limit = max(0.5, math.ceil(2*max(abs(v) for row in changes for v in row))/2)
    names = [str(s['study']) for s in studies]
    short = [n if len(n) <= 34 else n[:31]+'…' for n in names]
    repeated = Counter(short)
    ticks = [html.escape(n if repeated[n] == 1 else f"{n} [#{s['source_row']}]")
             for n, s in zip(short, studies)]
    row_ids = [f'study_{i}' for i in range(len(studies))]
    details = [[[weight, changes[i][j], html.escape(names[i]), studies[i]['source_row'], MULTIPLIERS[j]*base]
                for j, weight in enumerate(row)] for i, row in enumerate(matrix)]
    headers = [f'τ² = {v*base:.3g}<br>'+('No heterogeneity' if v == 0 else
               'REML reference' if v == 1 and re is not None and re['tau2'] > 0 else f'{v:g} × reference')
               for v in MULTIPLIERS]
    figure = {'data': [{'type': 'heatmap', 'z': changes, 'x': labels, 'y': row_ids,
        'text': [[f'{weight:.2f}' for weight in row] for row in matrix],
        'customdata': details,
        'colorscale': [[0, '#486b91'], [0.5, '#f7f8fa'], [1, '#b08862']],
        'zmin': -limit, 'zmax': limit,
        'xgap': 2, 'ygap': 1,
        'texttemplate': '%{text}', 'textfont': {'size': 11},
        'hovertemplate': '%{customdata[2]}<br>Source row: %{customdata[3]}<br>τ²: %{customdata[4]:.5g}'
                         '<br>Weight: %{customdata[0]:.3f}%<br>Change vs τ² = 0: %{customdata[1]:+.3f} pp<extra></extra>',
        'colorbar': {'title': {'text': 'Change vs τ² = 0<br>(percentage points)', 'font': {'size': 10}},
                     'thickness': 11, 'len': 0.82, 'outlinewidth': 0,
                     'tickmode': 'array', 'ticklabeloverflow': 'allow',
                     'tickvals': [-limit, -limit/2, 0, limit/2, limit],
                     'ticktext': [f'−{limit:g}', f'−{limit/2:g}', '0', f'+{limit/2:g}', f'+{limit:g}'],
                     'tickfont': {'size': 10}}}],
        'layout': {'template': 'plotly_white', 'font': {'family': 'Arial', 'size': 12, 'color': '#334155'},
            # Keep an explicit layout: Plotly's automatic margin expansion can
            # over-reserve space when jamovi uses a scaled desktop interface.
            'margin': {'l': min(245, max(115, 6*max(len(t) for t in ticks)+12)),
                       'r': 115, 't': 62, 'b': 12, 'autoexpand': False},
            'xaxis': {'side': 'top', 'tickmode': 'array', 'tickvals': labels, 'ticktext': headers,
                      'tickfont': {'size': 10}, 'tickangle': 0, 'automargin': False, 'fixedrange': True},
            'yaxis': {'autorange': 'reversed', 'tickmode': 'array', 'tickvals': row_ids,
                      'ticktext': ticks, 'tickfont': {'size': 11}, 'automargin': False, 'fixedrange': True}}}
    mzpjShowText('**Reading the map.** Cells show study weights (%). '
        'Blue = lower weight; warm brown = higher weight than at τ² = 0. '
        f'Reference τ² = {base:.5g} ({basis}).', name='heterogeneity_guide')
    mzpjShowPlotly(figure,
        name='heterogeneity_weight_map', title='Study weights across heterogeneity scenarios',
        width=context['presentation']['width'], height=max(320, ROW_HEIGHT*len(studies)+74),
        config={'displayModeBar': False}, result_type=context['presentation']['result_type'])
    mzpjShowTable([{'Scenario': label, 'Multiplier': multiplier, 'tau2': multiplier*base,
                    'Total weight %': math.fsum(column), 'Largest weight %': max(column)}
                   for label, multiplier, column in zip(labels, MULTIPLIERS, columns)],
        name='heterogeneity_scenarios', title='Explicit scenario assumptions',
        notes=[f'Reference = {base:.6g}, using {basis}. Analysis scale: ' + context['analysis']['effect_scale'],
               'tau2 has squared analysis-scale units. Pj computes 100 * (1 / (vi + tau2)) / sum(weights).',
               'Cells show rounded weights (%); colors show changes from tau2=0 in percentage points. '
               'Each full-precision column sums to 100%. Blue means lower weight; brown means higher weight. '
               'Larger tau2 tends to equalize weights; these colors do not assess study quality or influence.'])

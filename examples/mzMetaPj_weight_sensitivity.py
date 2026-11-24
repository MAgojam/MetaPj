# Personal sensitivity scenarios use the existing Pj helper; no model is refitted.
# tau2 has squared units of the analysis scale (log RR/log OR, RD, MD or SMD).
TAU2_VALUES = [0.0, 0.05, 0.10]

def mzRender(context):
    studies = context['studies']
    variances = [s['vi'] for s in studies]
    rows = [{'Study': s['study'], 'Source row': s['source_row']} for s in studies]
    for tau2 in TAU2_VALUES:
        weights = mzpjMetaWeights(variances, tau2=tau2)['percent']
        for row, weight in zip(rows, weights):
            row['Weight % at tau2=' + str(tau2)] = weight
    mzpjShowTable(rows, name='personal_weights', title='User-selected heterogeneity scenarios',
        notes=['Pj calculates normalized inverse-variance weights: 1 / (vi + tau2).',
               'The scenarios are user choices, not estimated tau2 values or new meta-analysis models.',
               'Original metafor results remain unchanged. Analysis scale: ' + context['analysis']['effect_scale']])

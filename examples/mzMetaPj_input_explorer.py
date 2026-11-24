# Load in MetaPj, then Run. Pj receives selected source columns as data.
def mzRender(context):
    columns = context['inputs']
    source = data
    if context['analysis']['kind'] == 'dichotomous':
        x, y = columns['ai'], columns['ci']
        title = 'Source event counts: group 1 versus group 2'
    elif context['analysis']['kind'] == 'means':
        x, y = columns['n1i'], columns['n2i']
        title = 'Source sample sizes: group 1 versus group 2'
    else:
        x = columns['yi']
        uncertainty = context['analysis']['input_type']
        if uncertainty == 'ci':
            y = 'Input CI width'
            source = {'effect': data[x], y: [None if lo is None or hi is None else hi-lo
                for lo, hi in zip(data[columns['ciLower']], data[columns['ciUpper']])]}
            source['row label'] = data[columns['study']] if columns.get('study') else [f'Row {i+1}' for i in range(len(data[x]))]
            x = 'effect'
        else:
            y = columns['vi' if uncertainty == 'variance' else 'sei']
        title = 'Supplied study effect versus ' + {'variance': 'sampling variance', 'se': 'standard error', 'ci': 'input CI width'}[uncertainty]
    label = 'row label' if source is not data else columns.get('study')
    mzpjShowScatter(source, x=x, y=y, labels=label,
        name='source_explorer', title=title,
        x_label=x, y_label=y, width=context['presentation']['width'], height=420,
        result_type=context['presentation']['result_type'])
    mzpjShowText('**Source-data exploration.** These are the selected source rows, '
        'including rows excluded from the meta-analysis when their plotted values '
        'are present. This graphic does not refit a model or test a treatment effect.',
        name='source_explanation')

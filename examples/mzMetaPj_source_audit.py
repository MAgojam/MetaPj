# Load in MetaPj > Python extension, then Run. All three tabs / both Python modes.
# Demonstrates immutable WideToLong + D3 aggregation on selected SOURCE rows.
# Unlike context['studies'], data also retains rows excluded from the fitted model.
# Only required numeric inputs are audited; study labels are optional.
import math


def mzRender(context):
    kind = context['analysis']['kind']
    if kind == 'dichotomous':
        roles = ['ai', 'bi', 'ci', 'di']
    elif kind == 'means':
        roles = ['n1i', 'm1i', 'sd1i', 'n2i', 'm2i', 'sd2i']
    else:
        roles = {'variance': ['yi', 'vi'], 'se': ['yi', 'sei'],
                 'ci': ['yi', 'ciLower', 'ciUpper']}[context['analysis']['input_type']]
    columns = context['inputs']
    total = len(data[columns[roles[0]]])
    included = {s['source_row'] for s in context['studies']}
    flags = {'Source row': list(range(1, total + 1))}
    for role in roles:
        # JSON null / non-finite input: flag only; no imputation or row deletion.
        flags[role] = [0 if v is not None and math.isfinite(float(v)) else 1
                       for v in data[columns[role]]]
    long = mzpjWideToLong(flags, columns=roles, id_columns=['Source row'],
                         names_to='Input role', values_to='Missing or nonfinite')
    long['Finite'] = [1-value for value in long['Missing or nonfinite']]
    mzpjShowBar(long, category='Input role', value='Finite', stat='sum',
        orientation='horizontal', color='#587295',
        name='finite_inputs', title='Finite required inputs before model exclusions',
        x_label='Source rows with finite values (missing counts in table)', y_label='Input role',
        width=context['presentation']['width'], height=360,
        result_type=context['presentation']['result_type'])
    mzpjShowTable([{'Role': role, 'Selected column': columns[role], 'Source rows': total,
                    'Missing/nonfinite': sum(flags[role]), 'Finite': total-sum(flags[role])}
                   for role in roles], name='source_completeness', title='Input-role mapping and completeness',
        notes=['Counts refer to the selected source frame, including rows excluded from the model.',
               'A finite value is not necessarily valid: this does not check counts, sample-size '
               'constraints, SD signs or generic variance/CI rules. MetaPj/metafor retains responsibility for model validation.'])
    mzpjShowTable([{'Source row': row, 'Included in fitted model': 'Yes' if row in included else 'No',
                    'Missing required inputs': sum(flags[role][row-1] for role in roles)}
                   for row in range(1, total+1)],
        name='source_row_audit', title='Source-row traceability',
        notes='Source row is the 1-based position in the supplied R frame, not a guaranteed '
              'global dataset row after filters. All transformations create copies; data remains unchanged.')

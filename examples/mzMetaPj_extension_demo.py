# Copy this entire file into MetaPj's Python extension field, then click Run Python extension.
# Works in all three input tabs with either Python interpreter. No extra packages are needed.
# MetaPj calls mzRender(context); do not add a call at the end of this file.
import math

MZ_SHOW_PRECISION_PLOT = True
MZ_SHOW_MODEL_COMPARISON = True


def mzRender(context):
    info = context['analysis']
    studies = context['studies']
    models = context['models']
    label = {'dichotomous': 'Dichotomous outcomes', 'means': 'Independent-group mean differences',
             'generic': 'Generic effect sizes'}[info['kind']]
    mzpjShowText(
        f"## My Python extension\n\n"
        f"**{label} — {info['measure']}**. "
        f"Included studies: **{info['k']}**; excluded rows: **{info['excluded']}**.\n\n"
        "The model was fitted by R/metafor. This function reads its results and "
        "adds calculations and graphics through Pj.",
        name='custom_intro')

    # Sampling variance is on the analysis scale, also when ratios are displayed as RR/OR.
    rows = []
    for study in studies:
        standard_error = math.sqrt(study['vi'])
        rows.append({
            'Study': study['study'],
            'Source row': study['source_row'],
            'Analysis effect': study['yi'],
            'Variance': study['vi'],
            'SE': standard_error,
            'Precision': 1.0 / standard_error,
        })
    mzpjShowTable(
        rows, name='custom_studies', title='Study effects and precision',
        notes=[f"Analysis scale: {info['effect_scale']}. SE = sqrt(vi); precision = 1 / SE.",
               'Source row is the position in the supplied R frame; filters may change its relation to global dataset rows. No excluded observations are reintroduced.'])

    weight_checks = []
    for model in models:
        column = 'weight_' + model['model']
        weights = [study[column] for study in studies]
        weight_checks.append({
            'Model': model['model'],
            'Total weight (%)': math.fsum(weights),
            'Minimum weight (%)': min(weights),
            'Maximum weight (%)': max(weights),
            'Pooled effect': model['estimate'],
            'Lower CI': model['lower'],
            'Upper CI': model['upper'],
        })
    mzpjShowTable(
        weight_checks, name='custom_weights', title='Model weights and pooled effects',
        notes=f"Weights were calculated by metafor and sum to 100% separately for each model. Effects and CI limits use the {info['measure']} display scale.")

    if MZ_SHOW_PRECISION_PLOT:
        points = {
            'study': [row['Study'] for row in rows],
            'effect': [row['Analysis effect'] for row in rows],
            'precision': [row['Precision'] for row in rows],
        }
        mzpjShowScatter(
            points, x='effect', y='precision', labels='study',
            name='custom_precision', title='Effect and study precision',
            x_label=info['effect_scale'], y_label='Precision (1 / SE)',
            result_type=context['presentation']['result_type'], width=context['presentation']['width'], height=420)
        mzpjShowText(
            "This is a descriptive precision plot. It does not perform a "
            "publication-bias test, identify influential studies or refit either model.",
            name='custom_precision_note')

    if MZ_SHOW_MODEL_COMPARISON:
        comparison = {
            'model': [model['model'] for model in models],
            'estimate': [model['estimate'] for model in models],
            'lower': [model['lower'] for model in models],
            'upper': [model['upper'] for model in models],
        }
        mzpjShowIntervals(
            comparison, estimate='estimate', lower='lower', upper='upper', labels='model',
            reference=1 if info['ratio'] else 0,
            interval_label=f"{info['level']}% confidence interval",
            name='custom_model_comparison', title='Selected pooled models',
            x_label=info['measure'] + ' (linear display scale)',
            result_type=context['presentation']['result_type'], width=context['presentation']['width'], height=280)

    print(f"Custom extension completed: {info['kind']}, {info['measure']}, {info['k']} studies.")

# MetaPj > Script > Load this file, then Python > Run. All three input tabs/Pythons.
# Native pj_stats_rust is supplied by installed Pj; no rebuild or pip install.
# Study-level percentile bootstrap of UNWEIGHTED mean/median analysis effects.
# RR/OR and generic log ratios: log effects; other inputs: supplied analysis scale.
# This is NOT FE/RE bootstrap.
# Independent studies representing a study population are assumed; no patients
# or treatment arms are resampled. Small k can give unreliable/discrete intervals.
import math
import platform
import statistics
import time
import pj_stats_rust as rust

REPLICATES = [1000, 10000]
BENCHMARK_REPEATS = 3       # Timed calls per configuration; median time reported.
COMPARE_PYTHON = True      # False skips the slower matched Python reference.
SEED = 20261124


class _mzSplitMix64:
    # Match the backend's seeded generator and unbiased index sampling so that
    # both implementations operate on the SAME resamples, not just the same B.
    def __init__(self, seed):
        self.state = seed

    def index(self, n):
        mask = (1 << 64) - 1
        threshold = ((1 << 64) - n) % n
        while True:
            self.state = (self.state + 0x9e3779b97f4a7c15) & mask
            z = self.state
            z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & mask
            z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & mask
            z ^= z >> 31
            if z >= threshold:
                return z % n


def _mzMean(values):
    anchor, n = values[0], len(values)
    return anchor + math.fsum((x-anchor)/n for x in values)


def _mzPythonBootstrap(values, statistic, reps, alpha, seed):
    rng = _mzSplitMix64(seed)
    calc = _mzMean if statistic == 'media' else statistics.median
    estimates = [calc([values[rng.index(len(values))] for _ in values]) for _ in range(reps)]
    center = _mzMean(estimates)
    se = math.sqrt(math.fsum((v-center)**2 for v in estimates)/(reps-1))
    estimates.sort()
    def quantile(p):
        pos = (len(estimates)-1)*p
        lo, hi = math.floor(pos), math.ceil(pos)
        return estimates[lo]*(1-(pos-lo)) + estimates[hi]*(pos-lo)
    original = calc(values)
    return {'stima_originale': original, 'stima_bootstrap': center,
            'bias': center-original, 'se_bootstrap': se,
            'ci_lower': quantile(alpha/2), 'ci_upper': quantile(1-alpha/2)}


def mzRender(context):
    if not callable(getattr(rust, 'bootstrap_statistica', None)):
        raise RuntimeError('Update Pj with pj_stats_rust bootstrap_statistica support.')
    if (not isinstance(REPLICATES, (list, tuple)) or not 1 <= len(REPLICATES) <= 4
            or any(isinstance(b, bool) or not isinstance(b, int) or not 200 <= b <= 250000 for b in REPLICATES)
            or len(set(REPLICATES)) != len(REPLICATES)):
        raise ValueError('REPLICATES: choose 1 to 4 distinct integers between 200 and 250000.')
    if (isinstance(BENCHMARK_REPEATS, bool) or not isinstance(BENCHMARK_REPEATS, int)
            or not 1 <= BENCHMARK_REPEATS <= 5 or not isinstance(COMPARE_PYTHON, bool)
            or isinstance(SEED, bool) or not isinstance(SEED, int) or not 0 <= SEED < 2**64):
        raise ValueError('Use 1 to 5 BENCHMARK_REPEATS, Boolean COMPARE_PYTHON and a uint64 SEED.')
    values = [s['yi'] for s in context['studies']]
    if len(values) < 3 or not all(math.isfinite(v) for v in values):
        raise ValueError('Bootstrap needs at least three finite included study effects.')
    work = len(values)*sum(REPLICATES)*2*BENCHMARK_REPEATS
    if work > (6000000 if COMPARE_PYTHON else 100000000):
        raise ValueError('Reduce REPLICATES/repeats or disable COMPARE_PYTHON: preview workload limit exceeded.')
    alpha = 1-context['analysis']['level']/100
    summaries, timings, comparisons = [], [], []
    for statistic, label in [('media', 'Unweighted mean'), ('mediana', 'Unweighted median')]:
        rust.bootstrap_statistica(values, statistica=statistic, n_reps=20, alpha=alpha, seed=SEED)
        if COMPARE_PYTHON:
            _mzPythonBootstrap(values, statistic, 20, alpha, SEED)
        for reps in sorted(REPLICATES):
            native_times, python_times = [], []
            for repetition in range(BENCHMARK_REPEATS):
                # Alternate order to reduce a systematic first/second-call advantage.
                order = ['Rust', 'Python'] if repetition % 2 == 0 else ['Python', 'Rust']
                for engine in order:
                    if engine == 'Python' and not COMPARE_PYTHON:
                        continue
                    start = time.perf_counter()
                    if engine == 'Rust':
                        native = rust.bootstrap_statistica(values, statistica=statistic,
                            n_reps=reps, alpha=alpha, seed=SEED)
                        native_times.append((time.perf_counter()-start)*1000)
                    else:
                        reference = _mzPythonBootstrap(values, statistic, reps, alpha, SEED)
                        python_times.append((time.perf_counter()-start)*1000)
            native_ms = statistics.median(native_times)
            for engine, elapsed in [('Rust', native_ms)] + ([('Python', statistics.median(python_times))] if COMPARE_PYTHON else []):
                timings.append({'Statistic': label, 'Engine': engine, 'Replicates': reps,
                                'Median ms': elapsed, 'Timed calls': BENCHMARK_REPEATS})
            if COMPARE_PYTHON:
                error = max(abs(native[key]-reference[key]) for key in reference)
                tolerance = 1e-10*max(1, max(abs(reference[key]) for key in reference))
                if error > tolerance:
                    raise RuntimeError('Matched bootstrap results disagree with the Python reference.')
                comparisons.append({'Statistic': label, 'Replicates': reps,
                    'Maximum absolute difference': error,
                    'Python/Rust time ratio': statistics.median(python_times)/max(native_ms, 1e-12)})
            if reps == max(REPLICATES):
                summaries.append({'Statistic': label, 'Studies': len(values), 'Replicates': reps,
                    'Estimate': native['stima_originale'], 'Bootstrap mean': native['stima_bootstrap'],
                    'Bias': native['bias'], 'Bootstrap SE': native['se_bootstrap'],
                    'Lower': native['ci_lower'], 'Upper': native['ci_upper']})
    mzpjShowTable(summaries, name='rust_bootstrap_estimates', title='Study-level percentile bootstrap',
        notes=[f"Unweighted study summaries on {context['analysis']['effect_scale']} scale; {context['analysis']['level']}% percentile intervals.",
               'Studies are sampled with replacement. No inverse-variance weighting, REML refitting, '
               'within-study resampling, BCa or studentized intervals. Original R models are unchanged.'])
    mzpjShowTable(timings, name='rust_bootstrap_times', title='Measured bootstrap computation time',
        notes=[f'pj_stats_rust {rust.__version__}; Python {platform.python_version()}; seed {SEED}. Warm-up excluded.',
               'Times include resampling, statistic, sorting, CI and Python/Rust conversion; exclude imports, '
               'Pj process startup, rendering and R fitting. Same draws/statistics; no guaranteed speedup. '
               'Native execution is not automatically parallel. Repeat timings are not additional inferential draws.'])
    if comparisons:
        mzpjShowTable(comparisons, name='rust_bootstrap_agreement', title='Matched draws: numerical agreement and timings')
    chart = {'Replicates': [r['Replicates'] for r in timings], 'Milliseconds': [r['Median ms'] for r in timings],
             'Implementation': [r['Engine']+' / '+r['Statistic'] for r in timings]}
    mzpjShowLine(chart, 'Replicates', 'Milliseconds', group='Implementation', sort_x=True,
        name='rust_bootstrap_scaling', title='Bootstrap time as replication count increases',
        x_label='Bootstrap replicates per call', y_label='Median computation time (ms)',
        width=context['presentation']['width'], height=400,
        result_type=context['presentation']['result_type'])
    intervals = {'Statistic': [r['Statistic'] for r in summaries], 'Estimate': [r['Estimate'] for r in summaries],
                 'Lower': [r['Lower'] for r in summaries], 'Upper': [r['Upper'] for r in summaries]}
    mzpjShowIntervals(intervals, 'Estimate', 'Lower', 'Upper', labels='Statistic', reference=0,
        interval_label=f"{context['analysis']['level']}% study-level percentile interval",
        name='rust_bootstrap_intervals', title='Unweighted study summaries: percentile intervals',
        x_label=context['analysis']['effect_scale'], color='#587295',
        width=context['presentation']['width'], height=280,
        result_type=context['presentation']['result_type'])

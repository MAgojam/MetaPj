# Load one file in MetaPj, then Run. All three input tabs, both Pythons, Html/Svg.
# Sign-flip test of the unweighted mean analysis effect against zero.
# Assumption: independent study effects, joint sign invariance under the null
# (e.g. each effect symmetric about zero). This is stronger than a zero mean.
# This is NOT a treatment-arm permutation from individual patient records.
# Rust 1.1 supplies batch row means, not a dedicated permutation/RNG function:
# Python builds sign patterns; Rust computes means; Python counts extreme draws.
import math
import platform
import random
import statistics
import time
import pj_stats_rust as rust

PERMUTATIONS = [999, 9999]
BENCHMARK_REPEATS = 3
BATCH_SIZE = 512            # Memory proportional to studies * batch, not all draws.
EXACT_MAX_STUDIES = 14      # Enumerate all 2**k signs if requested B is sufficient.
SEED = 20261124


def _mzSignFlip(values, requested, seed, repeats, batch_size, exact_max):
    k = len(values)
    exact = k <= exact_max and requested >= 2**k
    draws = 2**k if exact else requested
    rng = random.Random(seed)
    native_means, native_seconds, python_seconds = [], 0.0, 0.0
    generation_seconds, max_error = 0.0, 0.0
    for start in range(0, draws, batch_size):
        size = min(batch_size, draws-start)
        begin = time.perf_counter()
        if exact:
            columns = [[v if ((index >> j) & 1) else -v
                        for index in range(start, start+size)] for j, v in enumerate(values)]
        else:
            # One k-bit mask per draw: changing the batch size preserves the
            # seeded sign sequence, rather than changing which study gets a bit.
            patterns = [rng.getrandbits(k) for _ in range(size)]
            columns = [[v if ((mask >> j) & 1) else -v for mask in patterns]
                       for j, v in enumerate(values)]
        generation_seconds += time.perf_counter()-begin
        rt, pt = [], []
        for repeat in range(repeats):
            for engine in (['Rust', 'Python'] if repeat % 2 == 0 else ['Python', 'Rust']):
                begin = time.perf_counter()
                if engine == 'Rust':
                    result = rust.statistiche_righe(columns, statistica='media', min_validi=k)
                    rt.append(time.perf_counter()-begin)
                else:
                    # Same pre-generated signs; stable shifted mean, as in the backend.
                    reference = [row[0]+math.fsum((v-row[0])/k for v in row) for row in zip(*columns)]
                    pt.append(time.perf_counter()-begin)
        max_error = max(max_error, max(abs(a-b) for a, b in zip(result, reference)))
        native_means.extend(result)
        native_seconds += statistics.median(rt)
        python_seconds += statistics.median(pt)
    observed = values[0]+math.fsum((v-values[0])/k for v in values)
    tolerance = 1e-12*max(1, max(abs(v) for v in values))
    if max_error > tolerance:
        raise RuntimeError('Rust/Python sign-flip statistics disagree.')
    begin = time.perf_counter()
    extremes = sum(abs(v) >= abs(observed)-tolerance for v in native_means)
    p = extremes/draws if exact else (extremes+1)/(draws+1)
    counting_seconds = time.perf_counter()-begin
    return {'draws': draws, 'exact': exact, 'observed': observed, 'extremes': extremes, 'p': p,
            'mc_se': None if exact else math.sqrt(p*(1-p)/draws), 'values': native_means,
            'generation_ms': generation_seconds*1000, 'rust_ms': native_seconds*1000,
            'python_ms': python_seconds*1000, 'counting_ms': counting_seconds*1000,
            'max_error': max_error}


def mzRender(context):
    if not callable(getattr(rust, 'statistiche_righe', None)):
        raise RuntimeError('Update Pj with pj_stats_rust batch row statistics support.')
    if (not isinstance(PERMUTATIONS, (list, tuple)) or not 1 <= len(PERMUTATIONS) <= 4
            or any(isinstance(b, bool) or not isinstance(b, int) or not 199 <= b <= 100000 for b in PERMUTATIONS)
            or len(set(PERMUTATIONS)) != len(PERMUTATIONS)):
        raise ValueError('PERMUTATIONS: choose 1 to 4 distinct integers between 199 and 100000.')
    for name, value, lo, hi in [('BENCHMARK_REPEATS', BENCHMARK_REPEATS, 1, 5),
                               ('BATCH_SIZE', BATCH_SIZE, 32, 4096),
                               ('EXACT_MAX_STUDIES', EXACT_MAX_STUDIES, 0, 16),
                               ('SEED', SEED, 0, 2**64-1)]:
        if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
            raise ValueError(f'{name} must be an integer between {lo} and {hi}.')
    values = [s['yi'] for s in context['studies']]
    if len(values) < 3 or not all(math.isfinite(v) for v in values):
        raise ValueError('At least three finite included study effects are required.')
    if len(values)*sum(PERMUTATIONS)*BENCHMARK_REPEATS > 6000000 or len(values)*BATCH_SIZE > 1000000:
        raise ValueError('Reduce permutations, repeats or batch size: preview workload limit exceeded.')
    rust.statistiche_righe([[v, -v] for v in values], min_validi=len(values))
    summaries, timings = [], []
    for requested in sorted(PERMUTATIONS):
        result = _mzSignFlip(values, requested, SEED, BENCHMARK_REPEATS, BATCH_SIZE, EXACT_MAX_STUDIES)
        summaries.append({'Studies': len(values), 'Requested patterns': requested,
            'Used patterns': result['draws'], 'Method': 'Exact sign enumeration' if result['exact'] else 'Monte Carlo sign flips',
            'Observed unweighted mean': result['observed'], 'Extreme patterns': result['extremes'],
            'Two-sided p': result['p'], 'Approx MC SE': result['mc_se']})
        common = result['generation_ms'] + result['counting_ms']
        timings.append({'Patterns': result['draws'], 'Sign generation ms': result['generation_ms'],
            'Rust kernel ms': result['rust_ms'], 'Python kernel ms': result['python_ms'],
            'Counting ms': result['counting_ms'], 'Rust pipeline ms': common+result['rust_ms'],
            'Python pipeline ms': common+result['python_ms'],
            'Kernel Python/Rust ratio': result['python_ms']/max(result['rust_ms'], 1e-12),
            'Maximum absolute difference': result['max_error']})
    mzpjShowTable(summaries, name='rust_signflip_test', title='Unweighted study-effect sign-flip test',
        notes=[f"Analysis scale: {context['analysis']['effect_scale']}. Null = zero; for log ratios this corresponds to ratio 1.",
               'Requires independent effects with sign invariance under the null, not merely a zero mean. '
               'No inverse-variance weights, REML refits, patient-level permutations or replacement of metafor tests.',
               'Two-sided statistic = abs(mean). Exact p = extremes / 2^k; Monte Carlo p = (extremes+1)/(B+1). '
               'A tolerance handles numerical ties. MC SE is approximate; exact enumeration has no Monte Carlo error.'])
    mzpjShowTable(timings, name='rust_signflip_times', title='Shared signs: native kernel and complete pipeline',
        notes=[f'pj_stats_rust {rust.__version__}; Python {platform.python_version()}; seed {SEED}; batch {BATCH_SIZE}; repeats {BENCHMARK_REPEATS}.',
               'Kernel times sum within-batch medians; native time includes argument/result conversion. '
               'Pipeline estimates add the shared sign-generation/counting time, exclude warm-up, '
               'verification, imports, process startup and graphics. Sign generation is Python in both pipelines. '
               'No guaranteed speedup or native parallelism; repeated timings do not increase the tested draw count.'])
    mzpjShowHistogram({'Null mean': result['values']}, 'Null mean', bins=28,
        name='rust_signflip_distribution', title=f"Sign-flip reference distribution; observed mean = {result['observed']:.4g}",
        x_label='Unweighted mean on '+context['analysis']['effect_scale']+' scale', y_label='Sign patterns',
        color='#587295', width=context['presentation']['width'], height=400,
        result_type=context['presentation']['result_type'])

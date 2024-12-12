#!/usr/bin/env python3
'''
A wee utility that I use to benchmark katas
author: github.com/tmck-code

usage:

func_groups = [
    [f1,f2],
    [f3,f4,f5],
    [f6],
]
tests = [
    ( (arg1, arg2), {}, result1, ),
    ( (arg3, arg4), {}, result2, ),

bench.bench(
    tests, func_groups,
    n=100_000, sort=('BENCH_SORT' in os.environ)
)
'''

from collections import Counter, namedtuple
from functools import lru_cache, wraps
from itertools import chain, repeat
import operator
import pickle
import time, sys, os
from typing import Callable, Any
import statistics

import pp

Test = namedtuple('Test', 'args kwargs expected n')
class NoExpectation:
    'Denotes that a test/benchmark has no expected result (i.e. just benchmark it)'

def set_function_module(func):
    'Set the module of a function'
    if func.__module__ != '__main__':
        return
    module = sys.modules[func.__module__]
    if hasattr(module, '__file__'):
        # if the function is defined in the main module, set the module to the filename
        func.__module__ = os.path.basename(str(module.__file__)).split('.')[0]
    else:
        # if the module is not a file, set the module to the current directory
        func.__module__ = os.path.basename(os.getcwd())

@lru_cache
def _load_serialised_args(serialised_args):
    return pickle.loads(serialised_args)

def timeit_func(func, args, kwargs, expected: object = NoExpectation, n: int = 10_000):
    'Time a function with arguments and return the result, whether it is correct, and the times'
    start, times = 0, Counter()
    # some functions may modify the input arguments, so a new copy is needed for every test
    # "pickle" is used instead of "deepcopy" as it's much faster
    args_ser = pickle.dumps(args)
    # ensure that the function module is meaningful (replace it if it's just "__main__")
    set_function_module(func)
    for _ in range(n):
        try:
            start = time.time()
            func(*_load_serialised_args(args_ser), **kwargs)
        except Exception:
            pass
        finally:
            times[time.time()-start] += 1
    try:
        result = func(*pickle.loads(args_ser), **kwargs)
    except Exception as e:
        result = e
    return result, expected is NoExpectation or result == expected, times

def _sum_times(times: Counter) -> float:
    'sum the values*counts in a Counter'
    return sum(map(operator.mul, *zip(*times.items())))

def _avg_times(times: Counter) -> float:
    return _sum_times(times) / times.total()

def _median_times(times: Counter) -> float:
    return statistics.median(list(times.elements()))

TEST_STATUS = {
    False: pp.ps('fail', 'red'),
    True:  pp.ps('pass', 'green'),
}
TRUNCATE = 40

def _truncate(s: str, n: int=TRUNCATE) -> str:
    'Truncate a string to n characters'
    if len(s) <= n:
        return s
    return s[:n-10] + '...' + str(s)[-10:]

def _format_time(i: float) -> str:
    '''
    Format a time in seconds to a human-readable string, rounding to the nearest unit
    e.g. 0.0000001 -> "100 ns"
    Uses chars from the "mathematical italic small" unicode block for the units
    '''
    unit = 's'
    for u in ('s ', '𝑚s', '𝜇s', '𝑛s'):
        if i >= 1:
            unit = u
            break
        i = i*10**3
    return f'{i:7.03f} {unit}'

RECORD_SEP = '│'
BORDER_SEP = '─'
HEADER_SEP = '┆'
BORDER_END, BORDER_PATTERN = '★', '-⎽__⎽-⎻⎺⎺⎻'

def gen_border():
    w = os.get_terminal_size().columns
    n = int(w/len(BORDER_PATTERN))
    r = max(int(n%len(BORDER_PATTERN)/2)-1, 0)
    b = (f'{BORDER_END}{" "*r}{BORDER_PATTERN*n}{" "*r}{BORDER_END}'
        f'\n{BORDER_SEP*w}')
    return b


def _print_header(s: str, test: Test) -> None:
    'Print the result of a timed test'
    print('\n{s:s}{border:s}\n\n{n_s:s}: {n:,d}, {args_s:s}: {args:20s}{kwargs_s:s}: {kwargs:20s}\n'.format(**{
        's':        s,
        'border':   pp.ps(gen_border(), 'brightyellow'),
        'n_s':      pp.ps('n', 'bold'),
        'n':        test.n,
        'args_s':   pp.ps('args', 'bold'),
        'args':     _truncate(str(test.args)+', '),
        'kwargs_s': pp.ps('kwargs', 'bold'),
        'kwargs':   _truncate(str(test.kwargs)),
    }))

def _print_result_header(width: int=1) -> None:
    msg = '{funcs:s}{status:<5s} {sep:s} {total:^10s} {sep:s} {median:^10s}'.format(**{
        'funcs':  f'{"function":<{width}s}'.format('function'),
        'status': 'status',
        'total':  'Σ ',
        'median': 'x̄',
        'sep':     HEADER_SEP,
    })
    border = BORDER_SEP*len(msg)
    print(msg, border, sep='\n')

def _print_result(func: Callable, result: Any, correct: bool, times: Counter, width: int=1, colour: str='', extra: str='') -> None:
    fail_sep, status_msg = '\n', ''
    if not correct:
        if os.get_terminal_size().columns >= 100:
            fail_sep = ' '
        result = _truncate(str(result))
        status_msg = pp.ps(f'{fail_sep}>> {result=}', 'yellow')

    msg = '{func_name:s}{status:<s}   {sep:s} {total:s} {sep:s} {median:s} {extra:s}{status_msg:s}'.format(**{
        'func_name':  pp.ps(f'{func.__module__+"."+func.__name__+", ":<{width}s}', style=colour),
        'total':      _format_time(_sum_times(times)),
        'median':     _format_time(_median_times(times)),
        'status':     TEST_STATUS[correct],
        'extra':      extra,
        'status_msg': status_msg,
        'width':      width+2,
        'sep':        RECORD_SEP,
    })
    print(msg)


def timeit(n=10_000):
    'Decorator to time a function'
    def decorator_with_args(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result, correct, times = timeit_func(func, args, kwargs, NoExpectation, n)
            _print_result(func, result, correct, times)
        return wrapper
    return decorator_with_args


def bench(tests, func_groups, n: int=10_000, sort: bool=False):
    'Run a series of timed tests on a list of functions'
    s, group_colours = '', ['yellow', 'brightred', 'cyan', 'bold']
    for func_group in func_groups:
        for func in func_group:
            set_function_module(func)
    width = max(len(func.__module__)+len(func.__name__)+3 for func in chain.from_iterable(func_groups))

    if 'BENCH_SORT' in os.environ:
        sort = True

    for test in tests:
        test, results = Test(*test, n=n), []
        _print_header(s, test)
        pp.pps('results:', 'bold')
        _print_result_header(width)
        for funcs, group_colour in zip(func_groups, group_colours):
            for func in funcs:
                result, correct, times = timeit_func(func, *test)
                _print_result(func, result, correct, times, width, group_colour)
                results.append((func, result, correct, times, width, group_colour))
        if sort:
            pp.pps('\nsorted by time:', 'bold')
            _print_result_header(width)
            base, extra = 0, ''

            for _, results in enumerate(sorted(results, key=lambda r: _median_times(r[3]))):
                if not results[2]:
                    continue
                if base == 0:
                    base = _median_times(results[3])
                else:
                    x = _median_times(results[3]) / base
                    extra = pp.ps(f' ↓ x{x:.2f}', 'bold')
                _print_result(*results, extra=extra)
        s = '\n'

from dataclasses import asdict, is_dataclass, dataclass
from datetime import datetime
import json
import random
from types import FunctionType

from pygments import highlight, console
from pygments.lexers import JsonLexer, OutputLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name, get_all_styles

STYLES = [
    'dracula', 'fruity', 'gruvbox-dark', 'gruvbox-light', 'lightbulb', 'material', 'one-dark',
    'perldoc', 'native', 'tango',
]

def _isnamedtuple(obj: object):
    return isinstance(obj, tuple) and hasattr(obj, '_fields')

def _normalise(obj: object):
    'step through obj and normalise namedtuples to dicts'
    if isinstance(obj, dict): return {k: _normalise(v) for k, v in obj.items()}
    if isinstance(obj, list): return [_normalise(i) for i in obj]
    if _isnamedtuple(obj):    return obj._asdict()
    return obj

def _json_default(obj: object):
    'Default JSON serializer, supports most main class types'
    if   isinstance(obj, str):          return obj # str
    elif isinstance(obj, list):         return [_json_default(i) for i in obj]
    elif is_dataclass(obj):             return asdict(obj) # dataclass
    elif isinstance(obj, datetime):     return obj.isoformat() # datetime
    elif isinstance(obj, FunctionType): return f'{obj.__name__}()' # function
    elif hasattr(obj, '__slots__'):     return {k: getattr(obj, k) for k in obj.__slots__} # class with slots.
    elif hasattr(obj, '__name__'):      return obj.__name__ # function/class name
    elif hasattr(obj, '__dict__'):      return obj.__dict__ # class
    return str(obj)

def ppd(d_obj, indent=2, style='dracula', random_style=False):
    'pretty-print a dict'
    d = _normalise(d_obj) # convert any namedtuples to dicts

    if random_style:
        style = random.choice(STYLES)
    code = json.dumps(d, indent=indent, default=_json_default)

    if style is None:
        print(code)
    else:
        print(highlight(
            code      = code,
            lexer     = JsonLexer(),
            formatter = Terminal256Formatter(style=get_style_by_name(style))
        ).strip())

def ppj(j, indent=2, style='dracula', random_style=False):
    'pretty-print a JSON string'
    ppd(json.loads(j), indent=indent, style=style, random_style=random_style)

def ps(s, style='yellow', random_style=False):
    'add color to a string'
    if random_style:
        style = random.choice(console.dark_colors + console.light_colors)
    return console.colorize(style, s)

def pps(s, style='yellow', random_style=False):
    'pretty-print a string'
    print(ps(s, style=style, random_style=random_style))

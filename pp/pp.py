from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
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

def _json_default(obj: object):
    'Default JSON serializer, supports most main class types'
    if   isinstance(obj, str):          return obj # str
    elif is_dataclass(obj):             return asdict(obj) # dataclass
    elif isinstance(obj, datetime):     return obj.isoformat() # datetime
    elif isinstance(obj, tuple) and \
       hasattr(obj, '_asdict'):         return obj._asdict() # namedtuple
    elif isinstance(obj, FunctionType): return f'{obj.__name__}()' # function
    elif hasattr(obj, '__slots__'):     return {k: getattr(obj, k) for k in obj.__slots__}
                                        # 'class with slots. watch out - namedtuples have __slots__ too
    elif hasattr(obj, '__name__'):      return obj.__name__ # function/class name
    elif hasattr(obj, '__dict__'):      return obj.__dict__ # class
    return str(obj)

def ppd(d, indent=2, style='dracula', random_style=False):
    'pretty-print a dict'
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

from pp import pp

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime

class TestJSONDefault:
    def test_json_default_str(self, capsys):
        pp.ppd({'a': 'b'}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "b"}'

    def test_json_default_dataclass(self, capsys):
        @dataclass
        class A:
            a: str
        pp.ppd(A('b'), indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "b"}'

    def test_json_default_datetime(self, capsys):
        pp.ppd({'a': datetime(2021, 1, 1, 12, 34, 56)}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "2021-01-01T12:34:56"}'

    def test_json_default_class(self, capsys):
        class A:
            def __init__(self, a):
                self.a = a
        pp.ppd({'a': A('b')}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": {"a": "b"}}'

    def test_json_default_function(self, capsys):
        def a(): pass

        pp.ppd({'a': a}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "a"}'

    def test_json_default_slots(self, capsys):
        class A:
            __slots__ = ['a']
            def __init__(self, a):
                self.a = a
        pp.ppd({'a': A('b')}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": {"a": "b"}}'

    def test_json_default_namedtuple(self, capsys):
        Testr = namedtuple('testr', ('a', 'b'))
        pp.ppd({'a': Testr(1, 2)}, indent=None, style=None)

        captured = capsys.readouterr()

        assert captured.out.strip() == '{"a": [1, 2]}'

    def test_json_default_other(self, capsys):
        class Testr:
            def t(self): pass
        
        t = Testr()
        pp.ppd({'a': t.t}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "t"}'

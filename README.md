# pp
terminal/cli/python helpers for colour and pretty-printing

- [pp](#pp)
  - [`bench`](#bench)
  - [`pp`](#pp-1)

---

## `bench`

```python
from pp import bench

bench.bench(
    tests=[
        (
            (range(2),), # args
            {},          # kwargs
            [0,1],       # expected
        )
    ],
    func_groups=[ [list] ],
    n=100
)
```

## `pp`

```python
from pp import pp

# Pretty-print a dict
pp.ppd([[1,2,3], [4,5,6], [7,8,9]])
# [
#   [1, 2, 3],
#   [4, 5, 6],
#   [7, 8, 9]
# ]

# Pretty-print a JSON string
pp.ppj('{"a": 1, "b": 2}')
# {
#   "a": 1,
#   "b": 2
# }
```
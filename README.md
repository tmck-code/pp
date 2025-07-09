# pp
terminal/cli/python helpers for colour and pretty-printing

- [pp](#pp)
  - [`bench`](#bench)
  - [`pp`](#pp-1)

---

## `pp`


https://github.com/user-attachments/assets/cce8f690-e411-459f-a04f-8e9bef533e4a


---

## `bench`


https://github.com/user-attachments/assets/4af823b0-8d18-4086-9754-c76c65b66898


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

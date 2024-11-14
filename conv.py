def rgb_to_ansi(r, g, b):
    'The golden formula'
    ''''
    The golden formula. Via https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

      0-  7:  standard colors (as in ESC [ 30–37 m)
      8- 15:  high intensity colors (as in ESC [ 90–97 m)
     16-231:  6 × 6 × 6 cube (216 colors): 16 + 36 × r + 6 × g + b (0 ≤ r, g, b ≤ 5)
    232-255:  grayscale from dark to light in 24 steps
    '''
    return 16 + (36*r + 6*g + b)


def ansi_to_rgb(n):
    if n < 16:
        return (0, 0, 0)
    if n < 232:
        n -= 16
        return (n // 36, (n % 36) // 6, n % 6)
    return (n-232, n-232, n-232)


def ansi_colour_cube() -> list[list[int]]

'6x6x6 rgb colour cube including pastels (i.e. no repeated colours)'

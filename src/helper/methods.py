def apply_n(n, f, x, **kwargs):
    out = x
    for _ in range(n):
        out = f(out, **kwargs)
    return out

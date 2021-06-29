def sublists(l, max_len=None):
    for i in range(len(l)):
        if max_len:
            assert isinstance(max_len, int)
            for j in range(i, min(i + max_len, len(l))):
                yield l[i:j + 1]
        else:
            for j in range(i, len(l)):
                yield l[i:j + 1]


def apply_n(n, f, x):
    out = x
    for i in range(n):
        out = f(out)
    return out

from numpy import zeros, inf, ndim
from scipy.spatial.distance import cdist


def fastdtw(x, y, warp=1):

    assert len(x)
    assert len(y)

    if ndim(x) == 1:
        x = x.reshape(-1, 1)

    if ndim(y) == 1:
        y = y.reshape(-1, 1)

    r, c = len(x), len(y)
    d0 = zeros((r + 1, c + 1))
    d0[0, 1:] = inf
    d0[1:, 0] = inf
    d1 = d0[1:, 1:]
    d0[1:, 1:] = cdist(x, y)
    for i in range(r):
        for j in range(c):
            min_list = [d0[i, j]]
            for k in range(1, warp + 1):
                min_list += [d0[min(i + k, r - 1), j], d0[i, min(j + k, c - 1)]]
            d1[i, j] += min(min_list)

    acc = d1

    return acc

import math


def arc_circle_gen(arc_length, radius):
    template = []
    k = (radius * 2 - 1.0) / 2
    radius_square = radius * radius
    for i in range(arc_length):
        template.append([i, - math.sqrt(radius_square - (i - k) * (i - k)) + radius])
    return template


def arc_quadratic_gen(arc_length, a, b, c):
    template = []
    for i in range(arc_length):
        template.append([i, (a * i + b) * i + c])
    return template


def arc_generator(arc_length, bottom):
    template = []
    mid = int(arc_length / 2)
    a = bottom / (arc_length * arc_length)
    for i in range(arc_length):
        template.append([i, a * (i - mid) * (i - mid)])
    return template


def arc_union(l, length):
    length_l = len(l)
    finished = False
    while length_l > 1 and not finished:
        if len(l) == 1:
            finished = True
        for e in range(1, len(l) + 1):
            if e == len(l):
                finished = True
            else:
                if l[e] - l[e - 1] < length:
                    del l[e]
                    break
        if finished:
            break
    return l


def horizon_check(date_index, price, arc_length):
    threshold = 0.02
    len_date = len(date_index)
    date_tag = []
    real_index = []
    for i in range(len_date):
        idx = date_index[i]
        a = price[idx]
        b = price[idx + arc_length - 1]
        date_tag.append(True)
        if abs(a - b) / min(a, b) > threshold:
            date_tag[i] = False
            print('c =', abs(a - b) / min(a, b))
    for i in range(len_date):
        if date_tag[i]:
            real_index.append(date_index[i])
    return real_index


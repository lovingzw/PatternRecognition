import numpy as np
import matplotlib.pyplot as plt
from dtw import fastdtw
import matplotlib as mpl
from arc import arc_circle_gen
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
import math
from template import template_gen

tem1 = arc_circle_gen(32, 16)
tem2 = template_gen('circle', 32, 16, 1.0)
print(tem1)
print(tem2)

tem1rev = []
for i in range(30):
    tem1rev.append([tem1[i][0], 15-tem1[i][1]])

print(fastdtw(tem1, tem2)[29][29])
print(fastdtw(tem1rev, tem2)[29][29])




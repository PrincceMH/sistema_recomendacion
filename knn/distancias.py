from math import sqrt
import pandas as pd

def distancia_euclidiana(v1, v2):
    suma = sum((a - b) ** 2 for a, b in zip(v1, v2) if not pd.isna(a) and not pd.isna(b))
    return sqrt(suma)

def distancia_manhattan(v1, v2):
    suma = sum(abs(a - b) for a, b in zip(v1, v2) if not pd.isna(a) and not pd.isna(b))
    return suma

def similitud_coseno(v1, v2):
    sum_xy = sum_x2 = sum_y2 = 0
    for a, b in zip(v1, v2):
        if not pd.isna(a) and not pd.isna(b):
            sum_xy += a * b
            sum_x2 += a ** 2
            sum_y2 += b ** 2
    if sum_x2 == 0 or sum_y2 == 0:
        return -1
    return sum_xy / (sqrt(sum_x2) * sqrt(sum_y2))

def correlacion_pearson(v1, v2):
    x = [a for a, b in zip(v1, v2) if not pd.isna(a) and not pd.isna(b)]
    y = [b for a, b in zip(v1, v2) if not pd.isna(a) and not pd.isna(b)]
    if not x or not y:
        return -1
    mean_x, mean_y = sum(x)/len(x), sum(y)/len(y)
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = sqrt(sum((a - mean_x) ** 2 for a in x))
    den_y = sqrt(sum((b - mean_y) ** 2 for b in y))
    if den_x == 0 or den_y == 0:
        return -1
    return num / (den_x * den_y)

from math import sqrt
import pandas as pd

def distancia_euclidiana(v1, v2):
    suma = 0
    for a, b in zip(v1, v2):
        if pd.notna(a) and pd.notna(b):
            suma += (float(a) - float(b)) ** 2
    return sqrt(suma)

def distancia_manhattan(v1, v2):
    suma = 0
    for a, b in zip(v1, v2):
        if pd.notna(a) and pd.notna(b):
            suma += abs(float(a) - float(b))
    return suma

def similitud_coseno(v1, v2):
    sum_xy = 0
    sum_x2 = 0
    sum_y2 = 0
    for a, b in zip(v1, v2):
        if pd.notna(a) and pd.notna(b):
            x = float(a)
            y = float(b)
            sum_xy += x * y
            sum_x2 += x ** 2
            sum_y2 += y ** 2
    if sum_x2 == 0 or sum_y2 == 0:
        return None
    return sum_xy / (sqrt(sum_x2) * sqrt(sum_y2))

def correlacion_pearson(v1, v2):
    x_vals = []
    y_vals = []
    for a, b in zip(v1, v2):
        if pd.notna(a) and pd.notna(b):
            x_vals.append(float(a))
            y_vals.append(float(b))
    if len(x_vals) == 0:
        return None
    mean_x = sum(x_vals) / len(x_vals)
    mean_y = sum(y_vals) / len(y_vals)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
    den_x = sqrt(sum((x - mean_x) ** 2 for x in x_vals))
    den_y = sqrt(sum((y - mean_y) ** 2 for y in y_vals))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)

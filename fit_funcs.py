import numpy as np

from tools import gaussianElimination


# 多项式拟合
def polynomialFit(x, y, degree):
    n = degree + 1  # 多项式系数个数：有多少个系数就有多少个方程
    A = [[0 for _ in range(n)] for _ in range(n)]  # 创建系数矩阵，初始化为0
    # 遍历矩阵赋值 ---> 确定A矩阵
    for i in range(len(A)):
        # 确定该行最大次数
        max_times = degree + i
        for j in range(len(A[i])):
            # 确定该元素次数
            cur_times = max_times - j
            # 矩阵元素赋值
            A[i][j] = sum([xk ** cur_times for xk in x])
    # 确定b矩阵 = Σ
    b = [0 for _ in range(n)]
    for i in range(len(b)):
        b[i] = sum([y[idx] * (xk ** i) for idx, xk in enumerate(x)])

    # 通过高斯列消元得到了多项式拟合曲线的系数，从高次到低次
    coeffs = gaussianElimination(A, b)
    return coeffs


def exponential(x, a, b):
    return a * np.exp(b * x)


def logarithmic(x, a, b):
    return a * np.log(b * x)


def sine(x, a, b, c):
    return a * np.sin(b * x + c)


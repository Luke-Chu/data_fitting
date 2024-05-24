import copy

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


# 展示错误信息
def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("错误")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    # 设置图标
    msg_box.setWindowIcon(QIcon("images/error.svg"))
    msg_box.exec_()


# 获取字体
def get_font(family_: str = '微软雅黑', bold: bool = False, size_: int = 40, weight_: int = 50):
    font = QtGui.QFont()
    font.setFamily(family_)
    font.setBold(bold)
    font.setPointSize(size_)
    font.setWeight(weight_)
    return font


# 高斯列主元消去
def gaussianElimination(A, b):
    n = len(b)
    M = copy.deepcopy(A)

    for i in range(n):
        maxEl = abs(M[i][i])
        maxRow = i
        for k in range(i + 1, n):
            # 在每一列，从当前行开始，寻找绝对值最大的元素所在的行（主元）
            if abs(M[k][i]) > maxEl:
                maxEl = abs(M[k][i])
                maxRow = k
        # 将找到的主元所在行与当前行交换，以确保主元位于对角线上
        for k in range(i, n):
            M[maxRow][k], M[i][k] = M[i][k], M[maxRow][k]
        # 对应地，交换常数向量𝑏中的元素
        b[maxRow], b[i] = b[i], b[maxRow]

        # 对于当前行以下的所有行，通过消去当前列的元素，形成上三角矩阵
        for k in range(i + 1, n):
            c = -M[k][i] / M[i][i]  # 用于消去元素的乘数
            # 把i行乘以系数c后加到第k行上
            for j in range(i, n):
                if i == j:
                    M[k][j] = 0
                else:
                    M[k][j] += c * M[i][j]
            b[k] += c * b[i]
    # 回代过程
    x = [0 for _ in range(n)]  # 初始解
    # 从最后一行开始，逐行向上计算每个变量的值
    for i in range(n - 1, -1, -1):
        x[i] = b[i] / M[i][i]
        for k in range(i - 1, -1, -1):
            b[k] -= M[k][i] * x[i]

    return x


# 获取多项式拟合的拟合函数
def get_poly_fun(coeffs: list) -> str:
    # 确定多项式的次数
    degree = len(coeffs) - 1
    fun_str = 'Y = '
    # 判断是不是第一个
    first = True
    for c in coeffs:    # 考虑是不是0，是考虑真值是否为0，而不是考虑保留值
        cr = round(c, 4)  # 保留小数点
        # 用于判断正负数
        neg = False
        if c < 0:
            neg = True
        # 确定符号+数字字符串： 如果是0，就没有这项了
        if not first and not neg:   # 不是第一项并且不是负数
            cs = f' + {cr}'
        elif not first and neg:   # 不是第一项，是负数
            cs = f' - {abs(cr)}'
        elif first and neg:
            cs = f'- {abs(cr)}'
        else:  # 是第一项，正数
            cs = f'{cr}'
        # 然后拼接
        fun_str = fun_str + cs + f'X^{degree}'
        # 度数减去1
        degree -= 1
        # 不是第一个了
        first = False
    return fun_str


# 根据拟合类型和系数获取拟合函数
def get_fit_funcs(coeffs: list, fit_type: str) -> str:
    fit_func = None
    if fit_type == "Polynomial":
        fit_func = get_poly_fun(coeffs)
    elif fit_type == "Exponential":
        fit_func = f'y = {round(coeffs[0])}e^({round(coeffs[1])}x)'
    elif fit_type == "Logarithmic":
        fit_func = f'y = {round(coeffs[0], 4)}log({round(coeffs[1], 4)}x)'
    elif fit_type == "Sine":
        if coeffs[2] < 0:
            fit_func = f'y = {round(coeffs[0], 4)}sin({round(coeffs[1], 4)}x - {abs(round(coeffs[2], 4))})'
        else:
            fit_func = f'y = {round(coeffs[0], 4)}sin({round(coeffs[1], 4)}x + {round(coeffs[2], 4)})'

    return fit_func

import csv
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QIntValidator
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLineEdit, QLabel, QComboBox,
                             QFormLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGridLayout, QHBoxLayout, QFileDialog, QSizePolicy, QSplitter)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.optimize import curve_fit

from fit_funcs import exponential, logarithmic, sine, polynomialFit
from tools import get_font, show_error_message, get_fit_funcs


class DataFittingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 获取屏幕分辨率
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # 计算窗口大小为屏幕的三分之二
        window_width = screen_width * 1 // 2
        window_height = screen_height * 2 // 3

        # 计算窗口左上角位置，使其居中显示
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        # 设置窗口几何参数
        self.setGeometry(window_x, window_y, window_width, window_height)
        self.setWindowTitle("Data Fitting Application")
        # self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.createInputForm()
        self.createTable()
        self.createPlot()

        # 设置大小策略
        self.inputForm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 创建QSplitter
        splitter = QSplitter(Qt.Vertical)

        # 将控件添加到QSplitter
        splitter.addWidget(self.inputForm)
        splitter.addWidget(self.tableWidget)
        splitter.addWidget(self.canvas)

        self.layout.addWidget(splitter)

        self.x_data = []
        self.y_data = []

        # 保存绘图时散点图和线图的句柄
        self.scatter = None
        self.line = None

        # 设置图标
        self.setWindowIcon(QIcon("images/icon.jpg"))

        # 设置全局字体 默认就好
        # self.set_global_font()

        # 用于定位是否修改了数据列表的某个数据
        self.old_value = None
        self.current_item = None

    def set_global_font(self):
        # 设置中文为宋体
        chinese_font = QFont("SimSun", 11)
        self.setFont(chinese_font)

        # 设置英文为 Times New Roman
        english_font = QFont("Times New Roman", 11)
        self.setFont(english_font)

    # 创建输入数据表单
    def createInputForm(self):
        # 输入表单容器
        self.inputForm = QWidget()
        self.inputLayout = QVBoxLayout(self.inputForm)  # 整个表单布局
        hexLayout = QHBoxLayout()  # 表单上半部分的水平布局
        formLayout1 = QVBoxLayout()  # 表单上半部分左边表单布局
        delLayout = QGridLayout()  # 表单上半部分右边删除按钮的布局
        self.formLayout2 = QFormLayout()  # 表单下半部分布局

        # 添加表单上半左边部分组件
        self.xInput = QLineEdit()
        self.xInput.setPlaceholderText("请输入自变量数据，以逗号或空格分隔")
        self.yInput = QLineEdit()
        self.yInput.setPlaceholderText("请输入因变量数据，以逗号或空格分隔")
        # 给个垂直布局
        vInputLayout = QFormLayout()
        vInputLayout.addRow("X:", self.xInput)
        vInputLayout.addRow("Y:", self.yInput)
        # 组合输入框和文件输入
        hexInputLayout = QHBoxLayout()
        # CSV 文件输入按钮
        self.csv_button = QPushButton("文件\n导入")
        self.csv_button.clicked.connect(self.import_csv)
        # 设置按钮大小
        self.csv_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        hexInputLayout.addLayout(vInputLayout)
        hexInputLayout.addWidget(self.csv_button)

        self.addButton = QPushButton("添加数据")
        # 创建信号与槽
        self.addButton.clicked.connect(self.addDataPoint)
        # 将组件添加到布局
        formLayout1.addLayout(hexInputLayout)
        formLayout1.addWidget(self.addButton)

        # 添加表单上半右边删除组件
        self.delBtn = QPushButton('\n一键\n清除\n')
        self.delBtn.setFont(get_font(family_='SimSum', size_=11, weight_=11))
        delLayout.addWidget(self.delBtn)
        # 创建信号与槽
        self.delBtn.clicked.connect(self.oneClickClear)
        # 然后组合上半布局
        hexLayout.addLayout(formLayout1)
        hexLayout.addLayout(delLayout)

        # 添加表单下半部分组件
        self.functionLabel = QLabel("选择拟合函数：")
        # 创建下拉选择框，用于选择拟合函数
        self.functionComboBox = QComboBox()
        self.functionComboBox.addItems(["Polynomial", "Exponential", "Logarithmic", "Sine"])
        # 连接信号与槽
        self.functionComboBox.currentIndexChanged.connect(self.onComboBoxIndexChanged)
        # 添加多项式次数组件
        self.degreeLabel = QLabel("多项式次数：")
        self.degreeInput = QLineEdit()
        self.degreeInput.setValidator(QIntValidator(0, 9))  # 限制输入次数范围
        self.degreeInput.setPlaceholderText("请输入多项式最高次数")
        # 拟合按钮组件
        self.fitButton = QPushButton("数据拟合")
        self.fitButton.clicked.connect(self.fitData)
        # 添加下半组件到布局
        self.formLayout2.addRow(self.functionLabel, self.functionComboBox)
        self.formLayout2.addRow(self.degreeLabel, self.degreeInput)
        self.formLayout2.addRow(self.fitButton)

        # 组合布局
        self.inputLayout.addLayout(hexLayout)
        self.inputLayout.addLayout(self.formLayout2)

    # 文件输入按钮的槽函数
    def import_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import CSV/TXT", "",
                                                   "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            x_values = []
            y_values = []
            if file_name.endswith('.csv'):
                with open(file_name, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if len(row) >= 2:
                            x_values.append(row[0])
                            y_values.append(row[1])
            elif file_name.endswith('.txt'):
                with open(file_name, 'r') as txtfile:
                    lines = txtfile.readlines()
                    for line in lines:
                        row = re.split(r'[ ,]+', line.strip())
                        if len(row) >= 2:
                            x_values.append(row[0])
                            y_values.append(row[1])

            # 将数据填充到输入框中
            self.xInput.setText(','.join(x_values))
            self.yInput.setText(','.join(y_values))

    # 创建数据显示表格
    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)  # 两列
        self.tableWidget.setHorizontalHeaderLabels(["X", "Y"])
        # 设置水平表头列的自动调整模式为拉伸
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 连接 currentItemChanged 信号到槽函数
        self.tableWidget.currentItemChanged.connect(self.onCurrentItemChanged)
        # 将单元格修改信号连接到槽函数
        self.tableWidget.itemChanged.connect(self.onItemChanged)

    # 创建绘图区
    def createPlot(self):
        plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 宋体和Time New Roman
        self.figure, self.ax = plt.subplots()
        # 将 Matplotlib 图表嵌入到 GUI 应用程序中
        self.canvas = FigureCanvas(self.figure)
        # 设置 FigureCanvas 的大小策略为 Expanding
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # 根据拟合函数选择判断是否需要给多项式拟合的最高次数
    def onComboBoxIndexChanged(self, index):
        # 根据下拉选择框的选择，决定是否显示输入框
        if index == 0:
            # 如果选择了第一个选项，则添加输入框
            self.formLayout2.insertRow(1, self.degreeLabel, self.degreeInput)
        else:
            # 如果选择了其他选项，则移除输入框
            self.degreeLabel.setParent(None)
            self.degreeInput.setParent(None)

    # 在用户切换当前单元格时触发，记录当前单元格和其旧值
    def onCurrentItemChanged(self, current):
        if current is not None:
            self.current_item = current
            self.old_value = current.text()  # 确保初始 old_value 是当前项的值

    # 表格数据改变的槽函数
    def onItemChanged(self, item):
        if self.current_item is item:
            new_value = item.text()
            if new_value == "":  # 如果新值为空，则恢复旧值
                item.setText(self.old_value)
                show_error_message('无效值')
                return
            else:
                # 更新旧值为新值
                self.old_value = new_value

        # 获取所有数据并排序
        self.x_data, self.y_data = self.get_all_data()
        self.sort_data()

        # 移除 scatter 图并重新绘制
        self.scatter.remove()
        self.scatter = self.ax.scatter(self.x_data, self.y_data, color='red', label='Data Points')
        self.ax.legend()
        self.canvas.draw()

    # 获取表格所有数据
    def get_all_data(self):
        # 在本程序中 该变量是一个二维列表：横代表点，纵代表自变量X 和 自变量Y
        x_datas = []
        y_datas = []
        for row in range(self.tableWidget.rowCount()):
            x_item = self.tableWidget.item(row, 0)
            y_item = self.tableWidget.item(row, 1)
            if x_item is not None and y_item is not None:
                x_datas.append(float(x_item.text()))
                y_datas.append(float(y_item.text()))
        return x_datas, y_datas

    # 添加数据
    def addDataPoint(self):
        try:
            # 用了一个正则表达式匹配一个逗号和一个空格的任意组合
            x_values = re.split(r'[ ,]+', self.xInput.text().strip())
            y_values = re.split(r'[ ,]+', self.yInput.text().strip())
            if len(x_values) != len(y_values):
                raise ValueError("数据长度不匹配")
            if not self.xInput.text().strip():
                raise ValueError('请输入拟合数据')
            # 暂时断开信号槽连接
            self.tableWidget.blockSignals(True)
            # 处理输出数据
            for x_str, y_str in zip(x_values, y_values):
                x = float(x_str.strip())
                y = float(y_str.strip())
                self.x_data.append(x)
                self.y_data.append(y)

                # 获取表格的行数，插入到表格中显示
                rowPosition = self.tableWidget.rowCount()
                # 新插入一行
                self.tableWidget.insertRow(rowPosition)
                # 设置X和Y的值
                self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(x)))
                self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(y)))
            # 重新连接信号槽
            self.tableWidget.blockSignals(False)

            # 对值排序
            self.sort_data()

            # 绘制 scatter 图并保存句柄
            if self.scatter is not None:
                self.scatter.remove()
            self.scatter = self.ax.scatter(self.x_data, self.y_data, color='red', label='Data Points')
            self.ax.legend()
            self.canvas.draw()

            self.xInput.clear()
            self.yInput.clear()
        except ValueError as e:
            show_error_message(str(e))

    # 将x和y按照x值升序排序，以免画线图出错
    def sort_data(self):
        # 将x_data和y_data升序排序以便画线图: 先将两个列表合成一个
        combined = list(zip(self.x_data, self.y_data))
        # 再按照x值升序排序
        sorted_combined = sorted(combined, key=lambda x_: x_[0])
        # 然后解压回两个列表
        sorted_x_data, sorted_y_data = zip(*sorted_combined)
        self.x_data = list(sorted_x_data)
        self.y_data = list(sorted_y_data)

    # 清除数据
    def oneClickClear(self):
        # 清楚输入的自变量因变量数据
        self.xInput.clear()
        self.yInput.clear()
        self.x_data = []
        self.y_data = []
        # 清除最高次数
        self.degreeInput.clear()
        # 清除数据展示区和绘图区
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        # 表结构完全被重置，需要重新设置
        self.tableWidget.setColumnCount(2)  # 两列
        self.tableWidget.setHorizontalHeaderLabels(["X", "Y"])
        self.ax.clear()
        # 刷新绘图
        self.canvas.draw()

    # 数据拟合槽函数
    def fitData(self):
        try:
            row_count = self.tableWidget.rowCount()
            if row_count < 1:
                raise ValueError('请添加拟合数据')
            fit_type = self.functionComboBox.currentText()
            if fit_type == "Polynomial":
                # 对于多项式拟合来说，应该先判断给的点的个数是否大于拟合函数的最高次数
                degree = int(self.degreeInput.text())
                if row_count <= degree:
                    raise ValueError(f'数据点不足以支撑拟合{degree}次多项式')
                degree = int(self.degreeInput.text())
                coeffs = polynomialFit(self.x_data, self.y_data, degree)
                self.plotData(coeffs, fit_type)
            elif fit_type == "Exponential":
                # 对于指数函数拟合来说，点的个数至少为2个，因为有2个待求系数
                if row_count < 2:
                    raise ValueError(f'数据点不足以支撑拟合拟合函数')
                # 返回即残差最小时参数的值
                popt, _ = curve_fit(exponential, self.x_data, self.y_data)
                self.plotData(popt, fit_type)
            elif fit_type == "Logarithmic":
                # 对于对数函数拟合来说，点的个数至少为2个，因为有2个待求系数
                if row_count < 2:
                    raise ValueError(f'数据点不足以支撑拟合对数函数')
                popt, _ = curve_fit(logarithmic, self.x_data, self.y_data)
                self.plotData(popt, fit_type)
            elif fit_type == "Sine":
                # 对于正弦函数拟合来说，点的个数至少为3个，因为有3个待求系数
                if row_count < 3:
                    raise ValueError(f'数据点不足以支撑拟合对数函数')
                popt, _ = curve_fit(sine, self.x_data, self.y_data)
                self.plotData(popt, fit_type)
        except ValueError as e:
            show_error_message(str(e))

    def plotData(self, coeffs, fit_type):
        # 生成拟合线的 x 坐标
        x_fit = np.linspace(min(self.x_data), max(self.x_data), 100)
        if fit_type == "Polynomial":
            # 计算多项式拟合曲线，polyval函数需要的次数是从高次到低次
            y_fit = np.polyval(coeffs, x_fit)
        elif fit_type == "Exponential":
            y_fit = exponential(x_fit, *coeffs)
        elif fit_type == "Logarithmic":
            y_fit = logarithmic(x_fit, *coeffs)
        elif fit_type == "Sine":
            y_fit = sine(x_fit, *coeffs)
        else:
            show_error_message('异常错误')
            return

        if self.line:
            line = self.line[0]  # 获取列表中的第一个线条对象
            line.remove()  # 移除线条对象
        self.line = self.ax.plot(x_fit, y_fit, label=f'{fit_type} Fit')

        # 设置图的标题
        self.ax.set_title(get_fit_funcs(coeffs, fit_type))

        # 使坐标轴自适应数据范围
        self.ax.relim()
        self.ax.autoscale_view()

        self.ax.legend()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataFittingApp()
    window.show()
    sys.exit(app.exec_())

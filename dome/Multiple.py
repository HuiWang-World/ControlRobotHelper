import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建表格
        self.table = QTableWidget()
        self.table.setRowCount(5)  # 设置行数
        self.table.setColumnCount(3)  # 设置列数

        # 填充示例数据
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                # 根据列给不同长度的数据，模拟内容长度不同
                text = f"Item {i},{j}" + ' extra text' * j  # 假设第j列有更多的内容
                self.table.setItem(i, j, QTableWidgetItem(text))

        # 在填充完数据后调用，自适应列宽
        self.table.resizeColumnsToContents()

        # 设置窗口布局
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        # 设置窗口的中央小部件
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 设置窗口标题
        self.setWindowTitle("QTableWidget Auto Column Width")

# 运行应用程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

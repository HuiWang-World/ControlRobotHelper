import sys
# sqlite3 本地数据库
import sqlite3
# QT 6 相关包引入
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QToolBar, QTableWidget, QWidget, QHeaderView,
                               QPushButton, QMessageBox, QLineEdit, QCheckBox, QHBoxLayout, QRadioButton,
                               QTableWidgetItem)
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator, QIcon
from PySide6.QtCore import Qt, QRegularExpression
# uuid
import uuid

# 线程执行类
from util.WorkerThread import WorkerThread
# 线程策略
from util.WorkerBotStrategy import WorkerBotStrategy
# 权限工具
from util.Power import Power
# 面向对象
from bot.model.Machine import Machine

# IPv4
ipv4Regex = QRegularExpression(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
# 开始按钮
start = "开始"
# 停止按钮
stop = "停止"


# 构建复选框
def buildCheckBox():
    # 创建一个Widget来放置CheckBox
    widget = QWidget()
    checkBox = QCheckBox()
    # 使用布局来居中CheckBox
    layout = QHBoxLayout(widget)
    layout.addWidget(checkBox)
    layout.setAlignment(Qt.AlignCenter)  # 居中对齐
    layout.setContentsMargins(0, 0, 0, 0)  # 无边距
    widget.setLayout(layout)
    return widget


def buildRadioButton(self, row):
    # 创建单选按钮容器
    widget = QWidget()
    layout = QHBoxLayout(widget)  # 使用水平布局

    strategyOption = WorkerBotStrategy().getBotStrategyOption()
    # 创建并添加多个单选按钮到容器
    for i in range(len(strategyOption)):  # 示例中每个单元格添加3个单选按钮
        radio_button = QRadioButton(strategyOption[i])
        layout.addWidget(radio_button)
        # 默认选中每行的第一个单选按钮
        if i == 0:
            radio_button.setChecked(True)
            # 重新设置窗口大小 根据选项数量重新设置窗口宽度
            width = 500 + (len(strategyOption) * 15)
            height = self.size().height()
            self.resize(width, height)
    layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距
    widget.setLayout(layout)
    return widget


# 窗口类
class MainWindow(QMainWindow):
    # 构造方法
    def __init__(self,machineNum):
        super().__init__()
        # 数量控制
        self.machineNum = machineNum
        self.initUI()

        self.existingMachineNumbers = {}
        self.threads = {}
        self.initDB()
        self.loadData()
        # 初始化状态栏
        self.statusBar().showMessage('')

    # 初始化数据库
    def initDB(self):
        self.db = sqlite3.connect("database/machines.db")
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS machines (
                            id TEXT PRIMARY KEY,
                            machine_number INTEGER UNIQUE,
                            machine_ip TEXT,
                            execute_type TEXT)''')
        self.db.commit()

    def initUI(self):
        self.resize(500, 600)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.toolbar = QToolBar("工具栏")
        self.addToolBar(self.toolbar)
        self.toolbar.addAction("添加", self.addRow)
        self.toolbar.addAction("保存", self.saveData)
        self.toolbar.addAction("删除", self.deleteSelectedRows)
        # 设置工具栏不可移动
        self.toolbar.setMovable(False)

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(["选项", "ID", "机器编号", "机器IP", "类型", "操作"])
        self.table.setColumnHidden(1, True)
        self.table.verticalHeader().setVisible(False)

        # 平均分布
        # for i in range(2, 6):
        #    self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        layout.addWidget(self.table)

    # 加载数据
    def loadData(self):
        self.table.setRowCount(0)
        self.table.clearContents()
        self.table.viewport().update()
        self.existingMachineNumbers = {}
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM machines order by machine_number")
        for machine in cursor.fetchall():
            self.addRowWithData(machine[0], str(machine[1]), machine[2], machine[3])
        # 设置伸缩模式
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount() - 1):
            # 连接toggled信号到槽函数
            # 添加自动保存
            radio_Widget = self.table.cellWidget(col, 4)
            if radio_Widget:
                # 宽度自适应
                self.table.resizeColumnsToContents()
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.Stretch)
                # 查找子按钮 添加选中事件
                radio_buttons = radio_Widget.findChildren(QRadioButton)
                for radio_button in radio_buttons:
                    radio_button.toggled.connect(
                        lambda checked, rb=radio_button, r=col: self.onRadioButtonToggled(checked, rb, r))
        self.toolbar.setFocus()

    # 表格里面添加一行数据
    def addRowWithData(self, id, machine_number, machine_ip, execute_type):
        rowPosition = self.addRow(id)
        # 控制行数
        if None == rowPosition:
            return None
        # id
        self.table.cellWidget(rowPosition, 1).setText(id)
        # 机器编号
        self.table.cellWidget(rowPosition, 2).setText(machine_number)
        # 机器IP
        self.table.cellWidget(rowPosition, 3).setText(machine_ip)
        # 设置选中位置
        # 单选按钮组
        radio_buttons = self.table.cellWidget(rowPosition, 4).findChildren(QRadioButton)
        for radio_button in radio_buttons:
            if execute_type == radio_button.text():
                radio_button.setChecked(True)

        # 运行类型
        runFlag = False  # 是否在运行
        buttonName = start
        for item in self.threads.items():
            thread_id = item[0]
            if thread_id == id:
                # 按钮名称
                runFlag = True
                buttonName = stop if (True == item[1].running) else start
        # 没有运行默认开始状态
        self.table.cellWidget(rowPosition, 5).setText(buttonName)
        # 设置可以编辑状态
        self.changeEdit(rowPosition, runFlag)
        # 添加缓存数据
        self.existingMachineNumbers[id] = machine_number

    # 添加一行数据，传入了uuid则使用传入的ID，否则使用生成的ID
    def addRow(self, uuidSrt=None):
        # 获取所有行
        rowPosition = self.table.rowCount()
        # 数量控制
        if self.machineNum <= rowPosition:
            return None;
        # 一次只能添加一行
        for row in range(rowPosition):
            id = self.table.cellWidget(row, 1).text()
            machine_number = self.table.cellWidget(row, 2).text()
            machine_ip = self.table.cellWidget(row, 3).text()
            if not machine_number and not machine_ip:
                QMessageBox.information(self, "提示", "请勿重复添加，一次只能添加一行。")
                return
        # 生成uuid
        uuidSrt = uuidSrt if uuidSrt else uuid.uuid4()
        self.table.insertRow(rowPosition)
        # 复选框
        # checkBox = QCheckBox()
        # self.table.setCellWidget(rowPosition, 0, checkBox)
        self.table.setCellWidget(rowPosition, 0, buildCheckBox())
        # id
        self.table.setCellWidget(rowPosition, 1, QLineEdit(str(uuidSrt)))
        # 设备编号
        machineNumberItem = QLineEdit()
        machineNumberItem.setValidator(QIntValidator(0, 99999))
        machineNumberItem.editingFinished.connect(
            lambda mn=machineNumberItem, rp=rowPosition: self.checkUniqueMachineNumber(mn, rp, 2))
        self.table.setCellWidget(rowPosition, 2, machineNumberItem)
        # machineNumberItem.setFocus()
        # 设备IP
        machineIPItem = QLineEdit()
        machineIPItem.setValidator(QRegularExpressionValidator(ipv4Regex))
        self.table.setCellWidget(rowPosition, 3, machineIPItem)

        # 设置单选按钮
        executeTypeItem = buildRadioButton(self, rowPosition)
        self.table.setCellWidget(rowPosition, 4, executeTypeItem)
        # 开始/暂停按钮
        actionButton = QPushButton()
        actionButton.clicked.connect(lambda: self.toggleAction(actionButton, rowPosition))
        self.table.setCellWidget(rowPosition, 5, actionButton)

        return rowPosition

    # 输入检查
    def checkUniqueMachineNumber(self, machineNumberWidget, row, col):
        currentNumber = machineNumberWidget.text()
        # 没有数据
        if not currentNumber:
            return
        # 获取ID
        id = self.table.cellWidget(row, 1).text()

        # 验证是否存在相同数据
        if [i for i in self.existingMachineNumbers if i != id and currentNumber == self.existingMachineNumbers[i]]:
            machineNumberWidget.clear()
            machineNumberWidget.setFocus()
            QMessageBox.information(self, "提示", "重复的机器编号，机器编号必须唯一。")
        else:
            self.existingMachineNumbers[id] = currentNumber
            self.saveData()

            '''
            # 触发排序
            for index in range(self.table.rowCount()):
                item = QTableWidgetItem()
                self.table.setItem(index, col, item)
                item.setData(Qt.EditRole, int(self.table.cellWidget(index, col).text()))  # 设置或更新数据
            self.table.sortItems(col, Qt.AscendingOrder)  # 按列排序
            '''

    # 启动设备
    def toggleAction(self, button, row):
        machine = self.findRow(button)
        if button.text() == start:
            id = machine[0]
            machine_ip = machine[2]
            # 验证是不是标准的IPv4
            if ipv4Regex.match(machine_ip).hasMatch():
                machineModel = Machine(machine[0], machine[1], machine[2], machine[3])  # 转对象
                thread = WorkerThread(machineModel)
                if thread.bot.init:
                    thread.start()
                    self.threads[id] = thread
                    self.changeEdit(row, True)
                    button.setText(stop)
                else:
                    QMessageBox.information(self, "提示", "设备初始化失败，请确认IP是否有效，检查IP是否能够联通")
            else:
                QMessageBox.information(self, "提示", "IP地址错误，请输入完整的IP地址")
        else:
            button.setText(start)
            id = machine[0]
            if id in self.threads:
                self.changeEdit(row, False)
                self.threads[id].stop()
                del self.threads[id]

    # 根据按钮查找操作对象
    def findRow(self, widget):
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 5) == widget:
                execute_type = self.getCheckedRadioButton(row).text()
                return [self.table.cellWidget(row, 1).text(), self.table.cellWidget(row, 2).text(),
                        self.table.cellWidget(row, 3).text(), execute_type]
        return -1

    # 保存数据
    def saveData(self):
        self.toolbar.setFocus()
        cursor = self.db.cursor()
        for row in range(self.table.rowCount()):
            id = self.table.cellWidget(row, 1).text()
            machine_number = self.table.cellWidget(row, 2).text()
            machine_ip = self.table.cellWidget(row, 3).text()
            execute_type = self.getCheckedRadioButton(row).text()
            # 按钮名称，名称为空表示添加，不为空则修改数据
            buttonName = self.table.cellWidget(row, 5).text()
            if machine_number or machine_ip:
                if buttonName:
                    cursor.execute(
                        "UPDATE machines set machine_number = ? , machine_ip = ?,execute_type=? where id = ?",
                        (machine_number, machine_ip, execute_type, id))
                else:
                    cursor.execute(
                        "INSERT INTO machines (id,machine_number, machine_ip,execute_type) VALUES (?,?, ?,?)",
                        (id, machine_number, machine_ip, execute_type))
        self.db.commit()
        mainWindow.statusBar().showMessage("保存成功！", 500)
        self.loadData()

    # 删除数据
    def deleteSelectedRows(self):
        cursor = self.db.cursor()
        for row in range(self.table.rowCount() - 1, -1, -1):
            chkBoxWidget = self.table.cellWidget(row, 0)
            id = self.table.cellWidget(row, 1).text()
            if chkBoxWidget and chkBoxWidget.children()[1].isChecked():
                # if chkBoxWidget and chkBoxWidget.isChecked():
                # 正在运行不允许删除
                if [i for i in self.threads if i == id and True == self.threads[i].running]:
                    QMessageBox.information(self, "提示", "当前机器正在运行，不能删除。")
                else:
                    idWidget = self.table.cellWidget(row, 1)
                    id = idWidget.text()
                    # 清除缓存数据
                    if [i for i in self.existingMachineNumbers if id == self.existingMachineNumbers[i]]:
                        del self.existingMachineNumbers[id]
                    # 删除数据库数据
                    cursor.execute("DELETE FROM machines WHERE id = ?", (id,))
                    # 清除表格数据
                    self.table.removeRow(row)
                    self.db.commit()
        # 循环完成开始查询
        self.loadData()
        mainWindow.statusBar().showMessage("删除成功！", 500)

    # 获取单选按钮名称
    def getCheckedRadioButton(self, row):
        # 单选按钮组
        radio_buttons = self.table.cellWidget(row, 4).findChildren(QRadioButton)
        for radio_button in radio_buttons:
            if radio_button.isChecked():
                return radio_button

    # 自动保存数据
    def onRadioButtonToggled(self, checked, rb, r):
        if checked:
            self.saveData()

    # 改变状态
    def changeEdit(self, row, status):
        self.table.cellWidget(row, 2).setReadOnly(status)
        self.table.cellWidget(row, 3).setReadOnly(status)
        self.table.cellWidget(row, 4).setEnabled(not status)
        # 按钮颜色
        if True == status:
            self.table.cellWidget(row, 5).setStyleSheet("background-color: lightcoral;")
        else:
            self.table.cellWidget(row, 5).setStyleSheet("background-color: lightblue;")


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon/icons.ico"))  # 设置图标
    # 数量控制 限制只能添加多少行数据
    machineNum = Power().getMachineNum('cjq')
    mainWindow = MainWindow(machineNum)
    mainWindow.setWindowTitle("PythonHelper")  # 修改标题
    mainWindow.show()
    sys.exit(app.exec())

# 多线程
import threading

# 执行策略
from util.WorkerBotStrategy import WorkerBotStrategy

# 面向对象
from bot.model.Machine import Machine


# threading.Thread 多线程类
class WorkerThread(threading.Thread):
    def __init__(self, machine):
        super().__init__()
        self.machine = machine
        self.bot = WorkerBotStrategy().getBotStrategy(self.machine)  # 获取对应执行类
        self.running = False
        self.daemon = True

    def run(self):
        self.running = True
        print(f"准备运行 {self.machine.id},{self.machine.machineNumber},{self.machine.machineIp},{self.machine.executeType}")
        if not self.bot.init or not self.running:
            print(f"初始化失败，停止运行 {self.machine.id},{self.machine.machineNumber},{self.machine.machineIp},{self.machine.executeType}")
            self.stop()
        else:
            # 初始化成功才运行
            while self.bot.init and self.running:
                threading.Event().wait(2)
                self.bot.execute(threading)

    def stop(self):
        self.running = False
        threading.Event().wait(1)
        print(
            f"停止运行 {self.machine.id},{self.machine.machineNumber},{self.machine.machineIp},{self.machine.executeType}")

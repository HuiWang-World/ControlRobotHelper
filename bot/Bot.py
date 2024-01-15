# 机器接口
class Bot:
    def __init__(self, machine):
        self.machine = machine
        self.init = False # 是否初始化成功

    def execute(self,threading):
        raise NotImplementedError  # 手动抛异常

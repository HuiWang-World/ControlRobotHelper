from bot.impl.Ruyi import Ruyi
from bot.impl.TestBot import TestBot

# 类型
strategyOption = ["如意", "TestBot"]


class WorkerBotStrategy():
    # 机器类型
    def getBotStrategy(self, machine):
        machineName = machine.executeType
        if "如意" == machineName:
            return Ruyi(machine)
        elif "TestBot" == machineName:
            return TestBot(machine)

    # 获取可以执行选项
    def getBotStrategyOption(self):
        return strategyOption

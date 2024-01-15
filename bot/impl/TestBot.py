from bot.Bot import Bot


class TestBot(Bot):
    def __init__(self, machine):
        super().__init__(machine)

    def execute(self,threading):  # 执行业务
        print('开始运行----------' + self.machine.executeType)

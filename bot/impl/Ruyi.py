from bot.Bot import Bot  # 父类
from bot.control.HttpControl import HttpControl  # http 控制
import json  # json 解析包
import sys

# 首页 任务 体现 按钮组
__tab_widget__ = 'android.widget.LinearLayout'

# -------------------- static begin
# 红包补偿 x y
__cl_red_x__, __cl_red_y__ = ((131 / 3) * 2), ((131 / 3) * 2)
# 福袋补偿
__iv_lottery_x__, __iv_lottery_y__ = ((131 / 3) * 2), ((131 / 3) * 2)
# 全都要补偿 x y
__tv_take_all_x__, __tv_take_all_y__ = ((450 / 3) * 2), ((120 / 3) * 2)
# 红包 ID
__cl_red_name__ = 'com.danyan.ruyi:id/cl_red'
# 福袋 ID
__iv_lottery__ = 'com.danyan.ruyi:id/iv_lottery'
# 全都要 ID
__tv_take_all__ = 'com.danyan.ruyi:id/tv_take_all'


class Ruyi(Bot):
    # sys.setrecursionlimit(10000000)

    def __init__(self, machine):
        super().__init__(machine)
        self._httpControl = HttpControl(self.machine.machineIp)
        self.tabPosition = {}  # 当前所在页面
        # 获取屏幕信息
        sceenSize = self._httpControl.getSceenSize()
        # 判断是否初始化成功
        if sceenSize:
            self.init = True
            # 显示屏信息
            self.sceenSize = json.loads(sceenSize)
            return

    def execute(self, threading):  # 执行业务
        print('开始运行----------' + self.machine.executeType)

        # 获取 全都要 元素
        tv_take_all = self._httpControl.getDom(__tv_take_all__)
        tv_take_all_arr = json.loads(tv_take_all)
        if 0 < len(tv_take_all_arr):
            # 循环 全都要 元素
            for dom in tv_take_all_arr:
                left, top, right, bottom = self.getPosition(dom)
                # 点击dom
                tap = self._httpControl.inputTap(self.getXY(left, top, right, bottom))
                print("点击全都要" + tap)
        else:
            self.getInitTabChecked()
            # 首页逻辑1
            if 0 < len(self.tabPosition) and True == self.tabPosition["首页"][0]:
                # 获取 福袋 元素
                iv_lottery = self._httpControl.getDom(__iv_lottery__)
                # 循环 福袋 元素
                for dom in json.loads(iv_lottery):
                    left, top, right, bottom = self.getPosition(dom)
                    # 点击dom
                    tap = self._httpControl.inputTap(self.getXY(left, top, right, bottom))
                    print("点击福袋" + tap)

                # 获取 红包 元素
                cl_red = self._httpControl.getDom(__cl_red_name__)
                # 循环 红包 元素
                for dom in json.loads(cl_red):
                    left, top, right, bottom = self.getPosition(dom)
                    # 点击dom
                    tap = self._httpControl.inputTap(self.getXY(left, top, right, bottom))
                    print("点击红包" + tap)
            elif 0 < len(self.tabPosition) and True == self.tabPosition["任务"][0]:
                print("任务页面延迟3秒")
                threading.Event().wait(3)
                left, top, right, bottom = self.tabPosition["首页"][1]
                tap = self._httpControl.inputTap(self.getXY(left, top, right, bottom))
                print("首页页面延迟1秒")
                threading.Event().wait(1)
                # 滑动屏幕
                self.swipe()

    # 获取元素 位置 left, top, right, bottom
    def getPosition(self, dom):
        return dom['payload']['position']

    def click(self, left, top):
        return self._httpControl.inputTap((left + __iv_lottery_x__), (top + __iv_lottery_y__))

    # 获取XY
    def getXY(self, left, top, right, bottom):
        return [(left + (((right - left) / 3) * 1.5)), (top + (((bottom - top) / 3) * 1.5))]

    # 递归获取所有元素
    def buildElement(self, domAll, domAllObj):
        for dom in domAll:
            if "children" in dom and dom['children'] and 0 < len(dom['children']):
                for childrenDom in dom['children']:
                    domAllObj.append(childrenDom)
                    self.buildElement([childrenDom], domAllObj)
            else:
                domAllObj.append(dom)

    # 初始化选中tab
    def getInitTabChecked(self):
        # 获取选中 tab
        tv_name = self._httpControl.getDomAll()
        domAll = []
        self.buildElement([json.loads(tv_name)], domAll)
        # tab 是否存在数据
        for dom in domAll:
            # 缓存临时位置
            if "name" in dom and dom['name'] == __tab_widget__:
                self.tabPosition[dom['children'][0]['payload']['text']] = [dom['payload']['selected'],
                                                                           self.getPosition(dom)]

    # 滑动屏幕
    def swipe(self):
        x = self.sceenSize['h'] / 2
        startY, endY = self.sceenSize['w'] / 4 * 3, self.sceenSize['w'] / 4 * 2
        self._httpControl.swipe(x, startY, x, endY)

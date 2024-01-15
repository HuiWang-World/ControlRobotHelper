# 导入 requests 包
import requests

# 默认端口
port = "1082"
# --------------------method name begin
# sceenSize 获取屏幕大小
sceenSize = "sceenSize"
# sceenSize 获取屏幕大小
dom = "dom"
# 点击屏幕
tap = "tap"
# 滑动屏幕
swipe = "swipe"


# --------------------method name end
# -------------------- static end
class HttpControl:

    ## 初始化
    def __init__(self, ip):
        self.ip = "http://" + ip + ":" + port + "/"

    # 获取屏幕大小
    def getSceenSize(self):
        return self._requestUrl(sceenSize)

    # 获取所有dom元素
    def getDomAll(self):
        return self._requestUrl(dom)

    # 获取指定dom
    def getDom(self, id):
        return self._requestUrl(dom + "?id=" + id)

    # 点击屏幕
    def inputTap(self, position):
        return self._requestUrl(tap + "?x=" + str(int(position[0])) + "&y=" + str(int(position[1])) + "&delay=0.1")

    #http://192.168.3.24:1082/swipe
    def swipe(self,start_x,start_y,end_x,end_y):
        return self._requestUrl(swipe+"?start_x="+str(int(start_x))+"&start_y="+str(int(start_y))+"&end_x="+str(int(end_x))+"&end_y="+str(int(end_y))+"&duration=0.2")

    # http 请求
    def _requestUrl(self, url):
        url = self.ip + url
        print("url:" + url)
        response = requests.get(url)
        # 调用失败返回None
        if 200 != response.status_code:
            # print(requests.status_codes._codes[response.status_code][0])
            return None
        else:
            return requests.get(url).text

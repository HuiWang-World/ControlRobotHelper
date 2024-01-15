# 导入 requests 包
import requests
# json 解析包
import json
# xml解析库
from lxml import etree


class Power:

    # 调用远程服务获取授权数量
    def getMachineNum(self, person):
        try:
            response = requests.get("https://blog.carnation.cc/Android-Control.html").text
            controlText = etree.HTML(response).xpath('//article/p/text()')[0]
            controlTextReplace = controlText.replace("”", "\"").replace("“", "\"")  # 解析替换
            parse = json.loads(controlTextReplace)
            return int(parse[person])
        except Exception:
            print("网络异常")
            return 0


if __name__ == '__main__':
    power = Power();
    number = power.getMachineNum('cjq')
    print(number)

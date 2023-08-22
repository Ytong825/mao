"""
@Qim出品 仅供学习交流，请在下载后的24小时内完全删除 请勿将任何内容用于商业或非法目的，否则后果自负。
微信阅读_V1.0   入口：https://i.postimg.cc/RV8Y0tQL/1692250358858.png
阅读文章抓出cookie，time，sign 建议手动阅读5篇左右再使用脚本，不然100%黑！！！一小时一次，每天到底几轮自己测试
export ydtoken=cookie@time@sign
time和sign只需要后面的
多账号用'===='隔开 例 账号1====账号2
cron：23 7-23/1 * * *
"""

import re

import os
import requests
response = requests.get('https://netcut.cn/p/e9a1ac26ab3e543b')
note_content_list = re.findall(r'"note_content":"(.*?)"', response.text)
formatted_note_content_list = [note.replace('\\n', '\n').replace('\\/', '/') for note in note_content_list]
for note in formatted_note_content_list:
    print(note)

# 获取 xwytoken 环境变量值
accounts = os.getenv('ydtoken')

# 检查 xwytoken 是否存在
if accounts is None:
    print('你没有填入ydtoken，咋运行？')
else:
    # 获取环境变量的值，并按指定字符串分割成多个账号的参数组合
    accounts_list = os.environ.get('ydtoken').split('====')

    # 输出有几个账号
    num_of_accounts = len(accounts_list)
    print(f"获取到 {num_of_accounts} 个账号")

    # 遍历所有账号
    for i, account in enumerate(accounts_list, start=1):
        # 按@符号分割当前账号的不同参数
        values = account.split('@')
        cookie, time, sign = values[0], values[1], values[2]
        # 输出当前正在执行的账号
        print(f"\n=======开始执行账号{i}=======")
        url = "http://2477726.9o.10r8cvn6b1.cloud/person/info"

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; V1923A Build/PQ3B.190801.06161913; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36 MMWEBID/5635 MicroMessenger/8.0.40.2420(0x28002837) WeChat/arm64 Weixin Android Tablet NetType/WIFI Language/zh_CN ABI/arm64",
            "Cookie": cookie
        }

        data = {
            "time": time,
            "sign": sign
        }

        response = requests.get(url, headers=headers, json=data).json()

        if response['code'] == 0:
            pid = response['data']['pid']
            remain = response['data']['remain']
            print(f"ID:{pid}\n钢镚余额:{remain}")

        else:
            print(response['message'])

        print("============开始执行阅读文章============")
        for i in range(30):
            url = "http://2477726.9o.10r8cvn6b1.cloud/read/task"

            response = requests.get(url, headers=headers, json=data).json()

            if response['code'] == 1:
                print(response['message'])
            else:
                mid = response['data']['link'].split('&mid=')[1].split('&')[0]
                print(f"获取文章成功---{mid}")
                import time
                time.sleep(8)
                url = "http://2477726.9o.10r8cvn6b1.cloud/read/finish"
                response = requests.post(url, headers=headers, data=data).json()
                if response['code'] == 0:
                    if response['data']['check'] is False:  # 注意这里使用 is False
                        gain = response['data']['gain']
                        print(f"阅读文章成功---获得钢镚{gain}")
                    else:
                        print("check=True,请手动阅读过检测")
                        break
                else:
                    print(f"{response['message']}")
                    break


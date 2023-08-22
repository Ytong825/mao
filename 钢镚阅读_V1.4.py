"""
@Qim出品 仅供学习交流，请在下载后的24小时内完全删除 请勿将任何内容用于商业或非法目的，否则后果自负。
微信阅读_V1.4   入口：http://2477726.ekdlzhcad7fb.bmaw.lck1lp269c.cloud/?p=2477726
阅读文章抓出cookie（找不到搜索Cookie关键词） 建议手动阅读5篇左右再使用脚本，不然100%黑！！！2小时一次
8/18_update 修复bug
8/22_update  增加推送检测文章   将多个账号检测文章推送至目标微信，手动点击链接完成检测
export ydtoken=cookie
多账号用'===='隔开 例 账号1====账号2
cron：23 7-23/1 * * *
"""
# 企业微信推送 webhook机器人后面的 key，为空则不推送检测文章
key = ""               #请务必完善该参数！






import hashlib
import json
import os
import re
import time

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
        cookie, = values[0],
        # 输出当前正在执行的账号
        print(f"\n=======开始执行账号{i}=======")
        current_time = str(int(time.time()))

        # 计算 sign
        sign_str = f'key=4fck9x4dqa6linkman3ho9b1quarto49x0yp706qi5185o&time={current_time}'
        sha256_hash = hashlib.sha256(sign_str.encode())
        sign = sha256_hash.hexdigest()
        url = "http://2477726.neavbkz.jweiyshi.r0ffky3twj.cloud/share"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; V1923A Build/PQ3B.190801.06161913; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36 MMWEBID/5635 MicroMessenger/8.0.40.2420(0x28002837) WeChat/arm64 Weixin Android Tablet NetType/WIFI Language/zh_CN ABI/arm64",
            "Cookie": cookie
        }

        data = {
            "time": current_time,
            "sign": sign
        }
        response = requests.get(url, headers=headers, json=data).json()
        share_link = response['data']['share_link'][0]
        p_value = share_link.split('=')[1].split('&')[0]

        url = "http://2477726.neavbkz.jweiyshi.r0ffky3twj.cloud/read/info"

        response = requests.get(url, headers=headers, json=data).json()

        if response['code'] == 0:
            remain = response['data']['remain']
            read = response['data']['read']
            print(f"ID:{p_value}-----钢镚余额:{remain}\n今日阅读量::{read}\n推广链接:{share_link}")
        else:
            print(response['message'])

        print("============开始执行阅读文章============")
        for i in range(30):
            # 计算 sign
            sign_str = f'key=4fck9x4dqa6linkman3ho9b1quarto49x0yp706qi5185o&time={current_time}'
            sha256_hash = hashlib.sha256(sign_str.encode())
            sign = sha256_hash.hexdigest()
            url = "http://2477726.9o.10r8cvn6b1.cloud/read/task"

            response = requests.get(url, headers=headers, json=data).json()

            if response['code'] == 1:
                print(response['message'])
                break
            else:
                try:
                    mid = response['data']['link'].split('&mid=')[1].split('&')[0]
                    print(f"获取文章成功---{mid}")
                    import time

                    time.sleep(10)
                    url = "http://2477726.9o.10r8cvn6b1.cloud/read/finish"
                    response = requests.post(url, headers=headers, data=data).json()
                    if response['code'] == 0:
                        if response['data']['check'] is False:
                            gain = response['data']['gain']
                            print(f"阅读文章成功---获得钢镚[{gain}]")
                        else:
                            if key == "":
                                print("check=True,key为空，不执行推送")
                                break
                            else:
                                print("check=True,请手动阅读文章过检测\n以将该文章推送至微信--60s后继续运行")
                                url = "http://2477726.9o.10r8cvn6b1.cloud/read/task"
                                response = requests.get(url, headers=headers, json=data).json()
                                link = response['data']['link']
                                url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + key

                                messages = [
                                    f"出现检测文章！！！\n{link}\n请在60s内点击链接完成阅读",
                                ]

                                for message in messages:
                                    data = {
                                        "msgtype": "text",
                                        "text": {
                                            "content": message
                                        }
                                    }
                                    headers = {'Content-Type': 'application/json'}

                                    # 发送POST请求
                                    response = requests.post(url, headers=headers, data=json.dumps(data))
                                    time.sleep(60)
                                    url = "http://2477726.9o.10r8cvn6b1.cloud/read/finish"
                                    headers = {
                                        "User-Agent": "Mozilla/5.0 (Linux; Android 9; V1923A Build/PQ3B.190801.06161913; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36 MMWEBID/5635 MicroMessenger/8.0.40.2420(0x28002837) WeChat/arm64 Weixin Android Tablet NetType/WIFI Language/zh_CN ABI/arm64",
                                        "Cookie": cookie
                                    }
                                    data = {
                                        "time": current_time,
                                        "sign": sign
                                    }
                                    response = requests.post(url, headers=headers, data=data).json()
                                if response['code'] == 0:
                                    if response['data']['check'] is False:
                                        gain = response['data']['gain']
                                        print(f"阅读文章成功---获得钢镚[{gain}]")
                                else:
                                    print(f"过检测失败，请尝试重新运行")
                                    break



                    else:
                        print(f"{response['message']}")
                        break

                except KeyError:
                    print(f"获取文章失败,错误未知{response}")
                    break
        print(f"============开始微信提现============")
        url = "http://2477726.84.8agakd6cqn.cloud/withdraw/wechat"

        response = requests.get(url, headers=headers, json=data).json()
        if response['code'] == 0:
            print(response['message'])
        elif response['code'] == 1:
            print(response['message'])
        else:
            print(f"错误未知{response}")
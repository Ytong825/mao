'''
老登须知
达美乐,开一把游戏抓取openid的值。
一定要在我的奖品那绑定好手机号！
变量名1：dmlck，多账号用@隔开。备注信息用#隔开 如openid的值#老登
变量名2：pzid 填活动id 这次是 abalone（活动ID自己抓）
url = f"https://game.dominos.com.cn/{pzid}/game/gameDone"
'''

import os
import time
import requests
import json

# 初始化消息和推送配置
message = ''
wx_app_token = os.getenv('WX_PUSHER_APP_TOKEN')  # 从环境变量读取WxPusher Token
wx_uids = os.getenv('WX_PUSHER_UID', '')  # 接收通知的用户UID，多个用逗号分隔

# 获取账号和活动ID
accounts = os.getenv('dmlck')
pzid = os.getenv('pzid')

def send_wxpusher(title, content):
    """发送消息到WxPusher"""
    if not wx_app_token or not wx_uids:
        print("未配置WxPusher环境变量，跳过推送")
        return False
    url = "http://wxpusher.zjiecode.com/api/send/message"
    headers = {'Content-Type': 'application/json'}
    data = {
        "appToken": wx_app_token,
        "content": content,
        "summary": title,
        "contentType": 1,
        "uids": wx_uids.split(',')
    }
    try:
        response = requests.post(url, json=data, headers=headers).json()
        if response.get('code') == 1000:
            print("推送成功")
            return True
        else:
            print(f"推送失败：{response.get('msg')}")
            return False
    except Exception as e:
        print(f"推送异常：{str(e)}")
        return False

if not accounts:
    print('你没有填入dmlck，咋运行？')
    exit()

accounts_list = accounts.split('@')
num_accounts = len(accounts_list)
print(f"获取到 {num_accounts} 个账号")

for i, account in enumerate(accounts_list, start=1):
    values = account.split('#')
    openid = values[0]
    remark = values[1] if len(values) > 1 else f"账号{i}"  # 备注信息用于推送区分
    print(f"\n=======开始执行{remark}=======")
    
    # 固定参数
    url = f"https://game.dominos.com.cn/{pzid}/game/gameDone"
    headers = {
        'User-Agent': "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_2 like Mac OS X; sd-PK) AppleWebKit/535.42.7 (KHTML, like Gecko) Version/4.0.5 Mobile/8B111 Safari/6535.42.7",
        'Content-Type': "application/x-www-form-urlencoded",
        'Referer': "https://servicewechat.com/wx887bf6ad752ca2f3/63/page-frame.html"
    }
    payload = f"openid={openid}&score=t5%2Bhzvt2h6jpwH7D%2BJkNWvT%2Fb6J2mWDStIgcC4ZSrhkqPEqXtcDrCC9LVFvQLRtGkeVQ7z0W6RYqcXxmeXi9596r4HZ1Pt0E5PpRLYWZZL%2BXQXEpyc0WX8c4ewMqQymjBgGMcSRFp3aaLTDNaRLvLcnnh2t5PpL70pW%2B7LcM8tnhtP1J2rLaTe0Dno7%2B9Qf32LuHUS%2BUXCgQ6YbCJwj%2BWrmhP1zbFvGthkH6HB9lkI9mS%2F%2BY9582WQeFREMF9OflJpRVjgPd1%2FPWFRWKWrl%2F7VGztrHpQLZvLQ9HRINK99cN4FBBvPVkkHxyACadINkuFwxgC9ODPYInHXXpn5iElg%3D%3D"

    # 处理分享任务
    shrurl = f"https://game.dominos.com.cn/{pzid}/game/sharingDone"
    payload_share = f"openid={openid}&from=1&target=0"
    while True:
        res = requests.post(shrurl, data=payload_share, headers=headers).json()
        if res.get('errorMessage') == "今日分享已用完，请明日再来":
            print(f'{remark} 分享已达上限，开始抽奖')
            break

    # 抽奖逻辑
    account_msg = f"{remark} 抽奖结果：\n"
    while True:
        response = requests.post(url, data=payload, headers=headers).json()
        if response.get("statusCode") == 0:
            prize = response.get('content', {}).get('name', '未知奖品')
            print(f"抽中：{prize}")
            account_msg += f"  - {prize}\n"
            time.sleep(1)
        else:
            err = response.get('errorMessage', '未知错误')
            print(f"抽奖失败：{err}")
            account_msg += f"  - 错误：{err}\n"
            break
    
    message += account_msg + "\n"

# 汇总推送
try:
    if message:
        send_wxpusher("达美乐抽奖通知", message.strip())
    else:
        print("无有效结果，跳过推送")
except Exception as e:
    print(f"推送失败：{str(e)}")
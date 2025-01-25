'''
author：你的jige
2024 10.15更新
优化查券功能，简化推送。五等奖跟六等奖一样，不用管，只看一等奖。
达美乐,开一把游戏抓取openid的值。
每次活动更新一定要在我的奖品那重新绑定好手机号！
变量名1：dmlck，多账号用@隔开。备注信息用#隔开 如openid的值#大帅比
变量名2：pzid 填活动id。自己抓吧

'''
import os
import time
import requests
import json
import notify
message = ''
# from dotenv import load_dotenv
# load_dotenv()
accounts = os.getenv('dmlck')
pzid = os.getenv('pzid')

if accounts is None:
    print('你没有填入ck，咋运行？')
else:
    accounts_list = os.environ.get('dmlck').split('@')

    num_of_accounts = len(accounts_list)

    print(f"获取到 {num_of_accounts} 个账号")

    for i, account in enumerate(accounts_list, start=1):

        values = account.split('#')
        Cookie = values[0]
        account_no = values[1] if len(values) > 1 else ""
        print(f"\n=======开始执行账号{i} {account_no}=======")
        url = f"https://game.dominos.com.cn/{pzid}/game/gameDone"
        payload = f"openid={Cookie}&score=t5%2Bhzvt2h6jpwH7D%2BJkNWvT%2Fb6J2mWDStIgcC4ZSrhkqPEqXtcDrCC9LVFvQLRtGkeVQ7z0W6RYqcXxmeXi9596r4HZ1Pt0E5PpRLYWZZL%2BXQXEpyc0WX8c4ewMqQymjBgGMcSRFp3aaLTDNaRLvLcnnh2t5PpL70pW%2B7LcM8tnhtP1J2rLaTe0Dno7%2B9Qf32LuHUS%2BUXCgQ6YbCJwj%2BWrmhP1zbFvGthkH6HB9lkI9mS%2F%2BY9582WQeFREMF9OflJpRVjgPd1%2FPWFRWKWrl%2F7VGztrHpQLZvLQ9HRINK99cN4FBBvPVkkHxyACadINkuFwxgC9ODPYInHXXpn5iElg%3D%3D"
        headers = {
            'User-Agent': "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_2 like Mac OS X; sd-PK) AppleWebKit/535.42.7 (KHTML, like Gecko) Version/4.0.5 Mobile/8B111 Safari/6535.42.7",
            'Accept-Encoding': "gzip,compress,br,deflate",
            'Content-Type': "application/x-www-form-urlencoded",
            'charset': "utf-8",
            'Referer': "https://servicewechat.com/wx887bf6ad752ca2f3/63/page-frame.html"
        }

        while True:
            shrurl = f"https://game.dominos.com.cn/{pzid}/game/sharingDone"
            payload2 = f"openid={Cookie}&from=1&target=0"
            res = requests.post(shrurl, data=payload2, headers=headers).json()
            if res['errorMessage'] == "今日分享已用完，请明日再来":
                print(f'账号{i}分享已达上限，开始抽奖\n')
                break
        message += f"\n账号{i}:"
        while True:
            response = requests.post(url, data=payload, headers=headers)
            response = response.json()
            if response["statusCode"] == 0:
                prize = response['content']['name']
                print(f"{prize}")
                time.sleep(1)

            if response["statusCode"] != 0:
                print(response)
                err = response['errorMessage']
                message += f'\n {err}'
                break
        #查询优惠券
        checkurl = "https://game.dominos.com.cn/bulgogi//game/myPrize"
        params = {
            'openid': Cookie
        }
        checkresponse = requests.get(checkurl, params=params, headers=headers)
        json_data = checkresponse.json()
        prize_mapping = {
            "001": "一等奖",
            "002": "二等奖",
            "003": "三等奖",
            "004": "四等奖",
            "005": "五等奖",
            "006": "六等奖"
        }

        # 初始化计数器
        prize_count = {
            "一等奖": 0,
            "二等奖": 0,
            "三等奖": 0,
            "四等奖": 0,
            "五等奖": 0,
            "六等奖": 0
        }

        # 遍历 content 列表并统计每个奖项的获奖次数
        for item in json_data["content"]:
            id_value = item["id"]
            if id_value in prize_mapping:
                prize_name = prize_mapping[id_value]
                prize_count[prize_name] += 1

        # 输出每个奖项的获奖次数
        for prize, count in prize_count.items():
            mes = (f"\n{prize}: {count}张")
            message += mes

try:
    notify.send('达美乐',message)
except Exception as e:
    print(e)
    print('推送失败')

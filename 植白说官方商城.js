"""
@Qim出品 仅供学习交流，请在下载后的24小时内完全删除 请勿将任何内容用于商业或非法目的，否则后果自负。
植白说官方商城_V1.0  活动入口https://i.postimg.cc/fytx3nxQ/bc307f91d48671893a471f752c55e05.png
签到/分享 牛奶活动 如需完成刷人头奖励联系 https://t.me/qianmo98

抓https://zbs.20171026.com/demo/取出X-Dts-Token

export zbstoken=X-Dts-Token
多账号用'===='隔开 例 账号1====账号2
corn：0 0 8 * * ?
"""


import os

import requests

# from dotenv import load_dotenv
# load_dotenv()
accounts = os.getenv('zbstoken')

if accounts is None:
    print('你没有填入zbstoken，咋运行？')
else:
    # 获取环境变量的值，并按指定字符串分割成多个账号的参数组合
    accounts_list = os.environ.get('zbstoken').split('====')

    # 输出有几个账号
    num_of_accounts = len(accounts_list)
    print(f"获取到 {num_of_accounts} 个账号")

    # 遍历所有账号
    for i, account in enumerate(accounts_list, start=1):
        # 按@符号分割当前账号的不同参数
        values = account.split('@')
        zbstoken = values[0]
        # 输出当前正在执行的账号
        print(f"\n=======开始执行账号{i}=======")
        url = 'https://zbs.20171026.com/demo/wx/home/signDay'
        headers = {
            'X-DTS-Token': zbstoken,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.39 (0x18002733) NetType/WIFI Language/zh_CN',
        }

        response = requests.get(url, headers=headers)
        response.code = response.json()
        # 处理响应
        if response.code['errno'] == 0:
            signCount = response.code['data']['signCount']
            integral = response.code['data']['integral']
            print(f"签到成功----{signCount}\n积分余额----{integral}")
        else:
            print('请求失败')

        for i in range(3):
            url = 'https://zbs.20171026.com/demo/wx/user/addIntegralByShare'
            response = requests.get(url, headers=headers)
            response.code = response.json()
            # 处理响应
            if response.code['errno'] == 0:
                print(f"第{i+1}分享成功")
            else:
                print('请求失败')
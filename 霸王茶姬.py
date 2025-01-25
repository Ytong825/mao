'''
有点潦草，凑合一下
抓包qm_user_token。
青龙环境变量名bwcjck。多账户换行
'''

import requests
import os
import time
import random
global gpstr
import json
gpstr = ''
from dotenv import load_dotenv
load_dotenv()
def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        print(f'环境变量{var_name}未设置，请检查。')
        return None
    accounts = value.strip().split('\n')
    num_accounts = len(accounts)
    print(f'-----------本次账号运行数量：{num_accounts}-----------')
    print(f'----------项目：霸王茶姬 -1.1----------')
    return accounts

def ck(qm_user_token):
    global gpstr
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.120 Mobile Safari/537.36 XWEB/1220133 MMWEBSDK/20240301 MMWEBID/8518 MicroMessenger/8.0.48.2580(0x28003036) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        'Accept': "v=1.0",
        'Accept-Encoding': "gzip,compress,br,deflate",
        'Content-Type': "application/json",
        'qm-from': "wechat",
        'qm-user-token': qm_user_token,
        'charset': "utf-8",
        'qm-from-type': "catering",
        'Referer': "https://servicewechat.com/wxafec6f8422cb357b/179/page-frame.html"
    }

    payload = json.dumps({
        "activityId": "947079313798000641",
        "appid": "wxafec6f8422cb357b"
    })

    while True:
        try:
            response = requests.post('https://webapi2.qmai.cn/web/cmk-center/sign/takePartInSign', headers=headers,
                                     data=payload)
            response.raise_for_status()  # 主动抛出异常，如果状态码不是200
            response_json = response.json()
            # print(response_json)

            # 检查响应是否为"上限已达"消息
            if response_json.get('code') == 0 and response_json.get('message') == '该用户今日已签到':
                print("已达上限，停止请求。")
                gpstr += f'今天已签到\n'
                break

            # 成功获取奖品的情况
            if response_json.get('code') == 0 and 'data' in response_json:
                num = response_json['data']['rewardDetailList'][0]['sendNum']
                print(f"签到成功！积分+{num}")
                response1 = requests.post('https://webapi2.qmai.cn/web/cmk-center/sign/userSignStatistics',
                                          headers=headers, data=payload).json()
                sign_days = response1["data"]["signDays"]
                print(f'靓仔你已经连续签到{sign_days}天啦！')
                response2 = requests.post('https://webapi.qmai.cn/web/catering/crm/points-info',headers=headers, data=data).json()
                total_points = response2["data"]["totalPoints"]
                print(f'当前总共获得了{total_points}积分')
                gpstr += f'签到成功！获得积分{num}，已经签到{sign_days}天，总共获得{total_points}积分'




        except requests.exceptions.HTTPError as http_err:
            print(f"发生HTTP错误: {http_err}")
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")

            # 不论成功或异常，均等待1-3秒
        time.sleep(random.randint(1, 3))

# 调用函数，传入qm-user-token的值
# 主函数
def main():
    var_name = 'bwcjck'
    tokens = get_env_variable(var_name)
    if not tokens:
        print(f'环境变量{var_name}未设置，请检查。')
        return

    total_accounts = len(tokens)
    for i, token in enumerate(tokens):
        parts = token.split('#')
        if len(parts) < 1:
            print("令牌格式不正确。跳过处理。")
            continue

        token = parts[0]  # Token 值
        account_no = parts[1] if len(parts) > 1 else ""  # 备注信息
        print(f'------账号 {i+1}/{total_accounts} {account_no} 签到-------')
        ck(token)

if __name__ == "__main__":
     main()
     try:
         import notify

         notify.send('霸王茶姬', gpstr)
     except Exception as e:
         print(e)
         print('推送失败')
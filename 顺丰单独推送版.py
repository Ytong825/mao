#2025/2/26 顺丰速运Cookie绑定UID单独推送版
#变量名：sfsyUrl（格式：cookie1#uid1&cookie2#uid2）
import hashlib
import json
import os
import random
import time
import requests
from urllib.parse import unquote

requests.packages.urllib3.disable_warnings()

# ================== 全局配置 ==================
APP_NAME = '顺丰速运'
ENV_NAME = 'sfsyUrl'
WX_TOKEN = os.getenv('WX_PUSHER_APP_TOKEN')

class SFExpress:
    def __init__(self, cookie, uid, index):
        self.index = index + 1
        self.uid = uid.strip()
        self.mobile = '未知账号'
        self.total_point = '获取失败'
        self.usable_honey = '获取失败'
        self.sign_days = 0
        self.cookie = cookie.strip()
        self.session = requests.Session()
        self.session.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            'platform': 'MINI_PROGRAM'
        }

    def login(self):
        try:
            decoded_url = unquote(self.cookie)
            res = self.session.get(decoded_url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                return False
            
            phone = self.session.cookies.get('_login_mobile_', '')
            if len(phone) >= 11:
                self.mobile = f"{phone[:3]}****{phone[7:]}"
                return True
            return False
        except Exception as e:
            print(f"账号{self.index}登录异常: {str(e)}")
            return False

    def generate_sign(self):
        timestamp = str(int(time.time() * 1000))
        raw = f'token=wwesldfs29aniversaryvdld29&timestamp={timestamp}&sysCode=MCS-MIMP-CORE'
        sign = hashlib.md5(raw.encode()).hexdigest()
        self.headers.update({
            'sysCode': 'MCS-MIMP-CORE',
            'timestamp': timestamp,
            'signature': sign
        })

    def get_data(self, url, data=None, method='POST'):
        self.generate_sign()
        try:
            if method == 'GET':
                response = self.session.get(url, headers=self.headers, timeout=10)
            else:
                response = self.session.post(url, json=data, headers=self.headers, timeout=10)
            return response.json() if response.text else {}
        except Exception as e:
            print(f"请求异常: {str(e)}")
            return {}

    def execute_tasks(self):
        if not self.login():
            print(f"❌ 账号{self.index} 登录失败")
            return False
        
        # 执行签到
        sign_res = self.get_data(
            'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage',
            {'comeFrom': 'vioin', 'channelFrom': 'WEIXIN'}
        )
        if sign_res.get('success'):
            self.sign_days = sign_res.get('obj', {}).get('countDay', 0) + 1
        
        # 获取积分
        point_res = self.get_data(
            'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES',
            {'channelType': '1', 'deviceId': self._generate_deviceId()}
        )
        if point_res.get('success'):
            self.total_point = point_res.get('obj', {}).get('totalPoint', '获取失败')
        
        # 获取丰蜜
        honey_res = self.get_data(
            'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~indexData',
            {'inviteUserId': ''}
        )
        if honey_res.get('success'):
            self.usable_honey = honey_res.get('obj', {}).get('usableHoney', '获取失败')
        
        return True

    def _generate_deviceId(self):
        return ''.join(random.choices('abcdef0123456789', k=36))

def send_notification(mobile, point, honey, days, uid):
    if not WX_TOKEN or not uid:
        print("⚠️ 未配置推送参数")
        return

    message = [
        "🏣 顺丰速运账号报告\n",
        f"📱 账号：{mobile}\n",
        f"🏅 积分：{point}\n",
        f"🍯 蜂蜜：{honey}\n",
        f"📆 连续签到：{days}天\n"
    ]
    
    try:
        res = requests.post(
            "https://wxpusher.zjiecode.com/api/send/message",
            json={
                "appToken": WX_TOKEN,
                "content": ''.join(message),
                "contentType": 1,
                "uids": [uid]
            },
            timeout=10
        )
        if res.json().get('code') == 1000:
            print(f"📤 推送到{uid}成功")
        else:
            print(f"推送到{uid}失败：{res.text}")
    except Exception as e:
        print(f"推送到{uid}异常：{str(e)}")

if __name__ == '__main__':
    raw_cookies = os.getenv(ENV_NAME, '').split('&')
    print(f"📦 共检测到 {len(raw_cookies)} 个账号")

    for idx, item in enumerate(raw_cookies):
        if not item.strip():
            continue

        # 解析cookie和uid
        if '#' not in item:
            print(f"❌ 第{idx+1}个账号格式错误，缺少#分隔符")
            continue
            
        cookie, uid = item.split('#', 1)
        if not cookie or not uid:
            print(f"❌ 第{idx+1}个账号配置不完整")
            continue

        print(f"\n====== 正在处理第 {idx+1} 个账号 ======")
        sf = SFExpress(cookie, uid, idx)
        if sf.execute_tasks():
            send_notification(sf.mobile, sf.total_point, sf.usable_honey, sf.sign_days, sf.uid)
        time.sleep(random.randint(2, 5))
#2025/1/6 顺丰速运多账号合并推送版
#变量名：sfsyUrl
import hashlib
import json
import os
import random
import time
from datetime import datetime
import requests
from urllib.parse import unquote

requests.packages.urllib3.disable_warnings()

# ================== 全局配置 ==================
APP_NAME = '顺丰速运'
ENV_NAME = 'sfsyUrl'
WX_TOKEN = os.getenv('WX_PUSHER_APP_TOKEN')
WX_UIDS = os.getenv('WX_PUSHER_UID', '').split(',')

# ================== 结果收集器 ==================
class ResultCollector:
    def __init__(self):
        self.results = []
        self.success_count = 0
        self.fail_count = 0

    def add_result(self, mobile, point, honey, days):
        self.results.append({
            'mobile': mobile,
            'point': point,
            'honey': honey,
            'days': days
        })
        self.success_count += 1

    def add_fail(self):
        self.fail_count += 1

collector = ResultCollector()

# ================== 核心功能类 ==================
class SFExpress:
    def __init__(self, cookie, index):
        self.index = index + 1
        self.mobile = '未知账号'
        self.total_point = '获取失败'
        self.usable_honey = '获取失败'
        self.sign_days = 0
        self.cookie = cookie
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

    # ============= 主要业务逻辑 =============
    def execute_tasks(self):
        if not self.login():
            print(f"❌ 账号{self.index} 登录失败")
            collector.add_fail()
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
        
        # 记录结果
        collector.add_result(self.mobile, self.total_point, self.usable_honey, self.sign_days)
        return True

    def _generate_deviceId(self):
        return ''.join(random.choices('abcdef0123456789', k=36))

# ================== 推送处理器 ==================
def send_combined_notification():
    if not WX_TOKEN or not WX_UIDS:
        print("⚠️ 未配置推送参数")
        return

    message = ["🏣 顺丰速运任务报告 🏣\n"]
    
    # 添加汇总信息
    message.append(f"✅ 成功执行：{collector.success_count}个")
    if collector.fail_count > 0:
        message.append(f"❌ 失败账号：{collector.fail_count}个")
    message.append("----------------")
    
    # 添加详细结果
    for idx, result in enumerate(collector.results, 1):
        message.append(
            f"{idx}. {result['mobile']}\n"
            f"   🏅 积分：{result['point']}\n"
            f"   🍯 蜂蜜：{result['honey']}\n"
            f"   📆 签到：{result['days']}天\n"
            "----------------"
        )
    
    # 构建最终消息
    full_msg = '\n'.join(message)
    
    # 发送请求
    try:
        res = requests.post(
            "https://wxpusher.zjiecode.com/api/send/message",
            json={
                "appToken": WX_TOKEN,
                "content": full_msg,
                "contentType": 1,
                "uids": WX_UIDS
            },
            timeout=10
        )
        if res.json().get('code') == 1000:
            print("📤 合并推送发送成功")
        else:
            print(f"推送失败：{res.text}")
    except Exception as e:
        print(f"推送异常：{str(e)}")

# ================== 主执行逻辑 ==================
if __name__ == '__main__':
    cookies = os.getenv(ENV_NAME, '').split('&')
    print(f"📦 共检测到 {len(cookies)} 个账号")
    
    for idx, cookie in enumerate(cookies):
        if not cookie.strip():
            continue
        
        print(f"\n====== 正在处理第 {idx+1} 个账号 ======")
        sf = SFExpress(cookie, idx)
        sf.execute_tasks()
        time.sleep(random.randint(2, 5))  # 随机间隔避免风控
    
    print("\n====== 正在生成汇总报告 ======")
    send_combined_notification()
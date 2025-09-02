#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 抓包下面链接的passToken和userId，填在脚本的后面
# https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket
"""
小米钱包自动任务脚本 - 环境变量版
功能：执行每日任务获取视频会员天数
特点：
1. 显示总收益和每日收益
2. 预估兑换会员所需天数
3. 明确标识无效账号
5. 总天数30天计算
6. 添加自动兑换会员功能（10点抢兑）
7.添加日志ID打码功能
8.添加通知功能
"""

import os
import sys
import time
import requests
import urllib3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 环境变量名称
ENV_NAME = "xmqb"

# 目标兑换天数
TARGET_DAYS = 30

# ==================== 自动兑换功能设置 ====================
# 总开关：是否开启自动兑换功能 (True/False)
AUTO_EXCHANGE_SWITCH = True

# 兑换会员类型 (目前支持: iqiyi/tencent/youku/mango)
EXCHANGE_TYPE = "iqiyi"

# =======================================================

# 青龙通知变量名称（带中文注释）
NOTIFY_ENV_NAMES = [
    # 常用通知服务
    "PUSH_KEY",                # Server酱推送
    "BARK_PUSH",               # Bark推送
    "BARK_SOUND",              # Bark声音
    "DD_BOT_ACCESS_TOKEN",     # 钉钉机器人Token
    "DD_BOT_SECRET",           # 钉钉机器人Secret
    "FSKEY",                   # 飞书机器人Key
    "QYWX_AM",                 # 企业微信应用消息
    "QYWX_KEY",                # 企业微信机器人
    "TG_BOT_TOKEN",            # Telegram机器人Token
    "TG_USER_ID",              # Telegram用户ID
    "PUSH_PLUS_TOKEN",         # PushPlus推送Token
    "PUSH_PLUS_USER",          # PushPlus推送群组
    
    # 其他通知服务
    "CONSOLE",                 # 控制台输出
    "GOBOT_URL",               # go-cqhttp地址
    "GOBOT_QQ",                # go-cqhttp推送QQ号
    "GOBOT_TOKEN",             # go-cqhttp推送Token
    "GOTIFY_URL",              # Gotify地址
    "GOTIFY_TOKEN",            # Gotify令牌
    "IGOT_PUSH_KEY",           # iGot推送Key
    "QMSG_KEY",                # Qmsg推送Key
    "QMSG_TYPE",               # Qmsg推送类型
    "QQ_SKEY",                 # QQ推送Skey
    "QQ_MODE",                 # QQ推送模式
    "TG_PROXY_AUTH",           # Telegram代理认证
    "TG_PROXY_HOST",           # Telegram代理主机
    "TG_PROXY_PORT",           # Telegram代理端口
    "TG_API_HOST",             # Telegram API地址
    "TENCENTBOT_SECRET_ID",    # 腾讯云机器人SecretId
    "TENCENTBOT_SECRETKEY",    # 腾讯云机器人SecretKey
    "TENCENTBOT_REGION",       # 腾讯云机器人区域
    "TENCENTBOT_SESSIONID",    # 腾讯云机器人SessionId
    "TENCENTBOT_PARAMETERS",   # 腾讯云机器人参数
    "DEER_KEY",                # PushDeer推送Key
    "MI_PUSH",                 # 小米推送
    
    # 邮件通知
    "SMTP_SERVER",             # SMTP服务器
    "SMTP_PORT",               # SMTP端口
    "SMTP_USER",               # SMTP用户
    "SMTP_PASSWORD",           # SMTP密码
    "SMTP_FROM",               # 发件人邮箱
    "SMTP_TO",                 # 收件人邮箱
    "SMTP_SSL",                # 是否使用SSL
    "SMTP_HTML",               # 是否使用HTML格式
    "SMTP_ATTACHMENTS"         # 邮件附件
]

class RnlRequest:
    def __init__(self, cookies: Union[str, dict]):
        self.session = requests.Session()
        self._base_headers = {
            'Host': 'm.jr.airstarfinance.net',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3',
        }
        self.update_cookies(cookies)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        headers = {**self._base_headers, **kwargs.pop('headers', {})}
        try:
            resp = self.session.request(
                verify=False,
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                **kwargs
            )
            resp.raise_for_status()
            return resp.json()
        except:
            return None

    def update_cookies(self, cookies: Union[str, dict]) -> None:
        if cookies:
            if isinstance(cookies, str):
                dict_cookies = self._parse_cookies(cookies)
            else:
                dict_cookies = cookies
            self.session.cookies.update(dict_cookies)
            self._base_headers['Cookie'] = self.dict_cookie_to_string(dict_cookies)

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        return dict(
            item.strip().split('=', 1)
            for item in cookies_str.split(';')
            if '=' in item
        )

    @staticmethod
    def dict_cookie_to_string(cookie_dict):
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append(f"{key}={value}")
        return "; ".join(cookie_list)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None,
             json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('POST', url, data=data, json=json, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class RNL:
    def __init__(self, c):
        self.t_id = None
        self.activity_code = '2211-videoWelfare'
        self.rr = RnlRequest(c)
        self.total_days = 0.0
        self.today_gain = 0.0
        self.exchanged = False  # 记录是否已兑换
        self.has_exchanged_before = False  # 记录是否曾经兑换过

    def get_task_list(self):
        data = {'activityCode': self.activity_code}
        try:
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTaskList',
                data=data,
            )
            if response and response['code'] == 0:
                return [task for task in response['value']['taskInfoList'] if '浏览组浏览任务' in task['taskName']]
        except:
            pass
        return None

    def get_task(self, task_code):
        try:
            data = {
                'activityCode': self.activity_code,
                'taskCode': task_code,
                'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ==',
            }
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTask',
                data=data,
            )
            if response and response['code'] == 0:
                return response['value']['taskInfo']['userTaskId']
        except:
            pass
        return None

    def complete_task(self, task_id, t_id, brows_click_urlId):
        try:
            url = f'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode={self.activity_code}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&taskId={task_id}&browsTaskId={t_id}&browsClickUrlId={brows_click_urlId}&clickEntryType=undefined&festivalStatus=0'
            response = self.rr.get(url)
            if response and response['code'] == 0:
                return response['value']
        except:
            pass
        return None

    def receive_award(self, user_task_id):
        try:
            url = f'https://m.jr.airstarfinance.net/mp/api/generalActivity/luckDraw?imei=&device=manet&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:true,%22com.tencent.qqlive%22:true,%22com.hunantv.imgo.activity%22:true,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:true,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:true,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode={self.activity_code}&userTaskId={user_task_id}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D'
            response = self.rr.get(url)
            if response and response['code'] == 0:
                return int(response.get('value', {}).get('value', 0))
        except:
            pass
        return 0

    def query_user_info(self):
        """查询用户总天数和今日收益"""
        try:
            # 查询总天数
            total_res = self.rr.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare')
            if total_res and total_res['code'] == 0:
                self.total_days = int(total_res['value']) / 100
            
            # 查询当天记录
            self.today_gain = 0.0
            current_date = datetime.now().strftime("%Y-%m-%d")
            history_res = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            
            if history_res and history_res['code'] == 0:
                for record in history_res['value']['data']:
                    if record['createTime'].startswith(current_date):
                        self.today_gain += int(record['value']) / 100
            
            # 检查是否曾经兑换过
            self.has_exchanged_before = self.check_exchange_history()
            
            return True
        except:
            return False

    def check_exchange_history(self):
        """检查兑换历史记录，判断是否曾经兑换过"""
        try:
            # 查询兑换记录
            history_res = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserExchangeList?activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            
            if history_res and history_res['code'] == 0:
                # 如果有兑换记录，则说明曾经兑换过
                return len(history_res['value']['data']) > 0
        except:
            pass
        return False

    def run_tasks(self):
        """执行任务并返回是否有效账号"""
        # 查询用户信息
        if not self.query_user_info():
            return False, "无法查询账户信息"
        
        # 记录初始今日收益
        initial_gain = self.today_gain
        
        # 获取任务列表
        tasks = self.get_task_list()
        if not tasks:
            return False, "无法获取任务列表"
        
        # 执行任务
        for i, task in enumerate(tasks[:2]):  # 只执行前两个任务
            try:
                t_id = task['generalActivityUrlInfo']['id']
                self.t_id = t_id
            except:
                t_id = self.t_id or ""
            
            task_id = task.get('taskId', "")
            task_code = task.get('taskCode', "")
            brows_click_url_id = task['generalActivityUrlInfo'].get('browsClickUrlId', "")
            
            # 等待
            time.sleep(13)
            
            # 完成任务
            user_task_id = self.complete_task(
                task_id=task_id,
                t_id=t_id,
                brows_click_urlId=brows_click_url_id,
            )
            
            if not user_task_id:
                user_task_id = self.get_task(task_code=task_code)
                time.sleep(2)
            
            # 领取奖励
            if user_task_id:
                award_value = self.receive_award(user_task_id=user_task_id)
                if award_value > 0:
                    # 更新今日收益
                    self.today_gain += award_value / 100
                time.sleep(2)
        
        # 更新用户信息
        self.query_user_info()
        
        # 计算本次获得的收益
        gain_this_run = self.today_gain - initial_gain
        
        # 计算预估天数
        remaining_days = TARGET_DAYS - self.total_days
        if gain_this_run > 0 and remaining_days > 0:
            estimated_days = remaining_days / gain_this_run
        else:
            estimated_days = 0
        
        # 有效账号
        return True, {
            "total_days": self.total_days,
            "today_gain": self.today_gain,
            "gain_this_run": gain_this_run,
            "estimated_days": estimated_days,
            "has_exchanged_before": self.has_exchanged_before
        }

    def exchange_member(self, phone: str) -> bool:
        """兑换会员"""
        try:
            # 检查是否已兑换过
            if self.exchanged:
                print("⚠️ 该账号今日已兑换过，跳过")
                return False
                
            # 兑换请求
            url = f"https://m.jr.airstarfinance.net/mp/api/generalActivity/exchange?activityCode={self.activity_code}&exchangeCode={EXCHANGE_TYPE}&phone={phone}&app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1%7D"
            response = self.rr.get(url)
            
            if response:
                if response.get('code') == 0:
                    self.exchanged = True
                    return True
                else:
                    # 如果返回了错误消息，显示具体错误
                    print(f"兑换失败: {response.get('message', '缺货补货中')}")
            else:
                # 提示缺货补货中
                print("兑换失败: 缺货补货中，明天再试")
        except Exception as e:
            print(f"兑换请求异常: {str(e)}")
        return False


def get_xiaomi_cookies(pass_token, user_id):
    """获取小米钱包cookies"""
    login_url = 'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.127 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3',
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }

    try:
        session = requests.Session()
        session.get(url=login_url, headers=headers, verify=False, timeout=10)
        cookies = session.cookies.get_dict()
        if 'cUserId' in cookies and 'serviceToken' in cookies:
            return f"cUserId={cookies.get('cUserId')};jrairstar_serviceToken={cookies.get('serviceToken')}"
    except:
        pass
    return None

def format_days(days):
    """格式化天数显示（保留一位小数）"""
    # 直接显示天数，不转换为分钟
    return f"{days:.1f}天"

def mask_user_id(user_id):
    """格式化用户ID显示，只显示前三位和后三位，中间用星号代替"""
    if len(user_id) <= 6:
        # 如果ID长度小于等于6，全部显示星号
        return '*' * len(user_id)
    # 显示前3位 + 6个星号 + 后3位
    return user_id[:3] + '*' * 6 + user_id[-3:]

def send_notification(title, content):
    """发送青龙面板通知"""
    # 检查是否有通知环境变量设置
    has_notify = False
    for env_name in NOTIFY_ENV_NAMES:
        if os.getenv(env_name):
            has_notify = True
            break
    
    if not has_notify:
        print("⚠️ 未检测到通知环境变量设置")
        print("如需接收通知，请在青龙面板的环境变量中设置任意支持的通知变量")
        print("支持的变量名称请查看脚本中的NOTIFY_ENV_NAMES列表（带中文注释）")
        return
    
    # 尝试导入通知模块
    try:
        from notify import send
        send(title, content)
        print("✅ 通知已发送")
    except ImportError:
        print("⚠️ 无法导入通知模块，请确保在青龙面板中运行")
    except Exception as e:
        print(f"⚠️ 发送通知失败: {str(e)}")

def main():
    # 环境变量检测
    env_value = os.getenv(ENV_NAME)
    if not env_value:
        print(f"❌ 环境变量 {ENV_NAME} 未设置")
        print("请在青龙面板中添加环境变量，格式：passToken1&userId1@passToken2&userId2")
        sys.exit(1)
    
    # 解析账号信息
    accounts = []
    account_strs = env_value.split('@')
    for acc_str in account_strs:
        if '&' not in acc_str:
            print(f"⚠️ 账号格式错误: {acc_str}，跳过")
            continue
        parts = acc_str.split('&', 1)
        if len(parts) != 2:
            print(f"⚠️ 账号格式错误: {acc_str}，跳过")
            continue
        pass_token, user_id = parts
        accounts.append({
            'passToken': pass_token.strip(),
            'userId': user_id.strip()
        })
    
    if not accounts:
        print("❌ 未找到有效账号信息")
        sys.exit(1)
    
    print(f"✅ 找到 {len(accounts)} 个账号")
    print(f"⏱️ 目标兑换天数: {TARGET_DAYS}天")
    print(f"🔌 自动兑换功能: {'已开启' if AUTO_EXCHANGE_SWITCH else '已关闭'}")
    if AUTO_EXCHANGE_SWITCH:
        print(f"📱 兑换会员类型: {EXCHANGE_TYPE}")
        print(f"🎯 兑换条件: 总天数≥7天且从未兑换过")
    print("=" * 60)
    
    # 获取兑换手机号环境变量
    exchange_phones = []
    exchange_phones_str = os.getenv("EXCHANGE_PHONES", "")
    if exchange_phones_str:
        exchange_phones = exchange_phones_str.split('@')
        print(f"📱 找到 {len(exchange_phones)} 个兑换手机号")
    else:
        print("⚠️ 未设置兑换手机号环境变量 EXCHANGE_PHONES")
    
    # 执行每个账号的任务
    valid_count = 0
    exchange_count = 0
    account_results = []  # 存储每个账号的执行结果
    
    for idx, account in enumerate(accounts):
        user_id = account.get('userId', '未知')
        masked_id = mask_user_id(user_id)  # 获取脱敏后的用户ID
        print(f"\n▶️ 开始账号 {idx+1}/{len(accounts)} (ID: {masked_id})")
        
        # 获取 cookies
        start_time = time.time()
        cookies = get_xiaomi_cookies(
            account.get('passToken', ''), 
            account.get('userId', '')
        )
        
        if not cookies:
            print("❌ 无效账号 - 登录失败")
            account_results.append(f"❌ {masked_id} - 登录失败")
            continue
        
        # 执行任务
        try:
            rnl = RNL(cookies)
            is_valid, result = rnl.run_tasks()
            
            if not is_valid:
                print("❌ 无效账号 - 无法获取任务")
                account_results.append(f"❌ {masked_id} - 无效账号")
                continue
                
            # 有效账号计数
            valid_count += 1
            
            # 输出结果
            elapsed = time.time() - start_time
            print(f"✅ 账号有效 - 任务完成")
            print(f"⏱️ 耗时: {elapsed:.1f}秒")
            print(f"💎 当前总天数: {format_days(result['total_days'])}")
            print(f"📈 今日总收益: {format_days(result['today_gain'])}")  # 直接显示小数形式的天数
            
            if result['gain_this_run'] > 0:
                print(f"🎁 本次获得: {format_days(result['gain_this_run'])}")
                
                # 计算预估天数
                if result['estimated_days'] > 0:
                    print(f"⏳ 预估兑换: 约 {result['estimated_days']:.1f} 天后可兑换会员")
                else:
                    print("🎉 恭喜！已达成兑换目标")
            else:
                print("ℹ️ 今日已无任务可完成")
            
            # 进度条
            progress = min(100, result['total_days'] / TARGET_DAYS * 100)
            print(f"\n📊 进度: [{('=' * int(progress//5)).ljust(20)}] {progress:.1f}%")
            print(f"🎯 目标: {TARGET_DAYS}天 | 剩余: {max(0, TARGET_DAYS - result['total_days']):.1f}天")
            
            # 显示兑换历史状态
            if result['has_exchanged_before']:
                print("ℹ️ 该账号曾经兑换过会员")
            else:
                print("ℹ️ 该账号从未兑换过会员")
            
            # ================ 自动兑换功能 ================
            exchange_status = "未尝试兑换"
            if AUTO_EXCHANGE_SWITCH:
                # 获取当前时间（UTC+8）
                beijing_time = datetime.utcnow() + timedelta(hours=8)
                current_hour = beijing_time.hour
                
                # 检查兑换条件：
                # 1. 总天数≥7天
                # 2. 从未兑换过
                # 3. 当前时间是10点
                if (result['total_days'] >= 7 and 
                    not result['has_exchanged_before'] and 
                    current_hour == 10):
                    
                    # 获取手机号
                    phone = ""
                    if idx < len(exchange_phones) and exchange_phones[idx]:
                        phone = exchange_phones[idx].strip()
                        print(f"⏰ 检测到10点，满足兑换条件（≥7天且首次兑换），开始兑换{EXCHANGE_TYPE}会员到手机: {phone}")
                        
                        # 执行兑换
                        if rnl.exchange_member(phone):
                            exchange_count += 1
                            print(f"🎉 {EXCHANGE_TYPE}会员兑换成功！")
                            exchange_status = "兑换成功"
                        else:
                            print("⚠️ 兑换失败，请检查日志")
                            exchange_status = "兑换失败"
                    else:
                        print(f"⚠️ 未找到对应的兑换手机号，无法兑换{EXCHANGE_TYPE}会员")
                        exchange_status = "无手机号"
                else:
                    # 显示不兑换的原因
                    reasons = []
                    if result['total_days'] < 7:
                        reasons.append(f"总天数不足7天（当前{result['total_days']:.1f}天）")
                    if result['has_exchanged_before']:
                        reasons.append("该账号已兑换过会员")
                    if current_hour != 10:
                        reasons.append(f"当前时间 {beijing_time.strftime('%H:%M')} 非10点")
                    
                    if reasons:
                        print(f"ℹ️ 不满足兑换条件: {'，'.join(reasons)}")
                        exchange_status = "条件不满足"
            # ===========================================
            
            # 记录账号结果
            account_results.append(
                f"✅ {masked_id} | 总天数: {format_days(result['total_days'])} | "
                f"今日收益: {format_days(result['today_gain'])} | "
                f"状态: {exchange_status}"
            )
            
        except Exception as e:
            print(f"⚠️ 执行异常: {str(e)}")
            account_results.append(f"❌ {masked_id} - 执行异常")
        
        print(f"🔚 账号 {masked_id} 处理完成")
        print("-" * 50)
        time.sleep(3)
    
    # 最终统计
    print("\n" + "=" * 60)
    print(f"✅ 任务完成 - 有效账号: {valid_count}/{len(accounts)}")
    print(f"🎁 成功兑换会员: {exchange_count}个")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 构建通知内容
    title = "小米钱包任务完成"
    content = [
        f"📊 账号总数: {len(accounts)}",
        f"✅ 有效账号: {valid_count}",
        f"🎁 兑换成功: {exchange_count}",
        f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📋 账号详情:"
    ]
    content.extend(account_results)
    
    # 发送通知
    send_notification(title, "\n".join(content))

if __name__ == "__main__":
    main()
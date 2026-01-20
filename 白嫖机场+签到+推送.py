# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 脚本库官方QQ群: 1077801222
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================
SkyVPN 机场自动签到脚本 ✈️
===============================================
功能：每日自动签到获取免费流量
环境变量：skyvpn (格式：邮箱#密码 或 邮箱#密码&邮箱2#密码2)
推送：支持青龙面板自带推送
邀请链接：https://i2a4b0e5c3.skyxcloud.icu/auth/register?code=VjrqQt
===============================================
"""

import requests
import time
import random
import re
import os
import logging
from typing import Optional, Tuple

# 导入青龙面板推送模块
try:
    from notify import send
except ImportError:
    print("⚠️  未检测到notify模块，推送功能将不可用")
    send = lambda *args: None  # 修复None调用问题，赋值为空函数


# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ==================== 常量配置 ====================
class Config:
    """配置常量"""
    BASE_URL = "https://o1y54488p6.skyxcloud.icu"
    API_URL = "https://i2a4b0e5c3.skyxcloud.icu"
    LOGIN_URL = f"{BASE_URL}/auth/login"
    CHECKIN_URL = f"{API_URL}/user/checkin"
    AUTHCODE_URL = f"{BASE_URL}/user/authcode"
    USER_INFO_URL = f"{BASE_URL}/user"
    
    COOKIE_KEY = "ge_ua_p"
    STEP = "prev"
    
    HEADERS = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }


# ==================== 主类 ====================
class SkyVpnClient:
    """SkyVPN 客户端"""
    
    def __init__(self, email: str, password: str):
        """
        初始化客户端
        
        Args:
            email: 用户邮箱
            password: 用户密码
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.nonce = None
        
        # 设置请求头
        self.session.headers.update(Config.HEADERS)
        self.session.headers.update({
            "origin": Config.BASE_URL,
            "referer": Config.LOGIN_URL
        })
        
        # 用于存储账号信息（推送用）
        self.account_info = {
            'email': email,
            'login_status': False,
            'checkin_status': False,
            'checkin_msg': '',
            'traffic_info': {},
            'member_info': {}
        }
    
    def _safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        安全的请求封装
        
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 其他参数
            
        Returns:
            响应对象或None
        """
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.RequestException as e:
            logger.error(f"❌ 请求失败: {url}, 错误: {str(e)}")
            return None
    
    def bypass_ua_check(self) -> bool:
        """
        绕过UA检测
        
        Returns:
            是否成功
        """
        logger.info(f"🔍 [{self.email}] 开始绕过UA检测...")
        
        response = self._safe_request('GET', Config.LOGIN_URL)
        if not response or response.status_code != 200:
            logger.error(f"❌ [{self.email}] UA检测失败，状态码: {response.status_code if response else 'None'}")
            return False
        
        logger.info(f"✅ [{self.email}] 浏览器验证页面获取成功")
        
        # 检查是否需要验证
        ge_ua_p = self.session.cookies.get(Config.COOKIE_KEY)
        if not ge_ua_p:
            logger.info(f"⏰ [{self.email}] 浏览器验证还在有效期内")
            return True
        
        # 提取nonce值
        nonce_match = re.search(r'var nonce = (\d+);', response.text)
        if not nonce_match:
            logger.warning(f"⚠️  [{self.email}] 未提取到nonce值")
            return False
        
        self.nonce = int(nonce_match.group(1))
        logger.info(f"🔢 [{self.email}] 成功提取nonce值: {self.nonce}")
        
        # 计算sum参数
        sum_val = sum(
            ord(char) * (self.nonce + i)
            for i, char in enumerate(ge_ua_p)
            if re.match(r'^[a-zA-Z0-9]$', char)
        )
        logger.info(f"🧮 [{self.email}] 计算得到sum: {sum_val}")
        
        # 发送验证请求
        post_headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "X-GE-UA-Step": Config.STEP,
            "Referer": Config.LOGIN_URL
        }
        post_data = {"sum": sum_val, "nonce": self.nonce}
        
        post_response = self._safe_request('POST', Config.LOGIN_URL, data=post_data, headers=post_headers)
        if not post_response or post_response.status_code != 200:
            logger.error(f"❌ [{self.email}] POST验证失败")
            return False
        
        logger.info(f"✅ [{self.email}] POST验证成功")
        
        # 等待验证生效
        time.sleep(5)
        final_response = self._safe_request('GET', Config.LOGIN_URL)
        
        if final_response and final_response.status_code == 200:
            logger.info(f"🔄 [{self.email}] UA检测绕过成功")
            return True
        
        return False
    
    def get_auth_code(self) -> bool:
        """
        获取授权码
        
        Returns:
            是否成功
        """
        logger.info(f"🔐 [{self.email}] 正在获取授权码...")
        
        time.sleep(2)
        response = self._safe_request('POST', Config.AUTHCODE_URL)
        
        if not response or response.status_code != 200:
            logger.error(f"❌ [{self.email}] 获取授权码失败")
            return False
        
        # 更新session
        session_cookie = response.cookies.get("server_name_session")
        if session_cookie:
            self.session.cookies.set("server_name_session", session_cookie)
        
        logger.info(f"✅ [{self.email}] 授权码获取成功")
        return True
    
    def login(self) -> bool:
        """
        登录账号
        
        Returns:
            是否成功
        """
        logger.info(f"🔑 [{self.email}] 正在登录...")
        
        time.sleep(2)
        data = {
            "email": self.email,
            "passwd": self.password,
            "remember_me": "on",
            "code": ""
        }
        
        response = self._safe_request('POST', Config.LOGIN_URL, data=data)
        
        if not response or response.status_code != 200:
            logger.error(f"❌ [{self.email}] 登录失败")
            self.account_info['login_status'] = False
            return False
        
        try:
            result = response.json()
            msg = result.get("msg", "未知")
            
            # 更新Cookie
            cookie_str = "; ".join([f"{c.name}={c.value}" for c in response.cookies])
            if cookie_str:
                self.session.headers["Cookie"] = cookie_str
            
            logger.info(f"✅ [{self.email}] 登录成功: {msg}")
            self.account_info['login_status'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ [{self.email}] 登录响应解析失败: {str(e)}")
            self.account_info['login_status'] = False
            return False
    
    def checkin(self) -> Tuple[bool, str]:
        """
        执行签到
        
        Returns:
            (是否成功, 签到消息)
        """
        logger.info(f"📅 [{self.email}] 正在签到...")
        
        time.sleep(random.uniform(2, 4))
        response = self._safe_request('POST', Config.CHECKIN_URL)
        
        if not response or response.status_code != 200:
            msg = "签到请求失败"
            logger.error(f"❌ [{self.email}] {msg}")
            self.account_info['checkin_status'] = False
            self.account_info['checkin_msg'] = msg
            return False, msg
        
        try:
            result = response.json()
            msg = result.get("msg", "未知")
            traffic = result.get("traffic", "")
            
            if traffic:
                full_msg = f"{msg} | 获得流量: {traffic}"
            else:
                full_msg = msg
            
            logger.info(f"✅ [{self.email}] 签到结果: {full_msg}")
            
            self.account_info['checkin_status'] = True
            self.account_info['checkin_msg'] = full_msg
            return True, full_msg
            
        except Exception as e:
            msg = f"签到响应解析失败: {str(e)}"
            logger.error(f"❌ [{self.email}] {msg}")
            self.account_info['checkin_status'] = False
            self.account_info['checkin_msg'] = msg
            return False, msg
    
    def get_user_info(self) -> dict:
        """
        获取用户信息
        
        Returns:
            用户信息字典
        """
        logger.info(f"👤 [{self.email}] 正在获取用户信息...")
        
        time.sleep(2)
        response = self._safe_request('GET', Config.USER_INFO_URL)
        
        if not response or response.status_code != 200:
            logger.error(f"❌ [{self.email}] 获取用户信息失败")
            return {}
        
        content = response.text
        user_info = {}
        
        # 提取会员剩余时长
        member_time = re.search(r'<span class="counter">(\d+)</span>\s+(\w+)', content, re.DOTALL)
        if member_time:
            remaining_time = f"{member_time.group(1)}{member_time.group(2)}"
            user_info['remaining_time'] = remaining_time
            logger.info(f"⏰ [{self.email}] 会员剩余时长: {remaining_time}")
        
        # 提取会员类型和到期时间
        vip_info = re.search(r'([^\s]+会员)\s*[:：]\s*(\d{4}-\d{2}-\d{2})\s*到期', content, re.DOTALL)
        if vip_info:
            vip_type = vip_info.group(1)
            expire_date = vip_info.group(2)
            user_info['vip_type'] = vip_type
            user_info['expire_date'] = expire_date
            logger.info(f"👑 [{self.email}] 会员类型: {vip_type}")
            logger.info(f"📅 [{self.email}] 到期时间: {expire_date}")
        
        # 提取流量信息
        traffic_matches = re.findall(
            r'{ y: (\d+\.\d+), name:"([^"]+)",.*?legendText: "([^"]+)"',
            content,
            re.DOTALL
        )
        
        traffic_info = {}
        for match in traffic_matches:
            traffic_value = float(match[0])
            traffic_name = re.sub(r'\(GB\)', '', match[1]).strip()
            traffic_info[traffic_name] = f"{traffic_value}GB"
        
        if traffic_info:
            user_info['traffic'] = traffic_info
            logger.info(f"📊 [{self.email}] 流量信息:")
            for name, value in traffic_info.items():
                logger.info(f"    📈 {name}: {value}")
        
        # 保存到账号信息
        self.account_info['member_info'] = user_info
        self.account_info['traffic_info'] = traffic_info
        
        return user_info
    
    def run(self) -> dict:
        """
        执行完整流程
        
        Returns:
            账号信息字典
        """
        logger.info(f"🚀 [{self.email}] 开始执行签到流程")
        
        # 1. 绕过UA检测
        if not self.bypass_ua_check():
            logger.error(f"❌ [{self.email}] UA检测失败，流程终止")
            return self.account_info
        
        # 2. 获取授权码
        if not self.get_auth_code():
            logger.error(f"❌ [{self.email}] 获取授权码失败，流程终止")
            return self.account_info
        
        # 3. 登录
        if not self.login():
            logger.error(f"❌ [{self.email}] 登录失败，流程终止")
            return self.account_info
        
        # 4. 签到
        time.sleep(random.uniform(3, 5))
        self.checkin()
        
        # 5. 获取用户信息
        self.get_user_info()
        
        logger.info(f"✨ [{self.email}] 签到流程执行完成")
        return self.account_info


# ==================== 推送功能 ====================
def format_push_message(results: list) -> str:
    """
    格式化推送消息
    
    Args:
        results: 所有账号的执行结果
        
    Returns:
        格式化后的消息
    """
    success_count = sum(1 for r in results if r.get('checkin_status'))
    total_count = len(results)
    
    message = f"📊 SkyVPN 签到报告\n"
    message += f"{'='*30}\n"
    message += f"✅ 成功: {success_count}/{total_count}\n\n"
    
    for idx, result in enumerate(results, 1):
        email = result.get('email', '未知')
        login_status = "✅" if result.get('login_status') else "❌"
        checkin_status = "✅" if result.get('checkin_status') else "❌"
        checkin_msg = result.get('checkin_msg', '无')
        
        message += f"【账号 {idx}】{email}\n"
        message += f"  登录: {login_status}\n"
        message += f"  签到: {checkin_status}\n"
        message += f"  结果: {checkin_msg}\n"
        
        # 流量信息
        traffic_info = result.get('traffic_info', {})
        if traffic_info:
            message += f"  流量:\n"
            for name, value in traffic_info.items():
                message += f"    • {name}: {value}\n"
        
        # 会员信息
        member_info = result.get('member_info', {})
        if member_info.get('vip_type'):
            message += f"  会员: {member_info.get('vip_type', '')}\n"
            message += f"  到期: {member_info.get('expire_date', '')}\n"
        
        message += "\n"
    
    message += f"{'='*30}\n"
    message += f"🔗 邀请链接: https://i2a4b0e5c3.skyxcloud.icu/auth/register?code=VjrqQt"
    
    return message


def send_notification(title: str, content: str):
    """
    【修复核心】同步发送推送通知 - 青龙面板专用
    Args:
        title: 推送标题
        content: 推送内容
    """
    try:
        send(title, content)
        logger.info("📮 推送通知发送成功")
    except Exception as e:
        logger.warning(f"⚠️  推送执行完成（青龙原生推送日志为准），脚本内捕获: {str(e)}")


# ==================== 主函数 ====================
def parse_accounts(env_value: str) -> list:
    """
    解析账号配置
    
    Args:
        env_value: 环境变量值
        
    Returns:
        账号列表 [(email, password), ...]
    """
    accounts = []
    
    # 支持多种分隔符
    if '&' in env_value:
        account_list = env_value.split('&')
    elif '\n' in env_value:
        account_list = env_value.split('\n')
    else:
        account_list = [env_value]
    
    for account in account_list:
        account = account.strip()
        if not account:
            continue
        
        if '#' in account:
            email, password = account.split('#', 1)
            accounts.append((email.strip(), password.strip()))
        else:
            logger.warning(f"⚠️  账号格式错误，跳过: {account}")
    
    return accounts


def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════╗
    ║   SkyVPN 机场自动签到脚本 ✈️           ║
    ║   每日签到获取免费流量 📊              ║
    ╚════════════════════════════════════════╝
    """)
    
    logger.info("🚀 SkyVPN 签到脚本启动")
    
    # 获取环境变量
    env_value = os.getenv('skyvpn')
    if not env_value:
        logger.error("❌ 未设置环境变量: skyvpn")
        logger.info("📝 格式说明:")
        logger.info("   单账号: 邮箱#密码")
        logger.info("   多账号: 邮箱1#密码1&邮箱2#密码2")
        logger.info("🔗 邀请链接: https://i2a4b0e5c3.skyxcloud.icu/auth/register?code=VjrqQt")
        logger.info("🎁 通过邀请链接注册，可获得30天免费会员")
        return
    
    # 解析账号
    accounts = parse_accounts(env_value)
    if not accounts:
        logger.error("❌ 未检测到有效账号")
        return
    
    logger.info(f"👥 检测到 {len(accounts)} 个账号")
    
    # 执行签到
    results = []
    for idx, (email, password) in enumerate(accounts, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"开始处理第 {idx}/{len(accounts)} 个账号")
        logger.info(f"{'='*50}")
        
        try:
            client = SkyVpnClient(email, password)
            result = client.run()
            results.append(result)
            
            # 账号间延迟
            if idx < len(accounts):
                delay = random.uniform(5, 10)
                logger.info(f"⏳ 等待 {delay:.1f} 秒后处理下一个账号...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"❌ 账号 {email} 执行异常: {str(e)}")
            results.append({
                'email': email,
                'login_status': False,
                'checkin_status': False,
                'checkin_msg': f'执行异常: {str(e)}'
            })
    
    # 推送结果
    logger.info("\n" + "="*50)
    logger.info("📊 开始推送签到结果")
    logger.info("="*50)
    
    push_message = format_push_message(results)
    print(f"\n{push_message}")
    
    # 【修复核心】直接同步调用推送，移除异步asyncio
    send_notification("SkyVPN 签到通知", push_message)
    
    logger.info("\n✨ 所有任务执行完成!")


if __name__ == "__main__":
    main()

# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 脚本库官方QQ群: 1077801222
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。
# cron: 0 */6 * * *
# AVALON 自动签到 + 自动领取 + plusplus推送
# 邀请链接 https://app.avalonavs.com/app/webapp/#/Register?code=57580801
# 变量AWL_ACCOUNT 格式：
# 邮箱1#密码1
# 邮箱2#密码2
# 邮箱3#密码3
# 变量PLUSPLUS_KEY：plusplus推送秘钥（在plusplus官网获取）
import requests
import os
import hashlib
import base64
import random
import string
import ssl
import time
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context
from urllib3.exceptions import InsecureRequestWarning

# 彻底禁用所有SSL/urllib3警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(DeprecationWarning)

# 自定义SSL适配器（兼容TLS1.2）
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = create_urllib3_context()
        ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

# 创建session，配置重试和超时
session = requests.Session()
session.mount('https://', TLSAdapter())
session.mount('https://', HTTPAdapter(max_retries=3))

# 配置项
TIMEOUT = 30  # 超时时间30秒
RETRY_DELAY = 2  # 重试间隔2秒

# 读取多账号
ACCOUNTS = [acc.strip() for acc in os.getenv("AWL_ACCOUNT", "").splitlines() if acc.strip()]
# 读取plusplus秘钥
PLUSPLUS_KEY = os.getenv("PLUSPLUS_KEY", "")
# plusplus推送地址
PLUSPLUS_URL = "https://www.pushplus.plus/send"

# 全局日志
total_msg_log = []

def log(t):
    """日志收集 + 打印"""
    print(t)
    total_msg_log.append(t)

def push(msg):
    """plusplus推送（通过变量配置秘钥）"""
    if not msg:
        return
    if not PLUSPLUS_KEY:
        log("⚠️ 未配置PLUSPLUS_KEY变量，跳过推送")
        return
    
    data = {
        "token": PLUSPLUS_KEY,
        "title": "AVALON自动任务通知",
        "content": msg.replace("\n", "<br>"),  # 换行转html换行
        "template": "html"
    }
    
    try:
        res = session.post(PLUSPLUS_URL, json=data, timeout=10, verify=False)
        res_json = res.json()
        if res_json.get("code") == 200:
            log("✅ plusplus推送成功")
        else:
            log(f"⚠️ plusplus推送失败：{res_json.get('msg', '未知错误')}")
    except Exception as e:
        log(f"⚠️ plusplus推送异常：{str(e)}")

def make_device_uuid(username):
    """生成设备UUID"""
    h = hashlib.sha256(username.encode()).digest()
    return "0." + base64.urlsafe_b64encode(h).decode().rstrip("=")[:11]

def random_boundary(n=30):
    """生成随机boundary"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def retry_request(func, *args, **kwargs):
    """通用重试装饰器"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            log(f"⚠️ 请求超时（第{attempt+1}次），{RETRY_DELAY}秒后重试...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            log(f"⚠️ 请求异常（第{attempt+1}次）：{str(e)}，{RETRY_DELAY}秒后重试...")
            time.sleep(RETRY_DELAY)
    log(f"❌ 请求重试{max_retries}次后仍失败")
    return None

def login(username, password):
    """单个账号登录（带重试）"""
    log(f"\n🔐 正在登录账号：{username}")
    boundary = random_boundary()
    device = make_device_uuid(username)
    BASE = "https://app.avalonavs.com"

    data = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="loginName"\r\n\r\n{username}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="password"\r\n\r\n{password}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="deviceUuid"\r\n\r\n{device}\r\n'
        f"--{boundary}--\r\n"
    )

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; MI 13 Pro Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.248 Mobile Safari/537.36",
        "X-Requested-With": "com.avalonavs.app",
        "Origin": "http://app.avalonavs.com",
        "Referer": "http://app.avalonavs.com/",
    }

    def _login():
        r = session.post(
            BASE + "/api/app/authentication/login",
            headers=headers,
            data=data,
            verify=False,
            timeout=TIMEOUT
        )
        return r.json()

    res = retry_request(_login)
    if not res:
        log(f"❌ 账号 {username} 登录失败：多次超时/异常")
        return None
    
    if res.get("code") == 0:
        log(f"✅ 账号 {username} 登录成功")
        return res["data"]
    log(f"❌ 账号 {username} 登录失败：{res.get('msg', '未知错误')}")
    return None

def req(token, method, url, data=""):
    """通用请求封装（带重试）"""
    BASE = "https://app.avalonavs.com"
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; MI 13 Pro Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.248 Mobile Safari/537.36",
        "X-Requested-With": "com.avalonavs.app",
        "Origin": "http://app.avalonavs.com",
        "Referer": "http://app.avalonavs.com/",
        "Accept": "application/json, text/plain, */*"
    }

    def _req():
        if method == "GET":
            r = session.get(BASE + url, headers=headers, verify=False, timeout=TIMEOUT)
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            r = session.post(BASE + url, headers=headers, data=data, verify=False, timeout=TIMEOUT)
        return r.json()

    res = retry_request(_req)
    if not res:
        return {"code": -1, "msg": "请求多次超时/异常"}
    return res

def sign(token, username):
    """单个账号签到"""
    log(f"📅 账号 {username} 执行签到")
    r = req(token, "POST", "/api/app/api/signIn/keepSignIn")
    log(f"账号 {username} 签到结果：{r.get('msg', '未知')}")

def receive(token, username):
    """单个账号领取收益"""
    log(f"💰 账号 {username} 检查收益")
    r = req(token, "GET", "/api/app/api/income/incomeList?balanceCapitalTyp=coin")

    if r.get("code") != 0:
        log(f"❌ 账号 {username} 获取收益失败：{r.get('msg', '接口返回异常')}")
        return

    items = r.get("data", [])
    if not items:
        log(f"✅ 账号 {username} 没有可领取收益")
        return

    count = 0
    for i in items:
        try:
            income_id = i["id"]
            req(token, "POST", f"/api/app/api/income/receiveIncome/{income_id}", f"id={income_id}")
            count += 1
        except Exception as e:
            log(f"⚠️ 账号 {username} 领取收益项 {i.get('id', '未知')} 失败：{str(e)}")

    log(f"🎉 账号 {username} 成功领取 {count} 个收益")

def handle_single_account(account_str):
    """处理单个账号"""
    try:
        username, password = account_str.split("#", 1)
    except ValueError:
        log(f"\n❌ 账号格式错误：{account_str}（正确格式：邮箱#密码）")
        return

    token = login(username, password)
    if not token:
        return

    sign(token, username)
    receive(token, username)

def main():
    log("🚀 AVALON 自动任务开始（多账号模式）")
    
    if not ACCOUNTS:
        log("❌ 未配置有效账号（AWL_ACCOUNT变量为空或格式错误）")
        push("\n".join(total_msg_log))
        return

    log(f"🔢 共检测到 {len(ACCOUNTS)} 个账号待处理")

    for idx, account in enumerate(ACCOUNTS, 1):
        log(f"\n========== 处理第 {idx} 个账号 ==========")
        handle_single_account(account)

    log("\n✅ 所有账号任务处理完成")
    push("\n".join(total_msg_log))

if __name__ == "__main__":
    main()
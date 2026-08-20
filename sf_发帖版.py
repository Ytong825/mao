#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顺丰速运自动任务 动态 code 版

功能：
  1. 四端口本地服务获取微信 code
  2. UCMP 换取顺丰 Cookie
  3. 每日签到 + 做任务 + 领积分
  4. 会员日活动（每月26-28号自动抽奖）
  5. PushPlus 推送
  6. 品赞代理，业务请求优先代理，失败直连兆底
  7. 世界杯金豆兑奖（可开关）

环境变量：
  PLUSPLUS_TOKEN    PushPlus token，可选
  PROXY_API         品赞代理提取 API，可选
  PROXY_TYPE        http / socks5，默认 http
  SF_CODE_SERVERS   code 服务地址，可选（默认内置4个）

依赖：
  pip install requests
  socks5 代理需：
  pip install requests[socks]
"""

import hashlib
import json
import os
import sys
import random
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import unquote, urlparse, parse_qs, quote as url_encode
from threading import Lock
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SCRIPT_TITLE = "🔔 顺丰速运任务执行总结"


# ==================== 配置区域 ====================
ENABLE_DAILY_TASK = True         # 日常积分任务 (签到+做任务+领积分)
ENABLE_MEMBER_DAY = True         # 会员日活动 (每月26-28号自动执行)

ENABLE_WORLD_CUP_EXCHANGE = True    # 世界杯金豆兑奖 (关闭设为 False)
MASK_PRIVACY = True           # 发帖隐私脱敏（手机号、IP等自动打码）

# ===== 世界杯兑奖配置 =====
EXCHANGE_ADDRESS_INDEX = 0

# ===== 世界杯兑奖 - 账号兑换开关 =====
# 控制哪些 code 服务地址（账号）执行兑换，不在列表里的默认执行
# 设 True = 兑换，设 False = 不兑换
# 青龙面板可用环境变量覆盖，如 EXCHANGE_127=False
EXCHANGE_ACCOUNTS = {
    '127.0.0.1:8088': False,
    '192.168.31.36:8088': False,
    '192.168.31.88:8088': False,
    '192.168.31.62:8088': False,
}

# 环境变量覆盖示例：EXCHANGE_127=False → 关闭 127.0.0.1 的兑换
def _load_exchange_accounts_env():
    for key in list(EXCHANGE_ACCOUNTS.keys()):
        env_key = 'EXCHANGE_' + key.split(':')[0].replace('.', '_')
        env_val = os.environ.get(env_key, '').strip().lower()
        if env_val:
            EXCHANGE_ACCOUNTS[key] = env_val not in ('false', '0', 'off', 'no')
_load_exchange_accounts_env()

# ===== 世界杯兑奖 - 兑换内容开关 =====
# 每个兑换项独立控制，想兑换就设 True，不想就设 False
# 青龙面板可用同名环境变量覆盖，如 EXCHANGE_5YUAN=False
EXCHANGE_DAJIA = False       # 大疆云台相机 (4000金豆)
EXCHANGE_HUANGJIN = False    # 黄金足球金币 (3000金豆)
EXCHANGE_ZAYU = False        # 世界杯吉祥物ZAYU (1500金豆)
EXCHANGE_YUSAN = False       # 顺丰定制雨伞 (1000金豆)
EXCHANGE_HUANBAODAI = False  # 顺丰定制环保袋 (800金豆)
EXCHANGE_JINTIE = False      # 顺丰黄金金贴 (800金豆)
EXCHANGE_23YUAN = True       # 23元免单券 (800金豆)
EXCHANGE_12YUAN = True       # 12元寄件券 (400金豆)
EXCHANGE_5YUAN = True        # 5元寄件券 (200金豆)

# 环境变量覆盖（青龙面板用）
EXCHANGE_DAJIA = os.environ.get('EXCHANGE_DAJIA', str(EXCHANGE_DAJIA)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_HUANGJIN = os.environ.get('EXCHANGE_HUANGJIN', str(EXCHANGE_HUANGJIN)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_ZAYU = os.environ.get('EXCHANGE_ZAYU', str(EXCHANGE_ZAYU)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_YUSAN = os.environ.get('EXCHANGE_YUSAN', str(EXCHANGE_YUSAN)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_HUANBAODAI = os.environ.get('EXCHANGE_HUANBAODAI', str(EXCHANGE_HUANBAODAI)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_JINTIE = os.environ.get('EXCHANGE_JINTIE', str(EXCHANGE_JINTIE)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_23YUAN = os.environ.get('EXCHANGE_23YUAN', str(EXCHANGE_23YUAN)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_12YUAN = os.environ.get('EXCHANGE_12YUAN', str(EXCHANGE_12YUAN)).strip().lower() not in ('false', '0', 'off', 'no')
EXCHANGE_5YUAN = os.environ.get('EXCHANGE_5YUAN', str(EXCHANGE_5YUAN)).strip().lower() not in ('false', '0', 'off', 'no')

EXCHANGE_ITEMS = {
    '大疆云台相机': {
        'enabled': EXCHANGE_DAJIA,
        'shouldNum': 4000,
        'ruleCode': 'RC2071521968535695360',
        'giftPoolCode': 'RGP2071522071354847232',
        'giftBagCode': 'GB2072258393963130880',
        'limitLotteryNum': 1,
    },
    '黄金足球金币': {
        'enabled': EXCHANGE_HUANGJIN,
        'shouldNum': 3000,
        'ruleCode': 'RC2070401398901387264',
        'giftPoolCode': 'RGP2070401639801192448',
        'giftBagCode': 'GB2070345977872318464',
        'limitLotteryNum': 1,
    },
    '世界杯吉祥物ZAYU': {
        'enabled': EXCHANGE_ZAYU,
        'shouldNum': 1500,
        'ruleCode': 'RC2071545327583535104',
        'giftPoolCode': 'RGP2071545403261366272',
        'giftBagCode': 'GB2070342899488038912',
        'limitLotteryNum': 1,
    },
    '顺丰定制雨伞': {
        'enabled': EXCHANGE_YUSAN,
        'shouldNum': 1000,
        'ruleCode': 'RC2071522391409635328',
        'giftPoolCode': 'RGP2071522423131078656',
        'giftBagCode': 'GB2072281755598860288',
        'limitLotteryNum': 1,
    },
    '顺丰定制环保袋': {
        'enabled': EXCHANGE_HUANBAODAI,
        'shouldNum': 800,
        'ruleCode': 'RC2071523194698530816',
        'giftPoolCode': 'RGP2071523233667821568',
        'giftBagCode': 'GB2070342191682482176',
        'limitLotteryNum': 1,
    },
    '顺丰黄金金贴': {
        'enabled': EXCHANGE_JINTIE,
        'shouldNum': 800,
        'ruleCode': 'RC2071524307690606592',
        'giftPoolCode': 'RGP2071524350397050880',
        'giftBagCode': 'GB2072277419896434688',
        'limitLotteryNum': 1,
    },
    '23元免单券': {
        'enabled': EXCHANGE_23YUAN,
        'shouldNum': 800,
        'ruleCode': 'RC2070398330633777152',
        'giftPoolCode': 'RGP2070398549895229440',
        'giftBagCode': 'GB2000483494626267136',
        'limitLotteryNum': 2,
    },
    '12元寄件券': {
        'enabled': EXCHANGE_12YUAN,
        'shouldNum': 400,
        'ruleCode': 'RC2070399299203448832',
        'giftPoolCode': 'RGP2070399485015261184',
        'giftBagCode': 'GB2070346620188012544',
        'limitLotteryNum': 5,
    },
    '5元寄件券': {
        'enabled': EXCHANGE_5YUAN,
        'shouldNum': 200,
        'ruleCode': 'RC2071525126427197440',
        'giftPoolCode': 'RGP2071525224414441472',
        'giftBagCode': 'GB2062025763973922816',
        'limitLotteryNum': 12,
    },
}

EXCLUDE_PHONES = set()
PHONE_OVERRIDE = {}


TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

SF_WX_APPID = os.getenv("SF_WX_APPID", "wxd4185d00bf7e08ac")       # 小程序 appid
SF_PUBLIC_ID = os.getenv("SF_PUBLIC_ID", "gh_f9d9fca26a50")        # 小程序原始ID
SF_OAUTH_APPID = os.getenv("SF_OAUTH_APPID", "wx0d9aa0e894066e87") # 公众号 appid
SF_OAUTH_SCENE = os.getenv("SF_OAUTH_SCENE", "692")                # 活动场景号

# Code 服务地址列表（支持多个，用 & , 或换行分隔）
# 格式：http://ip:port（脚本自动拼接 /login?appId=xxx）
# 多账号示例: http://10.30.9.49:8088&http://10.30.9.50:8088
SF_CODE_SERVERS = [
    '127.0.0.1:8088',
    '192.168.31.36:8088',
    '192.168.31.88:8088',
    '192.168.31.62:8088',
]
SF_CODE_SERVERS_RAW = os.environ.get('SF_CODE_SERVERS') or os.environ.get('sf_code_servers') or '&'.join(SF_CODE_SERVERS)

DAILY_SKIP_TASKS = [
    '用行业模板寄件下单', '用积分兑任意礼品', '参与积分活动',
    '每月累计寄件', '完成每月任务', '去使用AI寄件',
    '去新增一个收件偏好', '设置你的顺丰ID', '去使用AI小丰寄件',
    '寄一单国际件',  # 需真实寄件，无法自动完成
]

EXECUTE_FIRST_KEYWORDS = [
    '浏览', '查看', '点击', '去微博', '打开', '去看看', '看小丰',
]

MEMBER_DAY_SKIP_TASK_TYPES = [
    'SEND_SUCCESS', 'INVITEFRIENDS_PARTAKE_ACTIVITY', 'OPEN_SVIP',
    'OPEN_NEW_EXPRESS_CARD', 'OPEN_FAMILY_CARD', 'CHARGE_NEW_EXPRESS_CARD',
    'INTEGRAL_EXCHANGE',
]

PLUSPLUS_TOKEN = os.getenv('PLUSPLUS_TOKEN', '')
PROXY_API = os.getenv('PROXY_API', '')
PROXY_TYPE = os.getenv('PROXY_TYPE', 'http').lower()
PROXY_RETRY_TIMES = 3
PROXY_VALIDATE_URL = 'http://httpbin.org/ip'
PROXY_FETCH_INTERVAL = 3
ENABLE_DIRECT_FALLBACK = True
REQUEST_TIMEOUT = 30
PROXY_CONTEXT = {'last_fetch_ts': 0}
PROXY_LOCK = Lock()
print_lock = Lock()
GLOBAL_NOTIFY_BUFFERS: List[Dict[str, Any]] = []
AUTO_COOKIE_INDEX_BY_VALUE: Dict[str, int] = {}
COOKIE_TO_SERVER: Dict[str, str] = {}  # cookie -> code server address
# 兑奖项由 EXCHANGE_xxx 开关控制


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_title() -> None:
    print()
    print("╔" + "═" * 50 + "╗")
    print("\u2551 🚚 顺丰速运自动任务 动\u6001 code 版               \u2551")
    print(f"\u2551 🕒 启动时间: {now_text():<32}\u2551")
    print("╚" + "═" * 50 + "╝")


def log_account_header(index: int, total: int, server: str) -> None:
    print()
    print("┌" + "─" * 50 + "┐")
    print(f"\u2502 🧩 账号 {index} / {total:<37}\u2502")
    print(f"\u2502 🌍 来源 {_mask_ip(server):<40}\u2502")
    print("└" + "─" * 50 + "┘")

class Logger:
    def __init__(self):
        pass

    def _log(self, icon: str, msg: str):
        line = f"{icon} {msg}"
        with print_lock:
            print(line)

    def info(self, msg): self._log('📝', msg)
    def success(self, msg): self._log('✅', msg)
    def warning(self, msg): self._log('⚠️', msg)
    def error(self, msg): self._log('❌', msg)
    def task(self, msg): self._log('🎯', msg)
    def medal(self, msg): self._log('🏅', msg)
    def points(self, pts, prefix="当前积分"): self._log('💰', f"{prefix}: 【{pts}】")


def _log_global(msg: str):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        # Windows 控制台默认 GBK 时，降级去掉无法编码字符，避免影响主流程
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(line.encode(encoding, errors="ignore").decode(encoding, errors="ignore"), flush=True)


def parse_env_accounts(raw: str) -> List[str]:
    normalized = (raw or "").replace("，", ",").replace(",", "&").replace("\n", "&")
    return [item.strip() for item in normalized.split("&") if item.strip()]


def mask_account(value: Any) -> str:
    value = str(value or "")
    if len(value) <= 12:
        return value
    return f"{value[:6]}...{value[-4:]}"



def _mask_phone(phone: str) -> str:
    """隐私脱敏：手机号中间4位打码"""
    if not MASK_PRIVACY:
        return phone
    p = str(phone).strip()
    if len(p) == 11 and p.isdigit():
        return p[:3] + "****" + p[7:]
    return p[:2] + "****" + p[-2:] if len(p) > 4 else p

def _mask_ip(ip_str: str) -> str:
    """隐私脱敏：IP地址部分打码"""
    if not MASK_PRIVACY:
        return ip_str
    # Mask private/local IPs: 192.168.x.x, 10.x.x.x, 127.x.x.x
    if ip_str.startswith(("192.168.", "10.", "127.")):
        parts = ip_str.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
    # Mask public proxy IPs: keep first octet only
    parts = ip_str.split(":")
    host = parts[0]
    port = parts[1] if len(parts) > 1 else ""
    octets = host.split(".")
    if len(octets) == 4:
        masked_host = f"{octets[0]}.*.*.{octets[3]}"
        return f"{masked_host}:{port}" if port else masked_host
    return ip_str
def direct_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.verify = False
    return session


def parse_proxy_response_pz(text):
    """Parse proxy response from Pizan API."""
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    text = text.strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        proxy_obj = None
        if isinstance(data.get("data"), list) and data["data"]:
            proxy_obj = data["data"][0]
        elif isinstance(data.get("data"), dict):
            proxy_obj = data["data"]
        elif data.get("ip") and data.get("port"):
            proxy_obj = data
        elif isinstance(data.get("result"), dict):
            proxy_obj = data["result"]
        if proxy_obj:
            host = proxy_obj.get("ip") or proxy_obj.get("host")
            port = proxy_obj.get("port")
            if host and port:
                return {
                    "host": str(host),
                    "port": int(port),
                    "username": proxy_obj.get("user") or proxy_obj.get("username") or "",
                    "password": proxy_obj.get("pass") or proxy_obj.get("password") or "",
                }
    except Exception:
        pass
    if ":" in text:
        parts = text.split(":")
        if len(parts) >= 2:
            try:
                return {
                    "host": parts[0],
                    "port": int(parts[1]),
                    "username": parts[2] if len(parts) > 2 else "",
                    "password": parts[3] if len(parts) > 3 else "",
                }
            except (ValueError, IndexError):
                pass
    return None


def build_proxy_dict_pz(proxy_info):
    """Build requests-compatible proxy dict from parsed proxy info."""
    if not proxy_info:
        return None
    host = proxy_info["host"]
    port = proxy_info["port"]
    username = proxy_info.get("username", "")
    password = proxy_info.get("password", "")
    auth = ""
    if username and password:
        auth = f"{url_encode(username)}:{url_encode(password)}@"
    scheme = "socks5" if PROXY_TYPE == "socks5" else "http"
    proxy_url = f"{scheme}://{auth}{host}:{port}"
    _log_global(f"🛠️ [代理] 生成 {scheme.upper()} 代理 {host}:{port}")
    return {"http": proxy_url, "https": proxy_url}


def validate_proxy_pz(proxies):
    """Validate proxy by requesting httpbin.org/ip."""
    if not proxies:
        return False, ""
    try:
        response = requests.get(PROXY_VALIDATE_URL, proxies=proxies, timeout=15, verify=False)
        if response.status_code == 200:
            try:
                ip = response.json().get("origin", "未知")
            except Exception:
                ip = "未知"
            _log_global(f"✅ [代理] 验证通过，出口 IP: {_mask_ip(ip)}")
            return True, ip
    except Exception as exc:
        _log_global(f"⚠️ [代理] 验证失败: {exc}")
    return False, ""


def get_valid_proxy_pz(account_name: str):
    """Get a validated proxy from Pizan API, with retry and fallback to direct."""
    if not PROXY_API:
        _log_global(f"⚠️ [代理] {account_name} 未配置 PROXY_API，使用直连")
        return None, ""
    _log_global(f"🌐 [代理] {account_name} 正在获取品赞代理...")
    for index in range(1, PROXY_RETRY_TIMES + 1):
        try:
            response = direct_session().get(PROXY_API, timeout=15)
            proxy_info = parse_proxy_response_pz(response.text)
            if not proxy_info:
                _log_global(f"⚠️ [代理] 第 {index} 次代理解析失败")
                continue
            _log_global(f"✅ [代理] 提取到 {_mask_ip(proxy_info['host'])}:{proxy_info['port']}")
            proxies = build_proxy_dict_pz(proxy_info)
            ok, ip = validate_proxy_pz(proxies)
            if ok:
                return proxies, ip
            _log_global(f"⚠️ [代理] 第 {index} 次代理不可用")
        except Exception as exc:
            _log_global(f"⚠️ [代理] 第 {index} 次获取代理异常: {exc}")
        if index < PROXY_RETRY_TIMES:
            time.sleep(2)
    _log_global("⚠️ [代理] 获取失败，使用直连")
    return None, ""


def request_with_proxy(
    method: str,
    url: str,
    *,
    proxies=None,
    server: str = "",
    **kwargs,
):
    """Make request with proxy, fallback to direct on failure."""
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    kwargs.setdefault("verify", False)
    if proxies:
        try:
            return requests.request(method, url, proxies=proxies, **kwargs)
        except Exception as exc:
            _log_global(f"⚠️ [代理] {server} 代理请求失败: {exc}")
            if not ENABLE_DIRECT_FALLBACK:
                raise
            _log_global("🔁 [兜底] 切换直连重试")
    session = direct_session()
    return session.request(method, url, **kwargs)


def send_pushplus(title: str, content: str) -> None:
    """Send push notification via PushPlus."""
    if not PLUSPLUS_TOKEN:
        _log_global("⚠️ [PushPlus] 未配置 PLUSPLUS_TOKEN，跳过推送")
        return
    try:
        requests.post(
            "https://www.pushplus.plus/send",
            json={
                "token": PLUSPLUS_TOKEN,
                "title": title,
                "content": content,
                "template": "txt",
            },
            timeout=10,
        )
        _log_global("✅ [PushPlus] 推送成功")
    except Exception as exc:
        _log_global(f"❌ [PushPlus] 推送失败: {exc}")

# ==================== AutoCookieManager ====================
UCMP_BASE = "https://ucmp.sf-express.com"

class AutoCookieManager:
    def __init__(self, wx_server: str = None):
        self.wx_server = (wx_server or "").strip().rstrip("/")
        self.session = requests.Session()
        self.session.verify = False
    
    def _get_wx_code(self, server: str = None, appid: str = None, max_retries: int = 3) -> Optional[str]:
        """通过 GET /login?appId=xxx 获取微信 code

        请求: GET {server}/login?appId={appid}
        成功响应: {"err":0,"msg":"success","code":"xxx"}
        """
        code_server = (server or self.wx_server).strip().rstrip("/")
        if not code_server:
            _log_global("❌ 未配置 code 服务地址，无法获取 code")
            return None
        target_appid = appid or SF_WX_APPID
        url = f"{code_server}/login"
        if not code_server.startswith("http"):
            url = f"http://{code_server}/login"

        for attempt in range(max_retries):
            try:
                r = self.session.get(url, params={"appId": target_appid}, timeout=30)
                j = r.json()

                # 兼容铛铛一下接口格式: {"err":0,"code":"xxx"}
                if j.get("err") == 0 and j.get("code"):
                    _log_global(f"✅ code 获取成功 appid={target_appid}")
                    return str(j["code"])

                # 兼容旧 POST 接口格式
                if j.get("code") == 0:
                    data = j.get("data") or {}
                    result = data.get("result") if isinstance(data, dict) else {}
                    if isinstance(result, dict) and result.get("code"):
                        return str(result["code"])

                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 3
                    _log_global(f"⚠️ code为空，{wait}s后重试({attempt+1}/{max_retries}) resp={str(j)[:160]}")
                    time.sleep(wait)
                    continue
                _log_global(f"❌ 获取code失败 appid={target_appid} resp={str(j)[:160]}")
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 3
                    _log_global(f"⚠️ code异常 {str(e)[:60]}，{wait}s后重试({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                _log_global(f"❌ 获取code异常 appid={target_appid} err={str(e)[:80]}")
                return None

    def _ucmp_app_on_login(self, code: str) -> Optional[Dict]:
        try:
            url = f"{UCMP_BASE}/wxaccess/weixin/appOnLogin"
            resp = request_with_proxy(
                "GET", url,
                params={"code": code, "publicId": SF_PUBLIC_ID},
                proxies=self.session.proxies if self.session.proxies else None,
                server="appOnLogin",
                timeout=25,
                cookies=self.session.cookies.get_dict(),
            )
            j = resp.json()
            if j.get("sessionId") and j.get("openid"):
                return j
            return None
        except Exception:
            return None


    def _get_oauth_redirect_info(self, ucmp_sid: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            s = requests.Session()
            s.verify = False
            s.headers.update({
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 MicroMessenger/8.0.50",
                "Accept": "text/html,*/*",
                "Cookie": f"suuid={ucmp_sid}",
            })
            r = s.get(f"{UCMP_BASE}/wxaccess/weixin/activity/sfmemfe?p1={SF_OAUTH_SCENE}", allow_redirects=False, timeout=25)
            oauth_url = r.headers.get("Location", "")
            if not oauth_url: return None, None
            parsed = urlparse(oauth_url)
            qs = parse_qs(parsed.query)
            redirect_uri = unquote(qs.get("redirect_uri", [""])[0])
            state = qs.get("state", [""])[0]
            return redirect_uri, state
        except Exception: return None, None
    
    def get_cookie_for_wxid(self, server: str) -> Optional[str]:
        """通过 GET /login?appId=xxx 拿到 code 后，走 UCMP 换取顺丰 Cookie。

        说明：
        - 旧版 OAuth 回调链路容易只拿到 sessionId，但 _login_mobile_ / _login_user_id_ 为空
        - 这里对齐 sfsy/sfkd 的 sfnewactivity 换绑流程，保证业务 Cookie 完整
        """
        code = self._get_wx_code(server, SF_WX_APPID)
        if not code:
            return None

        ucmp = self._ucmp_app_on_login(code)
        if not ucmp:
            _log_global(f"❌ {server} appOnLogin 失败")
            return None

        suuid = ucmp.get("sessionId", "")
        if not suuid:
            _log_global(f"❌ {server} appOnLogin 未返回 sessionId")
            return None

        try:
            s = requests.Session()
            s.verify = False
            ua = (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
                "MicroMessenger/8.0.69(0x1800452d) NetType/WIFI Language/zh_CN"
            )

            # 尝试查询绑定信息（失败不阻断，后续仍可从 Cookie 取手机号）
            try:
                bind_headers = {
                    "user-agent": ua,
                    "content-type": "application/json",
                    "accept": "application/json, text/plain, */*",
                    "cookie": f"suuid={suuid}",
                    "referer": f"https://servicewechat.com/{SF_WX_APPID}/663/page-frame.html",
                }
                s.post(
                    "https://ucmp.sf-express.com/wxopen/weixin/wxMemIsBind",
                    json={},
                    headers=bind_headers,
                    timeout=15,
                )
            except Exception:
                pass

            biz_code = json.dumps({
                "path": "/up-member/newPoints",
                "linkCode": "SFAC20230803190840424",
                "supportShare": "YES",
                "subCategoryCode": "1",
                "from": "mypoint",
                "categoryCode": "1",
            }, ensure_ascii=False)
            sfnew_url = (
                "https://ucmp.sf-express.com/wechat-act/weixin/activity/sfnewactivity?"
                f"bizCode={url_encode(biz_code)}&regSource=mypoint&citycode=025"
                f"&cityname={url_encode('广州')}&wxapp-version=V17.49&suuid={suuid}"
            )
            sfnew_headers = {
                "user-agent": ua,
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            s.get(sfnew_url, headers=sfnew_headers, timeout=25, allow_redirects=True)

            cookies = {}
            for c in s.cookies:
                if "mcs-mimp" in c.domain or "sf-express" in c.domain:
                    cookies[c.name] = c.value

            session_id = cookies.get("sessionId") or s.cookies.get("sessionId", "")
            login_mobile = cookies.get("_login_mobile_") or s.cookies.get("_login_mobile_", "")
            login_user_id = cookies.get("_login_user_id_") or s.cookies.get("_login_user_id_", "")

            # 兜底：部分环境下需要再访问会员页补齐 cookie
            if session_id and (not login_mobile or not login_user_id):
                try:
                    s.headers.update({
                        "User-Agent": ua,
                        "Cookie": f"sessionId={session_id}",
                    })
                    s.get(
                        "https://mcs-mimp-web.sf-express.com/mcs-mimp/app/index.html",
                        allow_redirects=True,
                        timeout=15,
                    )
                    for c in s.cookies:
                        if "mcs-mimp" in c.domain or "sf-express" in c.domain:
                            cookies[c.name] = c.value
                    login_mobile = cookies.get("_login_mobile_", "")
                    login_user_id = cookies.get("_login_user_id_", "")
                    session_id = cookies.get("sessionId", session_id)
                except Exception:
                    pass

            if not session_id or not login_mobile or not login_user_id:
                _log_global(
                    f"❌ {server} Cookie 不完整 session={bool(session_id)} "
                    f"mobile={bool(login_mobile)} uid={bool(login_user_id)}"
                )
                return None

            parts = [
                f"sessionId={session_id}",
                f"_login_mobile_={login_mobile}",
                f"_login_user_id_={login_user_id}",
            ]
            for k in ["HWWAFSESTIME", "HWWAFSESID", "JSESSIONID"]:
                if k in cookies and cookies[k]:
                    parts.append(f"{k}={cookies[k]}")

            cookie_str = ";".join(parts)
            _masked_phone = login_mobile[:3] + "****" + login_mobile[7:] if len(login_mobile) >= 7 else login_mobile
            _log_global(f"✅ {_mask_ip(server)} 自动获取凭证换绑成功 ➔ 手机: {_masked_phone}")
            return cookie_str
        except Exception as e:
            _log_global(f"❌ {server} 换取 Cookie 异常: {str(e)[:80]}")
            return None

    def get_cookies_for_servers(self, servers: List[str] = None) -> Dict[str, str]:
        """对每个 code 服务地址获取顺丰 Cookie。"""
        if not servers:
            servers = parse_env_accounts(SF_CODE_SERVERS_RAW)
        results = {}
        for i, server in enumerate(servers):
            try:
                cookie = self.get_cookie_for_wxid(server)
                if cookie: results[server] = cookie
            except Exception: pass
            if i < len(servers) - 1: time.sleep(2)
        return results
# ==================== HTTP 客户端 ====================
class SFHttpClient:
    def __init__(self, account_name: str = ""):
        self.session = requests.Session()
        self.session.verify = False
        self.proxy_display = '直连'
        self.session.proxies = {}
        self._setup_proxy(account_name)
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'channel': 'xcxpart',
            'platform': 'MINI_PROGRAM',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

    def _setup_proxy(self, account_name: str = ""):
        proxies, proxy_ip = get_valid_proxy_pz(account_name)
        if proxies:
            self.session.proxies = proxies
            self.proxy_display = proxy_ip or "代理"
        else:
            self.proxy_display = "直连"

    def switch_to_app_mode(self):
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 mediaCode=SFEXPRESSAPP-iOS-ML',
            'channel': '26sjbapp',
            'platform': 'SFAPP',
        })

    def switch_to_xcx_mode(self):
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027',
            'channel': 'xcxpart',
            'platform': 'MINI_PROGRAM',
        })

    def _generate_sign(self) -> Dict[str, str]:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        return {'syscode': SYS_CODE, 'timestamp': timestamp, 'signature': signature}

    def request(self, url: str, data: Optional[Dict] = None, extra_headers: Optional[Dict[str, str]] = None) -> Optional[Dict]:
        sign_data = self._generate_sign()
        headers = {**self.headers, **sign_data}
        if extra_headers:
            headers.update(extra_headers)
        try:
            resp = request_with_proxy(
                "POST", url,
                headers=headers,
                json=data or {},
                proxies=self.session.proxies if self.session.proxies else None,
                server=self.proxy_display,
                timeout=REQUEST_TIMEOUT,
                cookies=self.session.cookies.get_dict(),
            )
            resp.raise_for_status()
            # Update session cookies from response
            for name, value in resp.cookies.get_dict().items():
                self.session.cookies.set(name, value)
            return resp.json()
        except Exception:
            return None


    def login(self, url: str) -> Tuple[bool, str, str]:
        try:
            decoded = unquote(url)
            if decoded.startswith('sessionId=') or '_login_mobile_=' in decoded:
                cookie_dict = {}
                for item in decoded.split(';'):
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        cookie_dict[k] = v
                for k, v in cookie_dict.items():
                    self.session.cookies.set(k, v, domain='mcs-mimp-web.sf-express.com')
                user_id = cookie_dict.get('_login_user_id_', '')
                phone = cookie_dict.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
            else:
                self.session.get(decoded, headers=self.headers, timeout=REQUEST_TIMEOUT)
                cookies = self.session.cookies.get_dict()
                user_id = cookies.get('_login_user_id_', '')
                phone = cookies.get('_login_mobile_', '')
                return (True, user_id, phone) if phone else (False, '', '')
        except Exception: return False, '', ''


# ==================== 日常积分任务执行器 ====================
class DailyTaskExecutor:
    def __init__(self, http: SFHttpClient, logger: Logger, user_id: str):
        self.http = http
        self.logger = logger
        self.user_id = user_id
        self.total_points = 0
        self.taskId = ""
        self.taskCode = ""
        self.strategyId = 0
        self.title = ""
        self.point = 0
        self.completed_count = 0
        self.rewarded_count = 0

    @staticmethod
    def generate_device_id() -> str:
        result = ""
        for char in "xxxxxxxx-xxxx-xxxx":
            result += random.choice("abcdef0123456789") if char == "x" else char
        return result

    def _extract_task_id_from_url(self, url: str) -> str:
        """从 buttonRedirect 的 _ug_view_param 中提取 taskId/taskCode。"""
        if not url:
            return ""
        try:
            parsed = urlparse(str(url))
            params = parse_qs(parsed.query)
            if "_ug_view_param" in params:
                ug_params = json.loads(unquote(params["_ug_view_param"][0]))
                for key in ("taskId", "taskCode", "task_id"):
                    if ug_params.get(key):
                        return str(ug_params[key])
            # 兜底：正则抓 taskId
            m = re.search(r'"taskId"\s*:\s*"([^"]+)"', str(url))
            if m:
                return m.group(1)
        except Exception:
            pass
        return ""

    def _resolve_task_code(self, task: Dict) -> str:
        code = str(task.get("taskCode") or "").strip()
        if code:
            return code
        # 部分浏览任务 taskCode 为空，真实 code 在跳转参数里
        for key in ("buttonRedirect", "taskJumpAddress", "redirectUrl"):
            extracted = self._extract_task_id_from_url(task.get(key, ""))
            if extracted:
                return extracted
        return ""

    def _set_task_attrs(self, task: Dict):
        self.taskId = str(task.get("taskId", "") or "")
        self.taskCode = self._resolve_task_code(task)
        try:
            self.strategyId = int(task.get("strategyId", 0) or 0)
        except Exception:
            self.strategyId = 0
        self.title = str(task.get("title", "未知任务") or "未知任务")
        try:
            self.point = int(task.get("point", 0) or task.get("awardIntegral", 0) or 0)
        except Exception:
            self.point = 0

    def sign_in(self) -> Tuple[bool, str]:
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage"
        resp = self.http.request(url, {"comeFrom": "vioin", "channelFrom": "WEIXIN"})
        if resp and resp.get("success"):
            obj = resp.get("obj") or {}
            packets = obj.get("integralTaskSignPackageVOList") or []
            count_day = obj.get("countDay", obj.get("countDays", "-"))
            if packets:
                self.logger.success(
                    f"小程序签到成功: 【{packets[0].get('packetName')}】，本周累计【{count_day}】天"
                )
            else:
                # hasFinishSign=1 表示今日已签
                if obj.get("hasFinishSign") == 1:
                    self.logger.info(f"小程序今日已签到，本周累计【{count_day}】天")
                else:
                    self.logger.success(f"小程序签到完成，本周累计【{count_day}】天")
            return True, ""
        err = (resp or {}).get("errorMessage") or "失败"
        self.logger.warning(f"小程序签到失败: {err}")
        return False, err

    def get_task_list(self) -> List[Dict]:
        """拉取多 channel 任务并去重，兼容 taskCode 为空的浏览任务。"""
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES"
        all_tasks: List[Dict] = []
        seen = set()

        for ct in ["1", "2", "3", "4", "01", "02", "03", "04"]:
            resp = self.http.request(url, {
                "channelType": ct,
                "deviceId": self.generate_device_id(),
            })
            if not (resp and resp.get("success") and resp.get("obj")):
                continue

            obj = resp["obj"] or {}
            # 优先记录 channel 1 的积分
            if ct in ("1", "01") or not self.total_points:
                self.total_points = int(obj.get("totalPoint", self.total_points) or self.total_points or 0)

            task_items = obj.get("taskTitleLevels") or obj.get("ESobj") or []
            if not isinstance(task_items, list):
                continue

            for task in task_items:
                if not isinstance(task, dict):
                    continue
                task = dict(task)
                tc = self._resolve_task_code(task)
                if tc:
                    task["taskCode"] = tc
                # 去重键：优先 taskCode，其次 taskId+title
                key = tc or f"{task.get('taskId','')}|{task.get('title','')}"
                if not key or key in seen:
                    continue
                seen.add(key)
                all_tasks.append(task)

        return all_tasks

    def execute_task(self) -> bool:
        if not self.taskCode:
            return False
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask"
        resp = self.http.request(url, {"taskCode": self.taskCode})
        if not resp:
            self.logger.warning(f"任务提交无响应: {self.title}")
            return False
        if resp.get("success"):
            # 有些任务 success=true 但 obj=false，表示服务端接受但未真正完成
            if resp.get("obj") is False:
                self.logger.warning(f"任务提交返回未完成: {self.title}")
                return False
            self.logger.success(f"任务提交成功: {self.title}")
            self.completed_count += 1
            return True
        err = resp.get("errorMessage") or "未知错误"
        self.logger.warning(f"任务提交失败: {self.title} ➔ {err}")
        return False

    def receive_task_reward(self) -> bool:
        if not self.taskCode:
            return False
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral"
        data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": self.taskCode,
            "deviceId": self.generate_device_id(),
        }
        resp = self.http.request(url, data)
        if resp and resp.get("success"):
            self.logger.success(f"日常任务奖励领取成功 ➔ {self.title} (+{self.point})")
            self.rewarded_count += 1
            return True
        err = (resp or {}).get("errorMessage") or "领取失败"
        self.logger.warning(f"奖励领取失败: {self.title} ➔ {err}")
        return False

    def run(self) -> Tuple[int, int]:
        self.logger.task("开始获取日常积分任务列表")
        tasks = self.get_task_list()
        if not tasks:
            self.logger.warning("日常任务列表为空")
            return 0, 0

        points_before = self.total_points
        self.logger.points(points_before, "执行前积分")
        self.logger.info(f"共发现 {len(tasks)} 个日常任务")

        for task in tasks:
            title = str(task.get("title") or "未知任务")
            status = task.get("status")
            try:
                status = int(status)
            except Exception:
                pass

            # 3 = 已完成
            if status == 3:
                self.logger.info(f"已完成: {title}")
                continue

            if title in DAILY_SKIP_TASKS:
                self.logger.info(f"跳过不可自动完成任务: {title}")
                continue

            self._set_task_attrs(task)
            if not self.taskCode:
                self.logger.warning(f"无法提取 taskCode，跳过: {title}")
                continue

            self.logger.task(f"处理任务: {title} (status={status}, +{self.point})")

            # status 1 = 待完成，先提交
            if status == 1:
                # 连续签到类进度未满则跳过
                process = str(task.get("process") or "")
                if "连签" in title and "/" in process:
                    try:
                        current, total = map(int, process.split("/", 1))
                        if current < total:
                            self.logger.info(f"{title} 进度 {process}，暂不可领")
                            continue
                    except Exception:
                        pass

                if self.execute_task():
                    time.sleep(2)
                    status = 2
                else:
                    time.sleep(1)
                    continue

            # status 2 = 可尝试领奖；失败则先完成再领
            if status == 2:
                # 浏览类关键词优先完成再领
                need_execute_first = any(kw in title for kw in EXECUTE_FIRST_KEYWORDS)
                if need_execute_first:
                    self.execute_task()
                    time.sleep(2)
                    if self.receive_task_reward():
                        time.sleep(1)
                        continue

                # 先尝试直接领奖
                if self.receive_task_reward():
                    time.sleep(1)
                    continue

                # 直接领失败，再执行一次后重试
                if self.execute_task():
                    time.sleep(2)
                    self.receive_task_reward()
                time.sleep(1)
                continue

            time.sleep(1)

        # 刷新积分
        self.get_task_list()
        points_after = self.total_points
        self.logger.points(points_after, "执行后积分")
        earned = points_after - points_before
        if self.completed_count == 0 and self.rewarded_count == 0:
            self.logger.info(
                "说明: 当前可自动完成的浏览/点击类任务已全部完成；"
                "剩余未完成任务多为真实寄件/设置类，需人工操作"
            )
        self.logger.info(
            f"日常任务统计: 提交成功 {self.completed_count}，领奖成功 {self.rewarded_count}，积分变化 {earned:+d}"
        )
        return points_before, points_after


# ==================== 会员日活动执行器 ====================
class MemberDayExecutor:
    MAX_LEVEL = 8
    def __init__(self, http: SFHttpClient, logger: Logger, user_id: str):
        self.http = http
        self.logger = logger
        self.user_id = user_id
        self.black = False
        self.red_packet_map: Dict[int, int] = {}

    def get_index(self) -> Optional[Dict]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~index'
        resp = self.http.request(url, {'inviteUserId': ''})
        return resp.get('obj', {}) if resp and resp.get('success') else None

    def lottery(self) -> Optional[str]:
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'
        resp = self.http.request(url, {})
        if resp and resp.get('success'):
            name = resp.get('obj', {}).get('productName', '未抽中')
            self.logger.success(f'会员日抽奖成功 ➔ 获得: {name}')
            return name
        return None

    def run(self) -> Dict[str, Any]:
        result = {'lottery_prizes': []}
        index_info = self.get_index()
        if not index_info: return result
        lottery_num = index_info.get('lotteryNum', 0)
        for _ in range(lottery_num):
            prize = self.lottery()
            if prize: result['lottery_prizes'].append(prize)
        return result



# ==================== 世界杯兑奖执行器 ====================
class ExchangeExecutor:
    BASE_URL = 'https://mcs-mimp-web.sf-express.com/mcs-mimp'

    def __init__(self, http: SFHttpClient, logger: Logger, phone: str, selected_items: Optional[set] = None):
        self.http = http
        self.logger = logger
        self.phone = phone
        # selected_items: 要兑换的奖品名称集合；None=用配置表里 enabled=True 的
        self.selected_items = selected_items

    def _post(self, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        url = f'{self.BASE_URL}{path}'
        return self.http.request(url, data=data or {})

    # ===== 接口 =====

    def get_prize_pool(self) -> Optional[List[Dict]]:
        """获取奖池（含抽奖 LOTTERY 和兑换 EXCHANGE）"""
        resp = self._post('/commonPost/~memberNonactivity~worldCupLotteryService~prizePool')
        if resp and resp.get('success'):
            return resp.get('obj', [])
        return None

    def prize_draw(self, rule_type: str, should_num: int, rule_code: str, gift_pool_code: str) -> Optional[Dict]:
        """兑换/抽奖下单"""
        data = {
            "ruleType": rule_type,
            "shouldNum": should_num,
            "ruleCode": rule_code,
            "giftPoolCode": gift_pool_code,
        }
        resp = self._post('/commonPost/~memberNonactivity~worldCupLotteryService~prizeDraw', data)
        if resp and resp.get('success'):
            return resp.get('obj', {})
        err = resp.get('errorMessage', '未知错误') if resp else '请求失败'
        self.logger.warning(f'兑换失败: {err}')
        return None

    def query_address_book(self) -> Optional[List[Dict]]:
        """查询地址簿"""
        resp = self._post('/commonPost/~memberActivity~addressBookService~queryAddressBook')
        if resp and resp.get('success'):
            obj = resp.get('obj', {})
            return obj.get('result', [])
        return None

    def fill_receive_info(self, order_no: str, addr: Dict) -> bool:
        """填写实物收货地址"""
        data = {
            "orderNo": order_no,
            "receiver": addr.get("contactName", ""),
            "receiverMobile": addr.get("contactTel", "") or addr.get("contactPhone", ""),
            "addrDetail": addr.get("address", ""),
            "provinceCode": addr.get("provinceCode", ""),
            "provinceName": addr.get("province", ""),
            "cityCode": addr.get("cityCode", ""),
            "cityName": addr.get("city", ""),
            "countyCode": addr.get("countyCode", ""),
            "countyName": addr.get("county", ""),
        }
        resp = self._post('/commonPost/~activityCore~deliverOrderService~fillReceiveInfo', data)
        return bool(resp and resp.get('success'))

    # ===== 主流程 =====

    def run(self) -> Dict[str, Any]:
        result = {'exchange_items': [], 'failed_items': []}

        # 先查一次奖池，获取已兑次数（lotteryNum）和库存状态
        self.logger.info('查询兑奖奖池...')
        pool = self.get_prize_pool()
        if pool is None:
            self.logger.error('获取奖池失败')
            return result

        # 从奖池中提取每项的已兑次数和售罄状态
        pool_map = {}  # ruleCode -> {lotteryNum, soldOut, soldOutToday}
        for item in pool:
            if item.get('ruleType') == 'EXCHANGE':
                pool_map[item.get('ruleCode', '')] = {
                    'lotteryNum': item.get('lotteryNum', 0),
                    'soldOut': item.get('soldOut', False),
                    'soldOutToday': item.get('soldOutToday', False),
                }

        # 遍历配置表，根据 selected_items 或 enabled 决定兑换项
        for name, cfg in EXCHANGE_ITEMS.items():
            # 如果指定了 selected_items，用它判断；否则用配置表的 enabled
            if self.selected_items is not None:
                if name not in self.selected_items:
                    continue
            else:
                if not cfg.get('enabled'):
                    continue

            rule_code = cfg['ruleCode']
            should_num = cfg['shouldNum']
            gift_pool_code = cfg['giftPoolCode']
            limit = cfg.get('limitLotteryNum', 1)

            # 检查奖池状态
            pool_info = pool_map.get(rule_code, {})
            already = pool_info.get('lotteryNum', 0)
            sold_out = pool_info.get('soldOut', False)
            sold_today = pool_info.get('soldOutToday', False)

            if sold_out or sold_today:
                self.logger.info(f'[{name}] 已售罄，跳过')
                continue

            remaining = limit - already
            if remaining <= 0:
                self.logger.info(f'[{name}] 已兑 {already}/{limit} 次，跳过')
                continue

            self.logger.task(f'[{name}] 兑换（{should_num}金豆/次，剩余 {remaining}/{limit} 次）')

            # 按剩余次数循环兑换
            for i in range(remaining):
                draw_result = self.prize_draw('EXCHANGE', should_num, rule_code, gift_pool_code)
                if draw_result is None:
                    result['failed_items'].append({'name': name, 'reason': f'第{i+1}次兑换失败'})
                    break

                # 检查产品类型：SFM=实物, SFC=优惠券
                product_list = draw_result.get('productDTOList', [])
                order_no = ''
                is_physical = False
                product_names = []

                for p in product_list:
                    p_type = p.get('productType', '')
                    p_name = p.get('productName', '?')
                    product_names.append(p_name)
                    if p_type == 'SFM':
                        is_physical = True
                        order_no = p.get('orderNo', '')

                product_str = ', '.join(product_names) if product_names else name
                self.logger.success(f'[{name}] 第{i+1}/{remaining}次 兑换成功: {product_str}')

                if is_physical and order_no:
                    # 实物 → 查地址簿并填地址
                    self.logger.task(f'实物奖品，填写收货地址（订单 {order_no}）...')
                    time.sleep(1)
                    addr_book = self.query_address_book()
                    if addr_book:
                        idx = min(EXCHANGE_ADDRESS_INDEX, len(addr_book) - 1)
                        addr = addr_book[idx]
                        addr_str = f'{addr.get("contactName", "")} {_mask_phone(addr.get("contactTel", "")) or _mask_phone(addr.get("contactPhone", ""))} {addr.get("address", "")}'
                        self.logger.info(f'使用地址: {addr_str}')
                        if self.fill_receive_info(order_no, addr):
                            self.logger.success('地址填写成功')
                        else:
                            self.logger.warning('地址填写失败，需手动填写')
                    else:
                        self.logger.warning(f'未获取到地址簿，需手动填写地址（订单 {order_no}）')
                else:
                    # 虚拟券
                    self.logger.info('虚拟奖品（优惠券），无需填写地址')

                result['exchange_items'].append({
                    'name': product_str,
                    'cost': should_num,
                    'is_physical': is_physical,
                    'order_no': order_no,
                })

                time.sleep(2)

        return result

# ==================== 核心处理器 ====================
def run_account(account_raw: str, index: int) -> Dict[str, Any]:
    logger = Logger()
    # fixed_proxy removed, using pizan proxy instead
    account_url = account_raw.split('#')[0].strip() if '#' in account_raw else account_raw
    
    http = SFHttpClient(f'账号{index+1}')
    success, user_id, phone = http.login(account_url)
    if not success:
        return {'success': False, 'phone': '未登录账号'}
        
    masked = phone[:3] + "****" + phone[7:] if len(phone) >= 7 else phone
    logger.success(f"账号 [{index + 1}] ➔ 【{masked}】激活认证成功")
    
    result = {'success': True, 'phone': masked, 'index': index, 'points_earned': 0, 'member_day_prizes': []}
    
    if ENABLE_DAILY_TASK:
        logger.task("开始执行日常积分任务（签到 + 做任务 + 领积分）")
        daily = DailyTaskExecutor(http, logger, user_id)
        # 小程序签到
        daily.sign_in()
        time.sleep(1)
        pb, pa = daily.run()
        result['points_earned'] = pa - pb
        logger.info(f"日常任务积分变化: {pb} -> {pa} ({(pa - pb):+d})")
        
    if ENABLE_MEMBER_DAY and 26 <= datetime.now().day <= 28:
        md = MemberDayExecutor(http, logger, user_id)
        result['member_day_prizes'] = md.run().get('lottery_prizes', [])

    # ── 世界杯金豆兑奖 ──
    _account_server = COOKIE_TO_SERVER.get(account_raw, '')
    _account_exchange_enabled = EXCHANGE_ACCOUNTS.get(_account_server, EXCHANGE_ACCOUNTS.get(account_url, True))
    if ENABLE_WORLD_CUP_EXCHANGE and not _account_exchange_enabled:
        logger.info(f'\u3010{_mask_ip(_account_server or account_url)}\u3011\u5151\u6362\u5df2\u5173\u95ed\uff0c\u8df3\u8fc7')
    elif ENABLE_WORLD_CUP_EXCHANGE and _account_exchange_enabled:
        enabled_list = [k for k, v in EXCHANGE_ITEMS.items() if v.get('enabled')]
        if enabled_list:
            print(f"\u26bd \u4e16\u754c\u676f\u5151\u5956: {enabled_list}")
        else:
            print('\u26bd \u4e16\u754c\u676f\u5151\u5956: \u65e0\u5f00\u542f\u9879')
        logger.task("开始执行世界杯金豆兑奖")
        http.switch_to_app_mode()

        real_phone = phone if phone and '*' not in phone else ''
        if not real_phone:
            try:
                real_phone = http.session.cookies.get('_login_mobile_', '') or ''
            except Exception:
                pass

        if real_phone in EXCLUDE_PHONES:
            logger.info(f'【{_mask_phone(real_phone)}】在排除名单，跳过兑奖')
            result['world_cup_exchange'] = {'exchange_items': [], 'failed_items': [], 'skipped': True}
        else:
            items_for_this_phone = None  # None=use EXCHANGE_ITEMS enabled config
            if real_phone in PHONE_OVERRIDE:
                items_for_this_phone = PHONE_OVERRIDE[real_phone]
                logger.info(f'【{_mask_phone(real_phone)}】使用单独配置: {items_for_this_phone}')

            executor = ExchangeExecutor(http, logger, real_phone, items_for_this_phone)
            wc_result = executor.run()
            result['world_cup_exchange'] = wc_result

            ex_items = wc_result.get('exchange_items', [])
            fail_items = wc_result.get('failed_items', [])
            if ex_items:
                for item in ex_items:
                    tag = '实物' if item.get('is_physical') else '券'
                    logger.success(f'兑奖成功: {item["name"]}({tag})')
            if fail_items:
                for item in fail_items:
                    logger.warning(f'兑奖失败: {item["name"]} - {item.get("reason", "")}')

        http.switch_to_xcx_mode()

    return result


def _auto_fetch_cookies() -> List[str]:
    """通过 SF_CODE_SERVERS 中的 code 服务地址获取多账号 Cookie。"""
    servers = parse_env_accounts(SF_CODE_SERVERS_RAW)
    if not servers:
        _log_global("❌ SF_CODE_SERVERS 为空，无法获取 code")
        return []

    mgr = AutoCookieManager()
    _log_global(f"🔎 解析到 {len(servers)} 个 code 服务地址")
    cookies: List[str] = []
    AUTO_COOKIE_INDEX_BY_VALUE.clear()
    COOKIE_TO_SERVER.clear()

    for index, server in enumerate(servers, 1):
        log_account_header(index, len(servers), server)
        try:
            cookie = mgr.get_cookie_for_wxid(server)
        except Exception as exc:
            cookie = None
            _log_global(f"❌ 账号[{index}] {server} 自动换 Cookie 异常：{str(exc)[:80]}")

        if cookie and "_login_mobile_" in cookie:
            cookies.append(cookie)
            AUTO_COOKIE_INDEX_BY_VALUE[cookie] = index
            COOKIE_TO_SERVER[cookie] = server
            _log_global(f"✅ 账号[{index}] {server} 自动换 Cookie 成功")
            continue

        _log_global(f"❌ 账号[{index}] {server} 自动换 Cookie 失败")
        GLOBAL_NOTIFY_BUFFERS.append({
            "index": index,
            "account": server,
            "ok": False,
            "points": 0,
            "member_day_prizes": [],
            "message": f"自动换取顺丰 Cookie 失败，请检查 code 服务 {server} 是否可用",
        })
        if index < len(servers):
            time.sleep(2)

    _log_global(f"📦 顺丰 Cookie 换取成功 {len(cookies)} / 服务地址 {len(servers)}")
    return cookies


def append_notify_result(index: int, result: Dict[str, Any]) -> None:
    GLOBAL_NOTIFY_BUFFERS.append({
        "index": index,
        "account": _mask_phone(result.get("phone") or "未知账号"),
        "ok": bool(result.get("success")),
        "points": int(result.get("points_earned") or 0),
        "member_day_prizes": result.get("member_day_prizes") or [],
        "world_cup_exchange": result.get("world_cup_exchange") or {},
        "message": result.get("error") or "登录失效",
    })


def build_notify_report() -> str:
    total = len(GLOBAL_NOTIFY_BUFFERS)
    success = sum(1 for item in GLOBAL_NOTIFY_BUFFERS if item.get("ok"))
    failed = total - success
    total_earned = sum(int(item.get("points") or 0) for item in GLOBAL_NOTIFY_BUFFERS if item.get("ok"))

    lines = [
        "==============================",
        f"🕒 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"📊 统计数据：成功 {success} / 总计 {total}",
        f"✅ 成功账号：{success} 个",
        f"❌ 失败账号：{failed} 个",
        f"💰 累计积分：+{total_earned}",
        "==============================",
    ]

    for item in GLOBAL_NOTIFY_BUFFERS:
        ok = bool(item.get("ok"))
        account_icon = "🧑‍💻" if ok else "🧟"
        lines.extend([
            f"{account_icon} 【账号{item.get('index')}】{item.get('account')}",
            f"{'✅' if ok else '❌'} 状态：{'执行成功' if ok else '执行失败'}",
        ])

        if ok:
            lines.append(f"💰 积分：+{item.get('points')}")
            prizes = item.get("member_day_prizes") or []
            if prizes:
                lines.append(f"🎁 会员日：{', '.join(str(p) for p in prizes)}")
            wc = item.get("world_cup_exchange") or {}
            wc_items = wc.get("exchange_items", [])
            wc_failed = wc.get("failed_items", [])
            if wc_items:
                lines.append(f"⚽ 兑奖成功: {len(wc_items)}件")
            if wc_failed:
                lines.append(f"⚽ 兑奖失败: {len(wc_failed)}件")
        else:
            lines.append(f"🧨 原因：{item.get('message')}")

        lines.append("------------------------------")

    return "\n".join(lines)


def dispatch_notify() -> None:
    if not GLOBAL_NOTIFY_BUFFERS:
        return
    final_desp = build_notify_report()
    print("\n[推送报表阅览]\n" + final_desp)
    send_pushplus(SCRIPT_TITLE, final_desp)


def main():
    log_title()
    account_list = _auto_fetch_cookies()
    
    if not account_list:
        print("❌ 未捕获到顺丰账号凭证，请检查 SF_CODE_SERVERS 是否配置正确")
        GLOBAL_NOTIFY_BUFFERS.append({
            "index": 0,
            "account": "未配置",
            "ok": False,
            "points": 0,
            "member_day_prizes": [],
            "message": "未捕获到在线顺丰账号凭证",
        })
        dispatch_notify()
        return 1


    print("==================================================")
    print(f"🎉 顺丰速运任务启动... 共加载 {len(account_list)} 个账户")
    if ENABLE_WORLD_CUP_EXCHANGE:
        _any_account_exchange = any(EXCHANGE_ACCOUNTS.get(COOKIE_TO_SERVER.get(raw, ''), EXCHANGE_ACCOUNTS.get(raw, True)) for raw in account_list)
        enabled_list = [k for k, v in EXCHANGE_ITEMS.items() if v.get('enabled')]
        if _any_account_exchange and enabled_list:
            print(f"\u26bd \u4e16\u754c\u676f\u5151\u5956: {enabled_list}")
        elif enabled_list:
            print('\u26bd \u4e16\u754c\u676f\u5151\u5956: \u6240\u6709\u8d26\u53f7\u5df2\u5173\u95ed\u5151\u6362')
        else:
            print('\u26bd \u4e16\u754c\u676f\u5151\u5956: \u65e0\u5f00\u542f\u9879')
    ok_count = 0
    for idx, raw in enumerate(account_list):
        result = run_account(raw, idx)
        append_notify_result(AUTO_COOKIE_INDEX_BY_VALUE.get(raw, idx + 1), result)
        if result.get('success'):
            ok_count += 1
        time.sleep(2)

    success_count = sum(1 for item in GLOBAL_NOTIFY_BUFFERS if item.get("ok"))
    fail_count = len(GLOBAL_NOTIFY_BUFFERS) - success_count
    print()
    print("╔" + "═" * 50 + "╗")
    print("\u2551 🏁 顺丰速运任务执行完成                      \u2551")
    print(f"\u2551 ✅ 成功: {success_count:<39}\u2551")
    print(f"\u2551 ❌ 失败: {fail_count:<39}\u2551")
    print(f"\u2551 🕒 结束时间: {now_text():<32}\u2551")
    print("╚" + "═" * 50 + "╝")
    dispatch_notify()
    total_failed = sum(1 for item in GLOBAL_NOTIFY_BUFFERS if not item.get("ok"))
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

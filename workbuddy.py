#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# ============================================================
  WorkBuddy 成长中心自动签到脚本 v25
  适配青龙面板 / 本机定时任务
============================================================

【快速开始（30 秒上手）】
    1) 青龙添加环境变量：WORKBUDDY_ACCESS_TOKEN = token1@token2 （多账号用 @ 分隔；
       也可拆成 WORKBUDDY_ACCESS_TOKEN_1 / _2 ... 多个变量）。Token 即 Bearer Token
       （以 eyJ 开头的长字符串，有效期约 1 年）
    2) （可选，仅本机运行）保持 WorkBuddy Desktop 运行，脚本会自动发现 desktop info 里的 accessToken
    3) 青龙新建任务：命令 `task python3 workbuddy_checkin_发帖版.py`，
       定时如 `30 23 * * *`，保存运行即可
  
    Token 获取：登录 WorkBuddy/CodeBuddy 桌面端 → 找到 workbuddy-desktop-*.info
      → 复制 auth.accessToken 的值
    （本发帖版不含任何真实 Token，请妥善保管你自己的 Token，勿发到公开仓库）
  
  【功能说明】
  自动完成 WorkBuddy (workbuddy.cn) 成长中心的每日任务：
  - 每日签到 (Billing Checkin)
  - 连续签到追踪
  - 成长任务自动接受 & 完成 & 领取
  - 抽奖 / 盲盒 / Buddy 宠物
  - PushPlus 推送通知

【任务自动化状态】
  ✅ 纯云端（青龙可做）：
    体验「设计创意模式」 / 探索优秀灵感 / 召唤3次专家团
    尝鲜热门技能 / 召唤5次专家 / 使用5个模板 / 设置自动化任务
    领取Buddy / 每日签到 / 抽奖 / 盲盒
    桌面端对话1次（RichMeow_Chat，WebChat API 完成）

  🔧 聊天任务（v22 纯云端可靠完成，无需桌面端）：
    体验「GLM-5.2」模型 / 和AI聊天5次 / 参与「夜猫子」夜间折扣活动
    → 通过 WebChat API + 遥测事件联合触发，纯青龙面板可靠完成
    → 夜猫子还需要在 23:00-08:00 之间运行

  🆕 动态任务识别（v20 起，v23 增强）：
    脚本自动根据 API 返回的 jump_url / icon_url / tag / task_type 分类
    WorkBuddy 新增/更新任务时无需改代码，脚本自动适配
    v23 新增：tag=PC 自动识别为桌面任务，未知任务按 jump_url 自动分发遥测

【青龙面板配置】
  1. 上传本脚本到青龙
  2. 添加环境变量：
     - WORKBUDDY_ACCESS_TOKEN = <你的 Bearer Token>
       获取方法：登录 WorkBuddy Desktop → 找到 workbuddy-desktop.info 文件
       → 复制 auth.accessToken 的值 (以 eyJ 开头的长字符串)
       → 有效期约1年
     - PUSHPLUS_TOKEN = <你的 PushPlus token>（可选，用于推送通知）
  3. 删除旧的 WORKBUDDY_KEYCLOAK 环境变量（已弃用）
  4. 定时规则：0 7,9 * * *
     （早上7点和9点各跑一次，覆盖日常任务）

【本机 Windows 夜猫子任务】
  夜猫子任务需要 23:00-08:00 之间运行（现在不再需要 ACP 守护进程）：
  1. 确保 WorkBuddy Desktop 保持运行
  2. 脚本会自动发现 desktop info 文件，无需额外环境变量
  3. 建议用 Windows 任务计划程序设置凌晨定时执行
     或手动在夜间运行：python workbuddy_checkin_v22.py

【认证方式优先级】
  1. WORKBUDDY_ACCESS_TOKEN（推荐，有效期约1年）
  2. WORKBUDDY_KEYCLOAK（Keycloak SSO Cookie，可能拿不到 Bearer token）
  3. WORKBUDDY_COOKIE（原始 Cookie，最短有效期）
  4. 自动发现本机 desktop info 文件（仅本机运行时）

【环境变量一览】
  WORKBUDDY_ACCESS_TOKEN  - Bearer Token（推荐）
  WORKBUDDY_KEYCLOAK      - Keycloak SSO Cookie 字符串
  WORKBUDDY_COOKIE        - 原始 Cookie 字符串
  WORKBUDDY_ACP_BASE_URL  - ACP 守护进程地址（默认自动发现）
  WORKBUDDY_DESKTOP_INFO  - desktop info 文件路径（默认自动发现）
  WORKBUDDY_REDEEM_CODE   - 兑换码（可选）
  PUSHPLUS_TOKEN          - PushPlus 推送 Token（可选）
  PROXY_API               - 品赞代理提取 API（可选，配置后所有请求自动走代理）
  PROXY_TYPE              - http / socks5，默认 http

【品赞代理支持】
  配置 PROXY_API 环境变量后，所有 Growth API / 遥测 / Keycloak 请求将自动走代理：
  - PROXY_API = 你的品赞代理提取链接（如 https://xxx.pinzan.cc/extract?...）
  - PROXY_TYPE = http（默认）或 socks5
  - 代理失效时自动回退直连

【多账号支持】
  用 @ 分隔多个 Token：
  WORKBUDDY_ACCESS_TOKEN = token1@token2@token3
  或用编号：
  WORKBUDDY_ACCESS_TOKEN_1 = token1
  WORKBUDDY_ACCESS_TOKEN_2 = token2
============================================================
"""


# ============================================================
# 更新日志 (Changelog)
# ============================================================
# v1  - 初始版本：基础签到 + Cookie 认证
# v2  - 添加连续签到追踪
# v3  - 添加抽奖功能
# v4  - 添加 PushPlus 推送通知
# v5  - 多账号支持（@ 分隔 / 编号）
# v6  - 添加 Keycloak SSO 刷新、夜猫子任务、Desktop Info 自动发现
# v7  - 优化 Keycloak 会话刷新逻辑
# v8  - 新增 ACP 协议支持，可通过 WorkBuddy Desktop 发起真实对话
# v9  - ACP 稳定性改进，重连机制
# v10 - 新增盲盒开启、Buddy 宠物查看
# v11 - 成长任务自动接受 & 领取流程优化
# v12 - 新增 CloudTelemetry 云端遥测，纯青龙面板也可完成大部分任务
#       体验设计创意模式 / 探索灵感 / 召唤专家 / 技能 / 模板 / 自动化
# v13 - CloudTelemetry 稳定性改进，expert/telemetry 事件映射修正
# v14 - 新增 Billing Checkin（计费签到），每日签到更可靠
# v15 - template_5 批量遥测修复（4事件合并一次 POST），使用5个模板任务可完成
#       black_cat 夜猫子时间窗口修正（23:00-08:00）
#       Cloud Chat fallback（无 ACP 时尝试云端遥测）
# v16 - 新增品赞代理支持（PROXY_API / PROXY_TYPE）
#       代理一次获取、全流程复用，失效自动回退直连
#       所有 HTTP 请求（Growth API / 遥测 / Keycloak）均走代理
# v17 - 修复任务接受 API：{"task_code":"xxx"} -> {"task_codes":["xxx"]}
#       修复任务领取 API：/tasks/claim -> /tasks/{code}/claim
#       解决全部 accept 返回 400 invalid request 的问题
# v18 - 修复青龙面板 user_id 缺失导致遥测无效、任务无法推进的问题
#       自动从 Bearer Token (JWT) 中解码 sub 字段作为 user_id
#       无需 desktop info 文件也能正确触发遥测事件
# v19 - 所有 chat 任务（chat_5/Model_chat_GLM5.2/black_cat）ACP 不可用时统一走云端回退
#       之前只有 black_cat 有 cloud fallback，chat_5 和 Model_chat_GLM5.2 直接跳过
#       chat_5 使用独立 conversationId，更接近真实对话行为
# v20 - 动态任务分类系统：基于 API 返回的 jump_url/icon_url 自动识别任务类型
#       新增 RichMeow_Chat（桌面端对话1次）任务支持
#       不再依赖硬编码 task_code 列表，新任务自动归类并尝试执行
#       当 WorkBuddy 更新任务时，脚本自动适应，无需手动更新代码
# v21 - WebChat Completions API：使用 /console/chat/completions 发起真实 AI 对话
#       替代云遥测 fallback（TaskCreated 事件无法推动聊天任务进度）
#       纯青龙面板也能完成 chat_5 / Model_chat_GLM5.2 / black_cat / 桌面端对话 等聊天任务
#       black_cat 任务仍需 23:00-08:00 之间运行
#       RichMeow_Chat / desktop_chat 也可通过 WebChat API 完成
#       保留 telemetry 作为补充手段（WebChat 失败时尝试）
# v22 - 关键修复：使用正确的遥测事件格式 chat_request_send / chat_request_response
#       前端 JS 逆向发现：Growth 系统只认 chat_request_* 事件，不认 agent_task_created
#       新流程：创建对话(/console/webchat/conversations) -> 发消息 -> 发正确遥测
#       逐轮进度检测 + 部分完成自动补发
# v23 - 修复聊天任务纯遥测无法推动进度的问题：
#       ACP 不可用时直接走 WebChat API（创建真实对话 + 正确遥测）
#       不再回退到纯遥测（cloud telemetry），因为纯遥测无法推动聊天任务进度
#       修复 in_progress 状态未被识别的问题，现在所有已接受状态均会触发任务执行
#       动态任务识别增强：利用 tag=PC 自动识别桌面任务
#       未知桌面任务按 jump_url 自动分发通用遥测
# v24 - 全部日志中文化 + emoji 图标，青龙面板可读性大幅提升
#       [Proxy]→[🌐代理] [Auth]→[🔐认证] [Growth]→[🌱成长] [Billing]→[✅签到]
#       [Desktop]→[💻桌面] [Telemetry]→[📡遥测] [ACP-Chat]→[💬对话]
#       [WebChat]→[💬聊天] [Keycloak]→[🔑SSO] [Cloud-Chat]→[☁️云端]
#       分节标题改为 ━━━ 成长中心 ━━━ / ━━━ 成长任务 ━━━ 等中文分栏
#       所有状态、进度、错误信息均为中文描述
# v25 - 新增「派猫猫旅行」功能（Buddy 旅行 / 活体猫猫状态机）：
#       自动调用 travel/config + travel/status 获取当前旅行状态，
#       空闲时自动派发 travel/depart (location_id) 出发旅行，每次 cron 重跑自动推进状态机 idle->traveling->arrived
#       抵达后按一键 travel/claim 自动领取礼物（state 不在 arrived 不重复领取）
#       新增「一键领取」：连续签到奖励、抽奖、接受成长任务等点击领取全部统一为一次点击领取
#       修复：旅行方式变动导致任务准过度，打通通知后回退到正确路径，防止重复派发/重复领取
#       修复：旅行温度回差丢失、时间窗口判断连夜，现在按状态机推进不会报错
# ============================================================

import os, sys, json, time, random, uuid, hashlib, glob, re, traceback
from datetime import datetime, date

try:
    import requests
except ImportError:
    print("Missing requests lib: pip3 install requests")
    sys.exit(1)

# Suppress SSL warnings
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    pass

def send_notify(title, content):
    try:
        from notify import send
        send(title, content)
    except ImportError:
        try:
            print(f"[📣通知] {title}: {content}")
        except UnicodeEncodeError:
            sys.stdout.buffer.write((f"[📣通知] {title}: {content}\n").encode("utf-8", errors="replace"))

class Logger:
    def __init__(self):
        self.msgs = []
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        try:
            print(line)
        except UnicodeEncodeError:
            sys.stdout.buffer.write((line + "\n").encode("utf-8", errors="replace"))
        self.msgs.append(line)
    def result(self):
        return "\n".join(self.msgs)

logger = Logger()

def gen_trace_id():
    return str(uuid.uuid4()).replace("-", "")[:24]

def gen_client_token(prefix="u"):
    return f"{prefix}-{uuid.uuid4()}"

def clean_proxy_env():
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(key, None)

PROXY_API = os.environ.get("PROXY_API", "").strip()
PROXY_TYPE = os.environ.get("PROXY_TYPE", "http").lower()
PROXY_RETRY_TIMES = 3
_current_proxies = None  # module-level cache for proxy dict
_proxy_fetched = False   # only fetch once per run

def parse_proxy_response(text):
    """Parse Pinzan proxy API response into {host, port, username, password}."""
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
                    "host": str(host), "port": int(port),
                    "username": proxy_obj.get("user") or proxy_obj.get("username") or "",
                    "password": proxy_obj.get("pass") or proxy_obj.get("password") or "",
                }
    except Exception:
        pass
    if ":" in text:
        parts = text.split(":")
        if len(parts) >= 2:
            return {
                "host": parts[0], "port": int(parts[1]),
                "username": parts[2] if len(parts) > 2 else "",
                "password": parts[3] if len(parts) > 3 else "",
            }
    return None

def build_proxy_dict(proxy_info):
    """Build requests-style proxies dict from parsed proxy info."""
    if not proxy_info:
        return None
    from urllib.parse import quote
    host = proxy_info["host"]
    port = proxy_info["port"]
    username = proxy_info.get("username", "")
    password = proxy_info.get("password", "")
    auth = ""
    if username and password:
        auth = f"{quote(username)}:{quote(password)}@"
    scheme = "socks5" if PROXY_TYPE == "socks5" else "http"
    proxy_url = f"{scheme}://{auth}{host}:{port}"
    logger.log("  [🌐代理] 使用 " + scheme.upper() + " 代理 " + host + ":" + str(port))
    return {"http": proxy_url, "https": proxy_url}

def fetch_proxy():
    """Fetch a proxy from Pinzan API. Returns proxies dict or None.
    Only fetches once per run; caches result (even None) to avoid repeated fetches."""
    global _current_proxies, _proxy_fetched
    if _proxy_fetched:
        return _current_proxies
    _proxy_fetched = True
    if not PROXY_API:
        return None
    logger.log("  [🌐代理] 正在从品赞 API 获取代理...")
    for attempt in range(1, PROXY_RETRY_TIMES + 1):
        try:
            s = requests.Session()
            s.trust_env = False
            r = s.get(PROXY_API, timeout=15)
            proxy_info = parse_proxy_response(r.text)
            if not proxy_info:
                logger.log("  [🌐代理] 第 " + str(attempt) + " 次尝试: 解析失败")
                continue
            proxies = build_proxy_dict(proxy_info)
            # Skip httpbin validation - actual requests will verify the proxy works
            logger.log("  [🌐代理] 获取代理成功，请求将走代理 (失败自动回退直连)")
            _current_proxies = proxies
            return proxies
        except Exception as e:
            logger.log("  [🌐代理] 第 " + str(attempt) + " 次尝试: 获取失败 - " + str(e)[:60])
        if attempt < PROXY_RETRY_TIMES:
            time.sleep(2)
    logger.log("  [🌐代理] 所有获取尝试失败，使用直连")
    return None

def get_proxies():
    """Get current proxy dict. Fetches once per run, then returns cache."""
    global _current_proxies, _proxy_fetched
    if _proxy_fetched:
        return _current_proxies
    return fetch_proxy()

# ==== SSE Parser ====
def parse_sse_lines(response):
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        line = line.strip()
        if line.startswith("data:"):
            line = line[5:].strip()
        if not line or line == "[✅完成]":
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass

# ==== ACP Chat Client ====
class ACPChatClient:
    def __init__(self, base_url=None, logger=None):
        self.base_url = base_url
        self.logger = logger or globals().get("logger")
        self.headers = {}
        self.connected = False
        self._user_id = ""

    def _log(self, msg):
        if self.logger:
            self.logger.log(msg)

    @staticmethod
    def discover_daemon():
       home = os.path.expanduser("~")
       sessions_dir = os.path.join(home, ".workbuddy", "sessions")
       if not os.path.isdir(sessions_dir):
           return None
       best_url = None
       best_time = 0
       for f in glob.glob(os.path.join(sessions_dir, "*.json")):
           try:
               with open(f, "r", encoding="utf-8") as fh:
                   data = json.load(fh)
               url = data.get("url") or data.get("endpoint", "")
               updated = data.get("updatedAt", data.get("lastHeartbeat", 0))
               if url and updated > best_time:
                   best_url = url
                   best_time = updated
           except Exception:
               continue
       return best_url

    @staticmethod
    def _probe_port(url, timeout=3):
        """Check if daemon is actually listening on the port."""
        try:
            import socket
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 80
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def connect(self):
        if not self.base_url:
            self.base_url = self.discover_daemon()
            if not self.base_url:
                self._log("  [🔌ACP] WorkBuddy daemon not found")
                return False
            # Probe if daemon is actually running
            if not self._probe_port(self.base_url):
                self._log("  [🔌ACP] Daemon port not responding: " + self.base_url)
                return False
        self._log("  [🔌ACP] Connecting to daemon: " + self.base_url)
        conn_id = str(uuid.uuid4())
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "acp-connection-id": conn_id,
        }
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp/connect", headers=headers, timeout=8, stream=True)
            if r.status_code != 200:
                self._log("  [🔌ACP] Connect failed: HTTP " + str(r.status_code))
                return False
            for data in parse_sse_lines(r):
                real_conn_id = data.get("connectionId", "")
                session_token = data.get("sessionToken", "")
                if real_conn_id and session_token:
                    headers["acp-connection-id"] = real_conn_id
                    headers["acp-session-token"] = session_token
                    break
            r.close()
            self.headers = headers

            # Initialize
            r2 = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "initialize", "params": {
                    "protocolVersion": 1, "capabilities": {},
                    "clientInfo": {"name": "workbuddy-checkin", "version": "13.0"},
                }, "id": 1,
            }, timeout=8, stream=True)
            r2.close()
            self.connected = True
            self._log("  [🔌ACP] Connected!")
            return True
        except Exception as e:
            self._log("  [🔌ACP] Connect error: " + str(e)[:100])
            return False

    def create_session(self, cwd=None):
        if not self.connected:
            return None
        if not cwd:
            cwd = os.path.expanduser("~")
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "session/new", "params": {
                    "cwd": cwd, "mcpServers": [],
                }, "id": 10,
            }, timeout=30, stream=True)
            session_id = None
            for data in parse_sse_lines(r):
                if "result" in data:
                    session_id = data["result"].get("sessionId")
                elif "error" in data:
                    self._log("  [🔌ACP] session/new error: " + json.dumps(data["error"], ensure_ascii=False)[:200])
            r.close()
            return session_id
        except Exception as e:
            self._log("  [🔌ACP] Create session error: " + str(e)[:100])
            return None

    def create_session_with_welcome_mode(self, welcome_mode, cwd=None):
        if not self.connected:
            return None
        if not cwd:
            cwd = os.path.expanduser("~")
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "session/new", "params": {
                    "cwd": cwd, "mcpServers": [],
                    "options": {"_meta": {"codebuddy.ai": {"welcomeMode": welcome_mode}}},
                }, "id": 10,
            }, timeout=30, stream=True)
            session_id = None
            for data in parse_sse_lines(r):
                if "result" in data:
                    session_id = data["result"].get("sessionId")
                elif "error" in data:
                    self._log("  [🔌ACP] session/new error: " + json.dumps(data["error"], ensure_ascii=False)[:200])
            r.close()
            return session_id
        except Exception as e:
            self._log("  [🔌ACP] Create session error: " + str(e)[:100])
            return None

    def _send_prompt_request(self, params, timeout=120):
        return self._send_prompt_request_ex(params, timeout=timeout, fire_and_forget=False)

    def _send_prompt_request_fire_and_forget(self, params, timeout=10):
        """Send prompt and return as soon as first session/update is received.
        Growth events in _meta are processed server-side immediately."""
        return self._send_prompt_request_ex(params, timeout=timeout, fire_and_forget=True)

    def _send_prompt_request_ex(self, params, timeout=120, fire_and_forget=False):
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "session/prompt",
                "params": {k: v for k, v in params.items() if v is not None},
                "id": 20,
            }, timeout=timeout, stream=True)
            stop_reason = None
            chunk_text = ""
            for data in parse_sse_lines(r):
                method = data.get("method", "")
                if method == "session/update":
                    events = data.get("params", {}).get("events", [])
                    for ev in events:
                        ev_type = ev.get("type", "")
                        if ev_type == "agent_message_chunk":
                            chunk = ev.get("data", {}).get("chunk", "")
                            chunk_text += chunk
                        elif ev_type == "session_end":
                            stop_reason = ev.get("data", {}).get("stopReason", "?")
                        # Fire-and-forget: return as soon as server acknowledges
                        if fire_and_forget and ev_type in ("agent_message_chunk", "session_end"):
                            r.close()
                            return "end_turn", ""
                elif "result" in data:
                    stop_reason = data["result"].get("stopReason", "?")
                    if fire_and_forget:
                        r.close()
                        return "end_turn", ""
                elif "error" in data:
                    err_msg = json.dumps(data["error"], ensure_ascii=False)[:200]
                    return None, err_msg
            r.close()
            return stop_reason, chunk_text
        except requests.exceptions.Timeout:
            return None, "timeout"
        except Exception as e:
            return None, str(e)

    def send_prompt(self, session_id, text, meta=None, model_id=None, timeout=120):
        params = {
            "sessionId": session_id,
            "prompt": [{"type": "text", "text": text}],
        }
        if model_id:
            params["modelId"] = model_id
        if meta:
            params["_meta"] = meta
        return self._send_prompt_request(params, timeout)

    def send_prompt_fire_and_forget(self, session_id, text, meta=None, model_id=None, timeout=10):
        """Send prompt without waiting for full response. Growth events processed immediately."""
        params = {
            "sessionId": session_id,
            "prompt": [{"type": "text", "text": text}],
        }
        if model_id:
            params["modelId"] = model_id
        if meta:
            params["_meta"] = meta
        return self._send_prompt_request_fire_and_forget(params, timeout)

    def send_prompt_with_blocks(self, session_id, prompt_blocks, meta=None, timeout=120):
        params = {
            "sessionId": session_id,
            "prompt": prompt_blocks,
        }
        if meta:
            params["_meta"] = meta
        return self._send_prompt_request(params, timeout)

    def send_prompt_with_blocks_fire_and_forget(self, session_id, prompt_blocks, meta=None, timeout=10):
        """Send prompt blocks without waiting for full response."""
        params = {
            "sessionId": session_id,
            "prompt": prompt_blocks,
        }
        if meta:
            params["_meta"] = meta
        return self._send_prompt_request_fire_and_forget(params, timeout)

    def set_mode(self, session_id, mode_id):
        if not self.connected:
            return False
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "session/set_mode", "params": {
                    "sessionId": session_id, "modeId": mode_id,
                }, "id": 30,
            }, timeout=10, stream=True)
            r.close()
            return True
        except:
            return False

    def set_model(self, session_id, model_id):
        if not self.connected:
            return False
        try:
            r = requests.post(f"{self.base_url}/api/v1/acp", headers=self.headers, json={
                "jsonrpc": "2.0", "method": "session/set_model", "params": {
                    "sessionId": session_id, "modelId": model_id,
                }, "id": 31,
            }, timeout=10, stream=True)
            r.close()
            return True
        except:
            return False

# ==== Keycloak Session Refresher ====
class KeycloakRefresher:
    AUTH_URL_TEMPLATE = (
        "https://www.workbuddy.cn/auth/realms/copilot/protocol/openid-connect/auth"
        "?response_type=code&scope=openid%20offline_access&client_id=console"
        "&redirect_uri=https%3A%2F%2Fwww.workbuddy.cn%2Fconsole%2Faccounts%2F.apisix%2Fredirect"
        "&state={state}"
    )
    TOKEN_URL = "https://www.workbuddy.cn/auth/realms/copilot/protocol/openid-connect/token"

    @staticmethod
    def parse_keycloak_cookies(cookie_str):
        kc_names = {"AUTH_SESSION_ID", "KC_RESTART", "KEYCLOAK_IDENTITY", "KEYCLOAK_SESSION"}
        cookies = {}
        for part in cookie_str.split(";"):
            part = part.strip()
            if "=" in part:
                name, _, value = part.partition("=")
                if name.strip() in kc_names:
                    cookies[name.strip()] = value.strip()
        return cookies

    @staticmethod
    def refresh_session(keycloak_cookie_str):
        """Refresh Keycloak SSO session and extract Bearer access_token.
        Returns (requests.Session, access_token) or (None, None)."""
        kc_cookies = KeycloakRefresher.parse_keycloak_cookies(keycloak_cookie_str)
        if not kc_cookies:
            logger.log("  [🔑SSO] 未找到有效的 Keycloak Cookie")
            return None, None
        missing = {"KEYCLOAK_IDENTITY", "AUTH_SESSION_ID"} - set(kc_cookies.keys())
        if missing:
            logger.log("  [🔑SSO] 缺少必要 Cookie: " + "、".join(missing))
            return None, None
        logger.log("  [🔑SSO] 发现 " + str(len(kc_cookies)) + " 个 SSO Cookie, 刷新 Session 中...")
        sess = requests.Session()
        sess.trust_env = False
        kc_proxies = get_proxies()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        for name, value in kc_cookies.items():
            value = value.strip('"')
            sess.cookies.set(name, value, domain="www.workbuddy.cn", path="/auth/realms/copilot/")
        sess.cookies.set("i18next", "zh-CN", domain="www.workbuddy.cn", path="/")

        access_token = None

        # Step 1: Try to extract authorization code from OIDC redirect
        state = hashlib.md5((str(time.time()) + str(random.random())).encode()).hexdigest()[:32]
        auth_url = KeycloakRefresher.AUTH_URL_TEMPLATE.format(state=state)
        try:
            # Don't follow all redirects - capture the redirect with code param
            r = sess.get(auth_url, allow_redirects=False, timeout=30, proxies=kc_proxies)
            # Follow redirects manually to find the one with ?code=
            for _ in range(10):
                if r.status_code not in (301, 302, 303, 307, 308):
                    break
                location = r.headers.get("Location", "")
                if "code=" in location:
                    # Extract authorization code
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(location)
                    qs = parse_qs(parsed.query)
                    auth_code = qs.get("code", [None])[0]
                    if auth_code:
                        logger.log("  [🔑SSO] 获取授权码，换取 Token...")
                        # Exchange code for access_token
                        token_data_req = {
                            "grant_type": "authorization_code",
                            "client_id": "console",
                            "code": auth_code,
                            "redirect_uri": "https://www.workbuddy.cn/console/accounts/.apisix/redirect",
                        }
                        try:
                            token_r = requests.post(KeycloakRefresher.TOKEN_URL, data=token_data_req, timeout=15, verify=False, proxies=kc_proxies)
                        except Exception:
                            token_r = requests.post(KeycloakRefresher.TOKEN_URL, data=token_data_req, timeout=15, verify=False)
                        if token_r.status_code == 200:
                            token_data = token_r.json()
                            access_token = token_data.get("access_token", "")
                            if access_token:
                                logger.log("  [🔑SSO] 获取 Bearer Token 成功!")
                                # Also try to get refresh_token for future use
                                refresh_tok = token_data.get("refresh_token", "")
                                break
                        logger.log("  [🔑SSO] Token 交换失败: " + str(token_r.status_code))
                    break
                # Follow redirect
                if location.startswith("/"):
                    from urllib.parse import urljoin
                    location = urljoin(str(r.url), location)
                r = sess.get(location, allow_redirects=False, timeout=30, proxies=kc_proxies)

            # Step 2: Also do full redirect to get session cookies
            r2 = sess.get(auth_url, allow_redirects=True, timeout=30, proxies=kc_proxies)
            session_cookies = {
                c.name for c in sess.cookies
                if c.name in ("session", "session_2") and c.domain == "www.workbuddy.cn"
            }
            if "session" in session_cookies and "session_2" in session_cookies:
                logger.log("  [🔑SSO] Session Cookie 已获取 (session + session_2)")
            elif "session" in session_cookies:
                logger.log("  [🔑SSO] Session Cookie 不完整，重试中...")
                state2 = hashlib.md5((str(time.time()) + str(random.random())).encode()).hexdigest()[:32]
                auth_url2 = KeycloakRefresher.AUTH_URL_TEMPLATE.format(state=state2)
                sess.get(auth_url2, allow_redirects=True, timeout=30, proxies=kc_proxies)

            if access_token or ("session" in session_cookies):
                return sess, access_token

            logger.log("  [🔑SSO] Session 刷新失败 - Cookie 可能已过期")
            return None, None
        except Exception as e:
            logger.log("  [🔑SSO] 刷新错误: " + str(e)[:100])
            return None, None

    @staticmethod
    def try_token_refresh(refresh_token):
        try:
            refresh_data = {
                "client_id": "console",
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
            proxies = get_proxies()
            try:
                r = requests.post(KeycloakRefresher.TOKEN_URL, data=refresh_data, timeout=15, verify=False, proxies=proxies)
            except Exception:
                r = requests.post(KeycloakRefresher.TOKEN_URL, data=refresh_data, timeout=15, verify=False)
            if r.status_code == 200:
                data = r.json()
                return data.get("access_token", ""), data.get("refresh_token", "")
        except:
            pass
        return None, None

# ==== Desktop Info ====
def discover_desktop_info():
    paths = []
    env_path = os.environ.get("WORKBUDDY_DESKTOP_INFO", "").strip()
    if env_path and os.path.isfile(env_path):
        paths.append(env_path)
    home = os.path.expanduser("~")
    search_dirs = [
        os.path.join(home, "Downloads"),
        os.path.join(home, "AppData", "Local", "CodeBuddyExtension", "Data", "Public", "auth"),
    ]
    for d in search_dirs:
        if os.path.isdir(d):
            for f in glob.glob(os.path.join(d, "workbuddy-desktop-*.info")):
                paths.append(f)
            # Also match plain workbuddy-desktop.info (no suffix)
            plain = os.path.join(d, "workbuddy-desktop.info")
            if os.path.isfile(plain) and plain not in paths:
                paths.append(plain)
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            auth = data.get("auth", {})
            access_token = auth.get("accessToken", "")
            refresh_token = auth.get("refreshToken", "")
            expires_at = auth.get("expiresAt", 0)
            uid = data.get("account", {}).get("uid", "")
            if access_token:
                logger.log("  [💻桌面] 发现配置: " + os.path.basename(path))
                now_ms = int(time.time() * 1000)
                if expires_at and expires_at > now_ms:
                    logger.log("  [💻桌面] accessToken 仍有效")
                    return access_token, refresh_token, uid
                else:
                    logger.log("  [💻桌面] accessToken 已过期，尝试 refreshToken...")
                    if refresh_token:
                        new_access, new_refresh = KeycloakRefresher.try_token_refresh(refresh_token)
                        if new_access:
                            logger.log("  [💻桌面] Token 刷新成功")
                            return new_access, new_refresh, uid
                    logger.log("  [💻桌面] 无法刷新 Token")
        except Exception as e:
            logger.log("  [💻桌面] 读取 " + os.path.basename(path) + " 失败: " + str(e))
    return None, None, ""

# ==== Growth Event Constants & Helpers ====
GROWTH_EVENT_TASK_CREATED = "TaskCreated"
GROWTH_EVENT_TASK_CREATED_WITH_TEMPLATE = "TaskCreatedWithTemplate"
GROWTH_EVENT_EXPERT_ACTUAL_USE = "ExpertActualUse"
GROWTH_EVENT_PLAYBOOK_PROMPT_SEND = "PlaybookPromptSend"
GROWTH_EVENT_SKILL_ACTION = "SkillAction"
GROWTH_EVENT_SKILL_REQUEST_SEND = "SkillRequestSend"
GROWTH_EVENT_SKILL_INSTALLED = "SkillInstalled"

EXPERT_MARKETPLACE_URL = "https://acc-1258344699.cos.accelerate.myqcloud.com/workbuddy/expert-marketplace/expert_center.json"

_expert_cache = None

def fetch_expert_marketplace():
    global _expert_cache
    if _expert_cache is not None:
        return _expert_cache
    try:
        s = requests.Session()
        s.trust_env = False
        s.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        r = s.get(EXPERT_MARKETPLACE_URL, timeout=15, verify=False)
        if r.status_code == 200:
            _expert_cache = r.json()
            return _expert_cache
    except Exception as e:
        logger.log("  [🎯专家CDN] 获取失败: " + str(e)[:80])
    return None

def _extract_name(val):
    if isinstance(val, dict):
        return val.get("zh", val.get("en", str(val)))
    return str(val)

def get_team_experts(count=5):
    data = fetch_expert_marketplace()
    if not data:
        return []
    experts = data.get("experts", [])
    team = []
    for e in experts:
        meta = e.get("_meta", {})
        if meta.get("expertType") == "team" or e.get("expertType") == "team":
            name = _extract_name(e.get("displayName", e.get("name", {})))
            industry_id = meta.get("industryId", e.get("industryId", ""))
            profession = _extract_name(e.get("profession", ""))
            dip = _extract_name(e.get("defaultInitPrompt", ""))
            team.append({"id": e["id"], "name": name, "industryId": industry_id,
                         "profession": profession, "defaultInitPrompt": dip})
    return team[:count]

def get_normal_experts(count=10):
    data = fetch_expert_marketplace()
    if not data:
        return []
    experts = data.get("experts", [])
    normal = []
    for e in experts:
        meta = e.get("_meta", {})
        et = meta.get("expertType", e.get("expertType", ""))
        if et == "agent":
            name = _extract_name(e.get("displayName", e.get("name", {})))
            industry_id = meta.get("industryId", e.get("industryId", ""))
            profession = _extract_name(e.get("profession", ""))
            dip = _extract_name(e.get("defaultInitPrompt", ""))
            normal.append({"id": e["id"], "name": name, "industryId": industry_id,
                           "profession": profession, "defaultInitPrompt": dip})
    return normal[:count]

def get_template_scenes(count=5):
    data = fetch_expert_marketplace()
    if not data:
        return [
            {"id": "01-ProductDesign", "name": "产品设计"},
            {"id": "02-Marketing", "name": "营销文案"},
            {"id": "03-DataAnalysis", "name": "数据分析"},
            {"id": "04-CodeReview", "name": "代码审查"},
            {"id": "05-Report", "name": "报告撰写"},
        ][:count]
    cats = data.get("categories", [])
    scenes = []
    for c in cats[:count]:
        name = _extract_name(c.get("name", {}))
        scenes.append({"id": c["id"], "name": name})
    return scenes[:count]

def build_growth_event(event_code, event_id, extra=None, expert_type=None):
    event = {"eventCode": event_code, "id": event_id}
    if extra:
        event["extra"] = extra
    if expert_type:
        event["expertType"] = expert_type
    return event

def build_meta_with_growth_events(growth_events, mode=None, model=None, expert_id=None,
                                   expert_meta=None, session_id=None, user_id=None,
                                   tags=None, is_automation=False):
    codebuddy_meta = {}
    # Append growth events
    for event in growth_events:
        existing_raw = codebuddy_meta.get("growthEvent", "[]")
        try:
            existing = json.loads(existing_raw) if isinstance(existing_raw, str) else existing_raw
            if not isinstance(existing, list):
                existing = [existing]
        except (json.JSONDecodeError, TypeError):
            existing = []
        existing.append(event)
        codebuddy_meta["growthEvent"] = json.dumps(existing, ensure_ascii=False)

    codebuddy_meta["promptRequestId"] = gen_trace_id()
    codebuddy_meta["clientSendTime"] = int(time.time() * 1000)
    if session_id:
        codebuddy_meta["conversationId"] = session_id
    if user_id:
        codebuddy_meta["userId"] = user_id
    if mode:
        codebuddy_meta["mode"] = mode
    if model:
        codebuddy_meta["model"] = model
    if expert_id:
        codebuddy_meta["expertId"] = expert_id
    if expert_meta:
        codebuddy_meta["expert"] = expert_meta
    if tags:
        codebuddy_meta["tags"] = tags
    if is_automation:
        codebuddy_meta["isAutomationBackground"] = True

    return {"codebuddy.ai": codebuddy_meta}

# ==== Aegis Telemetry Reporter ====
# ==== Cloud Telemetry Reporter ====
# Uses /v2/report endpoint (same auth as Growth API) instead of direct Aegis POST
# This is how the web frontend reports telemetry events that trigger growth progress

EVENT_NAME_MAPPING = {
    "ExpertActualUse": "expert_actual_use",
    "ExpertSummoned": "expert_summoned",
    "TaskCreated": "agent_task_created",
    "TaskCreatedWithTemplate": "agent_task_created_with_template",
    "PlaybookPromptSend": "playbook_prompt_send",
    "TemplateUsed": "template_used",
    "SkillAction": "skill_action",
    "SkillInstalled": "skill_installed",
    "SkillRequestSend": "skill_request_send",
    "AutomatedTaskCreateSuc": "automated_task_create_suc",
    "AutomatedTaskExecute": "automated_task_execute",
    "DesignCanvasOpen": "wbx_design_canvas_open",
    "DesignCanvasTaskCreate": "wbx_design_canvas_task_create",
}

class CloudTelemetryReporter:
    """Reports telemetry via /v2/report endpoint (cloud-mode, same as web frontend)."""

    def __init__(self, http_session=None, user_id="", logger=None):
        self.sess = http_session
        self.user_id = user_id
        self.logger = logger or globals().get("logger")

    def set_user_id(self, uid):
        self.user_id = uid

    def set_session(self, http_session):
        self.sess = http_session

    def _report(self, event_code, payload):
        if not self.sess:
            return False
        mapped = EVENT_NAME_MAPPING.get(event_code, event_code)
        # For agent_task_created, map fields like the frontend does:
        # mode -> source, agent_mode -> mode, task_mode -> name, model -> requestModelId, template_id -> action
        if mapped == "agent_task_created" and isinstance(payload, dict):
            mode_val = payload.pop("mode", None)
            task_mode = payload.pop("task_mode", None)
            agent_mode = payload.pop("agent_mode", None)
            model_val = payload.pop("model", None)
            template_id = payload.pop("template_id", None)
            if mode_val is not None:
                payload["source"] = mode_val
            if task_mode is not None:
                payload["name"] = task_mode
            if agent_mode is not None:
                payload["mode"] = agent_mode
            if model_val is not None:
                payload["requestModelId"] = model_val
            if template_id is not None:
                payload["action"] = template_id
        event = {
            "eventCode": mapped,
            "timestamp": int(time.time() * 1000),
            "reportDelay": 0,
            "userId": self.user_id,
            "ideName": "web-Agents",
            "ideType": "web-Agents",
            "machineId": str(uuid.uuid4()),
            "mode": "CLOUD",
            **payload,
        }
        try:
            proxies = get_proxies()
            try:
                r = self.sess.post("https://www.workbuddy.cn/v2/report", json=[event], timeout=10, verify=False, proxies=proxies)
            except Exception:
                r = self.sess.post("https://www.workbuddy.cn/v2/report", json=[event], timeout=10, verify=False)
            ok = r.status_code == 200
            if ok:
                try:
                    data = r.json()
                    ok = data.get("code") == 0
                except:
                    pass
            if not ok and self.logger:
                self.logger.log("  [📡遥测] /v2/report 失败: " + str(r.status_code) + " " + r.text[:100])
            return ok
        except Exception as e:
            self.logger.log("  [📡遥测] /v2/report 错误: " + str(e)[:80])
            return False

    def report_batch(self, events_raw):
        """Send a batch of pre-built telemetry events in a single POST (works for template_5)."""
        if not self.sess:
            return False
        events = []
        for event_code, payload in events_raw:
            mapped = EVENT_NAME_MAPPING.get(event_code, event_code)
            event = {
                "eventCode": mapped,
                "timestamp": int(time.time() * 1000),
                "reportDelay": 0,
                "userId": self.user_id,
                "ideName": "web-Agents",
                "ideType": "web-Agents",
                "machineId": str(uuid.uuid4()),
                "mode": "CLOUD",
                **payload,
            }
            # Apply agent_task_created field mapping
            if mapped == "agent_task_created" and isinstance(payload, dict):
                mode_val = payload.pop("source", None)
                task_mode = payload.pop("name", None)
                agent_mode = payload.pop("mode", None)
                model_val = payload.pop("requestModelId", None)
                template_id = payload.pop("action", None)
                if mode_val is not None:
                    event["source"] = mode_val
                if task_mode is not None:
                    event["name"] = task_mode
                if agent_mode is not None:
                    event["mode"] = agent_mode
                if model_val is not None:
                    event["requestModelId"] = model_val
                if template_id is not None:
                    event["action"] = template_id
            events.append(event)
        try:
            proxies = get_proxies()
            try:
                r = self.sess.post("https://www.workbuddy.cn/v2/report", json=events, timeout=10, verify=False, proxies=proxies)
            except Exception:
                r = self.sess.post("https://www.workbuddy.cn/v2/report", json=events, timeout=10, verify=False)
            ok = r.status_code == 200
            if ok:
                try:
                    data = r.json()
                    ok = data.get("code") == 0
                except:
                    pass
            if not ok and self.logger:
                self.logger.log("  [📡遥测] /v2/report 批量失败: " + str(r.status_code))
            return ok
        except Exception as e:
            if self.logger:
                self.logger.log("  [📡遥测] /v2/report 批量错误: " + str(e)[:80])
            return False

    def report_expert_actual_use(self, expert_id, expert_name, expert_title="",
                                  industry_id="", conversation_id="", expert_type=""):
        return self._report("ExpertActualUse", {
            "id": expert_id,
            "name": expert_name,
            "type": expert_type or "agent",
            "expertTitle": expert_title,
            "expertType": expert_type or "agent",
            "conversationId": conversation_id,
            "cost": 100,
            "characterCount": 30,
            "requestModelId": "default",
            "requestModelName": "",
        })

    def report_playbook_prompt_send(self, template_id, template_name, category_id="", conversation_id=""):
        return self._report("PlaybookPromptSend", {
            "ext1": gen_trace_id(),
            "requestId": str(uuid.uuid4()),
            "id": template_id,
            "name": template_name,
            "categoryId": category_id,
            "type": "other",
            "promptLength": 30,
            "isOfficial": 1,
            "skills": "",
            "skillNames": "",
            "source": "growth-center",
            "conversationId": conversation_id,
        })

    def report_template_used(self, template_id):
        return self._report("TemplateUsed", {"templateId": template_id, "templateName": ""})

    def report_task_created_with_template(self, template_id, template_name):
        return self._report("TaskCreatedWithTemplate", {
            "templateId": template_id,
            "templateName": template_name,
            "isCustomModel": True,
            "id": template_id,
            "name": template_name,
        })

    def report_skill_action(self, skill_name, action="enable", outcome="success"):
        return self._report("SkillAction", {
            "skillName": skill_name,
            "name": skill_name,
            "skillId": skill_name,
            "skillVersion": "1.0.0",
            "action": action,
            "source": "installed",
            "durationMs": 500,
            "outcome": outcome,
        })

    def report_skill_installed(self, skill_name, is_official=True):
        return self._report("SkillInstalled", {
            "skillName": skill_name,
            "name": skill_name,
            "skillId": skill_name,
            "skillVersion": "1.0.0",
            "source": "marketplace",
            "isOfficial": is_official,
            "skillType": "official" if is_official else "custom",
        })

    def report_skill_request_send(self, skill_name):
        return self._report("SkillRequestSend", {
            "ext1": gen_trace_id(),
            "requestId": str(uuid.uuid4()),
            "skillName": skill_name,
            "skills": skill_name,
            "skillNames": skill_name,
            "isOfficial": 1,
        })

    def report_task_created(self, task_mode="", agent_mode="craft", model="default",
                             template_id="", has_expert=False, expert_id="",
                             has_skill=False, skill_names=None, is_automation=False):
        payload = {
            "mode": "CLOUD",
            "task_mode": task_mode,
            "agent_mode": agent_mode,
            "model": model,
            "template_id": template_id,
            "has_expert": has_expert,
            "expert_id": expert_id,
            "has_skill": has_skill,
            "skill_names": skill_names or [],
            "has_repo": False,
            "has_template": bool(template_id),
            "has_mention": False,
        }
        if is_automation:
            payload["isAutomationBackground"] = True
        return self._report("TaskCreated", payload)

    def report_design_canvas(self, action="open"):
        # The task create event is what triggers growth progress for create_canvas
        return self._report("DesignCanvasTaskCreate", {})

    def report_automated_task_create(self):
        return self._report("AutomatedTaskCreateSuc", {"action": "create"})

    def report_automated_task_execute(self):
        return self._report("AutomatedTaskExecute", {"action": "execute"})

# ==== Task Classification ====
CHAT_TASK_CODES = {"chat_5", "Model_chat_GLM5.2", "black_cat", "RichMeow_Chat", "desktop_chat"}
DESKTOP_TASK_CODES = {"create_canvas", "playbook_prompt", "Expert_team_use_3", "expert_5", "skill_1", "template_5", "automation_1"}

# Dynamic task classification rules based on API task fields
CHAT_JUMP_PATTERNS = ["workbuddy://chat"]
EXPERT_JUMP_PATTERNS = ["workbuddy://expert", "workbuddy://experts"]
TEMPLATE_JUMP_PATTERNS = ["workbuddy://playbook", "workbuddy://templates"]
SKILL_JUMP_PATTERNS = ["workbuddy://skills"]
AUTOMATION_JUMP_PATTERNS = ["workbuddy://automation"]
CHAT_ICON_SUFFIXES = ["chat.png", "team_task.png"]


def classify_task_code(task_code, task_data=None):
    """Classify a task code into chat, desktop, or auto based on known codes or API metadata.
    
    This enables the script to automatically handle NEW tasks that weren't
    hardcoded, by examining jump_url, icon_url, and task_type from the API.
    """
    if task_code in CHAT_TASK_CODES:
        return "chat"
    if task_code in DESKTOP_TASK_CODES:
        return "desktop"
    if task_code in ("first_buddy",):
        return "auto"
    
    if task_data and isinstance(task_data, dict):
        jump_url = task_data.get("jump_url", "")
        icon_url = task_data.get("icon_url", "")
        task_type = task_data.get("task_type", "")
        
        if task_type == "auto":
            return "auto"
        
        # tag="PC" means desktop-only task (cannot be done without WorkBuddy Desktop)
        tag = task_data.get("tag", "")
        if tag in ("PC",):
            return "desktop"
        
        # Chat tasks: jump_url contains chat with team_task/chat icon
        for pat in CHAT_JUMP_PATTERNS:
            if pat in jump_url:
                for ep in EXPERT_JUMP_PATTERNS + TEMPLATE_JUMP_PATTERNS:
                    if ep in jump_url:
                        return "desktop"
                for sfx in CHAT_ICON_SUFFIXES:
                    if icon_url.endswith(sfx):
                        return "chat"
                return "chat"
        
        for pat in EXPERT_JUMP_PATTERNS:
            if pat in jump_url:
                return "desktop"
        for pat in TEMPLATE_JUMP_PATTERNS:
            if pat in jump_url:
                return "desktop"
        for pat in SKILL_JUMP_PATTERNS:
            if pat in jump_url:
                return "desktop"
        for pat in AUTOMATION_JUMP_PATTERNS:
            if pat in jump_url:
                return "desktop"
    
    lower = task_code.lower()
    if "chat" in lower or "meow" in lower or "cat" in lower:
        return "chat"
    if any(k in lower for k in ("expert", "team", "template", "skill", "canvas", "playbook", "automation")):
        return "desktop"
    
    return "chat"

# ==== Main Checkin Class ====
class WorkBuddyCheckin:
    BASE = "https://www.workbuddy.cn"
    TASK_NOT_ACCEPTED = "not_accepted"
    TASK_ACCEPTED = "accepted"
    TASK_IN_PROGRESS = "in_progress"
    TASK_COMPLETED = "completed"
    TASK_CLAIMED = "claimed"

    def __init__(self, access_token="", cookie_str="", keycloak_cookie_str=""):
        clean_proxy_env()
        self.sess = requests.Session()
        self.sess.trust_env = False
        self._auth_ok = None
        self._use_bearer = bool(access_token)
        self._bearer_token = access_token
        self.acp = None
        self._user_id = ""
        self.telemetry = CloudTelemetryReporter()

        self.sess.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.workbuddy.cn",
            "Referer": "https://www.workbuddy.cn/profile/growth-center",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

        if access_token:
            self.sess.headers["Authorization"] = "Bearer " + access_token
            logger.log("  [🔐认证] 使用 Bearer Token 认证")
        elif keycloak_cookie_str:
            refreshed_sess, kc_token = KeycloakRefresher.refresh_session(keycloak_cookie_str)
            if refreshed_sess:
                for c in refreshed_sess.cookies:
                    self.sess.cookies.set(c.name, c.value, domain=c.domain, path=c.path)
                if kc_token:
                    self._bearer_token = kc_token
                    self.sess.headers["Authorization"] = "Bearer " + kc_token
                    self._use_bearer = True
                    logger.log("  [🔐认证] Keycloak SSO -> Bearer Token 成功")
                else:
                    logger.log("  [🔐认证] 通过 Keycloak SSO 获取 Session (仅 Cookie, Growth API 可能不可用)")
            else:
                logger.log("  [🔐认证] Keycloak SSO 刷新失败")
        elif cookie_str:
            self._set_cookies_from_string(cookie_str)
            logger.log("  [🔐认证] 使用原始 Cookie 认证")
            # Raw cookie alone returns 401 for Growth API; try OIDC to get Bearer token
            logger.log("  [🔐认证] 尝试通过 OIDC 流程提取 Bearer Token...")
            try:
                oidc_sess = requests.Session()
                oidc_sess.trust_env = False
                oidc_proxies = get_proxies()
                oidc_sess.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                })
                # Copy all cookies to the OIDC session
                for c in self.sess.cookies:
                    oidc_sess.cookies.set(c.name, c.value, domain=c.domain, path=c.path)
                oidc_sess.cookies.set("i18next", "zh-CN", domain="www.workbuddy.cn", path="/")
                # Try OIDC auth flow
                from urllib.parse import urlparse, parse_qs, urljoin
                state = hashlib.md5((str(time.time()) + str(random.random())).encode()).hexdigest()[:32]
                auth_url = KeycloakRefresher.AUTH_URL_TEMPLATE.format(state=state)
                r = oidc_sess.get(auth_url, allow_redirects=False, timeout=30, proxies=oidc_proxies)
                for _ in range(10):
                    if r.status_code not in (301, 302, 303, 307, 308):
                        break
                    location = r.headers.get("Location", "")
                    if "code=" in location:
                        parsed = urlparse(location)
                        qs = parse_qs(parsed.query)
                        auth_code = qs.get("code", [None])[0]
                        if auth_code:
                            logger.log("  [🔐认证] 获取授权码，换取 Token...")
                            oidc_token_data = {
                                "grant_type": "authorization_code",
                                "client_id": "console",
                                "code": auth_code,
                                "redirect_uri": "https://www.workbuddy.cn/console/accounts/.apisix/redirect",
                            }
                            try:
                                token_r = requests.post(KeycloakRefresher.TOKEN_URL, data=oidc_token_data, timeout=15, verify=False, proxies=oidc_proxies)
                            except Exception:
                                token_r = requests.post(KeycloakRefresher.TOKEN_URL, data=oidc_token_data, timeout=15, verify=False)
                            if token_r.status_code == 200:
                                token_data = token_r.json()
                                at = token_data.get("access_token", "")
                                if at:
                                    self._bearer_token = at
                                    self.sess.headers["Authorization"] = "Bearer " + at
                                    self._use_bearer = True
                                    logger.log("  [🔐认证] Cookie -> Bearer Token 提取成功!")
                                    break
                        break
                    if location.startswith("/"):
                        location = urljoin(str(r.url), location)
                    r = oidc_sess.get(location, allow_redirects=False, timeout=30, proxies=oidc_proxies)
                if not self._use_bearer:
                    logger.log("  [🔐认证] 无法从 Cookie 提取 Bearer Token")
            except Exception as e:
                logger.log("  [🔐认证] OIDC 提取错误: " + str(e)[:80])

        # Try desktop access token as fallback (if no bearer token yet)
        if not self._use_bearer:
            dt, _, uid = discover_desktop_info()
            if dt:
                self._bearer_token = dt
                self.sess.headers["Authorization"] = "Bearer " + dt
                self._use_bearer = True
                logger.log("  [🔐认证] 使用桌面端 accessToken")
            if uid:
                self._user_id = uid
                self.telemetry.set_user_id(uid)
        # Extract user_id from JWT if still missing
        if not self._user_id and self._bearer_token:
            try:
                import base64
                parts = self._bearer_token.split(".")
                if len(parts) >= 2:
                    payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
                    jwt_data = json.loads(base64.urlsafe_b64decode(payload))
                    uid = jwt_data.get("sub", "")
                    if uid:
                        self._user_id = uid
                        self.telemetry.set_user_id(uid)
                        logger.log("  [🔐认证] 从 JWT 提取用户ID: " + uid[:8] + "...")
            except Exception:
                pass
        self.telemetry.set_session(self.sess)

    def _set_cookies_from_string(self, cookie_str):
        for part in cookie_str.split(";"):
            part = part.strip()
            if "=" in part:
                name, _, value = part.partition("=")
                name = name.strip()
                value = value.strip()
                if name and value:
                    self.sess.cookies.set(name, value, domain=".workbuddy.cn", path="/")

    def _get(self, path):
        url = self.BASE + path
        try:
            proxies = get_proxies()
            try:
                r = self.sess.get(url, timeout=30, verify=False, proxies=proxies)
            except Exception:
                r = self.sess.get(url, timeout=30, verify=False)
            if r.status_code == 401:
                if self._auth_ok is not False:
                    logger.log("  [🌱成长] ❌认证已过期，请更新环境变量")
                self._auth_ok = False
                return None
            self._auth_ok = True
            try:
                return r.json()
            except Exception:
                return None
        except Exception as e:
            logger.log("  [🌱成长] GET " + path + " 失败: " + str(e)[:80])
            return None

    def _post(self, path, data=None):
        url = self.BASE + path
        try:
            proxies = get_proxies()
            try:
                r = self.sess.post(url, json=data or {}, timeout=60, verify=False, proxies=proxies)
            except Exception:
                r = self.sess.post(url, json=data or {}, timeout=60, verify=False)
            if r.status_code == 401:
                if self._auth_ok is not False:
                    logger.log("  [🌱成长] ❌认证已过期 (POST)")
                self._auth_ok = False
                return None
            self._auth_ok = True
            return r.json()
        except Exception as e:
            logger.log("  [🌱成长] POST " + path + " 失败: " + str(e)[:80])
            return None

    def init_acp(self):
        acp_url = os.environ.get("WORKBUDDY_ACP_BASE_URL", "").strip()
        acp = ACPChatClient(base_url=acp_url or None, logger=logger)
        if acp.connect():
            self.acp = acp
            return True
        logger.log("  [🔌ACP] 无法连接守护进程，桌面任务将被跳过")
        return False

    # ==== Growth API Methods ====
    def get_profile(self):
        resp = self._get("/v2/activity/growth/profile")
        if resp and resp.get("code") == 0:
            data = resp.get("data", {})
            level = data.get("level", "?")
            level_name = data.get("level_name", "?")
            completed = data.get("completed", "?")
            total = data.get("total", "?")
            logger.log("  [🌱成长] 等级: " + str(level) + " (" + str(level_name) + "), 进度: " + str(completed) + "/" + str(total))
            self._auth_ok = True
            return data
        if self._auth_ok is not False:
            logger.log("  [🌱成长] 获取个人信息失败")
        return None

    def get_streak(self):
        resp = self._get("/v2/activity/growth/streak")
        if resp and resp.get("code") == 0:
            data = resp.get("data", {}).get("streak", {})
            self._streak_data = data
            days = data.get("days", 0)
            signed_today = data.get("signed_today", False)
            next_tier = data.get("next_tier", "?")
            remaining = data.get("next_tier_remaining", 0)
            sign_str = "✅已签到" if signed_today else "❌未签到"
            logger.log("  [🌱成长] 连续签到: " + str(days) + "天, 今日: " + sign_str + ", 下一档: " + str(next_tier) + " (还差 " + str(remaining) + " 天)")
            return data
        return None

    def do_redeem_by_streak(self):
        """网页「兑换奖励」：按连登档位自动兑换，无需兑换码。
        门槛由连续签到天数决定（7d/14d/28d 三档分别对应连续 7/14/28 天）；
        已兑换(409)/天数不足(403)则跳过。兼容旧变量 WORKBUDDY_REDEEM_CODE。"""
        logger.log("━━━ 🎁网页兑换奖励 ━━━")
        streak = getattr(self, "_streak_data", None)
        # 连登档位阈值：档位名 -> 需要的连续签到天数
        tiers = [("7d", "入门", 7), ("14d", "进阶", 14), ("28d", "巅峰", 28)]
        days = int(streak.get("days", 0)) if streak else 0
        if streak:
            for tier, label, need in tiers:
                if days >= need:
                    logger.log("  [🌱成长] 连登" + label + "档可兑换 (已连登 " + str(days) + " 天)，发起: " + tier)
                    self.do_redeem(tier=tier)
                else:
                    logger.log("  [🌱成长] 连登" + label + "档暂不可兑换 (需 " + str(need) + " 天, 当前 " + str(days) + "): " + tier)
        else:
            logger.log("  [🌱成长] 未获取到连登信息，跳过自动兑换")
        # 兼容旧环境变量：若设置了兑换码（实为档位名），也尝试兑换一次
        legacy = os.environ.get("WORKBUDDY_REDEEM_CODE", "").strip()
        if legacy:
            logger.log("  [🌱成长] 兼容变量 WORKBUDDY_REDEEM_CODE 触发兑换: " + legacy)
            self.do_redeem(tier=legacy)

    def get_heatmap(self):
        resp = self._get("/v2/activity/growth/heatmap")
        if resp and resp.get("code") == 0:
            cells = resp.get("data", {}).get("cells", [])
            signed = sum(1 for c in cells if c.get("score", 0) > 0)
            logger.log("  [🌱成长] 热力图: 已签到 " + str(signed) + " 天")
            return cells
        return None

    def get_energy(self):
        resp = self._get("/v2/activity/growth/energy")
        if resp and resp.get("code") == 0:
            data = resp.get("data", {})
            balance = data.get("balance", 0)
            logger.log("  [🌱成长] ⚡能量: " + str(balance))
            return data
        return None

    def get_badges(self):
        resp = self._get("/v2/activity/growth/badges")
        if resp and resp.get("code") == 0:
            badges = resp.get("data", {}).get("badges", resp.get("data", {}).get("list", []))
            if badges:
                earned = [b.get("badge_name", b.get("name", "")) for b in badges
                          if isinstance(b, dict) and b.get("earned", False)]
                logger.log("  [🌱成长] 🏅已获徽章: " + str(len(earned)) + " 个")
            return badges
        return None

    def get_tasks(self):
        resp = self._get("/v2/activity/growth/tasks")
        if resp and resp.get("code") == 0:
            return resp.get("data", {}).get("tasks", [])
        return []

    def accept_tasks(self, task_codes):
        """Accept tasks in bulk. API expects {"task_codes": ["code1", "code2", ...]}."""
        resp = self._post("/v2/activity/growth/tasks/accept", {"task_codes": task_codes})
        if resp and resp.get("code") == 0:
            results = resp.get("data", {}).get("results", [])
            for r in results:
                tc = r.get("task_code", "?")
                st = r.get("status", "")
                msg = r.get("message", "")
                if st == "success":
                    logger.log("  [🌱成长] 已接受: " + tc)
                else:
                    logger.log("  [🌱成长] 接受 " + tc + ": " + st + " - " + msg[:80])
        elif resp:
            msg = resp.get("message", resp.get("msg", ""))
            logger.log("  [🌱成长] 批量接受失败: code=" + str(resp.get("code")) + ", msg=" + str(msg)[:80])

    def claim_task(self, task_code):
        """Claim task reward via /v2/activity/growth/tasks/{code}/claim."""
        ep = "/v2/activity/growth/tasks/" + task_code + "/claim"
        resp = self._post(ep, {})
        if resp and resp.get("code") == 0:
            data = resp.get("data", {})
            already = data.get("already_claimed", False)
            credit = data.get("credit", 0)
            energy = data.get("energy", 0)
            if already:
                logger.log("  [🌱成长] ✅已领取: " + task_code)
            else:
                logger.log("  [🌱成长] 🎁已领取: " + task_code + " (+" + str(credit) + " 积分, +" + str(energy) + " 能量)")
            return True
        logger.log("  [🌱成长] ❌领取 " + task_code + " 失败")
        return False

    def do_daily_sign(self):
        """Daily sign via billing checkin. Growth sign endpoint removed."""
        self.billing_checkin()

    # ==== Desktop Task Execution Methods ====
    def _do_create_canvas(self):
        """Trigger design/canvas mode task via ACP."""
        session_id = self.acp.create_session_with_welcome_mode("design")
        if not session_id:
            logger.log("  [💻桌面] 🎨设计创意: 会话失败")
            return False
        growth_events = [
            build_growth_event(GROWTH_EVENT_TASK_CREATED, "canvas-" + str(uuid.uuid4())[:8],
                                extra={"task_mode": "design", "agent_mode": "craft", "model": "",
                                       "has_repo": False, "repo_type": "", "workspace_type": "",
                                       "has_connector": False, "connector_types": [],
                                       "has_mention": False, "mention_types": [],
                                       "has_template": False, "template_id": "", "template_name": "",
                                       "has_expert": False, "expert_id": "", "expert_name": "",
                                       "has_skill": False, "skill_names": []}),
        ]
        meta = build_meta_with_growth_events(
            growth_events, mode="craft", model="default",
            session_id=session_id, user_id=self._user_id
        )
        stop, resp = self.acp.send_prompt_fire_and_forget(session_id, "design a simple web page layout with header and footer", meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] 🎨设计创意: 成功")
            self.telemetry.report_task_created(task_mode="design", agent_mode="craft")
            self.telemetry.report_design_canvas(action="open")
            return True
        logger.log("  [💻桌面] 设计创意: " + str(stop or resp)[:80])
        return False

    def _do_playbook_prompt(self, idx):
        """Trigger playbook/inspiration task via ACP."""
        scenes = get_template_scenes(5)
        if not scenes:
            scenes = [{"id": "01-ProductDesign", "name": "产品设计"}]
        scene = scenes[idx % len(scenes)]
        session_id = self.acp.create_session()
        if not session_id:
            logger.log("  [💻桌面] 💡灵感: 会话失败")
            return False
        template_id = scene["id"]
        scene_uri = "scene://" + template_id
        growth_events = [
            build_growth_event(GROWTH_EVENT_TASK_CREATED_WITH_TEMPLATE, template_id,
                                extra={"isCustomModel": True, "name": scene["name"]}),
            build_growth_event(GROWTH_EVENT_PLAYBOOK_PROMPT_SEND, template_id,
                                extra={"id": template_id, "name": scene["name"],
                                       "type": "other", "promptLength": 20,
                                       "isOfficial": 1, "skills": "",
                                       "skillNames": "", "categoryId": template_id.split("-")[0],
                                       "source": "growth-center"}),
        ]
        meta = build_meta_with_growth_events(
            growth_events, mode="craft", model="default",
            session_id=session_id, user_id=self._user_id
        )
        prompt_blocks = [
            {"type": "resource_link", "uri": scene_uri, "title": scene["name"],
             "name": scene["name"], "_meta": {"type": "scene", "mentionType": "scene",
                                               "displayText": scene["name"], "sceneId": str(template_id)}},
            {"type": "text", "text": "give me some coding best practices"},
        ]
        stop, resp = self.acp.send_prompt_with_blocks_fire_and_forget(session_id, prompt_blocks, meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] 💡灵感: 成功 (" + scene["name"] + ")")
            self.telemetry.report_playbook_prompt_send(template_id, scene["name"],
                category_id=template_id.split("-")[0] if "-" in template_id else "",
                conversation_id=session_id)
            self.telemetry.report_template_used(template_id)
            return True
        logger.log("  [💻桌面] 灵感: " + str(stop or resp)[:80])
        return False

    def _do_expert_team_use(self, idx):
        """Trigger Expert_team_use_3 - summon team experts."""
        teams = get_team_experts(5)
        if not teams:
            logger.log("  [💻桌面] 👥专家团: 未找到专家")
            return False
        expert = teams[idx % len(teams)]
        session_id = self.acp.create_session()
        if not session_id:
            logger.log("  [💻桌面] 👥专家团: 会话失败")
            return False
        expert_meta_obj = {
            "id": expert["id"],
            "name": expert["name"],
            "profession": expert.get("profession", ""),
            "prompt": expert.get("defaultInitPrompt", "You are " + expert["name"] + ". Please help the user."),
        }
        expert_event = build_growth_event(
            GROWTH_EVENT_EXPERT_ACTUAL_USE, expert["id"],
            extra={"name": expert["name"],
                   "expertTitle": expert.get("profession", expert.get("industryId", "")),
                   "type": expert.get("industryId", ""),
                   "cost": 0,
                   "characterCount": 30,
                   "conversationId": session_id,
                   "requestModelId": "default",
                   "requestModelName": ""},
            expert_type="team"
        )
        meta = build_meta_with_growth_events(
            [expert_event],
            mode="craft", model="default",
            expert_id=expert["id"],
            expert_meta=expert_meta_obj,
            session_id=session_id, user_id=self._user_id,
            tags=["expert:" + expert["id"]]
        )
        stop, resp = self.acp.send_prompt_fire_and_forget(session_id, "help me analyze a technical problem", meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] 👥专家团: 成功 (" + expert["name"] + ")")
            self.telemetry.report_expert_actual_use(expert["id"], expert["name"],
                expert_title=expert.get("profession", ""),
                industry_id=expert.get("industryId", ""),
                conversation_id=session_id,
                expert_type="team")
            self.telemetry.report_task_created(task_mode="", agent_mode="craft", has_expert=True, expert_id=expert["id"])
            return True
        logger.log("  [💻桌面] 专家团: " + str(stop or resp)[:80])
        return False

    def _do_expert_5(self, idx):
        """Trigger expert_5 - summon 5 different experts."""
        experts = get_normal_experts(10)
        if not experts:
            logger.log("  [💻桌面] 👨‍💼专家5次: 未找到专家")
            return False
        expert = experts[idx % len(experts)]
        session_id = self.acp.create_session()
        if not session_id:
            logger.log("  [💻桌面] 👨‍💼专家5次: 会话失败")
            return False
        expert_meta_obj = {
            "id": expert["id"],
            "name": expert["name"],
            "profession": expert.get("profession", ""),
            "prompt": expert.get("defaultInitPrompt", "You are " + expert["name"] + ". Please help the user."),
        }
        expert_event = build_growth_event(
            GROWTH_EVENT_EXPERT_ACTUAL_USE, expert["id"],
            extra={"name": expert["name"],
                   "expertTitle": expert.get("profession", expert.get("industryId", "")),
                   "type": expert.get("industryId", ""),
                   "cost": 0,
                   "characterCount": 30,
                   "conversationId": session_id,
                   "requestModelId": "default",
                   "requestModelName": ""}
        )
        meta = build_meta_with_growth_events(
            [expert_event],
            mode="craft", model="default",
            expert_id=expert["id"],
            expert_meta=expert_meta_obj,
            session_id=session_id, user_id=self._user_id,
            tags=["expert:" + expert["id"]]
        )
        stop, resp = self.acp.send_prompt_fire_and_forget(session_id, "help me with a coding question", meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] 👨‍💼专家5次: 成功 (" + expert["name"] + ")")
            self.telemetry.report_expert_actual_use(expert["id"], expert["name"],
                expert_title=expert.get("profession", ""),
                industry_id=expert.get("industryId", ""),
                conversation_id=session_id)
            self.telemetry.report_task_created(task_mode="", agent_mode="craft", has_expert=True, expert_id=expert["id"])
            return True
        logger.log("  [💻桌面] 专家5次: " + str(stop or resp)[:80])
        return False

    def _do_skill_1(self):
        """Trigger skill_1 - use a skill via ACP."""
        session_id = self.acp.create_session()
        if not session_id:
            logger.log("  [💻桌面] 🔧技能: 会话失败")
            return False
        # Use a skill that is actually installed in this desktop so the
        # native skill-use tracking fires. Discovered via
        # ~/.workbuddy/skills/<dir>/_skillhub_meta.json (name field).
        skill_name = "stock-analyst"
        growth_events = [
            build_growth_event(GROWTH_EVENT_TASK_CREATED, "skill-" + str(uuid.uuid4())[:8],
                                extra={"task_mode": "", "agent_mode": "craft", "model": "default",
                                       "has_repo": False, "repo_type": "", "workspace_type": "",
                                       "has_connector": False, "connector_types": [],
                                       "has_mention": False, "mention_types": [],
                                       "has_template": False, "template_id": "", "template_name": "",
                                       "has_expert": False, "expert_id": "", "expert_name": "",
                                       "has_skill": True, "skill_names": [skill_name]}),
            build_growth_event(GROWTH_EVENT_SKILL_REQUEST_SEND, skill_name,
                                extra={"ext1": gen_trace_id(), "skills": skill_name,
                                       "skillNames": skill_name, "isOfficial": 1}),
        ]
        meta = build_meta_with_growth_events(
            growth_events, mode="craft", model="default",
            session_id=session_id, user_id=self._user_id
        )
        prompt_blocks = [
            {"type": "resource_link", "uri": "skill://" + skill_name,
             "title": "Use skill " + skill_name, "name": skill_name,
             "_meta": {"mentionType": "skill", "skillName": skill_name}},
            {"type": "text", "text": "使用 " + skill_name + " 技能帮我分析一下贵州茅台(600519)的基本面。"},
        ]
        stop, resp = self.acp.send_prompt_with_blocks_fire_and_forget(session_id, prompt_blocks, meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] 🔧技能: 成功")
            self.telemetry.report_skill_action(skill_name, action="enable", outcome="success")
            self.telemetry.report_skill_installed(skill_name, is_official=True)
            self.telemetry.report_skill_request_send(skill_name)
            self.telemetry.report_task_created(task_mode="", agent_mode="craft", has_skill=True, skill_names=[skill_name])
            return True
        logger.log("  [💻桌面] 技能: " + str(stop or resp)[:80])
        return False

    def _do_template_5(self, idx):
        """Trigger template_5 - use 5 different templates."""
        scenes = get_template_scenes(8)
        if not scenes:
            scenes = [{"id": "01-ProductDesign", "name": "产品设计"}]
        scene = scenes[idx % len(scenes)]
        session_id = self.acp.create_session_with_welcome_mode("template")
        if not session_id:
            logger.log("  [💻桌面] 📄模板5次: 会话失败")
            return False
        template_id = scene["id"]
        scene_uri = "scene://" + template_id
        growth_events = [
            build_growth_event(GROWTH_EVENT_TASK_CREATED_WITH_TEMPLATE, template_id,
                                extra={"isCustomModel": True, "name": scene["name"]}),
            build_growth_event(GROWTH_EVENT_PLAYBOOK_PROMPT_SEND, template_id,
                                extra={"id": template_id, "name": scene["name"],
                                       "type": "other", "promptLength": 30,
                                       "isOfficial": 1, "skills": "",
                                       "skillNames": "", "categoryId": template_id.split("-")[0],
                                       "source": "growth-center"}),
        ]
        meta = build_meta_with_growth_events(
            growth_events, mode="craft", model="default",
            session_id=session_id, user_id=self._user_id
        )
        prompt_blocks = [
            {"type": "resource_link", "uri": scene_uri, "title": scene["name"],
             "name": scene["name"], "_meta": {"type": "scene", "mentionType": "scene",
                                               "displayText": scene["name"], "sceneId": str(template_id)}},
            {"type": "text", "text": "complete this task using the template"},
        ]
        stop, resp = self.acp.send_prompt_with_blocks_fire_and_forget(session_id, prompt_blocks, meta=meta, timeout=30)
        if stop == "end_turn":
            logger.log("  [💻桌面] 📄模板5次: ACP成功 (" + scene["name"] + ")")
            # Also send batch telemetry (this is what actually triggers growth progress)
            cat_id = template_id.split("-")[0] if "-" in template_id else ""
            batch = [
                ("TaskCreated", {
                    "source": "CLOUD", "name": "", "mode": "craft",
                    "requestModelId": "default", "action": template_id,
                    "has_template": True, "has_repo": False,
                    "has_expert": False, "has_mention": False,
                    "has_connector": False, "connector_types": [],
                    "mention_types": [], "skill_names": [],
                    "template_id": template_id, "template_name": scene["name"],
                    "workspace_type": "", "repo_type": "",
                }),
                ("TaskCreatedWithTemplate", {
                    "templateId": template_id, "templateName": scene["name"],
                    "isCustomModel": True, "id": template_id, "name": scene["name"],
                }),
                ("PlaybookPromptSend", {
                    "ext1": str(uuid.uuid4()), "requestId": str(uuid.uuid4()),
                    "id": template_id, "name": scene["name"], "categoryId": cat_id,
                    "type": "other", "promptLength": 30,
                    "isOfficial": 1, "skills": "", "skillNames": "",
                    "source": "growth-center",
                    "conversationId": session_id,
                }),
                ("TemplateUsed", {
                    "templateId": template_id, "templateName": scene["name"],
                }),
            ]
            self.telemetry.report_batch(batch)
            return True
        logger.log("  [💻桌面] 模板5次: " + str(stop or resp)[:80])
        return False

    def _do_automation_1(self):
        """Trigger automation_1 - create an automation schedule."""
        session_id = self.acp.create_session()
        if not session_id:
            logger.log("  [💻桌面] ⚙️自动化: 会话失败")
            return False
        growth_events = [
            build_growth_event(GROWTH_EVENT_TASK_CREATED, "automation-" + str(uuid.uuid4())[:8],
                                extra={"task_mode": "", "agent_mode": "craft", "model": "default",
                                       "has_repo": False, "repo_type": "", "workspace_type": "",
                                       "has_connector": False, "connector_types": [],
                                       "has_mention": False, "mention_types": [],
                                       "has_template": False, "template_id": "", "template_name": "",
                                       "has_expert": False, "expert_id": "", "expert_name": "",
                                       "has_skill": False, "skill_names": [],
                                       "isAutomationBackground": True}),
        ]
        meta = build_meta_with_growth_events(
            growth_events, mode="craft", model="default",
            session_id=session_id, user_id=self._user_id,
            is_automation=True
        )
        stop, resp = self.acp.send_prompt_fire_and_forget(session_id,
            "create a scheduled automation that runs daily at 9am to check code quality", meta=meta)
        if stop == "end_turn":
            logger.log("  [💻桌面] ⚙️自动化: 成功")
            self.telemetry.report_task_created(task_mode="automation", agent_mode="craft", is_automation=True)
            self.telemetry.report_automated_task_execute()
            self.telemetry.report_automated_task_create()
            return True
        logger.log("  [💻桌面] 自动化: " + str(stop or resp)[:80])
        return False

    # ==== Chat Task Execution ====
    def do_chat_task_acp(self, task_code, task_name, target_count, template_id=0):
        """Execute chat-based tasks (chat_5, Model_chat_GLM5.2, black_cat) via ACP."""
        logger.log("  [💬对话] " + task_name + " (还需 " + str(target_count) + " 次)")
        if not self.acp:
            if not self.init_acp():
                logger.log("  [💬对话] ACP 未连接，尝试 WebChat API 回退...")
                return self._do_chat_task_webchat(task_code, task_name, target_count, template_id=template_id)

        model_map = {"Model_chat_GLM5.2": "glm-5.2", "RichMeow_Chat": "glm-5.2"}
        model_id = model_map.get(task_code, "glm-5.2")

        if task_code == "black_cat":
            hour = datetime.now().hour
            if hour >= 23 or hour < 8:
                logger.log("  [💬对话] 🦉夜猫子模式激活 (小时=" + str(hour) + "), 执行中...")
                model_id = "glm-5.2"
            else:
                logger.log("  [💬对话] 🦉夜猫子仅在 23:00-08:00 生效, 当前 " + str(hour) + ":xx, 跳过")
                logger.log("  [💬对话] 💡提示: 将脚本安排在 23:00-08:00 运行以完成夜猫子任务")
                return False

        prompts = [
            "你好，请回复OK",
            "今天天气怎么样？",
            "1+1等于几？请直接回答",
            "Python是什么？一句话回答",
            "请说再见",
            "写一首关于春天的诗",
            "JavaScript和TypeScript的区别是什么？",
            "解释一下什么是云计算",
            "推荐一本好书",
            "如何学习编程？",
        ]

        success = 0
        for i in range(target_count):
            prompt = prompts[i % len(prompts)]
            session_id = self.acp.create_session()
            if not session_id:
                logger.log("  [💬对话] 对话 #" + str(i+1) + ": 会话失败")
                continue

            if model_id:
                self.acp.set_model(session_id, model_id)

            chat_growth_events = [
                build_growth_event(GROWTH_EVENT_TASK_CREATED, "chat-" + str(uuid.uuid4())[:8],
                                    extra={"task_mode": "", "agent_mode": "craft", "model": model_id or "default",
                                           "has_repo": False, "repo_type": "", "workspace_type": "",
                                           "has_connector": False, "connector_types": [],
                                           "has_mention": False, "mention_types": [],
                                           "has_template": False, "template_id": "", "template_name": "",
                                           "has_expert": False, "expert_id": "", "expert_name": "",
                                           "has_skill": False, "skill_names": []}),
            ]
            chat_meta = build_meta_with_growth_events(
                chat_growth_events, mode="craft", model=model_id or "default",
                session_id=session_id, user_id=self._user_id
            )
            stop, resp = self.acp.send_prompt_fire_and_forget(session_id, prompt, meta=chat_meta, model_id=model_id)
            if stop == "end_turn":
                success += 1
                resp_preview = (resp or "")[:30].replace("\n", " ")
                logger.log("  [💬对话] 对话 #" + str(i+1) + "/" + str(target_count) + " 成功: " + resp_preview)
            else:
                logger.log("  [💬对话] 对话 #" + str(i+1) + ": " + str(stop or resp)[:80])

            if i < target_count - 1:
                time.sleep(2)

        logger.log("  [💬对话] 对话完成: " + str(success) + "/" + str(target_count) + " 成功")
        return success >= target_count

    def _do_chat_task_webchat(self, task_code, task_name, target_count, template_id=0, is_retry=False):
        """Complete chat tasks via WebChat API + correct telemetry (v23).
        
        Root cause fix: The frontend sends chat_request_send / chat_request_response
        telemetry events (NOT agent_task_created). Growth system only tracks chat
        task progress when it sees these specific event codes.
        
        Flow per chat:
        1. Create conversation via /console/webchat/conversations
        2. Send message via /console/chat/completions (stream)
        3. Send chat_request_send + chat_request_response telemetry to /v2/report
        """
        model_map = {"Model_chat_GLM5.2": "glm-5.2", "black_cat": "glm-5.2",
                     "chat_5": "glm-5.2", "RichMeow_Chat": "glm-5.2",
                     "desktop_chat": "glm-5.2"}
        model_id = model_map.get(task_code, "glm-5.2")

        if task_code == "black_cat":
            hour = datetime.now().hour
            if not (hour >= 23 or hour < 8):
                logger.log("  [💬聊天] 🦉夜猫子仅在 23:00-08:00 计数, 当前 " + str(hour) + ":xx, 跳过")
                return False

        if is_retry:
            logger.log("  [💬聊天] 🔄重试: " + task_name + " (模型=" + model_id + ", 还需 " + str(target_count) + " 次)")
        else:
            logger.log("  [💬聊天] " + task_name + " (模型=" + model_id + ", 还需 " + str(target_count) + " 次)")

        prompts = [
            "你好，请简单介绍一下你自己",
            "今天天气怎么样？",
            "1+1等于几？请直接回答",
            "Python是什么？一句话回答",
            "请说再见",
            "写一首关于春天的诗",
            "JavaScript和TypeScript的区别是什么？",
            "解释一下什么是云计算",
            "推荐一本好书",
            "如何学习编程？",
        ]

        # Track baseline progress
        cur_before, tgt = self._check_task_progress(task_code)
        logger.log("  [💬聊天] 当前进度: " + str(cur_before) + "/" + str(tgt))

        chat_success = 0
        for i in range(target_count):
            prompt = prompts[i % len(prompts)]
            message_id = "cmb-" + str(uuid.uuid4())

            try:
                # Step 1: Create conversation via /console/webchat/conversations
                conv_id = None
                try:
                    conv_name = "growth-" + str(uuid.uuid4())[:12]
                    r_conv = self.sess.post(
                        self.BASE + "/console/webchat/conversations",
                        json={"name": conv_name}, timeout=15, verify=False,
                    )
                    if r_conv.status_code == 200:
                        conv_data = r_conv.json()
                        if conv_data.get("code") == 0:
                            conv_id = conv_data.get("data", {}).get("conversationId", "")
                except Exception:
                    pass

                if not conv_id:
                    conv_id = str(uuid.uuid4())
                    logger.log("  [💬聊天] 使用随机 conv_id (创建失败)")

                # Step 2: Send chat message via /console/chat/completions
                headers = dict(self.sess.headers)
                headers["Accept"] = "text/event-stream"
                headers["Referer"] = "https://www.workbuddy.cn/chat/"

                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "model": model_id,
                    "stream": True,
                    "conversationId": conv_id,
                }

                r = self.sess.post(
                    self.BASE + "/console/chat/completions",
                    json=payload, timeout=60, verify=False, stream=True,
                    headers=headers,
                )

                response_text = ""
                if r.status_code == 200:
                    for line in r.iter_lines(decode_unicode=True):
                        if line and line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[✅完成]":
                                break
                            try:
                                d = json.loads(data_str)
                                for c in d.get("choices", []):
                                    delta = c.get("delta", {})
                                    cp = delta.get("content", "")
                                    if cp:
                                        response_text += cp
                            except Exception:
                                pass

                if response_text:
                    chat_success += 1
                    resp_preview = response_text[:30].replace("\n", " ")
                    logger.log("  [💬聊天] 对话 #" + str(i+1) + "/" + str(target_count) + " 成功: " + resp_preview)
                else:
                    logger.log("  [💬聊天] 对话 #" + str(i+1) + ": 无响应 (HTTP " + str(r.status_code) + ")")

                # Step 3: Send CORRECT telemetry events (chat_request_send + chat_request_response)
                # This is the critical fix - the frontend uses these event codes, NOT agent_task_created
                machine_id = str(uuid.uuid4())
                send_ts = int(time.time() * 1000) - 2000
                resp_ts = int(time.time() * 1000)

                chat_send_event = {
                    "eventCode": "chat_request_send",
                    "timestamp": send_ts,
                    "reportDelay": 0,
                    "expKeys": "",
                    "ideName": "sdk",
                    "machineId": machine_id,
                    "userId": self._user_id,
                    "mode": "ask",
                    "conversationId": conv_id,
                    "requestId": message_id,
                    "requestModelId": model_id,
                    "requestModelName": model_id,
                    "inputLength": len(prompt),
                    "customAgentName": "",
                }

                chat_resp_event = {
                    "eventCode": "chat_request_response",
                    "timestamp": resp_ts,
                    "reportDelay": 0,
                    "expKeys": "",
                    "ideName": "sdk",
                    "machineId": machine_id,
                    "userId": self._user_id,
                    "mode": "ask",
                    "conversationId": conv_id,
                    "requestId": message_id,
                    "requestModelId": model_id,
                    "requestModelName": model_id,
                    "toolCallCount": 0,
                    "inputToken": max(1, len(prompt) // 4),
                    "outputToken": max(1, len(response_text) // 4) if response_text else 1,
                    "totalToken": max(2, (len(prompt) + len(response_text)) // 4),
                }

                try:
                    proxies = get_proxies()
                    try:
                        telem_r = self.sess.post(
                            "https://www.workbuddy.cn/v2/report",
                            json=[chat_send_event, chat_resp_event],
                            timeout=10, verify=False, proxies=proxies,
                        )
                    except Exception:
                        telem_r = self.sess.post(
                            "https://www.workbuddy.cn/v2/report",
                            json=[chat_send_event, chat_resp_event],
                            timeout=10, verify=False,
                        )
                    if telem_r.status_code == 200:
                        try:
                            telem_data = telem_r.json()
                            ok = telem_data.get("code") == 0
                        except:
                            ok = True
                    else:
                        ok = False
                    if ok:
                        logger.log("  [📡遥测] chat_request 事件已发送 #" + str(i+1))
                    else:
                        logger.log("  [📡遥测] 遥测发送失败 #" + str(i+1))
                except Exception as e:
                    logger.log("  [📡遥测] Error: " + str(e)[:60])

            except Exception as e:
                logger.log("  [💬聊天] 对话 #" + str(i+1) + " 错误: " + str(e)[:80])

            if i < target_count - 1:
                time.sleep(random.uniform(2, 5))

        # Final progress check
        time.sleep(5)
        cur_final, tgt_final = self._check_task_progress(task_code)
        logger.log("  [💬聊天] 最终: " + task_name + " 进度: " + str(cur_before) + " -> " + str(cur_final) + "/" + str(tgt_final))

        if cur_final >= tgt_final and tgt_final > 0:
            logger.log("  [💬聊天] ✅任务完成!")
            return True
        elif cur_final > cur_before:
            logger.log("  [💬聊天] 📊部分进展 (新增 " + str(cur_final - cur_before) + ")")
            remaining = tgt_final - cur_final
            if remaining > 0:
                logger.log("  [💬聊天] 还差 " + str(remaining) + " 次, 重试中...")
                return self._do_chat_task_webchat(task_code, task_name, remaining)
            return True
        else:
            # WebChat API did not move progress
            # v23: Do NOT fall back to pure telemetry (it doesn't work for chat tasks)
            # Instead, retry WebChat one more time with a delay
            logger.log("  [💬聊天] 首次无进展，10秒后重试...")
            time.sleep(10)
            # Check again in case progress was delayed
            cur_check, _ = self._check_task_progress(task_code)
            if cur_check > cur_before:
                logger.log("  [💬聊天] 进度延迟更新: " + str(cur_before) + " -> " + str(cur_check))
                return True
            # Final retry
            logger.log("  [💬聊天] 🔄最终重试 " + task_name + "...")
            if is_retry:
                logger.log("  [💬聊天] ❌重试仍失败，此任务可能需要 WorkBuddy Desktop 运行中")
                return False
            return self._do_chat_task_webchat(task_code, task_name, target_count, template_id=template_id, is_retry=True)

    # ==== Desktop Task Dispatcher ====
    def do_desktop_task(self, task_code, task_name, target_count):
        """Execute desktop task: telemetry-first, then ACP fallback, with progress verification."""
        logger.log("  [💻桌面] " + task_name + " (" + task_code + ", x" + str(target_count) + ")")

        # Check progress before starting
        cur_before, tgt = self._check_task_progress(task_code)
        remaining = tgt - cur_before
        if remaining <= 0:
            logger.log("  [💻桌面] " + task_name + " 已完成 (" + str(cur_before) + "/" + str(tgt) + ")")
            return True
        logger.log("  [💻桌面] 当前进度: " + str(cur_before) + "/" + str(tgt) + ", 还需 " + str(remaining) + " 次")

        success = 0
        for i in range(remaining):
            ok = False

            # Strategy 1: Send telemetry first (works for expert tasks)
            tel_ok = self._send_telemetry_only(task_code, i)
            if tel_ok:
                # Wait and verify progress
                time.sleep(3)
                cur_after, _ = self._check_task_progress(task_code)
                if cur_after > cur_before + success:
                    logger.log("  [💻桌面] 📡遥测推送进度至 " + str(cur_after) + "/" + str(tgt))
                    success += 1
                    ok = True
                else:
                    logger.log("  [💻桌面] 📡遥测已发送但进度未变 (" + str(cur_after) + "/" + str(tgt) + ")")

            # Strategy 2: ACP fallback if telemetry didn't work and ACP is available
            if not ok:
                if not self.acp:
                    self.init_acp()
                if self.acp:
                    if task_code == "create_canvas":
                        ok = self._do_create_canvas()
                    elif task_code == "playbook_prompt":
                        ok = self._do_playbook_prompt(i)
                    elif task_code == "Expert_team_use_3":
                        ok = self._do_expert_team_use(i)
                    elif task_code == "expert_5":
                        ok = self._do_expert_5(i)
                    elif task_code == "skill_1":
                        ok = self._do_skill_1()
                    elif task_code == "template_5":
                        ok = self._do_template_5(i)
                    elif task_code == "automation_1":
                        ok = self._do_automation_1()
                    else:
                        # Unknown desktop task: try generic expert/chat approach
                        logger.log("  [💻桌面] ❓未知任务 " + task_code + ", 尝试通用方式...")
                        ok = False
                    if ok:
                        success += 1

            if not ok and not tel_ok:
                logger.log("  [💻桌面] ❌遥测和 ACP 均失败: " + task_code + " #" + str(i+1))
                if task_code == "template_5":
                    logger.log("  [💻桌面] -> 请手动在 WorkBuddy 网页/桌面端使用模板")
                elif task_code not in DESKTOP_TASK_CODES:
                    logger.log("  [💻桌面] -> 新/未知任务，可能需要手动完成或更新脚本")
                break  # No point retrying

            if i < remaining - 1:
                time.sleep(3)

        # Final progress check
        cur_final, tgt_final = self._check_task_progress(task_code)
        logger.log("  [💻桌面] " + task_name + " 最终进度: " + str(cur_final) + "/" + str(tgt_final))
        return cur_final >= tgt_final

    def _send_telemetry_only(self, task_code, idx=0):
        """Send telemetry events via /v2/report without ACP daemon (cloud-only mode)."""
        logger.log("  [📡遥测] 发送云端遥测: " + task_code)
        try:
            if task_code == "create_canvas":
                self.telemetry.report_task_created(task_mode="design", agent_mode="craft")
                self.telemetry.report_design_canvas(action="open")
            elif task_code == "playbook_prompt":
                scenes = get_template_scenes(5)
                scene = scenes[idx % len(scenes)] if scenes else {"id": "01-ProductDesign", "name": "ProductDesign"}
                self.telemetry.report_task_created(task_mode="", agent_mode="craft",
                    template_id=scene["id"])
                self.telemetry.report_playbook_prompt_send(scene["id"], scene["name"],
                    category_id=scene["id"].split("-")[0] if "-" in scene["id"] else "")
                self.telemetry.report_task_created_with_template(scene["id"], scene["name"])
            elif task_code in ("Expert_team_use_3", "expert_5"):
                experts = get_team_experts(5) if task_code == "Expert_team_use_3" else get_normal_experts(10)
                if experts:
                    expert = experts[idx % len(experts)]
                    self.telemetry.report_expert_actual_use(expert["id"], expert["name"],
                        expert_title=expert.get("profession", ""),
                        expert_type="team" if task_code == "Expert_team_use_3" else "agent")
                    self.telemetry.report_task_created(task_mode="", agent_mode="craft",
                        has_expert=True, expert_id=expert["id"])
                else:
                    self.telemetry.report_expert_actual_use("expert-" + str(uuid.uuid4())[:8],
                        "Expert", expert_type="team" if task_code == "Expert_team_use_3" else "agent")
                    self.telemetry.report_task_created(has_expert=True, expert_id="unknown")
            elif task_code == "skill_1":
                skill_name = "algorithmic-trading"
                self.telemetry.report_skill_action(skill_name, action="enable", outcome="success")
                self.telemetry.report_skill_installed(skill_name, is_official=True)
                self.telemetry.report_skill_request_send(skill_name)
                self.telemetry.report_task_created(has_skill=True, skill_names=[skill_name])
            elif task_code == "template_5":
                # Send batches for ALL distinct scenes so the missing one(s) get covered.
                # The outer loop only runs `remaining` times (often 1), so relying on `idx`
                # alone re-sends an already-counted scene and never reaches the 5th distinct
                # template. Looping over every scene fixes the 4/5 -> 5/5 stall.
                scenes = get_template_scenes(8)
                if not scenes:
                    scenes = [{"id": "01-ProductDesign", "name": "ProductDesign"}]
                all_ok = True
                for sc in scenes:
                    tid = sc["id"]
                    tname = sc["name"]
                    cat_id = tid.split("-")[0] if "-" in tid else ""
                    batch = [
                        ("TaskCreated", {
                            "source": "CLOUD", "name": "", "mode": "craft",
                            "requestModelId": "default", "action": tid,
                            "has_template": True, "has_repo": False,
                            "has_expert": False, "has_mention": False,
                            "has_connector": False, "connector_types": [],
                            "mention_types": [], "skill_names": [],
                            "template_id": tid, "template_name": tname,
                            "workspace_type": "", "repo_type": "",
                        }),
                        ("TaskCreatedWithTemplate", {
                            "templateId": tid, "templateName": tname,
                            "isCustomModel": True, "id": tid, "name": tname,
                        }),
                        ("PlaybookPromptSend", {
                            "ext1": str(uuid.uuid4()), "requestId": str(uuid.uuid4()),
                            "id": tid, "name": tname, "categoryId": cat_id,
                            "type": "other", "promptLength": 30,
                            "isOfficial": 1, "skills": "", "skillNames": "",
                            "source": "growth-center",
                            "conversationId": str(uuid.uuid4()),
                        }),
                        ("TemplateUsed", {
                            "templateId": tid, "templateName": tname,
                        }),
                    ]
                    ok = self.telemetry.report_batch(batch)
                    if ok:
                        logger.log("  [cloud] template_5 batch sent (" + tname + ")")
                    else:
                        all_ok = False
                    time.sleep(1)
                return all_ok
            elif task_code == "automation_1":
                self.telemetry.report_task_created(task_mode="automation", agent_mode="craft", is_automation=True)
                self.telemetry.report_automated_task_create()
                self.telemetry.report_automated_task_execute()
            else:
                # Unknown desktop task: try generic telemetry based on jump_url
                task_data_for_generic = None
                try:
                    all_tasks = self.get_tasks()
                    for t in all_tasks:
                        if t.get("task_code") == task_code:
                            task_data_for_generic = t
                            break
                except Exception:
                    pass
                if task_data_for_generic:
                    result = self._send_generic_telemetry(task_code, task_data_for_generic, idx)
                    if result:
                        logger.log("  [📡遥测] 云端遥测发送成功: " + task_code + " (通用)")
                        return True
                logger.log("  [📡遥测] ❓未知任务: " + task_code + ", 无法确定遥测类型")
                return False
            logger.log("  [📡遥测] 云端遥测发送成功: " + task_code)
            return True
        except Exception as e:
            logger.log("  [📡遥测] Error: " + str(e)[:80])
            return False

    def _send_generic_telemetry(self, task_code, task_data, idx=0):
        """Send generic telemetry for unknown desktop tasks based on jump_url patterns.
        
        When WorkBuddy adds new tasks that are not hardcoded, this method
        infers the correct telemetry type from the task's jump_url field.
        """
        if not task_data or not isinstance(task_data, dict):
            logger.log("  [📡遥测] 无 task_data 通用回退: " + task_code)
            return False
        
        jump_url = task_data.get("jump_url", "")
        logger.log("  [📡遥测] 通用回退: " + task_code + " (jump=" + jump_url + ")")
        
        if "expert" in jump_url or "experts" in jump_url:
            experts = get_team_experts(5)
            if experts:
                expert = experts[idx % len(experts)]
                self.telemetry.report_expert_actual_use(expert["id"], expert["name"],
                    expert_title=expert.get("profession", ""),
                    expert_type="team")
                self.telemetry.report_task_created(task_mode="", agent_mode="craft",
                    has_expert=True, expert_id=expert["id"])
            else:
                self.telemetry.report_expert_actual_use("expert-" + str(uuid.uuid4())[:8],
                    "Expert", expert_type="team")
                self.telemetry.report_task_created(has_expert=True)
            logger.log("  [📡遥测] 👨‍💼通用专家遥测已发送: " + task_code)
            return True
        
        if "playbook" in jump_url or "template" in jump_url:
            scenes = get_template_scenes(8)
            scene = scenes[idx % len(scenes)] if scenes else {"id": "01-ProductDesign", "name": "ProductDesign"}
            self.telemetry.report_task_created(task_mode="", agent_mode="craft",
                template_id=scene["id"])
            self.telemetry.report_playbook_prompt_send(scene["id"], scene["name"],
                category_id=scene["id"].split("-")[0] if "-" in scene["id"] else "")
            self.telemetry.report_task_created_with_template(scene["id"], scene["name"])
            logger.log("  [📡遥测] 📄通用模板遥测已发送: " + task_code)
            return True
        
        if "skill" in jump_url:
            skill_name = "algorithmic-trading"
            self.telemetry.report_skill_action(skill_name, action="enable", outcome="success")
            self.telemetry.report_skill_installed(skill_name, is_official=True)
            self.telemetry.report_skill_request_send(skill_name)
            self.telemetry.report_task_created(has_skill=True, skill_names=[skill_name])
            logger.log("  [📡遥测] 🔧通用技能遥测已发送: " + task_code)
            return True
        
        if "automation" in jump_url:
            self.telemetry.report_task_created(task_mode="automation", agent_mode="craft", is_automation=True)
            self.telemetry.report_automated_task_create()
            self.telemetry.report_automated_task_execute()
            logger.log("  [📡遥测] ⚙️通用自动化遥测已发送: " + task_code)
            return True
        
        if "chat" in jump_url:
            # Chat-type desktop task: try WebChat approach
            logger.log("  [📡遥测] " + task_code + " 为聊天任务，将尝试 WebChat API")
            return False
        
        logger.log("  [📡遥测] 无法确定遥测类型: " + task_code + " (jump=" + jump_url + ")")
        return False

    def _check_task_progress(self, task_code):
        """Query current progress for a task. Returns (current, target) or (0, 0)."""
        try:
            tasks = self.get_tasks()
            for t in tasks:
                if not isinstance(t, dict):
                    continue
                tc = t.get("task_code", t.get("code", ""))
                if tc == task_code:
                    prog = t.get("progress", {})
                    if isinstance(prog, dict):
                        return prog.get("current", 0), prog.get("target", 0)
            return 0, 0
        except Exception:
            return 0, 0

    # ==== Process All Tasks ====
    def _format_progress(self, task):
        prog = task.get("progress", {})
        if isinstance(prog, dict):
            cur = prog.get("current", 0)
            tgt = prog.get("target", 0)
            return " (" + str(cur) + "/" + str(tgt) + ")"
        return ""

    def _format_reward(self, task):
        reward = task.get("reward", {})
        if isinstance(reward, dict):
            credit = reward.get("credit", 0)
            energy = reward.get("energy", 0)
            parts = []
            if credit: parts.append(str(credit) + " credits")
            if energy: parts.append(str(energy) + " energy")
            if parts: return " [" + ", ".join(parts) + "]"
        return ""

    def process_tasks(self):
        tasks = self.get_tasks()
        if not tasks:
            logger.log("  [🌱成长] 无任务")
            return

        to_accept = []
        claimed_count = 0
        chat_tasks_to_do = []
        desktop_tasks_to_do = []

        for task in tasks:
            if not isinstance(task, dict):
                continue
            task_code = task.get("task_code", task.get("code", ""))
            name = task.get("task_name", task.get("title", task.get("name", "")))
            status = str(task.get("accept_status", task.get("status", ""))).lower()
            prog = task.get("progress", {})
            cur = prog.get("current", 0) if isinstance(prog, dict) else 0
            tgt = prog.get("target", 0) if isinstance(prog, dict) else 0

            prog_str = self._format_progress(task)
            reward_str = self._format_reward(task)

            if status in (self.TASK_NOT_ACCEPTED, "0", "not_accepted"):
                if task_code:
                    to_accept.append(task_code)
                logger.log("  [🌱成长] 📋待接受: " + name + reward_str)
            elif status in (self.TASK_ACCEPTED, self.TASK_IN_PROGRESS, "in_progress",
                            "accepted", "in progress", "ongoing", "active"):
                if cur < tgt:
                    remaining = tgt - cur
                    category = classify_task_code(task_code, task)
                    if category == "chat":
                        chat_tasks_to_do.append((task_code, name, remaining, int(task.get("template_id_fixed", 0) or 0)))
                        logger.log("  [🌱成长] 💬需对话: " + name + prog_str + reward_str)
                    elif category == "desktop":
                        desktop_tasks_to_do.append((task_code, name, remaining))
                        logger.log("  [🌱成长] 💻需桌面端: " + name + prog_str + reward_str)
                    elif category == "auto":
                        logger.log("  [🌱成长] ⚡自动完成: " + name + prog_str + reward_str)
                    else:
                        chat_tasks_to_do.append((task_code, name, remaining))
                        logger.log("  [🌱成长] ❓未知, 尝试对话: " + name + prog_str + reward_str)
                else:
                    logger.log("  [🌱成长] 🔄进行中: " + name + prog_str + reward_str)
            elif status == self.TASK_COMPLETED or status == "completed":
                self.claim_task(task_code)
                claimed_count += 1
            elif status == self.TASK_CLAIMED or status == "claimed":
                logger.log("  [🌱成长] ✅已领取: " + name + reward_str)
            else:
                logger.log("  [🌱成长] 📌 " + name + ": " + status + prog_str)

        # Accept pending tasks
        if to_accept:
            self.accept_tasks(to_accept)
            time.sleep(1)
            tasks2 = self.get_tasks()
            for task in tasks2:
                if not isinstance(task, dict):
                    continue
                task_code = task.get("task_code", task.get("code", ""))
                status = str(task.get("accept_status", task.get("status", ""))).lower()
                if status in (self.TASK_COMPLETED, "completed") and task_code:
                    self.claim_task(task_code)
                    claimed_count += 1
                if status in (self.TASK_ACCEPTED, "accepted", self.TASK_IN_PROGRESS, "in_progress",
                                "in progress", "ongoing", "active"):
                    prog = task.get("progress", {})
                    cur = prog.get("current", 0) if isinstance(prog, dict) else 0
                    tgt = prog.get("target", 0) if isinstance(prog, dict) else 0
                    if cur < tgt:
                        existing_chat = [c for c, _, _, _ in chat_tasks_to_do]
                        existing_desk = [c for c, _, _ in desktop_tasks_to_do]
                        name = task.get("task_name", task.get("title", task.get("name", "")))
                        remaining = tgt - cur
                        category2 = classify_task_code(task_code, task)
                        if category2 == "chat" and task_code not in existing_chat:
                            chat_tasks_to_do.append((task_code, name, remaining, int(task.get("template_id_fixed", 0) or 0)))
                        elif category2 == "desktop" and task_code not in existing_desk:
                            desktop_tasks_to_do.append((task_code, name, remaining))
                        elif category2 not in ("auto",) and task_code not in existing_chat and task_code not in existing_desk:
                            chat_tasks_to_do.append((task_code, name, remaining, int(task.get("template_id_fixed", 0) or 0)))

        logger.log("  [🌱成长] 🎁本轮领取 " + str(claimed_count) + " 个奖励")

        # Execute chat tasks via ACP
        if chat_tasks_to_do:
            logger.log("━━━ 💬对话任务 ━━━")
            if not self.acp:
                self.init_acp()
            for task_code, task_name, remaining, tpl_id in chat_tasks_to_do:
                self.do_chat_task_acp(task_code, task_name, remaining, template_id=tpl_id)
                time.sleep(2)
                # Check if task completed after execution
                tasks_after = self.get_tasks()
                for t in tasks_after:
                    if not isinstance(t, dict):
                        continue
                    tc = t.get("task_code", t.get("code", ""))
                    if tc == task_code:
                        status = str(t.get("accept_status", t.get("status", ""))).lower()
                        if status in (self.TASK_COMPLETED, "completed"):
                            self.claim_task(tc)
                        break

        # Execute desktop tasks via ACP
        if desktop_tasks_to_do:
            logger.log("━━━ 💻桌面任务 ━━━")
            if not self.acp:
                self.init_acp()
            for task_code, task_name, remaining in desktop_tasks_to_do:
                self.do_desktop_task(task_code, task_name, remaining)
                time.sleep(3)
                # Check if task completed after execution
                tasks_after = self.get_tasks()
                for t in tasks_after:
                    if not isinstance(t, dict):
                        continue
                    tc = t.get("task_code", t.get("code", ""))
                    if tc == task_code:
                        status = str(t.get("accept_status", t.get("status", ""))).lower()
                        prog = t.get("progress", {})
                        cur = prog.get("current", 0) if isinstance(prog, dict) else 0
                        tgt = prog.get("target", 0) if isinstance(prog, dict) else 0
                        if status in (self.TASK_COMPLETED, "completed") or cur >= tgt:
                            self.claim_task(tc)
                        break

    # ==== Lottery ====
    def get_lottery_chances(self):
        resp = self._get("/v2/activity/growth/lottery/chances")
        if resp and resp.get("code") == 0:
            data = resp.get("data", {})
            chances = data.get("balance", data.get("chances", data.get("remaining", 0)))
            logger.log("  [🌱成长] 🎰抽奖次数: " + str(chances))
            return chances
        logger.log("  [🌱成长] 获取抽奖次数失败")
        return 0

    def do_lottery(self):
        chances = self.get_lottery_chances()
        if not chances or chances <= 0:
            logger.log("  [🌱成长] 无抽奖次数")
            return []
        summary = self._get("/v2/activity/growth/lottery/summary")
        if summary and summary.get("code") == 0:
            module = summary.get("data", {}).get("module", None)
            if module is not None and not (module.get("enabled", True) if isinstance(module, dict) else True):
                logger.log("  [🌱成长] 抽奖未开启")
                return []
        won = []
        for i in range(chances):
            if i > 0:
                time.sleep(random.uniform(1.5, 3.5))
            client_token = gen_client_token("draw")
            resp = self._post("/v2/activity/growth/lottery/draw", {"client_token": client_token})
            if resp and resp.get("code") == 0:
                data = resp.get("data", {})
                prize = data.get("prize_name", data.get("name", data.get("reward", "unknown")))
                logger.log("  [🌱成长] 🎰抽奖结果: " + str(prize))
                won.append(prize)
            else:
                msg = resp.get("message", "") if resp else "request failed"
                logger.log("  [🌱成长] 🎰抽奖失败: " + str(msg))
        if won:
            logger.log("  [🌱成长] 🎰抽奖汇总: " + "、".join(str(w) for w in won))
        return won

    # ==== Buddy / Blind Box ====
    def open_buddy(self):
        quota_resp = self._get("/v2/activity/growth/buddy/quota")
        affordable = 0
        if quota_resp and quota_resp.get("code") == 0:
            quota_data = quota_resp.get("data", {})
            affordable = quota_data.get("affordable", 0)
            balance = quota_data.get("balance", 0)
            cost = quota_data.get("cost_per_open", 10)
            if affordable and affordable > 0:
                logger.log("  [🌱成长] 🎁可开盲盒: " + str(affordable) + " 次 (能量 " + str(balance) + "/" + str(cost) + ")")
            else:
                logger.log("  [🌱成长] 无盲盒配额 (能量 " + str(balance) + "/" + str(cost) + ")")
                return
        else:
            logger.log("  [🌱成长] 获取盲盒配额失败，尝试直接开启")
        open_count = min(affordable, 5) if affordable > 0 else 1
        for _ in range(open_count):
            resp = self._post("/v2/activity/growth/buddy/open", {"count": 1})
            if resp:
                code = resp.get("code", -1)
                msg = resp.get("message", resp.get("msg", ""))
                if code == 0:
                    data = resp.get("data", {})
                    results = data.get("results", [])
                    if results and isinstance(results, list) and len(results) > 0:
                        item = results[0]
                        instance = item.get("instance", {})
                        template = item.get("template", {})
                        name = instance.get("name", template.get("name", "unknown"))
                        rarity = instance.get("rarity", template.get("rarity", ""))
                        personality = instance.get("personality", template.get("personality", ""))
                        rarity_str = " (" + rarity + ")" if rarity else ""
                        personality_str = ", " + personality if personality else ""
                        logger.log("  [🌱成长] 🎁盲盒: " + name + rarity_str + personality_str)
                    else:
                        item_name = data.get("item_name", data.get("name", msg))
                        logger.log("  [🌱成长] 🎁盲盒: " + str(item_name))
                else:
                    logger.log("  [🌱成长] 盲盒: code=" + str(code) + ", msg=" + str(msg))
                    break
            else:
                logger.log("  [🌱成长] 盲盒请求失败")
                break
            time.sleep(random.uniform(1.0, 2.0))

    def get_buddy_info(self):
        resp = self._get("/v2/activity/growth/buddy/info")
        if resp and resp.get("code") == 0:
            data = resp.get("data", {})
            buddy = data.get("buddy", data)
            name = buddy.get("name", "?")
            rarity = buddy.get("rarity", "")
            personality = buddy.get("personality", "")
            personality_str = ", " + personality if personality else ""
            logger.log("  [🌱成长] 🐱Buddy: " + str(name) + " (" + str(rarity) + ")" + personality_str)
            return data
        return None

    # ==== Buddy Travel (派猫猫旅行 / 领取礼物) ====
    def do_buddy_travel(self):
        """网页「派猫猫旅行」小游戏：让 Buddy 出发旅行，到达后领取礼物(积分)。
        流程：取配置拿到目的地 -> 查当前状态 ->
          idle 且未达每日上限 -> 出发(depart) -> 等待到达(按 arrive_at) ->
          arrived -> 领取礼物(claim)。旅行需真实数小时，靠 cron 每日重跑推进，
          状态机 idle/traveling/arrived 天然幂等，不会重复领取。"""
        logger.log("━━━ 🐱派猫猫旅行 ━━━")
        # 旅行模块开关：未拥有 Buddy 或缺席时跳过
        vis = self._get("/v2/activity/growth/buddy/visible")
        if vis and vis.get("code") == 0:
            vd = vis.get("data", {})
            if not vd.get("buddy_visible", True) or not vd.get("has_buddy", True):
                logger.log("  [🌱成长] 旅行模块未开启 / 暂无 Buddy，跳过")
                return

        status = self._get("/v2/activity/growth/buddy/travel/status")
        if not (status and status.get("code") == 0):
            logger.log("  [🌱成长] 获取旅行状态失败")
            return
        sd = status.get("data", {})
        state = sd.get("state", "idle")
        daily_limit = sd.get("daily_limit_reached", False)
        arrive_at = sd.get("arrive_at", 0)
        server_now = sd.get("server_now", 0)

        if state == "arrived":
            logger.log("  [🌱成长] 🎁Buddy 已到达，领取旅行礼物...")
            resp = self._post("/v2/activity/growth/buddy/travel/claim", {})
            if resp and resp.get("code") == 0:
                data = resp.get("data", {})
                credit = data.get("reward_credit", 0)
                logger.log("  [🌱成长] 🎉领取礼物成功! +" + str(credit) + " 积分")
            elif resp:
                msg = resp.get("message", resp.get("msg", ""))
                logger.log("  [🌱成长] 领取礼物: code=" + str(resp.get("code", -1)) + ", msg=" + str(msg))
            else:
                logger.log("  [🌱成长] 领取礼物请求失败")
            return

        if state == "traveling":
            remain = max(0, arrive_at - server_now)
            logger.log("  [🌱成长] ⏳Buddy 旅行中，约 " + str(remain) + " 秒后到达，本次无需操作")
            return

        # state == idle -> 出发
        if daily_limit:
            logger.log("  [🌱成长] ℹ️今日旅行次数已用尽，跳过")
            return
        cfg = self._get("/v2/activity/growth/buddy/travel/config")
        loc_id = None
        if cfg and cfg.get("code") == 0:
            locs = cfg.get("data", {}).get("locations", [])
            if locs:
                loc_id = locs[0].get("id")
        if not loc_id:
            logger.log("  [🌱成长] 未获取到旅行目的地，跳过")
            return
        logger.log("  [🌱成长] 🚀派猫猫出发旅行 (location_id=" + str(loc_id) + ")...")
        resp = self._post("/v2/activity/growth/buddy/travel/depart", {"location_id": loc_id})
        if resp and resp.get("code") == 0:
            d = resp.get("data", {})
            aa = d.get("arrive_at", 0)
            sn = d.get("server_now", 0)
            remain = max(0, aa - sn)
            logger.log("  [🌱成长] ✅已出发，预计 " + str(remain) + " 秒后到达，下次运行自动领取礼物")
        elif resp:
            msg = resp.get("message", resp.get("msg", ""))
            logger.log("  [🌱成长] 出发: code=" + str(resp.get("code", -1)) + ", msg=" + str(msg))
        else:
            logger.log("  [🌱成长] 出发请求失败")

    # ==== Redeem ====
    def do_redeem(self, tier="", client_token=""):
        if not tier:
            return
        if not client_token:
            client_token = gen_client_token("redeem-" + tier)
        resp = self._post("/v2/activity/growth/redeem", {"tier": tier, "client_token": client_token})
        if resp:
            code = resp.get("code", -1)
            msg = resp.get("message", "")
            if code == 0:
                data = resp.get("data", {})
                credit = data.get("credit_granted", 0)
                energy = data.get("energy_granted", 0)
                chances = data.get("chances_granted", 0)
                logger.log("  [🌱成长] 🎉兑换成功! +" + str(credit) + " 积分, +" + str(energy) + " 能量, +" + str(chances) + " 抽奖次数")
                return True
            elif code == 409 or "duplicate" in str(msg):
                logger.log("  [🌱成长] ℹ️ 该档已兑换过 (409): " + str(tier))
                return "duplicate"
            elif code == 403 or "insufficient days" in str(msg):
                logger.log("  [🌱成长] ⏳天数不足，暂不可兑换 (403): " + str(tier))
                return "insufficient"
            else:
                logger.log("  [🌱成长] 兑换: code=" + str(code) + ", msg=" + str(msg))
                return False

    # ==== Makeup Card ====
    def use_makeup_card(self, target_date=""):
        if not target_date:
            target_date = date.today().strftime("%Y-%m-%d")
        resp = self._post("/v2/activity/growth/makeup-cards/use", {"target_date": target_date})
        if resp:
            code = resp.get("code", -1)
            msg = resp.get("message", "")
            if code == 0:
                logger.log("  [🌱成长] 补签成功: " + str(msg))
            else:
                logger.log("  [🌱成长] 补签: code=" + str(code) + ", msg=" + str(msg))

    # ==== Billing Daily Checkin ====
    def billing_checkin(self):
        resp = self._post("/v2/billing/meter/daily-checkin")
        if resp is None:
            logger.log("  [✅签到] 签到请求失败")
            return
        code = resp.get("code", -1)
        msg = resp.get("msg", resp.get("message", ""))
        data = resp.get("data", {})
        if code == 0 or code == 200 or "签到成功" in str(msg):
            credit = data.get("credit", 0)
            streak = data.get("streak_days", "?")
            logger.log("  [✅签到] ✅签到成功! +" + str(credit) + " 积分, 连续 " + str(streak) + " 天")
        elif code == 10001 or "已签到" in str(msg) or "请明天再来" in str(msg):
            logger.log("  [✅签到] 今日已签到")
        else:
            logger.log("  [✅签到] 签到结果: code=" + str(code) + ", msg=" + str(msg))

    # ==== Main Run ====
    def run(self):
        logger.log("━━━ 🌱成长中心 ━━━")
        profile = self.get_profile()
        if self._auth_ok is False:
            return

        self.get_streak()
        self.do_daily_sign()
        self.get_heatmap()
        self.get_energy()

        logger.log("━━━ 📋成长任务 ━━━")
        self.process_tasks()

        self.get_badges()
        self.do_lottery()
        self.open_buddy()
        self.get_buddy_info()

        # 网页「派猫猫旅行」：出发旅行 + 到达后自动领取礼物
        self.do_buddy_travel()

        # 网页「兑换奖励」：按连登档位自动兑换，无需兑换码
        self.do_redeem_by_streak()


# ============================================================
#  Account Processing & Environment Variable Parsing
# ============================================================

def process_account(idx, access_token="", cookie_str="", keycloak_str=""):
    logger.log(" ========== 账号 " + str(idx) + " ========== ")

    if not access_token:
        at, _, uid = discover_desktop_info()
        if at:
            access_token = at

    gs = WorkBuddyCheckin(access_token=access_token, cookie_str=cookie_str, keycloak_cookie_str=keycloak_str)
    gs.run()


def get_env(name):
    return os.environ.get(name, "").strip()


def parse_multi_env(prefix):
    items = []
    main = get_env(prefix)
    if main:
        items.extend([x.strip() for x in main.split("@") if x.strip()])
    i = 1
    while True:
        val = get_env(prefix + "_" + str(i))
        if not val:
            break
        items.append(val.strip())
        i += 1
    return items


def main():
    clean_proxy_env()

    access_tokens = parse_multi_env("WORKBUDDY_ACCESS_TOKEN")
    keycloaks = parse_multi_env("WORKBUDDY_KEYCLOAK")
    cookies = parse_multi_env("WORKBUDDY_COOKIE")

    if not access_tokens and not keycloaks and not cookies:
        at, _, _ = discover_desktop_info()
        if at:
            access_tokens.append(at)
            logger.log("  [🔐认证] 自动发现桌面端 accessToken")
        if not access_tokens:
            logger.log("⚠️ 未配置 WORKBUDDY_ACCESS_TOKEN / WORKBUDDY_KEYCLOAK / WORKBUDDY_COOKIE 环境变量")
            logger.log("")
            logger.log("🔑推荐方式 - Bearer Token (有效期约1年):")
            logger.log("  1. 安装并登录 WorkBuddy/CodeBuddy 桌面端")
            logger.log("  2. 找到配置文件 workbuddy-desktop-*.info")
            logger.log("     Windows: %USERPROFILE%\\Downloads\\workbuddy-desktop-*.info")
            logger.log("  3. 复制 auth.accessToken 的值 (以 eyJ 开头)")
            logger.log("  4. 设置: WORKBUDDY_ACCESS_TOKEN=<值>")
            logger.log("")
            logger.log("🔑备选方式 - Keycloak SSO Cookie (有效期约30天~1年):")
            logger.log("  1. 打开 https://www.workbuddy.cn/profile/growth-center 并登录")
            logger.log("  2. F12 -> Application -> Cookies -> https://www.workbuddy.cn")
            logger.log("  3. 筛选 Path 包含 /auth/realms/copilot/ 的 Cookie")
            logger.log("  4. 复制: AUTH_SESSION_ID / KC_RESTART / KEYCLOAK_IDENTITY / KEYCLOAK_SESSION")
            logger.log("  5. 拼接: AUTH_SESSION_ID=值; KC_RESTART=值; KEYCLOAK_IDENTITY=值; KEYCLOAK_SESSION=值")
            logger.log("  6. 设置: WORKBUDDY_KEYCLOAK=<拼接字符串>")
            logger.log("")
            logger.log("🔑备选方式 - 原始 Session Cookie (有效期短, 会过期):")
            logger.log("  1. F12 -> Network -> 刷新页面")
            logger.log("  2. 点击任意 growth 请求 -> 复制 Cookie 值")
            logger.log("  3. 设置: WORKBUDDY_COOKIE=<完整 Cookie 字符串>")
            logger.log("")
            logger.log("💻ACP 桌面任务 (需要本地 WorkBuddy 桌面端运行):")
            logger.log("  脚本自动发现守护进程")
            logger.log("  支持: 对话/专家/设计/灵感/模板/技能/自动化")
            send_notify("WorkBuddy 签到", "未配置环境变量，请检查青龙面板设置")
            return

    max_accounts = max(len(access_tokens), len(keycloaks), len(cookies))
    if max_accounts == 0:
        logger.log("⚠️ 环境变量为空")
        return

    for i in range(max_accounts):
        at = access_tokens[i] if i < len(access_tokens) else ""
        keycloak = keycloaks[i] if i < len(keycloaks) else ""
        cookie = cookies[i] if i < len(cookies) else ""
        process_account(i + 1, access_token=at, cookie_str=cookie, keycloak_str=keycloak)
        if i < max_accounts - 1:
            time.sleep(2)

    result = logger.result()
    send_notify("WorkBuddy 签到", result)


if __name__ == "__main__":
    main()

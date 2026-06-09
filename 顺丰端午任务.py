#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顺丰端午 2026 自动任务

环境变量：
  sfsyUrl                URL，多个账号用 & 分隔
  SFBF                  并发数量，默认1，最大20
  SF_DRAGONBOAT_LOTTERY  金币抽奖开关，1=开启，默认关闭

"""

# 说明：今日奖品汇总会自动过滤 12 元以下垃圾券。
import hashlib
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Optional
from urllib.parse import quote, unquote

import requests


print_lock = Lock()
reward_lock = Lock()
lottery_lock = Lock()
lottery_records: List[Dict[str, str]] = []
surprise_counts: Dict[str, int] = {}
MAX_SURPRISE_PER_ACCOUNT = 3
SUMMARY_EXCLUDE_PATTERNS = [
    r"9折寄件券",
    r"(?<!1)2元寄件券",
    r"92折寄件券",
    r"2元寄件券[（(]满20元可用[）)]",
    r"海底捞7\.9折夜宵券",
    r"5元寄件券",
]
LOW_VALUE_COUPON_LIMIT = 12


@dataclass
class Config:
    APP_NAME: str = "顺丰端午"
    VERSION: str = "1.0.0"
    ENV_NAME: str = "sfsyUrl"
    TOKEN: str = "wwesldfs29aniversaryvdld29"
    SYS_CODE: str = "MCS-MIMP-CORE"
    ACTIVITY_CODE: str = "DRAGONBOAT_2026"
    CHANNEL: str = "26duanwutanchuang4"
    TIMEOUT: int = 15


config = Config()
BASE = "https://mcs-mimp-web.sf-express.com"
RUM_URL = "https://fee-gw.sf-express.com/report/rum"

CONCURRENT_NUM = int(os.getenv("SFBF", "1") or "1")
if CONCURRENT_NUM > 20:
    CONCURRENT_NUM = 20
elif CONCURRENT_NUM < 1:
    CONCURRENT_NUM = 1

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 "
    "MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI "
    "MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) "
    "UnifiedPCWindowsWechat(0xf2541a1b) XWEB/19895 "
    "miniProgram/wxd4185d00bf7e08ac"
)

REFERER = (
    "https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/dragonBoat2026"
    "?path=/origin/a/mimp-activity/dragonBoat2026&supportShare=YES&from=26duanwutanchuang4"
)
BIZ_CODE = '{"path":"/origin/a/mimp-activity/dragonBoat2026","supportShare":"YES","from":"26duanwutanchuang4"}'
UCMP_ENTRY = "https://ucmp.sf-express.com/wechat-act3/weixin/activity/sfnewactivity"

TASK_LIST = "/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList"
DRAGON_INDEX = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026IndexService~index"
FINISH_TASK = "/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask"
FETCH_REWARD = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026TaskService~fetchTaskReward"
QUERY_STATUS = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026ZongziService~queryStatus"
CRUSH = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026ZongziService~crush"
EXTRA_REWARD_CARDS = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026ZongziService~queryExtraRewardCards"
LOTTERY_DRAW = "/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2026LotteryService~prizeDraw"
WECHAT_SIGNATURE = "/mcs-mimp/share/weChat/signature"

BUILTIN_ASSIST_TARGETS = [
    "4866EA6422D64E3EA688336F9055650F",
    "0477C90387D2455F91D2415C5EE881A3",
    "AE6A6F2A157147799A7B08E80490EB06",
    "BDD153450098476A90E318F9477F7EF7",
    "E27F9E034105473E9E5B7AB8D2101818",
]


def log(msg: str) -> None:
    with print_lock:
        print(msg, flush=True)


def mask_phone(text: str) -> str:
    return re.sub(r"(1\d{2})\d{4}(\d{4})", r"\1****\2", str(text or ""))


def reward_text(items: List[Dict[str, Any]], sep: str = "，") -> str:
    parts = []
    for item in items or []:
        currency = item.get("currency") or item.get("accountType") or "-"
        amount = item.get("amount") or item.get("balance") or 0
        task_type = item.get("taskType")
        suffix = f" ({task_type})" if task_type else ""
        parts.append(f"{currency} x{amount}{suffix}")
    return sep.join(parts)


def parse_cookie(cookie: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in unquote(str(cookie or "")).split(";"):
        if "=" not in part:
            continue
        k, v = part.strip().split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load_cookies() -> List[str]:
    raw = (os.getenv(config.ENV_NAME) or "").strip()
    if not raw:
        return []
    return [x.strip() for x in re.split(r"@@@|&|[\r\n]+", raw) if x.strip()]


def lottery_enabled() -> bool:
    return (os.getenv("SF_DRAGONBOAT_LOTTERY") or "").strip() == "1"


def add_lottery_record(account: str, gift: str, detail: str, source: str = "金币抽奖") -> None:
    with lottery_lock:
        lottery_records.append({
            "date": time.strftime("%Y-%m-%d"),
            "account": account,
            "gift": gift,
            "detail": detail,
            "source": source,
        })


def add_surprise_record(account: str, award: Dict[str, Any], total_crush_times: int) -> Optional[str]:
    if not award:
        return None
    with lottery_lock:
        current = surprise_counts.get(account, 0)
        if current >= MAX_SURPRISE_PER_ACCOUNT:
            return None
        surprise_counts[account] = current + 1

    name = award.get("couponName") or award.get("productName") or award.get("productCode") or "未知奖品"
    amount = award.get("amount") or 1
    expire = award.get("expirationDate")
    expire_text = f"，有效期至{expire}" if expire else ""
    detail = f"x{amount}{expire_text}，已砸{total_crush_times}次，惊喜礼盒{surprise_counts[account]}/{MAX_SURPRISE_PER_ACCOUNT}"
    add_lottery_record(account, name, detail, "惊喜礼盒")
    return f"惊喜礼盒: {name} {detail}"


def is_low_value_coupon(prize_text: str) -> bool:
    text = str(prize_text or "")
    if not any(word in text for word in ("券", "红包")):
        return False
    for value in re.findall(r"(\d+(?:\.\d+)?)\s*元", text):
        try:
            if float(value) < LOW_VALUE_COUPON_LIMIT:
                return True
        except Exception:
            continue
    return False


def print_lottery_summary() -> None:
    today = time.strftime("%Y-%m-%d")
    today_records = []
    for item in lottery_records:
        if item.get("date") != today:
            continue
        prize_text = f"{item.get('gift', '')} {item.get('detail', '')}"
        if any(re.search(pattern, prize_text) for pattern in SUMMARY_EXCLUDE_PATTERNS):
            continue
        if is_low_value_coupon(prize_text):
            continue
        today_records.append(item)
    log("=" * 50)
    log(f"🎁 今日奖品汇总（{today}）")
    if not today_records:
        log("📭 暂无奖品记录")
    else:
        for idx, item in enumerate(today_records, 1):
            detail = f"，{item['detail']}" if item.get("detail") else ""
            source = f"[{item.get('source', '奖品')}]"
            log(f"{idx}. {source} {item['account']}: {item['gift']}{detail}")
    log("=" * 50)


def sign_headers() -> Dict[str, str]:
    ts = str(int(time.time() * 1000))
    raw = f"token={config.TOKEN}&timestamp={ts}&sysCode={config.SYS_CODE}"
    return {
        "sysCode": config.SYS_CODE,
        "timestamp": ts,
        "signature": hashlib.md5(raw.encode()).hexdigest(),
    }


class DragonBoatClient:
    def __init__(self, account_value: str, index: int):
        self.account_value = account_value
        self.cookie = account_value
        self.entry_url = ""
        self.is_url_login = False
        self.index = index
        self.cookie_map = parse_cookie(account_value)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json",
            "channel": config.CHANNEL,
            "platform": "MINI_PROGRAM",
            "Origin": BASE,
            "Referer": self.build_referer(),
        })
        self.login(account_value)

    def sync_cookie_map(self) -> None:
        cookies = self.session.cookies.get_dict()
        useful_keys = {"JSESSIONID", "sessionId", "_login_user_id_", "_login_mobile_"}
        if cookies and any(k in cookies for k in useful_keys):
            self.cookie_map.update(cookies)
            self.cookie = "; ".join(f"{k}={v}" for k, v in self.cookie_map.items())
            self.session.headers.update({"Cookie": self.cookie})

    def login(self, account_value: str) -> None:
        decoded = unquote(str(account_value or "").strip())
        if decoded.startswith("http://") or decoded.startswith("https://"):
            self.is_url_login = True
            self.entry_url = decoded
            self.session.get(decoded, timeout=config.TIMEOUT, allow_redirects=True)
            self.sync_cookie_map()
        else:
            self.cookie_map = parse_cookie(decoded)
            self.cookie = decoded
            self.session.headers.update({"Cookie": self.cookie})
            for k, v in self.cookie_map.items():
                self.session.cookies.set(k, v, domain="mcs-mimp-web.sf-express.com")
        if self.cookie:
            self.session.headers.update({"Cookie": self.cookie})
        self.session.headers.update({"Referer": self.build_referer()})

    def build_referer(self) -> str:
        mobile = self.cookie_map.get("_login_mobile_", "")
        user_id = self.cookie_map.get("_login_user_id_", "")
        if mobile or user_id:
            return (
                "https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/dragonBoat2026"
                f"?mobile={mobile}&userId={user_id}"
                "&path=/origin/a/mimp-activity/dragonBoat2026&supportShare=YES&from=26duanwutanchuang4"
            )
        return REFERER

    def choose_assist_target(self) -> str:
        user_id = self.user_id
        targets = [x for x in BUILTIN_ASSIST_TARGETS if x and x != user_id]
        if not targets:
            return ""
        seed = user_id or self.name or str(self.index)
        idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(targets)
        return targets[idx]

    def ordered_assist_targets(self) -> List[str]:
        user_id = self.user_id
        return [x for x in BUILTIN_ASSIST_TARGETS if x and x != user_id]

    def build_assist_referer(self, invite_user_id: str) -> str:
        base = self.build_referer()
        if "inviteUserId=" in base:
            base = re.sub(
                r"([?&])inviteUserId=[^&]*",
                lambda m: f"{m.group(1)}inviteUserId={invite_user_id}",
                base,
            )
        else:
            sep = "&" if "?" in base else "?"
            base = f"{base}{sep}inviteUserId={invite_user_id}"
        if "type=" in base:
            base = re.sub(r"([?&])type=[^&]*", lambda m: f"{m.group(1)}type=task_invite", base)
        else:
            base += "&type=task_invite"
        return base

    def builtin_assist_once(self) -> None:
        for invite_user_id in self.ordered_assist_targets():
            referer = self.build_assist_referer(invite_user_id)
            try:
                data = self.post(
                    DRAGON_INDEX,
                    {"inviteType": 1, "inviteUserId": invite_user_id},
                    referer=referer,
                )
                if data.get("success"):
                    return
                msg = str(data.get("errorMessage") or data.get("msg") or "")
                if "已助力" in msg or "已达" in msg or "上限" in msg or "已满" in msg:
                    continue
                return
            except Exception:
                continue

    def build_ucmp_entry(self) -> str:
        suuid = hashlib.md5(f"{time.time()}-{random.random()}-{self.index}".encode()).hexdigest()
        return (
            f"{UCMP_ENTRY}?bizCode={quote(BIZ_CODE, safe='')}"
            f"&citycode=&cityname=&miniProgramAd=1&wxapp-version=V17.61&suuid={suuid}"
        )

    def enter_activity(self, silent: bool = False) -> bool:
        referer_url = self.build_referer()
        try:
            entry_url = referer_url
            if self.is_url_login:
                if self.entry_url.startswith("https://ucmp.sf-express.com/") or "/mcs-mimp/share/weChat/activityRedirect" in self.entry_url:
                    entry_url = self.entry_url
                else:
                    entry_url = self.build_ucmp_entry()
                self.session.get(
                    entry_url,
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-User": "?1",
                        "Sec-Fetch-Dest": "document",
                    },
                    timeout=config.TIMEOUT,
                    allow_redirects=True,
                )
                self.sync_cookie_map()
            resp = self.session.get(
                referer_url,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Referer": entry_url,
                },
                timeout=config.TIMEOUT,
                allow_redirects=True,
            )
            self.sync_cookie_map()
            self.session.headers.update({"Referer": referer_url})
            if not silent:
                log(f"🚪 模拟进入活动: HTTP={resp.status_code}")
            return 200 <= resp.status_code < 400
        except Exception as e:
            if not silent:
                log(f"⚠️ 模拟进入活动失败: {e}")
            return False

    def report_pageview(self) -> None:
        user_id = self.cookie_map.get("_login_user_id_", "") or self.session.cookies.get("_login_user_id_", "")
        href = self.build_referer()
        now_ms = int(time.time() * 1000)
        event_id = hashlib.md5(f"{user_id}-{now_ms}-{random.random()}".encode()).hexdigest()
        payload = {
            "data": [{
                "sdkInfo": {"sdkVersion": "1.0.0"},
                "userInfo": {
                    "userId": user_id,
                    "userTrackId": hashlib.md5(f"{user_id}-track".encode()).hexdigest(),
                },
                "timeInfo": {"time": now_ms, "clientTime": now_ms},
                "appInfo": {"appId": "637b5859cab6b3d12cd20489"},
                "pageInfo": {
                    "href": href,
                    "baseUrl": "https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/dragonBoat2026",
                    "title": "",
                },
                "eventInfo": {
                    "category": "precollect",
                    "type": "pageview",
                    "eventID": event_id,
                    "eventData": {"level": "critical", "pathname": "/dragonBoat2026"},
                },
            }]
        }
        try:
            self.session.post(
                RUM_URL,
                headers={
                    "Content-Type": "text/plain;charset=UTF-8",
                    "Accept": "*/*",
                    "Origin": BASE,
                    "Referer": "https://mcs-mimp-web.sf-express.com/",
                },
                data=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                timeout=config.TIMEOUT,
            )
        except Exception:
            pass

    def wechat_signature(self, silent: bool = False) -> Dict[str, Any]:
        href = self.build_referer()
        data = self.post(WECHAT_SIGNATURE, {"url": href})
        if not data.get("success"):
            if not silent:
                log(f"⚠️ 微信签名初始化失败: {data.get('errorMessage') or json.dumps(data, ensure_ascii=False)[:220]}")
            return {}
        return data.get("obj") or {}

    def activity_index(self, silent: bool = False, referer: str = "") -> Dict[str, Any]:
        data = self.post(DRAGON_INDEX, {}, referer=referer)
        if not data.get("success"):
            if not silent:
                log(f"⚠️ 活动首页初始化失败: {data.get('errorMessage') or json.dumps(data, ensure_ascii=False)[:220]}")
            return {}
        return data.get("obj") or {}

    def warmup_activity(self, silent: bool = False) -> None:
        self.enter_activity(silent=True)
        time.sleep(random.uniform(0.4, 0.9))
        try:
            self.wechat_signature(silent=True)
            time.sleep(random.uniform(0.2, 0.5))
            self.report_pageview()
            time.sleep(random.uniform(0.2, 0.5))
            self.activity_index(silent=True)
            time.sleep(random.uniform(0.2, 0.5))
            self.task_list(silent=True)
            time.sleep(random.uniform(0.3, 0.7))
            self.query_status(silent=True)
            time.sleep(random.uniform(0.3, 0.7))
            self.query_extra_reward_cards(silent=True)
            if not silent:
                log("🚪 模拟进入活动: 完成页面/任务/余额预热")
        except Exception as e:
            if not silent:
                log(f"⚠️ 活动预热失败: {e}")

    @property
    def name(self) -> str:
        phone = self.cookie_map.get("_login_mobile_", "")
        user_id = self.cookie_map.get("_login_user_id_", "")
        return mask_phone(phone) or (user_id[:6] + "***" if user_id else f"账号{self.index}")

    @property
    def user_id(self) -> str:
        return self.cookie_map.get("_login_user_id_", "") or self.session.cookies.get("_login_user_id_", "")

    def post(self, path: str, body: Optional[Dict[str, Any]] = None, referer: str = "") -> Dict[str, Any]:
        url = BASE + path
        headers = sign_headers()
        if referer:
            headers["Referer"] = referer
        resp = self.session.post(
            url,
            headers=headers,
            data=json.dumps(body if body is not None else {}, ensure_ascii=False, separators=(",", ":")),
            timeout=config.TIMEOUT,
        )
        text = resp.text
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"{path} HTTP={resp.status_code} 非JSON: {text[:200]}")
        if resp.status_code != 200:
            raise RuntimeError(f"{path} HTTP={resp.status_code}: {text[:300]}")
        return data

    def task_list(self, silent: bool = False) -> List[Dict[str, Any]]:
        data = self.post(TASK_LIST, {
            "activityCode": config.ACTIVITY_CODE,
            "channelType": "MINI_PROGRAM",
        })
        if not data.get("success"):
            if not silent:
                log(f"[{self.name}] 任务列表失败: {json.dumps(data, ensure_ascii=False)[:300]}")
            return []
        tasks = data.get("obj") or []
        return tasks if isinstance(tasks, list) else []

    def finish_task(self, task_code: str) -> bool:
        data = self.post(FINISH_TASK, {"taskCode": task_code})
        ok = bool(data.get("success") and data.get("obj") is True)
        log(f"✅ 完成浏览任务: {'成功' if ok else '失败'}")
        if not ok:
            log(f"⚠️ 完成返回: {json.dumps(data, ensure_ascii=False)[:300]}")
        return ok

    def fetch_reward_once(self) -> Dict[str, Any]:
        data = self.post(FETCH_REWARD, {
            "channelType": "MINI_PROGRAM",
            "activityCode": config.ACTIVITY_CODE,
        })
        return data

    def fetch_reward(self) -> Dict[str, Any]:
        with reward_lock:
            last_data: Dict[str, Any] = {}
            self.warmup_activity(silent=True)
            time.sleep(random.uniform(0.5, 1.0))
            for attempt in range(1, 3):
                data = self.fetch_reward_once()
                last_data = data
                if data.get("success"):
                    received = ((data.get("obj") or {}).get("receivedAccountList") or [])
                    if received:
                        log(f"✅ 领取奖励: {reward_text(received)}")
                    else:
                        log("📭 领取奖励: 暂无可领取")
                    time.sleep(random.uniform(1.5, 2.5))
                    return data

                err_code = str(data.get("errorCode") or "")
                err_msg = str(data.get("errorMessage") or "")
                if err_code == "100019" or "火爆" in err_msg:
                    if attempt < 2:
                        wait = random.uniform(1.5, 2.5)
                        self.warmup_activity(silent=True)
                        time.sleep(wait)
                        continue
                log(f"⚠️ 领取奖励失败: {err_msg or json.dumps(data, ensure_ascii=False)[:220]}")
                return {}

            err_msg = str(last_data.get("errorMessage") or "")
            log(f"⚠️ 领取奖励失败: {err_msg or '活动太火爆了，请稍后再试试~'}")
            return {}

    def query_status(self, silent: bool = False) -> Dict[str, int]:
        data = self.post(QUERY_STATUS, {})
        balances: Dict[str, int] = {}
        if not data.get("success"):
            if not silent:
                log(f"⚠️ 查询状态失败: {json.dumps(data, ensure_ascii=False)[:300]}")
            return balances
        obj = data.get("obj") or {}
        for item in obj.get("currentAccountList") or []:
            currency = str(item.get("currency") or "")
            try:
                balances[currency] = int(item.get("balance") or 0)
            except Exception:
                balances[currency] = 0
        balances["_totalCrushTimes"] = int(obj.get("totalCrushTimes") or 0)
        return balances

    def crush_once(self, crush_no: int) -> Dict[str, int]:
        data = self.post(CRUSH, {})
        balances: Dict[str, int] = {}
        if not data.get("success"):
            log(f"⚠️ 砸金粽失败，停止: {data.get('errorMessage') or json.dumps(data, ensure_ascii=False)[:220]}")
            return balances
        obj = data.get("obj") or {}
        coin_add = 0
        other_rewards = []
        total_crush_times = int(obj.get("totalCrushTimes") or 0)
        received = obj.get("receivedAccountList") or []
        for item in received:
            currency = str(item.get("currency") or item.get("accountType") or "")
            amount = item.get("amount") or item.get("balance") or 0
            if currency == "GOLD_COIN":
                try:
                    coin_add += int(amount or 0)
                except Exception:
                    pass
            else:
                name = item.get("currencyName") or item.get("name") or item.get("giftBagName") or currency or "未知奖励"
                reward = f"{name} x{amount}"
                other_rewards.append(reward)
                add_lottery_record(self.name, reward, "砸金粽获得", "砸金粽")
        for item in obj.get("currentAccountList") or []:
            currency = str(item.get("currency") or "")
            try:
                balances[currency] = int(item.get("balance") or 0)
            except Exception:
                balances[currency] = 0
        surprise_text = None
        if obj.get("extraCardType") == "SURPRISE":
            surprise_text = add_surprise_record(self.name, obj.get("award") or {}, total_crush_times)
        reward_parts = []
        if coin_add:
            reward_parts.append(f"+{coin_add}金币")
        reward_parts.extend(other_rewards)
        if surprise_text:
            reward_parts.append(surprise_text)
        reward_display = "，".join(reward_parts) if reward_parts else "无奖励"
        if reward_parts:
            log(f"🪙 砸粽第{crush_no}次: {reward_display}，剩余金粽{balances.get('GOLD_ZONGZI', 0)}，当前金币{balances.get('GOLD_COIN', 0)}")
        else:
            log(f"🪙 砸粽第{crush_no}次: 无奖励，剩余金粽{balances.get('GOLD_ZONGZI', 0)}，当前金币{balances.get('GOLD_COIN', 0)}")
        return balances

    def query_extra_reward_cards(self, silent: bool = False) -> None:
        data = self.post(EXTRA_REWARD_CARDS, {})
        if not data.get("success"):
            return
        cards = data.get("obj") or []
        if not cards:
            return
        if silent:
            return
        parts = []
        for item in cards:
            extra_type = item.get("extraType", "-")
            parts.append(str(extra_type))
        log(f"🏷️ 额外奖励卡: {', '.join(parts)}")

    def prize_draw_once(self) -> Dict[str, Any]:
        data = self.post(LOTTERY_DRAW, {"ruleType": "LOTTERY", "shouldNum": 2000})
        if not data.get("success"):
            log(f"⚠️ 金币抽奖失败: {data.get('errorMessage') or json.dumps(data, ensure_ascii=False)[:220]}")
            return {}

        obj = data.get("obj") or {}
        gift_name = obj.get("giftBagName") or "未知奖品"
        worth = obj.get("giftBagWorth")
        products = obj.get("productDTOList") or []
        detail_parts = []
        for product in products:
            name = product.get("couponName") or product.get("productName") or product.get("productCode") or "-"
            amount = product.get("amount") or 1
            expire = product.get("expirationDate")
            expire_text = f"，有效期至{expire}" if expire else ""
            detail_parts.append(f"{name} x{amount}{expire_text}")
        detail = "；".join(detail_parts)
        worth_text = f"，价值{worth}" if worth is not None else ""
        if detail:
            log(f"🎰 金币抽奖: {gift_name}{worth_text}，{detail}")
        else:
            log(f"🎰 金币抽奖: {gift_name}{worth_text}")
        add_lottery_record(self.name, f"{gift_name}{worth_text}", detail)
        return data

    def handle_lottery(self, coin: int) -> None:
        if coin < 2000:
            log(f"⚠️ 金币不足: {coin}/2000，暂不能抽奖")
            return
        if not lottery_enabled():
            return

        self.warmup_activity(silent=True)
        time.sleep(random.uniform(0.8, 1.5))
        self.prize_draw_once()
        time.sleep(random.uniform(0.8, 1.5))
        balances = self.query_status(silent=True)
        new_coin = int(balances.get("GOLD_COIN", 0) or 0)
        log(f"🪙 抽奖后金币: {new_coin}")

    def run_browse_task(self) -> None:
        tasks = self.task_list()
        browse = next((x for x in tasks if x.get("taskType") == "BROWSE_LIFE_SERVICE"), None)
        if not browse:
            log("⚠️ 浏览任务: 未找到看看生活服务任务")
            return

        task_code = str(browse.get("taskCode") or "")
        status = browse.get("status")
        process = browse.get("process")
        can_receive = int(browse.get("canReceiveTokenNum") or 0)

        if status == 2 and task_code:
            self.finish_task(task_code)
            time.sleep(random.uniform(0.8, 1.5))
            tasks = self.task_list()
            browse = next((x for x in tasks if x.get("taskType") == "BROWSE_LIFE_SERVICE"), browse)
            can_receive = int(browse.get("canReceiveTokenNum") or 0)
            process = browse.get("process")

        log(f"📝 累计任务进度: {process}（2个任务得1，5个任务得3，8个任务得5）")

        if can_receive > 0 or browse.get("status") == 1:
            self.fetch_reward()
        else:
            log("📭 领取奖励: 浏览任务暂无可领奖励")

    def crush_all(self) -> None:
        balances = self.query_status()
        zongzi = int(balances.get("GOLD_ZONGZI", 0) or 0)
        log(f"🪙 初始余额: 金币{balances.get('GOLD_COIN', 0)} 金粽{zongzi} 已砸{balances.get('_totalCrushTimes', 0)}次")
        max_crush = max(0, min(zongzi, int(os.getenv("SF_DRAGONBOAT_MAX_CRUSH", "20") or "20")))
        if max_crush <= 0:
            log("⚠️ 金粽不足，停止")
        else:
            for i in range(max_crush):
                balances = self.crush_once(i + 1)
                time.sleep(random.uniform(0.8, 1.6))
                if int(balances.get("GOLD_ZONGZI", 0) or 0) <= 0:
                    break

        coin = int((balances or {}).get("GOLD_COIN", 0) or 0)
        self.handle_lottery(coin)

    def run(self) -> None:
        log(f"========== 账号{self.index} {self.name} ==========")
        self.builtin_assist_once()
        self.warmup_activity(silent=True)
        time.sleep(random.uniform(0.5, 1.2))
        self.run_browse_task()
        self.crush_all()
        self.query_extra_reward_cards()


def main() -> None:
    cookies = load_cookies()
    if not cookies:
        log(f"未配置账号，请设置环境变量 {config.ENV_NAME}")
        log("格式与顺丰.py一致：只保留 sfsyUrl，多个账号用 & 分隔")
        return

    log("=" * 50)
    log(f"🎉 {config.APP_NAME} v{config.VERSION}")
    log(f"📱 共获取到 {len(cookies)} 个账号")
    log(f"⚙️ 并发数量: {CONCURRENT_NUM}")
    log(f"🎰 金币抽奖: {'开启' if lottery_enabled() else '关闭'}")
    log("=" * 50)

    clients: List[DragonBoatClient] = []
    for idx, cookie in enumerate(cookies, 1):
        try:
            clients.append(DragonBoatClient(cookie, idx))
        except Exception as e:
            log(f"[账号{idx}] 运行异常: {e}")

    def run_one(client: DragonBoatClient) -> None:
        try:
            client.run()
        except Exception as e:
            log(f"[账号{client.index}] 运行异常: {e}")

    if CONCURRENT_NUM <= 1:
        log("🔄 使用串行模式执行...")
        for idx, client in enumerate(clients, 1):
            run_one(client)
            if idx != len(clients):
                time.sleep(random.uniform(2, 4))
    else:
        log("🚀 使用并发模式执行...")
        with ThreadPoolExecutor(max_workers=CONCURRENT_NUM) as executor:
            futures = [
                executor.submit(run_one, client)
                for client in clients
            ]
            for future in as_completed(futures):
                future.result()

    print_lottery_summary()


if __name__ == "__main__":
    main()

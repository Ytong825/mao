"""
xxx阅读脚本优化版
饱了么脚本交流群：476250706
--------
1. 微信打开链接 http://65708.2172ef2.gmachd.cn/xiaoxinxin/wode/7335cadc8a6d796f998d1cd669f95d21?myid=ef2
2. 打开阅读任务页，点击「点击开始」进入文章页
3. 右上角「···」→复制链接
4. 从链接提取 rid=xxx 后面的值

环境变量: blmyd — 多账号换行分隔，每行一个 rid
"""
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

# --------------------- 配置 ---------------------
TOTAL_ROUNDS = 240
BATCH_SIZE = 40
BATCH_REST = 3600                # 每 40 轮休息 1 小时
ERR407_BASE = 60                 # 407 基础休息分钟
ERR407_DELTA = (1, 2)            # 407 额外随机分钟
WATCH = (8, 15)                  # 模拟阅读秒数
COOLDOWN = (10, 22)              # 轮间等待秒数
FAIL_DELAY = (5, 10)             # 失败后等待秒数
TIMEOUT = 10
RETRIES = 2

UA_FILE = "ua_cache.json"
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781 WindowsWechat XWEB/19841 Flue",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d30) NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.126 Mobile Safari/537.36 XWEB/5159219 MMWEBSDK/20230701 MicroMessenger/8.0.39.2405(0x2800255C) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro Build/UD1A.230803.041; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.144 Mobile Safari/537.36 XWEB/6531203 MMWEBSDK/20240201 MicroMessenger/8.0.47.2500(0x28002F33) WeChat/arm64 Weixin NetType/4G Language/zh_CN",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/WIFI Language/zh_CN",
]

BASE_URL = "http://r.myexst.top"
STATIC_REFERERS = [f"{BASE_URL}/xiaoxinxin/home.html?ysi=0"]

_print_lock = threading.Lock()
_write_lock = threading.Lock()


def log(tag: str, msg: str):
    """线程安全的统一日志输出"""
    ts = datetime.now().strftime("%H:%M:%S")
    with _print_lock:
        print(f"[{ts}] {tag} {msg}")


# --------------------- UA 缓存 ---------------------
def _load_ua_cache() -> dict:
    if not os.path.exists(UA_FILE):
        return {}
    try:
        with open(UA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_ua_cache(cache: dict):
    with _write_lock:
        try:
            with open(UA_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except IOError:
            pass


_ua_cache = _load_ua_cache()


# --------------------- 账号读取 ---------------------
def load_accounts() -> list:
    """从环境变量 blmyd 读取所有账号（换行分隔）"""
    raw = os.environ.get("blmyd", "").strip()
    if not raw:
        return []
    rids = [line.strip() for line in raw.splitlines() if line.strip()]
    changed = False
    for rid in rids:
        if rid not in _ua_cache:
            _ua_cache[rid] = random.choice(UA_POOL)
            changed = True
    if changed:
        _save_ua_cache(_ua_cache)
    return rids


# --------------------- 步骤执行 ---------------------
class StepError(Exception):
    """网络步骤失败（已重试）"""


class RateLimitError(Exception):
    """407 风控"""


def _retry(tag: str, name: str, action, retries: int = RETRIES):
    """带重试的 HTTP 调用，失败抛出 StepError"""
    for attempt in range(retries):
        try:
            return action()
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                log(tag, f"{name} 超时")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            if attempt == retries - 1:
                log(tag, f"{name} 连接失败")
            time.sleep(3)
        except Exception as exc:
            log(tag, f"{name} 异常: {exc}")
            break
    raise StepError()


# --------------------- 单账号任务 ---------------------
def run_one(rid: str, idx: int):
    sess = requests.Session()
    ua = _ua_cache[rid]
    tag = f"[{idx:02d}]"

    duliks_url = f"{BASE_URL}/xiaoxinxin/duliks"
    redirect_url = f"{BASE_URL}/x/r?rid={rid}"
    jinright_url = f"{BASE_URL}/xiaoxinxin/jinright"
    dudu_url = f"{BASE_URL}/xiaoxinxin/dudu"
    referers = [*STATIC_REFERERS, redirect_url, jinright_url]

    def headers():
        return {
            "User-Agent": ua,
            "Referer": random.choice(referers),
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "Android",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
        }

    log(tag, f"启动，目标 {TOTAL_ROUNDS} 轮")
    round_num = 0

    while round_num < TOTAL_ROUNDS:
        watch = random.randint(*WATCH)
        ts = int(time.time() * 1000)

        try:
            # 1. duliks
            _retry(tag, "duliks", lambda: sess.post(
                duliks_url,
                headers={**headers(), "Content-Type": "application/x-www-form-urlencoded"},
                timeout=TIMEOUT,
            ))
            time.sleep(random.uniform(1.5, 3))

            # 2. redirect
            _retry(tag, "redirect", lambda: sess.get(
                redirect_url, headers=headers(), timeout=TIMEOUT,
            ))
            time.sleep(watch)

            # 3. jinright
            _retry(tag, "jinright", lambda: sess.get(
                jinright_url, headers=headers(),
                params={"rid": rid, "time": 22, "timestamp": ts},
                timeout=TIMEOUT,
            ))
            time.sleep(random.uniform(1, 2))

            # 4. dudu
            resp = _retry(tag, "dudu", lambda: sess.get(
                dudu_url, headers=headers(),
                params={"rid": rid, "time": ts, "psgn": 168, "vs": 1002},
                timeout=TIMEOUT,
            ))
            data = resp.json()
            if data.get("errcode") == 407:
                raise RateLimitError()

        except StepError:
            time.sleep(random.uniform(*FAIL_DELAY))
            continue
        except RateLimitError:
            rest = (ERR407_BASE + random.randint(*ERR407_DELTA)) * 60
            log(tag, f"407 风控，休息 {rest // 60} 分钟")
            time.sleep(rest)
            continue
        except (requests.RequestException, json.JSONDecodeError, ValueError) as exc:
            log(tag, f"解析异常: {exc}")
            time.sleep(random.uniform(*FAIL_DELAY))
            continue

        round_num += 1
        delay = random.randint(*COOLDOWN)
        log(tag, f"{round_num:03d}/{TOTAL_ROUNDS} 阅读成功，等待 {delay}s")

        if round_num % BATCH_SIZE == 0 and round_num < TOTAL_ROUNDS:
            log(tag, f"批次休息 {BATCH_REST // 60} 分钟")
            time.sleep(BATCH_REST)
        else:
            time.sleep(delay)

    log(tag, f"完成 {TOTAL_ROUNDS} 轮")


# --------------------- 入口 ---------------------
def main():
    accounts = load_accounts()
    if not accounts:
        log("MAIN", "未读取到环境变量 blmyd")
        log("MAIN", "macOS/Linux: export blmyd=$'rid1\\nrid2'")
        log("MAIN", "Windows:   set blmyd=rid1 换行分隔多个值")
        return 1

    log("MAIN", "=" * 50)
    log("MAIN", f"启动 {len(accounts)} 账号 × {TOTAL_ROUNDS} 轮")
    log("MAIN", "=" * 50)

    with ThreadPoolExecutor(max_workers=len(accounts)) as pool:
        futures = [pool.submit(run_one, rid, i + 1) for i, rid in enumerate(accounts)]
        for fut in futures:
            try:
                fut.result()
            except Exception as exc:
                log("MAIN", f"线程异常: {exc}")

    log("MAIN", "=" * 50)
    log("MAIN", "全部任务结束")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

#脚本介绍
#变量步骤：微信打开链接http://76fa0.84110d5.jwqogt.cn/xiaoxinxin/wode/35eb75ec9f877e34d41c2d7cfd7d2390?myid=0d5
# 1.打开阅读任务页，点击「点击开始」进入文章页
# 2.右上角「···」→复制链接
# 3.从链接提取 rid=xxx 后面的值，如果不加更改变量
#冷却一次，需要更改一下变量，更新了域名，现在可以正常使用
import time
import random
import os
import json
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
# ===================== 配置 =====================
MAX_WORKERS = 30
TOTAL_ROUNDS = 240
BATCH_ROUNDS = 40
BATCH_REST = 3600       # 每40轮休息1小时
ERR407_REST = 3600      # 407基础休息60分钟
UA_SAVE_FILE = "ua_cache.json"
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781 WindowsWechat XWEB/19841 Flue",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d30) NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/113.0.5672.126 Mobile Safari/537.36 XWEB/5159219 MMWEBSDK/20230701 MicroMessenger/8.0.39.2405(0x2800255C) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN"
]
# 线程安全锁，防止日志乱序
log_lock = threading.Lock()
# 加载历史UA
ACCOUNT_UA_MAP = {}
if os.path.exists(UA_SAVE_FILE):
    with open(UA_SAVE_FILE, "r", encoding="utf-8") as f:
        ACCOUNT_UA_MAP = json.load(f)
# ===================== 读取账号 =====================
def get_all_rids():
    accounts = []
    for i in range(1, MAX_WORKERS + 1):
        rid = os.environ.get(f"od{i}", "").strip()
        if rid:
            accounts.append(rid)
            if rid not in ACCOUNT_UA_MAP:
                ACCOUNT_UA_MAP[rid] = random.choice(UA_POOL)
                with open(UA_SAVE_FILE, "w", encoding="utf-8") as f:
                    json.dump(ACCOUNT_UA_MAP, f, ensure_ascii=False, indent=2)
    return accounts
# ===================== 单账号任务 =====================
def run_single_account(rid, account_num):
    session = requests.Session()
    user_agent = ACCOUNT_UA_MAP[rid]
    acc_tag = f"[{account_num:02d}]"
    count = 0
    def log(msg):
        with log_lock:
            print(f"{acc_tag} {msg}")
    def count_down(sec):
        m = sec // 60
        s = sec % 60
        log(f"休息 {m}分{s}秒")
        time.sleep(sec)
    # ========== 全新域名myexst.top，接口路径完全不变 ==========
    DULIKS_URL = "http://r.myexst.top/xiaoxinxin/duliks"
    REDIRECT_URL = f"http://r.myexst.top/x/r?rid={rid}"
    JINRIGHT_URL = "http://r.myexst.top/xiaoxinxin/jinright"
    DUDU_URL = "http://r.myexst.top/xiaoxinxin/dudu"
    log("启动，目标240轮")
    while count < TOTAL_ROUNDS:
        watch_time = random.randint(8, 15)
        is_407 = False
        report_success = False
        referers = [
            "http://r.myexst.top/xiaoxinxin/home.html?ysi=0",
            REDIRECT_URL,
            JINRIGHT_URL
        ]
        referer = random.choice(referers)
        HEADERS = {
            "User-Agent": user_agent,
            "Referer": referer,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "Android",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate"
        }
        try:
            session.post(DULIKS_URL, headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"}, timeout=8)
            time.sleep(random.uniform(1.5, 3))
            session.get(REDIRECT_URL, headers=HEADERS, timeout=8)
            time.sleep(watch_time)
            ts = int(time.time()*1000)
            session.get(JINRIGHT_URL, headers=HEADERS, params={"rid": rid, "time": 22, "timestamp": ts}, timeout=8)
            time.sleep(random.uniform(1, 2))
            resp = session.get(DUDU_URL, headers=HEADERS, params={"rid": rid, "time": ts, "psgn": 168, "vs": 1002}, timeout=8)
            res_data = resp.json()
            if res_data.get("errcode") == 407:
                is_407 = True
            else:
                report_success = True
        except Exception:
            log("网络异常，跳过本轮")
            continue
        if is_407:
            add_min = random.randint(1, 2)
            total_wait = (60 + add_min) * 60
            log(f"⚠️ 407风控，休息{60+add_min}分钟")
            count_down(total_wait)
            continue
        count += 1
        next_wait = random.randint(10, 22)
        log(f"{count:03d}/240｜模拟阅读中｜等待中｜✅ 阅读成功")
        if count % BATCH_ROUNDS == 0 and count < TOTAL_ROUNDS:
            log("⏸ 批次休息1小时")
            count_down(BATCH_REST)
        time.sleep(next_wait)
    log("🎉 240轮全部完成")
# ===================== 主程序 =====================
if __name__ == "__main__":
    accounts = get_all_rids()
    if not accounts:
        print("❌ 未读取到 od1~od30 环境变量")
        exit()
    print("="*40)
    print(f"启动｜并发{len(accounts)}个账号")
    print("="*40)
    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        futures = [executor.submit(run_single_account, rid, idx+1) for idx, rid in enumerate(accounts)]
        for f in futures:
            try:
                f.result()
            except Exception as e:
                print(f"线程异常: {e}")

# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。
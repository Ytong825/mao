#某信小程序 战马能量星球
#环境变量zmnlxq 抓包搜索safe参数 变量格式safe#备注 多账号换行
#by 初安
import requests
import os
import sys
import time
import json
import re
import warnings

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BASE_URL = "https://m.wxx.ball.warhorsechina.jsinfo.org.cn/app/api/custom"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254151e) XWEB/17127"
REFERER = "https://servicewechat.com/wx94dca6ef07a54c55/178/page-frame.html"
SIGNATURE = "r7TnejnvEra1eDfXrSGpey4sTeX66Ag7K2b1EEcmtyhdJgJ3UC8PrTXjr2sc"

AUTHOR = "👨‍💻 作者：初安"
VERSION = "📦 版本：v1.0.0"

def print_header():
    print("=" * 50)
    print(f"🐴 战马能量星球自动签到脚本")
    print(AUTHOR)
    print(VERSION)
    print("=" * 50)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_task(name):
    print(f"\n📋 {name}")

def print_result(message):
    print(f"   ➤ {message}")

def get_headers():
    return {
        "Host": "m.wxx.ball.warhorsechina.com",
        "Connection": "keep-alive",
        "CUSTOMAPPID": "wx94dca6ef07a54c55",
        "User-Agent": USER_AGENT,
        "xweb_xhr": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "cGvnZetrWSWfLcdYaN40mLdFx6ObkRltdZmhS5hQkgDbuZd9bLcQevwBVEjx-war-horse-zm-2025": SIGNATURE,
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": REFERER,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

def request(url):
    try:
        resp = requests.get(url, headers=get_headers(), verify=False, timeout=10)
        resp.encoding = "utf-8"
        return json.loads(resp.text)
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def api(endpoint, params=""):
    url = f"{BASE_URL}/{endpoint}?{params}"
    return request(url)

def check_status(data, success_msg="成功", fail_msg="失败"):
    if data and data.get("status") == 1:
        print_result(data.get("msg", success_msg))
        return True
    print_result(data.get("msg", fail_msg) if data else fail_msg)
    return False

def get_score(safe):
    data = api("getusercenter", f"safe={safe}")
    if data and data.get("status") == 1:
        print_result(f"当前积分：{data['nowscore']}")
    else:
        print_error("获取积分失败")

def check_in(safe):
    check_status(api("checkin", f"safe={safe}"), "签到成功", "签到失败")

def share_app(safe):
    time.sleep(3)
    check_status(api("share", f"safe={safe}"), "分享成功", "分享失败")

def claim_horse(safe):
    time.sleep(3)
    check_status(api("starthorse", f"safe={safe}"), "领马成功", "领马失败")

def login_game(safe):
    time.sleep(3)
    check_status(api("horselogin", f"safe={safe}"), "登录成功", "登录失败")

def stroke_horse(safe):
    time.sleep(3)
    check_status(api("strokehorse", f"safe={safe}"), "抚摸成功", "抚摸失败")

def feed_horse(safe):
    time.sleep(3)
    check_status(api("horseeat", f"safe={safe}"), "喂马成功", "喂马失败")

def claim_task_reward(safe):
    time.sleep(3)
    data = api("gethorsetaskcenter", f"safe={safe}")
    if data and data.get("status") == 1:
        check_data = data.get("checkData", {})
        print_result(f"领取饲料：{check_data.get('feed', 0)}, 领取天数：{check_data.get('day', 0)}")
    else:
        print_result("领取签到任务失败")

def claim_help_feed(safe):
    time.sleep(3)
    check_status(api("checkslgift", f"safe={safe}"), "领取成功", "领取失败")

def share_game(safe):
    time.sleep(3)
    check_status(api("sharehorse", f"safe={safe}"), "分享成功", "分享失败")

def run_all_tasks(safe):
    tasks = [
        ("📅 每日签到", lambda: check_in(safe)),
        ("📤 分享小程序", lambda: share_app(safe)),
        ("🐴 领取小马", lambda: claim_horse(safe)),
       ("🎮 登录游戏", lambda: login_game(safe)),
        ("🤗 抚摸小马", lambda: stroke_horse(safe)),
        ("🎁 领取签到任务", lambda: claim_task_reward(safe)),
        ("🎲 分享小游戏", lambda: share_game(safe) ),
        ("🥕 喂养小马", lambda: feed_horse(safe)),
    ]
    
    for name, task in tasks:
        print_task(name)
        task()

def process_account(safe):
    try:
        print_info("开始执行任务...")
        get_score(safe)
        run_all_tasks(safe)
        time.sleep(3)
        print_info("任务执行完成，获取最终积分...")
        get_score(safe)
        print_task("🎉 领取额外奖励")
        claim_help_feed(safe)
    except Exception as e:
        print_error(f"执行错误: {e}")

def main():
    print_header()
    
    cookies = os.environ.get("zmnlyl", "")
    if not cookies:
        print_error("请设置环境变量 zmnlyl")
        sys.exit()
    
    accounts = [c for c in cookies.split('\n') if c.strip()]
    total = len(accounts)
    
    print_info(f"检测到 {total} 个账号，开始执行...")
    
    for i, account in enumerate(accounts):
        try:
            parts = account.split('#')
            safe = parts[0].strip()
            remark = parts[1].strip() if len(parts) > 1 else f"账号{i + 1}"
            
            print(f"\n{'=' * 50}")
            print(f"👤 {remark}")
            print(f"{'=' * 50}")
            process_account(safe)
        except Exception as e:
            print_error(f"账号{remark}执行出错，已跳过该账号：{e}")
    
    print(f"\n{'=' * 50}")
    print_success("所有账号执行完成！")
    print(f"{'=' * 50}\n")

if __name__ == '__main__':
    main()
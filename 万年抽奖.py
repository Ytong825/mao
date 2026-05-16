#微信打开链接:https://zhixing.quantbao.online/lottery?inviter=fbaa4d0d-8b17-4b5d-b798-dc99e8194074
#抓包zhixing.quantbao.online域名抓authorization值
#环境变量wnx填入token，多账号用 & 分隔，格式为 Bearer xxx&Bearer xxx
#羊毛交流群：476250706

import requests
import time
import os

BASE_URL = "https://zhixing.quantbao.online/api"
LATITUDE = 28.6946
LONGITUDE = 117.0584
ACCURACY = 30

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 15; PJX110 Build/UKQ1.231108.001; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/146.0.7680.177 "
    "Mobile Safari/537.36 XWEB/1460075 MMWEBSDK/20250503 MMWEBID/518 "
    "MicroMessenger/8.0.62.2900(0x28003E39) WeChat/arm64 Weixin "
    "NetType/5G Language/zh_CN ABI/arm64"
)


def build_headers(token):
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "authorization": token,
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
        "sec-ch-ua-mobile": "?1",
        "origin": "https://zhixing.quantbao.online",
        "x-requested-with": "com.tencent.mm",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://zhixing.quantbao.online/lottery",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }


def format_result(data):
    if not data:
        return "无数据"
    msg = data.get("message") or data.get("msg") or ""
    if "data" in data and isinstance(data["data"], dict):
        detail = data["data"]
        parts = []
        for key in ("points", "point", "score", "prizeName", "prize_name", "name", "reward"):
            if key in detail:
                parts.append(str(detail[key]))
        if parts:
            return f"{msg} -> {', '.join(parts)}" if msg else ", ".join(parts)
    return msg or str(data)


def post(name, url, headers, payload=None):
    try:
        res = requests.post(url, json=payload or {}, headers=headers, timeout=10)
        data = res.json()
        ok = data.get("code") in (0, 200, "0", "200") or res.status_code == 200
        icon = "+" if ok else "!"
        print(f"  [{icon}] {name}: {format_result(data)}")
        return data
    except Exception as e:
        print(f"  [x] {name}: 请求异常 ({e})")
        return None


def run_account(token, index, total):
    masked = token[-8:] if len(token) > 8 else "****"
    print(f"\n--- 账号 {index}/{total} (..{masked}) ---")
    headers = build_headers(token)

    post("签到", f"{BASE_URL}/points/checkin", headers)
    time.sleep(1)

    post("定位", f"{BASE_URL}/lottery/location/verify", headers,
         {"latitude": LATITUDE, "longitude": LONGITUDE, "accuracy": ACCURACY})
    time.sleep(1)

    post("抽奖", f"{BASE_URL}/lottery/draw", headers)


def main():
    raw = os.environ.get("wnx", "")
    if not raw:
        print("[x] 未设置环境变量 wnx，请填入token，多账号用 & 分隔")
        return

    tokens = [t.strip() for t in raw.split("&") if t.strip()]
    print(f"[*] 万年签到抽奖 | 共 {len(tokens)} 个账号")

    for i, token in enumerate(tokens, 1):
        run_account(token, i, len(tokens))
        if i < len(tokens):
            time.sleep(2)

    print(f"\n[*] 全部完成")


if __name__ == "__main__":
    main()

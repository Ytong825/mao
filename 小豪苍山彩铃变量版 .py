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

import requests
import json
import random
import time
import os
from datetime import datetime

# ========== 从环境变量读取参数 ==========
# 1. 设备ID（单个或多个用英文逗号分隔）
DEVICE_IDS = os.getenv("DEVICE_IDS", "").split(",") if os.getenv("DEVICE_IDS") else []
# 2. 多组cId（格式：cId1;cId2）
C_IDS = os.getenv("C_IDS", "")
# 3. 循环次数
LOOP_TIMES = int(os.getenv("LOOP_TIMES", 5))

# ========== 核心配置区（adPrice范围） ==========
AD_PRICE_MIN = 10000  # adPrice最小值
AD_PRICE_MAX = 100000 # adPrice最大值
# ======================================

# 解析cId列表
cid_list = C_IDS.split(";") if C_IDS else []

# 校验环境变量
if not (DEVICE_IDS and cid_list):
    print("错误：请配置环境变量 DEVICE_IDS 和 C_IDS！")
    exit()

# 固定uId（抓包值）
TRUE_UID = "4220315"

# ========== 防风控配置 ==========
DELAY_AFTER_ARTICLE = random.uniform(0.8, 1.5)
AD_DELAY_MIN = 12
AD_DELAY_MAX = 18
LOOP_DELAY_MIN = 25
LOOP_DELAY_MAX = 35
USER_AGENTS = [
    "okhttp/3.12.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1"
]
# ==============================

for i in range(LOOP_TIMES):
    print(f"\n===== 第 {i+1} 次循环 =====")
    
    # 按顺序读取设备ID和cId（循环复用）
    device_index = i % len(DEVICE_IDS)
    current_deviceId = DEVICE_IDS[device_index]
    cid_index = i % len(cid_list)
    current_cid = cid_list[cid_index]
    
    # 自动生成随机adPrice
    random_ad_price = random.randint(AD_PRICE_MIN, AD_PRICE_MAX)
    
    # 防风控：随机选择User-Agent
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Encoding': "gzip",
        'content-type': "application/json; charset=utf-8",
        'Timestamp': str(int(datetime.now().timestamp() * 1000))
    }
    
    print(f"当前参数：deviceId={current_deviceId}, cId={current_cid}, adPrice={random_ad_price}")
    
    # 1. 获取项目列表
    list_url = "https://cp.fjsuiyilai.com/api/xiangmu/xiangmuList"
    list_payload = {
        "id": "1",
        "keywords": "",
        "order": str(random.choice([1,2])),
        "page": str(random.choice([1,2])),
        "platfrom": "app",
        "platfromId": "69"
    }
    try:
        requests.post(list_url, data=json.dumps(list_payload), headers=headers, timeout=15)
        print("项目列表浏览完成")
    except Exception as e:
        print(f"获取项目列表失败：{e}")
    
    # 2. 随机延迟
    time.sleep(random.uniform(1.0, 2.0))
    
    # 3. 提交下载限制
    download_url = "https://cp.fjsuiyilai.com/api/taste/limitDownload"
    download_payload = {
        "deviceId": current_deviceId,
        "uId": TRUE_UID,
        "version": "1.2.10",
        "platfrom": "app",
        "platfromId": "69",
        "random": str(random.randint(1000,9999))
    }
    try:
        requests.post(download_url, data=json.dumps(download_payload), headers=headers, timeout=15)
        print("下载限制提交完成")
    except Exception as e:
        print(f"提交下载限制失败：{e}")
    
    # 4. 广告提交延迟
    ad_delay = random.randint(AD_DELAY_MIN, AD_DELAY_MAX)
    print(f"等待 {ad_delay} 秒后提交广告...")
    time.sleep(ad_delay)
    
    # 5. 提交广告（使用随机adPrice）
    ad_url = "https://cp.fjsuiyilai.com/api/picture/adRecord"
    ad_payload = {
        "uId": TRUE_UID,
        "bId": "0",
        "cId": current_cid,
        "isFree": "0",
        "adPrice": str(random_ad_price),
        "adFrom": "1",
        "adModel": "3",
        "ip": "",
        "platfrom": "app",
        "platfromId": "69",
        "deviceBrand": "",
        "deviceId": current_deviceId,
        "deviceModel": "",
        "deviceOrientation": "",
        "deviceSystem": "",
        "devicePixelRatio": "",
        "nonce": str(random.randint(100000, 999999))
    }
    try:
        ad_response = requests.post(ad_url, data=json.dumps(ad_payload), headers=headers, timeout=15)
        print("广告提交结果：", ad_response.text)
    except Exception as e:
        print(f"提交广告失败：{e}")
    
    # 循环间隔
    if i < LOOP_TIMES - 1:
        loop_delay = random.randint(LOOP_DELAY_MIN, LOOP_DELAY_MAX)
        print(f"下次循环等待 {loop_delay} 秒...")
        time.sleep(loop_delay)

print("\n===== 所有循环执行完毕 =====")


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
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
#https://cp.fjsuiyilai.com/h5/#/pages/mine/register?inviteCode=91032 先走邀请链接 然后注册成功后 首页下载仓山彩铃
# ========== 最主要参数 ==========
#抓包直接抓adPrice域名 请求头里的deviceId和cId  Cid好像是自己的邀请码。
DEVICE_ID = ""  # 设备ID
C_ID = ""                # 广告cId
# ========== 核心配置区（集中管理易修改参数） ==========
LOOP_TIMES = 5                # 循环次数
DELAY_AFTER_ARTICLE = 0.5     # 获取文章后延迟秒数（毫秒级可用小数）
LOOP_DELAY_MIN = 10           # 循环间隔最小延迟（秒）
LOOP_DELAY_MAX = 30           # 循环间隔最大延迟（秒）
AD_DELAY_MIN = 5              # 提交广告前最小延迟（秒）
AD_DELAY_MAX = 10             # 提交广告前最大延迟（秒）
AD_PRICE_MIN = 10000          # adPrice最小值
AD_PRICE_MAX = 100000         # adPrice最大值
# =====================================================

headers = {
    'User-Agent': "okhttp/3.12.0",
    'Accept-Encoding': "gzip",
    'content-type': "application/json; charset=utf-8"
}

# 循环执行流程
for i in range(LOOP_TIMES):
    print(f"\n===== 第 {i+1} 次循环 =====")
    
    # 1. 获取项目列表
    list_url = "https://cp.fjsuiyilai.com/api/xiangmu/xiangmuList"
    list_payload = {
        "id": "1",
        "keywords": "",
        "order": "2",
        "page": "1",
        "platfrom": "app",
        "platfromId": "69"
    }
    response = requests.post(list_url, data=json.dumps(list_payload), headers=headers)
    list_data = response.json()
    items = list_data.get("data", [])
    if not items:
        print("项目列表为空，跳过本次循环")
        # 空列表也执行循环间隔延迟
        if i < LOOP_TIMES - 1:
            loop_delay = random.randint(LOOP_DELAY_MIN, LOOP_DELAY_MAX)
            print(f"下次循环前等待 {loop_delay} 秒...")
            time.sleep(loop_delay)
        continue
    
    # 2. 随机选择项目的 id 和 uId
    selected = random.choice(items)
    target_id = selected.get("id")
    target_uid = selected.get("uId")
    print(f"随机选中：id={target_id}, uId={target_uid}")
    
    # 3. 获取项目详情并提取标题
    detail_url = "https://cp.fjsuiyilai.com/api/xiangmu/xiangmuDetail"
    detail_payload = {
        "id": target_id,
        "uid": target_uid,
        "platfrom": "app",
        "platfromId": "69"
    }
    detail_response = requests.post(detail_url, data=json.dumps(detail_payload), headers=headers)
    detail_data = detail_response.json()
    article_title = detail_data.get("data", {}).get("title", "未获取到标题")
    print(f"文章标题：{article_title}")
    
    # 4. 获取文章后固定延迟
    time.sleep(DELAY_AFTER_ARTICLE)
    
    # 5. 提交下载限制请求（使用配置区的DEVICE_ID）
    download_url = "https://cp.fjsuiyilai.com/api/taste/limitDownload"
    download_payload = {
        "deviceId": DEVICE_ID,
        "uId": target_uid,
        "version": "1.2.10",
        "platfrom": "app",
        "platfromId": "69"
    }
    requests.post(download_url, data=json.dumps(download_payload), headers=headers)
    
    # 6. 生成5~10秒随机延迟后提交广告
    ad_delay = random.randint(AD_DELAY_MIN, AD_DELAY_MAX)
    print(f"等待 {ad_delay} 秒后提交广告...")
    time.sleep(ad_delay)
    
    # 生成随机adPrice
    random_ad_price = random.randint(AD_PRICE_MIN, AD_PRICE_MAX)
    
    # 提交广告记录（使用配置区的DEVICE_ID和C_ID）
    ad_url = "https://cp.fjsuiyilai.com/api/picture/adRecord"
    ad_payload = {
        "uId": target_uid,
        "bId": "0",
        "cId": C_ID,
        "isFree": "0",
        "adPrice": str(random_ad_price),
        "adFrom": "1",
        "adModel": "3",
        "ip": "",
        "platfrom": "app",
        "platfromId": "69",
        "deviceBrand": "",
        "deviceId": DEVICE_ID,
        "deviceModel": "",
        "deviceOrientation": "",
        "deviceSystem": "",
        "devicePixelRatio": ""
    }
    ad_response = requests.post(ad_url, data=json.dumps(ad_payload), headers=headers)
    print("广告提交结果：", ad_response.text)
    print(f"本次广告价格：{random_ad_price}")
    
    # 7. 非最后一次循环，添加10~30秒随机延迟（下次循环前等待）
    if i < LOOP_TIMES - 1:
        loop_delay = random.randint(LOOP_DELAY_MIN, LOOP_DELAY_MAX)
        print(f"下次循环前等待 {loop_delay} 秒...")
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
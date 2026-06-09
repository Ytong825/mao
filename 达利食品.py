#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
薯片一元享乐 扫码脚本 V1.0.0
适用于可比克薯片「1元乐享」活动扫码

环境变量说明：
1. dadaming_sp_token (必需)
   - 说明：token（member:xxx格式），多账号用#分隔
   - 格式：member:token1#member:token2
   - 抓包路径：请求体 context.token

2. dadaming_sp_qrcode (可选，与文件二选一)
   - 说明：二维码，每行一个，支持完整URL或纯二维码
   - 示例：http://hh66.cn/a/U6QvDutvXC2zaavn95
   - 或纯码：U6QvDutvXC2zaavn95
   - 也可放入 薯片.txt 文件中（每行一个），脚本优先读取文件

3. dadaming_zb (可选)
   - 说明：经纬度坐标
   - 格式：维度#经度
   - 默认：35.259620666503906#113.65715789794922

用法：
  python 薯片一元享乐.py

接口说明：
  POST https://hzhuihe.cn/cpp/onethingoneyard/activity/scancode.json
  bizCode: OTOY (一元享乐)
"""

import requests
import os
import re
import time
import random
import json
import hashlib
from datetime import datetime


import uuid


# ========== 配置区 ==========

DEFAULT_LOCATION = "35.259620666503906,113.65715789794922"
BIZ_CODE = "OTOY"
CLIENT_TYPE = "wxapp_dl"
VERSION_NO = "20251125"
REQUEST_PATH = "daliOneCode/activity/index"

# 随机手机设备型号
DEVICE_LIST = [
    "Xiaomi 13", "Xiaomi 14", "Xiaomi 12", "Redmi K60", "Redmi Note 12",
    "OPPO Find X6", "OPPO Reno 10", "vivo X100", "vivo S18",
    "Huawei P60", "Huawei Mate 60", "Samsung S23", "Samsung S24",
    "OnePlus 11", "OnePlus 12", "Realme GT5", "iQOO 12",
]
ANDROID_VERSIONS = ["13", "14", "12"]


# 活动截止日期（根据实际调整）
EXPIRE_DATE = datetime(2026, 12, 31, 23, 59, 59)


# ========== 工具函数 ==========

def random_client_mac():
    """生成随机手机 clientMac"""
    device = random.choice(DEVICE_LIST)
    android_ver = random.choice(ANDROID_VERSIONS)
    return f"android;3.16.0;{device} Android {android_ver};4.1.9.62"


# ========== 环境变量读取 ==========

def get_accounts():
    """读取账号token，未设置环境变量则使用默认值"""
    if "dadaming_sp_token" in os.environ:
        tokens = re.split("#", os.environ["dadaming_sp_token"])
        return [t.strip() for t in tokens if t.strip()]
    # 默认token
    return [""]


def get_qrcodes():
    """读取二维码列表（优先从 薯片.txt 文件读取）"""
    raw_codes = []

    # 优先读取同目录下的 薯片.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(script_dir, "薯片.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            raw_codes = [line.strip() for line in f if line.strip()]
        print(f"📄 从 薯片.txt 读取到 {len(raw_codes)} 个二维码")

    # 文件不存在则从环境变量读取
    if not raw_codes and "dadaming_sp_qrcode" in os.environ:
        raw_codes = re.split(r"\n", os.environ["dadaming_sp_qrcode"])

    # 过滤和提取纯码
    result = []
    for c in raw_codes:
        c = c.strip()
        # 跳过注释行和空行
        if not c or c.startswith("#"):
            continue
        if "http" in c:
            parts = c.rstrip("/").split("/")
            c = parts[-1] if parts else c
        result.append(c)
    return result


def get_location():
    """读取坐标"""
    if "dadaming_zb" in os.environ:
        parts = re.split("#", os.environ["dadaming_zb"])
        if len(parts) >= 2:
            return f"{parts[0].strip()},{parts[1].strip()}"
    return DEFAULT_LOCATION


# ========== 签名算法 ==========

SIGN_KEY = "key=MKnEu6zaS04N23XoMUL8GOwOKIQwXMvT"
ACCESS_ID = "feRTnGetT3YTxbNF"
ACCESS_KEY = "wQaZiN2dDK6CxrjjGreAkfyyDJMaWhei"
# http://hh66.cn/a/MevNSJkUzRTzDrUA95

def generate_request_id():
    """生成随机 requestId（32位hex）"""
    return hashlib.md5(str(random.random()).encode()).hexdigest()


def generate_body_sign(token, timestamp):
    """
    生成请求体 sign 签名
    算法: MD5(token + timestamp + 'key=MKnEu6zaS04N23XoMUL8GOwOKIQwXMvT').toUpperCase()
    """
    content = token + timestamp + SIGN_KEY
    return hashlib.md5(content.encode()).hexdigest().upper()


def get_request_id(token):
    """
    获取 requestId（扫码前必调）
    接口: POST /wpp/commonrequest/getRequestId.json
    x-sign 先用空字符串
    """
    url = "https://hzhuihe.cn/wpp/commonrequest/getRequestId.json"
    timestamp = str(int(time.time() * 1000))

    context_dict = {
        "clientType": CLIENT_TYPE,
        "token": token,
        "clientMac": random_client_mac(),
        "versionNo": "20260602",
        "timestamp": timestamp,
        "requestPath": "pages/index/index"
    }

    payload = {
        "data": "",
        "context": context_dict,
        "sign": generate_body_sign(token, timestamp)
    }

    headers = {
        "Host": "hzhuihe.cn",
        "x-sign": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771",
        "xweb_xhr": "1",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx1e7ba839c6bc0a27/23/page-frame.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        text = resp.text
        print(f"   [DEBUG] HTTP {resp.status_code}, body前200: {text[:200]}")
        json_start = text.find('{')
        if json_start == -1:
            print(f"   ⚠️ 响应中未找到JSON")
            return None
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            print(f"   ⚠️ JSON括号不匹配")
            return None
        text = text[json_start:json_end + 1]
        result = json.loads(text)

        if result.get("status") == 1:
            data = result.get("data")
            if isinstance(data, dict):
                req_id = data.get("requestId", data)
            else:
                req_id = data
            if isinstance(req_id, str):
                return req_id
            return str(req_id) if req_id else None
        print(f"   ⚠️ getRequestId失败 status!=1: {result}")
    except json.JSONDecodeError as e:
        print(f"   ⚠️ getRequestId JSON解析失败: {e}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ getRequestId 网络错误: {e}")
    except Exception as e:
        print(f"   ⚠️ getRequestId异常: {e}")
    return None


def get_access_token():
    """
    获取 accessToken（用作 x-sign）
    接口: POST zzx/v1/accessToken.json
    签名: MD5(accessId + accessKey)
    """
    url = "https://hzhuihe.cn/zzx/v1/accessToken.json"
    sign = hashlib.md5((ACCESS_ID + ACCESS_KEY).encode()).hexdigest()
    
    headers = {
        "Host": "hzhuihe.cn",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
    }
    
    payload = {"sign": sign}
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        # 精确截取第一个完整JSON对象（处理乱码前后缀）
        text = resp.text
        json_start = text.find('{')
        if json_start == -1:
            return None
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            return None
        text = text[json_start:json_end + 1]
        result = json.loads(text)
        
        if result.get("code") == 1 or result.get("status") == 1:
            token = result.get("data", {}).get("accessToken") or result.get("data")
            if isinstance(token, str):
                return token
            return str(token) if token else None
        print(f"   ⚠️ accessToken获取失败: {result}")
    except Exception as e:
        print(f"   ⚠️ accessToken请求异常: {e}")
    return None





def list_home_group(token, location):
    """
    查询首页群组列表
    接口: POST /cpp/group/listHomeGroup.json
    不加 x-sign 和 x-requestid
    """
    url = "https://hzhuihe.cn/cpp/group/listHomeGroup.json"
    timestamp = str(int(time.time() * 1000))

    context_dict = {
        "clientType": CLIENT_TYPE,
        "token": token,
        "clientMac": random_client_mac(),
        "versionNo": "20260602",
        "timestamp": timestamp,
        "requestPath": "pages/index/index"
    }

    payload = {
        "data": {
            "locate": location,
            "history": 1,
            "currentPage": 1,
            "pageSize": 20
        },
        "context": context_dict,
        "sign": generate_body_sign(token, timestamp)
    }

    headers = {
        "Host": "hzhuihe.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771",
        "xweb_xhr": "1",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx1e7ba839c6bc0a27/23/page-frame.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        text = resp.text
        print(f"   [DEBUG] HTTP {resp.status_code}, body前500: {text[:500]}")
        json_start = text.find('{')
        if json_start == -1:
            print(f"   ⚠️ 响应中未找到JSON")
            return None
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            print(f"   ⚠️ JSON括号不匹配")
            return None
        text = text[json_start:json_end + 1]
        result = json.loads(text)
        print(f"   📋 listHomeGroup结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except json.JSONDecodeError as e:
        print(f"   ⚠️ listHomeGroup JSON解析失败: {e}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ listHomeGroup 网络错误: {e}")
    except Exception as e:
        print(f"   ⚠️ listHomeGroup异常: {e}")
    return None


def do_query_api_sign_value(token):
    """
    查询 API sign 值
    接口: POST /cpp/system/doQueryApiSignValue.json
    x-sign 非空，requestPath 为 scanGroup/index/index
    """
    url = "https://hzhuihe.cn/cpp/system/doQueryApiSignValue.json"
    timestamp = str(int(time.time() * 1000))

    context_dict = {
        "clientType": CLIENT_TYPE,
        "token": token,
        "clientMac": random_client_mac(),
        "versionNo": "20260602",
        "timestamp": timestamp,
        "requestPath": "scanGroup/index/index"
    }

    payload = {
        "data": "",
        "context": context_dict,
        "sign": generate_body_sign(token, timestamp)
    }

    headers = {
        "Host": "hzhuihe.cn",
        "x-sign": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541113) XWEB/16771",
        "Content-Type": "application/json",
        "charset": "utf-8",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx1e7ba839c6bc0a27/23/page-frame.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        text = resp.text
        print(f"   [DEBUG] doQueryApiSignValue HTTP {resp.status_code}, body前500: {text[:500]}")
        json_start = text.find('{')
        if json_start == -1:
            print(f"   ⚠️ 响应中未找到JSON")
            return None
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            print(f"   ⚠️ JSON括号不匹配")
            return None
        text = text[json_start:json_end + 1]
        result = json.loads(text)
        print(f"   📋 doQueryApiSignValue结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except json.JSONDecodeError as e:
        print(f"   ⚠️ doQueryApiSignValue JSON解析失败: {e}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ doQueryApiSignValue 网络错误: {e}")
    except Exception as e:
        print(f"   ⚠️ doQueryApiSignValue异常: {e}")
    return None


def check_dali_qr_code(token, qr_code, req_key):
    """
    校验大力码
    接口: POST /cpp/dali/checkDaliQrCode.json
    x-sign 先用空
    """
    url = "https://hzhuihe.cn/cpp/dali/checkDaliQrCode.json"
    timestamp = str(int(time.time() * 1000))

    context_dict = {
        "clientType": CLIENT_TYPE,
        "token": token,
        "clientMac": random_client_mac(),
        "versionNo": "20260602",
        "timestamp": timestamp,
        "requestPath": "scanGroup/index/index"
    }

    payload = {
        "data": {"qrCode": qr_code},
        "context": context_dict,
        "sign": generate_body_sign(token, timestamp)
    }

    headers = create_headers(token, "", req_key)
    headers["charset"] = "utf-8"

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        text = resp.text
        print(f"   [DEBUG] checkDaliQrCode HTTP {resp.status_code}, body前500: {text[:500]}")
        json_start = text.find('{')
        if json_start == -1:
            print(f"   ⚠️ 响应中未找到JSON")
            return None
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            print(f"   ⚠️ JSON括号不匹配")
            return None
        text = text[json_start:json_end + 1]
        result = json.loads(text)
        print(f"   📋 checkDaliQrCode结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except json.JSONDecodeError as e:
        print(f"   ⚠️ checkDaliQrCode JSON解析失败: {e}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ checkDaliQrCode 网络错误: {e}")
    except Exception as e:
        print(f"   ⚠️ checkDaliQrCode异常: {e}")
    return None


# ========== 请求头构造 ==========

def create_headers(token, x_sign, req_key=""):
    """创建请求头
    req_key: 暂未使用（保留兼容）
    x-requestid 使用 UUID 去掉 - 生成
    """
    x_requestid = uuid.uuid4().hex
    timestamp = str(int(time.time() * 1000))

    return {
        "Host": "hzhuihe.cn",
        "x-sign": x_sign or "",
        "x-requestid": x_requestid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254193e) XWEB/19841",
        "xweb_xhr": "1",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wx1e7ba839c6bc0a27/22/page-frame.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Priority": "u=1, i"
    }


# ========== 核心扫码接口 ==========

def scan_code(token, qr_code, location, req_key):
    """
    扫码接口

    Args:
        token: 用户token (member:xxx)
        qr_code: 二维码
        location: 经纬度 "lat,lng"
        req_key: getRequestId返回值(密钥)

    Returns:
        dict: 扫码结果
    """
    url = "https://hzhuihe.cn/cpp/onethingoneyard/activity/scancode.json"

    # 构造 data
    data_dict = {
        "locate": location,
        "qrCode": qr_code,
        "bizCode": BIZ_CODE,
        "qrCodeFullUrl": f"http://hh66.cn/a/{qr_code}"
    }

    # 构造 context
    context_dict = {
        "clientType": CLIENT_TYPE,
        "token": token,
        "clientMac": random_client_mac(),
        "versionNo": VERSION_NO,
        "timestamp": str(int(time.time() * 1000)),
        "requestPath": REQUEST_PATH
    }

    # 构造完整请求体
    payload = {
        "data": data_dict,
        "context": context_dict,
        "sign": generate_body_sign(token, context_dict["timestamp"])
    }

    headers = create_headers(token, "", req_key)

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        
        # 响应可能有乱码前缀/后缀，精确截取第一个完整JSON对象
        text = resp.text
        json_start = text.find('{')
        if json_start == -1:
            return {"success": False, "errorMsg": "响应中未找到JSON"}
        # 从第一个 { 开始，找到匹配的 }
        depth = 0
        json_end = -1
        for i in range(json_start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_end = i
                    break
        if json_end == -1:
            return {"success": False, "errorMsg": "JSON括号不匹配"}
        text = text[json_start:json_end + 1]
        result = json.loads(text)

        if result.get("status") == 1 and result.get("errorCode") == "SUCCESS":
            return {"success": True, "data": result.get("data", {})}
        else:
            return {
                "success": False,
                "errorCode": result.get("errorCode", "UNKNOWN"),
                "errorMsg": result.get("errorMsg", "未知错误")
            }

    except json.JSONDecodeError as e:
        return {"success": False, "errorMsg": f"JSON解析失败: {e}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "errorMsg": f"网络请求错误: {e}"}
    except Exception as e:
        return {"success": False, "errorMsg": f"请求异常: {e}"}


# ========== 显示 ==========

def print_banner():
    print("""
        免责声明:

DDM所发布的所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。
DDM对任何问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害。
间接使用脚本的任何用户，包括但不限于建立VPS或在某些行为违反国家/地区法律或相关法规的情况下进行传播。
DDM对于由此引起的任何隐私泄漏或其他后果概不负责。
如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。
任何以任何方式查看此项目的人或直接或间接使用该项目的任何脚本的使用者都应仔细阅读此声明。

本人所发布的所有文件不在包括但不限于 闲鱼/公众号 等平台发布
所发布的所有文件均不产生包括但不限于 收费/获利 等违法违规行为，因此产生纠纷/违法行为等后果均由传播者所承担 作者不负任何责任

所发布的内容仅供学习，禁止用于其他用途，您必须在下载后的24小时内从计算机或手机中完全删除以上内容。
严禁产生利益链！

DDM保留随时更改或补充此免责声明的权利。
一旦使用或复制了任何相关脚本或Script项目的规则，则视为您已接受此免责声明。

如您不同意，请马上删除所以相关文件

Github:
https://github.com/985Ming/qlk
    ╔══════════════════════════════════════════════╗
    ║                                              ║
    ║   ██████  ██████  ███    ███                ║
    ║   ██   ██ ██   ██ ████  ████                ║
    ║   ██   ██ ██   ██ ██ ████ ██                ║
    ║   ██   ██ ██   ██ ██  ██  ██                ║
    ║   ██████  ██████  ██      ██                ║
    ║                                              ║
    ║     薯片一元享乐扫码脚本 V1.0.0              ║
    ║     Created by 大大鸣                        ║
    ║     联系方式: v:xolag29638099                ║
    ║     大大鸣交流群：1025838653                 ║
    ╚══════════════════════════════════════════════╝
    """)


def display_reward(reward):
    """展示奖品信息"""
    goods_name = reward.get("goodsName", "未知奖品")
    goods_number = reward.get("goodsNumber", 0)
    present_type = reward.get("presentType", 0)
    voucher_list = reward.get("voucherNoList", [])

    type_map = {6: "实物奖品", 1: "红包", 2: "优惠券", 3: "积分"}
    type_name = type_map.get(present_type, f"类型{present_type}")

    print(f"   🎁 奖品: {goods_name}")
    print(f"   📦 数量: {goods_number}")
    print(f"   🏷️  类型: {type_name}")
    if voucher_list:
        print(f"   🔑 兑换码: {', '.join(voucher_list)}")


# ========== 主流程 ==========

def process_account(token, qrcodes, location, req_key, account_index, total_accounts):
    """处理单个账号的全部二维码"""
    print(f"\n{'=' * 50}")
    print(f"🎯 账号 {account_index}/{total_accounts}")
    print(f"{'=' * 50}")

    success_count = 0
    fail_count = 0
    rewards = []

    for idx, qr_code in enumerate(qrcodes, 1):
        print(f"\n[{idx}/{len(qrcodes)}] 扫码: {qr_code[:20]}...")

        result = scan_code(token, qr_code, location, req_key)

        if result.get("success"):
            data = result.get("data", {})
            reward_list = data.get("rewardVOList", [])

            if reward_list:
                print(f"   ✅ 扫码成功！获得 {len(reward_list)} 个奖品：")
                for reward in reward_list:
                    display_reward(reward)
                    rewards.append(reward)
                success_count += 1
            else:
                print(f"   ⚠️ 扫码成功但无奖品（可能已扫过或未中奖）")
                fail_count += 1
        else:
            error_code = result.get("errorCode", "UNKNOWN")
            error_msg = result.get("errorMsg", "未知错误")
            print(f"   ❌ 失败 [{error_code}]: {error_msg}")
            fail_count += 1

        # 间隔等待
        if idx < len(qrcodes):
            delay = random.randint(2, 5)
            time.sleep(delay)

    print(f"\n--- 账号 {account_index} 汇总 ---")
    print(f"✅ 成功: {success_count}  |  ❌ 失败: {fail_count}")

    return {"success": success_count, "fail": fail_count, "rewards": rewards}


def main():
    print_banner()

    # 检查过期
    if datetime.now() > EXPIRE_DATE:
        print("大大鸣提示您，免费脚本使用期已过，请联系大大鸣获取最新脚本，v:xolag29638099")
        return

    # 读取配置
    accounts = get_accounts()
    qrcodes = get_qrcodes()
    location = get_location()

    if not accounts:
        print("❌ 没有可用账号！请设置环境变量 dadaming_sp_token")
        print("   格式：member:token1#member:token2")
        return

    if not qrcodes:
        print("❌ 没有可用二维码！请检查 薯片.txt 或环境变量 dadaming_sp_qrcode")
        return

    # 测试 listHomeGroup 接口（不加 x-sign / x-requestid）
    print("🏠 正在查询 listHomeGroup...")
    list_home_group(accounts[0], location)

    # 测试 doQueryApiSignValue 接口
    print("🔐 正在查询 doQueryApiSignValue...")
    do_query_api_sign_value(accounts[0])

    # 测试 checkDaliQrCode 接口
    print("🔍 正在校验大力码...")
    check_dali_qr_code(accounts[0], qrcodes[0], "")

    # 获取 requestId
    print("🔑 正在获取 requestId...")
    req_id = get_request_id(accounts[0])  # 用第一个账号获取即可
    if req_id:
        print(f"✅ requestId: {req_id}\n")
        req_key = req_id
    else:
        print("⚠️ 获取 requestId 失败，将使用空字符串\n")
        req_key = ""
    print(f"\n📊 配置汇总：")
    print(f"   账号数: {len(accounts)}")
    print(f"   二维码数: {len(qrcodes)}")
    print(f"   坐标: {location}")

    total_success = 0
    total_fail = 0
    all_rewards = []

    for i, token in enumerate(accounts, 1):
        result = process_account(token, qrcodes, location, req_key, i, len(accounts))
        total_success += result["success"]
        total_fail += result["fail"]
        all_rewards.extend(result["rewards"])

        # 账号间等待
        if i < len(accounts):
            delay = random.randint(5, 10)
            print(f"\n⏳ 账号间隔等待 {delay} 秒...")
            time.sleep(delay)

    # 最终汇总
    print(f"\n{'=' * 50}")
    print(f"🎉 全部处理完成！")
    print(f"📊 扫码成功: {total_success}  |  扫码失败: {total_fail}")
    print(f"🎁 共获得 {len(all_rewards)} 个奖品")
    if all_rewards:
        print(f"\n📋 奖品明细：")
        for idx, r in enumerate(all_rewards, 1):
            print(f"   {idx}. {r.get('goodsName', '未知')} ×{r.get('goodsNumber', 1)}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()

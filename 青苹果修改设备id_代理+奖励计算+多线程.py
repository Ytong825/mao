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

# 26.1.18修改：解决之前的脚本导致丢设备的问题，创建文件保存device_id，若已有id则运行后手动替换即可
            # 可配合自动提现脚本 https://script.345yun.cn/download/1942 实现刷广不用手，薅羊毛全自动

# 业务规则说明：
# - 一个广告0.2元，不需要养机
# - 每天看20个广告上限=4元
# - 积分比例10000：1元（10000积分=1元）
# - 积分每天晚上12点自动到余额
# - 10元起提，一机一号一ip
# - 先注册并完成本人认证：https://api.zhenghui.xyz/user/#/register?inviteCode=egsi9WOL
# 变量名称pg  单账号： secretId&secretKey&代理 （代理可选） 多账号：每行一个账号，换行分隔
# 1. secretId ：账号唯一标识（必选） 2.  secretKey ：账号密钥（必选） 3.  代理 ：支持普通格式、带账号密码格式、竖线分隔格式（可选，省略则本地直连）
# 新增变量pgxc：自定义线程数，默认1，最大100
import requests
import json
import sys
import os
import secrets
import time
import random
import re
import urllib3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib  # 新增：用于账号哈希绑定固定机型
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True

# 全局配置常量
ENV_VAR_NAME = "pg"
LOOP_COUNT = int(os.environ.get("RUN_LOOP_COUNT", 10))
PROXY_TIMEOUT = 10
REQ_TIMEOUT = 30
LOGIN_RETRY = 3
REQ_RETRY = 2
POINT_TO_CASH_RATIO = 10000
DEFAULT_THREAD_NUM = 1
MAX_THREAD_NUM = 100
# 添加配置文件，修复设备id获取
DataFile = "勿删_devicedata.json"
# 线程数配置
try:
    CUSTOM_THREAD_NUM = int(os.environ.get("pgxc", DEFAULT_THREAD_NUM))
    CUSTOM_THREAD_NUM = max(DEFAULT_THREAD_NUM, min(CUSTOM_THREAD_NUM, MAX_THREAD_NUM))
except (ValueError, TypeError):
    CUSTOM_THREAD_NUM = DEFAULT_THREAD_NUM

# 接口URL
LOGIN_URL = "https://api.zhenghui.xyz/api/app/v1/auth/secretKeyLogin"
AD_URL = "https://api.zhenghui.xyz/api/app/v1/ad/next"
AD_PLAY_URL = "https://api.zhenghui.xyz/api/app/v1/ad/video/play"
AD_ENDED_URL = "https://api.zhenghui.xyz/api/app/v1/ad/video/ended"

# 全局状态与锁
account_limit_status = {}
limit_lock = threading.Lock()

# 设备型号配置（与原版本一致）
DEVICE_MODELS = {
    "huawei": ["TAS-AN00", "NOH-AN00", "EVR-AN00", "ANA-AN00", "JEF-AN00"],
    "xiaomi": ["Redmi Note 12", "Xiaomi 13", "Redmi K60", "Xiaomi 12S", "Redmi Note 11"],
    "oppo": ["Reno8", "Find X5", "A96", "Reno9", "Find N2"],
    "vivo": ["X90", "S16", "iQOO Neo7", "X80", "Y77"],
    "samsung": ["Galaxy S23", "Galaxy A54", "Galaxy S22", "Galaxy Note 20", "Galaxy A34"],
    "oneplus": ["11", "Nord 3", "10T", "Nord 2T", "9RT"]
}
ANDROID_VERSIONS = ["9", "10", "11", "12", "13"]
CHROME_VERSIONS = ["91.0.4472.114", "92.0.4515.131", "93.0.4577.63", "94.0.4606.81", "95.0.4638.54"]

def generate_device_id():
    """生成设备ID（保持原逻辑）"""
    return secrets.token_hex(16)

def get_fixed_device_info(secretId):
    """新增：基于secretId哈希生成固定设备信息，同一账号始终返回相同机型"""
    # 对secretId进行哈希，获取固定种子
    hash_obj = hashlib.md5(secretId.encode("utf-8"))
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # 基于哈希值选择固定品牌（取模确保结果在品牌列表范围内）
    brands = list(DEVICE_MODELS.keys())
    brand_index = hash_int % len(brands)
    brand = brands[brand_index]
    
    # 基于哈希值选择固定机型
    models = DEVICE_MODELS[brand]
    model_index = hash_int % len(models)
    model = models[model_index]
    
    # 基于哈希值选择固定系统版本和Chrome版本
    android_index = hash_int % len(ANDROID_VERSIONS)
    android_version = ANDROID_VERSIONS[android_index]
    
    chrome_index = hash_int % len(CHROME_VERSIONS)
    chrome_version = CHROME_VERSIONS[chrome_index]
    
    return {
        "brand": brand,
        "model": model,
        "android_version": android_version,
        "chrome_version": chrome_version
    }

def generate_random_user_agent(device_info):
    """生成User-Agent（保持原逻辑）"""
    build_code = secrets.token_hex(4).upper()
    return (
        f"Mozilla/5.0 (Linux; Android {device_info['android_version']}; {device_info['model']} Build/{build_code}; wv) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{device_info['chrome_version']} "
        f"Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/24.0)"
    )

def proxy_check(proxy):
    """代理检测（保持原逻辑）"""
    test_urls = ["http://httpbin.org/ip", "https://icanhazip.com", "http://ip-api.com/json"]
    if not proxy:
        for test_url in test_urls:
            try:
                resp = requests.get(test_url, timeout=PROXY_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    local_ip = resp.json().get("query", "未知") if "ip-api.com" in test_url else resp.text.strip() or "未知"
                    return {"valid": True, "proxy": None, "msg": f"✅ 无代理 IP:{local_ip}"}
            except:
                continue
        return {"valid": False, "proxy": None, "msg": f"❌ 本地网络异常：无法获取公网IP"}
    
    proxy_url = proxy.strip()
    # 代理格式转换（保持原逻辑）
    if "|" in proxy_url and "://" not in proxy_url:
        parts = proxy_url.split("|")
        if len(parts) >= 2:
            ip = parts[0].strip()
            port = parts[1].strip()
            user = parts[2].strip() if len(parts)>=3 else ""
            pwd = parts[3].strip() if len(parts)>=4 else ""
            proxy_url = f"socks5://{user}:{pwd}@{ip}:{port}" if user and pwd else f"socks5://{ip}:{port}"
    elif re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', proxy_url):
        proxy_url = f"socks5://{proxy_url}"
    
    proxy_protocols = {"http": proxy_url, "https": proxy_url}
    for retry in range(2):
        for test_url in test_urls:
            try:
                resp = requests.get(
                    test_url,
                    proxies=proxy_protocols,
                    timeout=PROXY_TIMEOUT,
                    headers={"User-Agent": "Mozilla/5.0"},
                    verify=False
                )
                if resp.status_code == 200:
                    proxy_ip = resp.json().get("query", "未知") if "ip-api.com" in test_url else resp.text.strip() or "未知"
                    return {"valid": True, "proxy": proxy_url, "msg": f"✅ 代理有效 IP:{proxy_ip}"}
            except requests.exceptions.ProxyError:
                print(f"⚠️  代理重试{retry+1}：连接拒绝")
            except requests.exceptions.Timeout:
                print(f"⚠️  代理重试{retry+1}：连接超时")
            except Exception as e:
                print(f"⚠️  代理重试{retry+1}：{str(e)[:20]}")
        time.sleep(1)
    return {"valid": False, "proxy": None, "msg": f"❌ 代理无效：多次检测失败"}

# 新增读取id函数，初次运行则自行生成
def getValue(id):
    id1=generate_device_id().upper()
    id2=generate_device_id().upper()
    file=os.path.join(os.path.dirname(__file__), DataFile)
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保读取的data中包含当前id的键（防止文件有数据但无此id）
                if str(id) not in data:
                    data[str(id)] = [id1,id2]
                    # 同步写入文件，保证数据一致性
                    with open(file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            data={}
            data[str(id)]=[id1,id2]
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print('初次运行，创建配置文件，请勿删除',file)
        return data[id]
    except json.JSONDecodeError:
        print(f'配置文件损坏，请查看配置文件 {DataFile} 是否还有数据，若有请备份，若无请手动删除该文件后重新运行')
        sys.exit(json.JSONDecodeError)

def load_accounts_from_pg():
    """加载账号（保持原逻辑）"""
    accounts = []
    pg_env = os.environ.get(ENV_VAR_NAME, "").strip()
    if not pg_env:
        return accounts
    account_lines = [line.strip() for line in pg_env.split("\n") if line.strip()]
    for seq, line in enumerate(account_lines, 1):
        parts = line.split("&")
        if len(parts) < 2:
            print(f"⚠️  跳过无效账号（第{seq}行）：格式错误")
            continue
        secretId = parts[0].strip()
        secretKey = parts[1].strip()
        proxy = parts[2].strip() if len(parts)>=3 and parts[2].strip() else ""
        did1,did2=getValue(secretId)
        if did1 and did2:
            print('获取设备id成功')
        accounts.append({
            "seq": seq,
            "secretId": secretId,
            "secretKey": secretKey,
            "deviceId": did1,
            "proxy": proxy
        })
        accounts.append({
            "seq": seq,
            "secretId": secretId,
            "secretKey": secretKey,
            "deviceId": did2,
            "proxy": proxy
        })
        # 修改device_id获取方式,每个账号自动生成两个id保存到文件中
        with limit_lock:
            account_limit_status[seq] = False
    return accounts

def all_accounts_limited():
    """检查所有账号是否都已超限（保持原逻辑）"""
    with limit_lock:
        return all(status for status in account_limit_status.values())

def get_final_concurrent_num(account_count):
    """计算最终并发数（保持原逻辑）"""
    return min(CUSTOM_THREAD_NUM, account_count, MAX_THREAD_NUM)
def account_run(account):
    """账号执行核心逻辑（修改机型获取逻辑，绑定固定机型）"""
    seq = account["seq"]
    secretId = account["secretId"].strip()
    secretKey = account["secretKey"].strip()
    proxy = account["proxy"]
    
    total_reward = 0.0
    successful_ads = 0
    proxies = None
    token = ""
    is_limit = False
    # 修改device_id获取方式
    device_id = account["deviceId"]
    # 关键修改：调用新增函数，基于secretId获取固定设备信息（同一账号始终相同）
    device_info = get_fixed_device_info(secretId)
    user_agent = generate_random_user_agent(device_info)
    
    # 代理检测（保持原逻辑）
    proxy_res = proxy_check(proxy)
    if proxy_res["valid"] and proxy_res["proxy"]:
        proxies = {"http": proxy_res["proxy"], "https": proxy_res["proxy"]}
    
    print(f"\n=== 账号 {seq} 开始任务 ===")
    print(f"账号 {seq} - {proxy_res['msg']}")
    print(f"账号 {seq} - 固定设备：{device_info['brand']} {device_info['model']}（Android {device_info['android_version']}）")
    print(f"账号 {seq} - 设备ID：{device_id}... | UA：{user_agent[:30]}...")
    
    # 基础请求头配置（保持原逻辑）
    base_headers = {
        "app-device": json.dumps({
            "id": device_id,
            "brand": device_info["brand"],
            "model": device_info["model"],
            "platform": "android",
            "system": f"Android {device_info['android_version']}",
            "version": "1.0.0"
        }, ensure_ascii=False),
        "app-version": "1.0.0",
        "user-agent": user_agent,
        "Host": "api.zhenghui.xyz",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    session = requests.Session()
    session.headers.update(base_headers)
    session.timeout = REQ_TIMEOUT
    session.verify = False
    if proxies:
        session.proxies.update(proxies)
    
    try:
        # 登录逻辑（保持原逻辑）
        login_success = False
        login_headers = {"Content-Type": "application/json"}
        login_payload = {"secretId": secretId, "secretKey": secretKey}
        
        for retry_idx in range(LOGIN_RETRY + 1):
            print(f"\n账号 {seq} - 登录尝试第{retry_idx+1}/{LOGIN_RETRY+1}次...")
            try:
                resp = session.post(LOGIN_URL, json=login_payload, headers=login_headers)
                resp.raise_for_status()
                login_result = resp.json()
                token = (
                    login_result.get("token")
                    or login_result.get("data", {}).get("token")
                    or login_result.get("access_token")
                    or login_result.get("data", {}).get("access_token")
                )
                if token:
                    print(f"账号 {seq} - 登录成功！Token：{token[:15]}...")
                    login_success = True
                    break
                else:
                    print(f"账号 {seq} - 登录无有效Token | 响应：{login_result.get('message', '无响应')}")
            except requests.exceptions.Timeout:
                print(f"账号 {seq} - 登录超时")
            except requests.exceptions.ProxyError:
                print(f"账号 {seq} - 代理连接失败")
            except json.JSONDecodeError:
                print(f"账号 {seq} - 响应解析失败 | 内容：{resp.text[:30]}")
            except Exception as e:
                print(f"账号 {seq} - 登录异常：{str(e)[:30]}")
            if retry_idx == LOGIN_RETRY - 1 and proxies:
                print(f"账号 {seq} - 代理登录失败，切换本地IP重试...")
                session.proxies.clear()
                proxies = None
            time.sleep(3)
        
        if not login_success:
            print(f"账号 {seq} - 多次登录失败，停止执行")
            with limit_lock:
                account_limit_status[seq] = True
            return
        
        # 广告观看逻辑（保持原逻辑）
        ad_headers = {"Authorization": f"Bearer {token}"}
        for loop in range(1, LOOP_COUNT + 1):
            if is_limit or all_accounts_limited():
                break
            print(f"\n账号 {seq} - === 第 {loop}/{LOOP_COUNT} 轮循环开始 ===")
            try:
                print(f"账号 {seq} - 正在获取广告...")
                ad_resp = session.get(AD_URL, headers=ad_headers)
                ad_resp.raise_for_status()
                ad_result = ad_resp.json()
                code = ad_result.get("code", -1)
                data = ad_result.get("data", {})
                data_status = data.get("status", -1)
                
                if data_status == 4000503:
                    err_msg = data.get("message", "今日播放量已超限")
                    print(f"账号 {seq} - ⚠️  {err_msg}，停止执行")
                    is_limit = True
                    with limit_lock:
                        account_limit_status[seq] = True
                    break
                if code != 0 or data_status != 0 or "result" not in data:
                    print(f"账号 {seq} - 广告获取失败 | 原因：{data.get('message', '无广告数据')}")
                    time.sleep(5)
                    continue
                
                ad_data = data["result"]
                if "id" not in ad_data:
                    print(f"账号 {seq} - 广告数据缺少ID字段")
                    time.sleep(5)
                    continue
                ad_id = ad_data["id"]
                ad_title = ad_data.get("title", "未知标题")
                ad_reward_str = ad_data.get("reward", "0")
                print(f"账号 {seq} - 广告信息：ID={ad_id} | 标题={ad_title[:20]}... | 奖励={ad_reward_str}")
                
                # 奖励解析（保持原逻辑）
                current_ad_reward = 0.0
                try:
                    if isinstance(ad_reward_str, (int, float)):
                        current_ad_reward = float(ad_reward_str)
                    elif isinstance(ad_reward_str, str):
                        match = re.search(r'(\d+(?:\.\d+)?)', ad_reward_str)
                        if match:
                            current_ad_reward = float(match.group(1))
                except Exception as e:
                    print(f"账号 {seq} - 奖励解析失败：{str(e)}")
                
                # 提交播放记录（保持原逻辑）
                print(f"账号 {seq} - 提交播放记录...")
                play_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                play_payload = {
                    "id": ad_id,
                    "clientIp": "0.0.0.0",
                    "playTime": datetime.utcnow().isoformat() + "Z",
                    "deviceInfo": {"deviceId": device_id, "platform": "android"}
                }
                play_resp = session.post(AD_PLAY_URL, json=play_payload, headers=play_headers)
                play_resp.raise_for_status()
                play_result = play_resp.json()
                play_id = play_result.get("data", {}).get("id", "")
                
                if not play_id:
                    print(f"账号 {seq} - 无有效播放ID")
                    time.sleep(5)
                    continue
                print(f"账号 {seq} - 播放记录成功 | 播放ID：{play_id}")
                
                # 等待广告播放完成（保持原逻辑）
                delay_seconds = random.randint(30, 50)
                print(f"账号 {seq} - 等待 {delay_seconds} 秒后提交结束记录...")
                time.sleep(delay_seconds)
                
                # 提交结束记录（保持原逻辑）
                print(f"账号 {seq} - 提交结束记录...")
                ended_headers = play_headers.copy()
                ended_payload = {
                    "id": play_id,
                    "clientIp": "0.0.0.0",
                    "endTime": datetime.utcnow().isoformat() + "Z",
                    "deviceInfo": {"deviceId": device_id, "platform": "android"}
                }
                ended_resp = session.post(AD_ENDED_URL, json=ended_payload, headers=ended_headers)
                ended_resp.raise_for_status()
                ended_result = ended_resp.json()
                
                if ended_result.get("message") == "success":
                    successful_ads += 1
                    total_reward += current_ad_reward
                    cash_reward = total_reward / POINT_TO_CASH_RATIO
                    print(f"账号 {seq} - 第{loop}轮成功！")
                    print(f"  - 本次：{current_ad_reward}积分 | 累计：{total_reward:.2f}积分（约{cash_reward:.2f}元）")
                    print(f"  - 成功广告数：{successful_ads}/{loop}")
                else:
                    print(f"账号 {seq} - 第{loop}轮失败 | 原因：{ended_result.get('message', '未知')}")
            
            except requests.exceptions.Timeout:
                print(f"账号 {seq} - 第{loop}轮超时")
                time.sleep(10)
            except requests.exceptions.ProxyError:
                print(f"账号 {seq} - 第{loop}轮代理断开，切换本地IP继续")
                session.proxies.clear()
                proxies = None
                time.sleep(10)
            except Exception as e:
                print(f"账号 {seq} - 第{loop}轮异常：{str(e)[:30]} | 10秒后重试")
                time.sleep(10)
            
            if loop < LOOP_COUNT and not is_limit and not all_accounts_limited():
                print(f"账号 {seq} - 本轮结束，等待20秒后开始下一轮...")
                time.sleep(20)
    
    finally:
        session.close()
        print(f"\n=== 账号 {seq} 任务结束 ===")
        print(f"📊 统计：成功{successful_ads}个 | 总积分{total_reward:.2f}（约{total_reward/POINT_TO_CASH_RATIO:.2f}元）")
        print(f"🔚 原因：{'今日超限' if is_limit else '完成所有轮次/全账号超限'}")

if __name__ == "__main__":
    """主函数（保持原逻辑）"""
    print(f"对生成设备id进行修改，创建文件到目录来保存设备id，请勿删除文件： {DataFile} \n由于修改了代码逻辑，建议一个账号使用一个代理（即：两个设备一个代理）")
    print(f"若已有device_id，在 {DataFile} 中修改对应secretId下的内容即可")

    ACCOUNT_LIST = load_accounts_from_pg()

    if not ACCOUNT_LIST:
        print("===== 请配置环境变量 =====")
        print(f"变量1：{ENV_VAR_NAME} = 'secretId&secretKey&代理'（多账号换行分隔）")
        print(f"变量2：pgxc = 线程数（默认{DEFAULT_THREAD_NUM}，最大{MAX_THREAD_NUM}）")
        print(f"变量3：RUN_LOOP_COUNT = 循环次数（默认{LOOP_COUNT}）")
        sys.exit()
    
    account_count = len(ACCOUNT_LIST)
    FINAL_THREAD_NUM = get_final_concurrent_num(account_count)
    
    print("===== 任务启动 =====")
    print(f"📊 账号数{account_count} | 线程数{FINAL_THREAD_NUM} | 循环数{LOOP_COUNT}轮")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("---------------------------")
    
    # 启动线程池执行任务（保持原逻辑）
    executor = ThreadPoolExecutor(max_workers=FINAL_THREAD_NUM)
    futures = []
    for acc in ACCOUNT_LIST:
        futures.append(executor.submit(account_run, acc))
        time.sleep(1)
    
    # 监控任务完成状态（保持原逻辑）
    while True:
        if all_accounts_limited() or all(future.done() for future in futures):
            executor.shutdown(wait=False)
            break
        time.sleep(20)
    
    print(f"\n===== 任务结束 =====")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔚 原因：{'所有账号超限' if all_accounts_limited() else '所有账号完成'}")


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
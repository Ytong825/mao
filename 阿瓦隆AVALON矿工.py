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

# 下载注册地址:https://app.avalonavs.com/app/webapp/#/Register?code=52589129

# 安装 requests PySocks fake_useragent 依赖
# AVALON挖矿，每个币目前1R
# 环境变量AWL_TOKEN 变量值：开启https抓包Authorization 示例：eyJhbGciOiJI...............
# 定时设置 0 0 */8 * * ?（此表达式将使任务在每天的0点、8点、16点执行）
# 推广奖励翻倍升级：原下一级20%、下二级10%、下3-10级3%，调整为下一级40%、下二级20%、下3-10级6%，收益直接翻倍

import requests
import os
import concurrent.futures
import threading
from datetime import datetime
import random
import string
import hashlib
import base64
from fake_useragent import UserAgent
from urllib.parse import quote


# == 配置区域 ==
# 并发工作者数量
CONCURRENT_WORKERS = 2

# 是否显示请求详情（调试用）
DEBUG = False

# == 工具函数 ==
def get_logger(account_id):
    # """为每个账号创建独立的日志器"""
    account_tag = f"[账号{account_id}]"
    def log(level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_icons = {"INFO": "📝", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "PROCESS": "🔄"}
        icon = level_icons.get(level, "📝")
        print(f"{timestamp} {account_tag} {icon} {message}")
    return log

def fetch_awl_tokens_from_env():
    """从环境变量中读取AWL_TOKEN（单个token）或AWL_TOKEN1到AWL_TOKEN999（账号密码格式）"""
    accounts = {}
    
    # 先检查是否存在单个AWL_TOKEN环境变量
    single_token = os.getenv("AWL_TOKEN")
    if single_token and single_token.strip():
        # 如果存在单个token，直接使用它
        accounts[1] = {
            "login_name": "direct_token",
            "password": "direct_token",
            "real_name": "",
            "id_card": "",
            "phone": "",
            "proxy": None,
            "direct_token": single_token.strip()  # 存储直接提供的token
        }
        return accounts
    
    # 如果没有单个token，再尝试读取AWL_TOKEN1到AWL_TOKEN999
    for i in range(1, 1000):
        env_name = f"AWL_TOKEN{i}"
        token_value = os.getenv(env_name)
        if token_value and token_value.strip():
            parts = token_value.strip().split("#")
            if len(parts) < 5:
                print(f"⚠️ 警告：环境变量 {env_name} 格式错误，至少需要5个部分（用户名#密码#姓名#身份证#手机号），已跳过。")
                continue
            login_name = parts[0].strip()
            password = parts[1].strip()
            real_name = parts[2].strip()
            id_card = parts[3].strip()
            phone = parts[4].strip()
            proxy = None
            if len(parts) > 5 and parts[5].strip():
                proxy_str = parts[5].strip()
                if proxy_str.startswith("socks5://"):
                    proxy = {"http": proxy_str, "https": proxy_str}
                    accounts[i] = {
                        "login_name": login_name,
                        "password": password,
                        "real_name": real_name,
                        "id_card": id_card,
                        "phone": phone,
                        "proxy": proxy
                    }
            else:
                accounts[i] = {
                  "login_name": login_name,
                  "password": password,
                  "real_name": real_name,
                  "id_card": id_card,
                  "phone": phone,
                  "proxy": None
                }
            return accounts
    
    return accounts
                
# == 核心请求函数 ==
def make_request(url, headers, method="GET", data=None, log_func=None, proxy=None):
    """统一的请求函数，带日志和错误处理，支持代理"""
    try:
        request_kwargs = {
            "headers": headers,
            "timeout": 30
        }
            # 如果有代理配置，添加到请求参数中
        if proxy:
            request_kwargs["proxies"] = proxy
            if DEBUG and log_func:
                log_func("INFO", f"使用代理: {proxy}")
        
        if method.upper() == "GET":
            response = requests.get(url, **request_kwargs)
        elif method.upper() == "POST":
            request_kwargs["data"] = data
            response = requests.post(url, **request_kwargs)
        elif method.upper() == "OPTIONS":
            response = requests.options(url, **request_kwargs)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
            
        if DEBUG and log_func:
            log_func("INFO", f"请求 {method} {url} - 状态码: {response.status_code}")
        return response
    except Exception as e:
        if log_func:
            log_func("ERROR", f"请求失败: {str(e)}")
        return None
    
# == 账号任务流程 ==
def process_single_account(account_id, account_info):
    """处理单个账号的完整流程"""
    login_name = account_info["login_name"]
    password = account_info["password"]
    real_name = account_info["real_name"]
    id_card = account_info["id_card"]
    phone = account_info["phone"]
    proxy = account_info.get("proxy")
    direct_token = account_info.get("direct_token")  # 检查是否有直接提供的token

    log = get_logger(account_id)
    log("INFO", f"开始处理账号: {login_name}")
    if proxy:
        log("INFO", f"使用代理服务器")
    
    # 生成User-Agent
    ua = UserAgent()
    
    # 检查是否有直接提供的token
    if direct_token:
        log("PROCESS", "使用直接提供的Token...")
        awl_token = direct_token
        if not awl_token.startswith('Bearer '):
            awl_token = f'Bearer {awl_token}'  # 确保token格式正确
        log("SUCCESS", "Token已准备好")
    else:
        # ==================== 执行登录获取token ====================
        log("PROCESS", "正在执行登录...")

        def generate_device_uuid(username: str) -> str:
            hash_obj = hashlib.sha256(username.encode('utf-8'))
            hash_bytes = hash_obj.digest()
            b64_str = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')
            uuid_suffix = b64_str[:11]
            device_uuid = f"0.{uuid_suffix}"
            return device_uuid

        def generate_random_boundary(length=30):
            chars = string.ascii_letters + string.digits
            return ''.join(random.choice(chars) for _ in range(length))

        def build_multipart_data(boundary, login_name, password, device_uuid):
            data_lines = []
            data_lines.append(f'--{boundary}')
            data_lines.append('Content-Disposition: form-data; name="loginName"')
            data_lines.append('')
            data_lines.append(login_name)
            data_lines.append(f'--{boundary}')
            data_lines.append('Content-Disposition: form-data; name="password"')
            data_lines.append('')
            data_lines.append(password)
            data_lines.append(f'--{boundary}')
            data_lines.append('Content-Disposition: form-data; name="deviceUuid"')
            data_lines.append('')
            data_lines.append(device_uuid)
            data_lines.append(f'--{boundary}--')
            data_lines.append('')
            return '\r\n'.join(data_lines)

        # 执行登录请求
        boundary = generate_random_boundary()
        device_uuid = generate_device_uuid(login_name)
        headers = {
            "Host": "app.avalonavs.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Authorization": "",
            "User-Agent": ua.random,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Origin": "http://app.avalonavs.com",
            "X-Requested-With": "com.avalonavs.app",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "http://app.avalonavs.com/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        data = build_multipart_data(boundary, login_name, password, device_uuid)
        url = "https://app.avalonavs.com/api/app/authentication/login"

        try:
            options_headers = {
                "Host": "app.avalonavs.com",
                "Connection": "keep-alive",
                "Accept": "*/*",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization",
                "Origin": "http://app.avalonavs.com",
                "User-Agent": headers["User-Agent"],
                "Sec-Fetch-Mode": "cors",
                "X-Requested-With": "com.avalonavs.app",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Dest": "empty",
                "Referer": "http://app.avalonavs.com/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            
            res_options = make_request(url, options_headers, "OPTIONS", log_func=log, proxy=proxy)
            if DEBUG and res_options:
                log("INFO", f"预检请求状态码: {res_options.status_code}")
            
            response = make_request(url, headers, "POST", data=data, log_func=log, proxy=proxy)
            
            if response and response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 0:
                        token = result.get('data')
                        if token and token.startswith('Bearer '):
                            awl_token = token  # 获取到的token
                            log("SUCCESS", "登录成功，获取到Token")
                        else:
                            log("ERROR", f"登录响应中未找到有效Token: {result}")
                            return {"account_id": account_id, "status": "login_failed"}
                    else:
                        log("ERROR", f"登录失败: {result.get('msg')}")
                        return {"account_id": account_id, "status": "login_failed"}
                except Exception as e:
                    log("ERROR", f"解析登录响应失败: {str(e)}")
                    return {"account_id": account_id, "status": "login_failed"}
            else:
                status = response.status_code if response else "无响应"
                log("ERROR", f"登录请求失败，状态码: {status}")
                return {"account_id": account_id, "status": "login_failed"}
        except Exception as e:
            log("ERROR", f"登录过程异常: {str(e)}")
            return {"account_id": account_id, "status": "login_failed"}

        # ==================== 执行实名认证 ====================
        if real_name and id_card and phone:
            log("PROCESS", "执行实名认证...")
            # 对中文姓名进行URL编码
            try:
                encoded_real_name = quote(real_name)
            except NameError:
                # 如果quote未定义或real_name不是中文需要编码，则使用原值
                encoded_real_name = real_name
            except Exception:
                encoded_real_name = real_name

            # 构建实名认证请求URL和头部
            auth_headers = {
                "Host": "app.avalonavs.com",
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*",
                "Authorization": awl_token,
                "User-Agent": headers["User-Agent"],
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://app.avalonavs.com",
                "X-Requested-With": "com.avalonavs.app",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "http://app.avalonavs.com/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            }

            # 构建实名认证数据
            auth_data = f"realName={encoded_real_name}&idCard={id_card}&phone={phone}&idCardPhoto1=&idCardPhoto2=&idCardPhoto3="
            auth_url = "https://app.avalonavs.com/api/app/api/customerEdit/realNameAuth"
            
            # 调用实名认证接口
            auth_response = make_request(auth_url, auth_headers, "POST", data=auth_data, log_func=log, proxy=proxy)

            if auth_response and auth_response.status_code == 200:
                try:
                    auth_result = auth_response.json()
                    if auth_result.get('code') == 0:
                        log("SUCCESS", f"实名认证成功: {auth_result.get('msg', '成功')}")
                    else:
                        log("WARNING", f"实名认证失败: {auth_result.get('msg', '未知错误')}")
                        # 实名失败不影响后续流程，继续执行
                except Exception as e:
                    log("ERROR", f"解析实名认证响应失败: {str(e)}")
            else:
                log("ERROR", "实名认证请求失败")

    # """处理单个账号的完整流程"""
    headers_base = {
        "Host": "app.avalonavs.com",
        "Connection": "keep-alive",
        "User-Agent": ua.random,  # 使用ua变量生成User-Agent，确保在直接使用token时也能正常工作
        "X-Requested-With": "com.avalonavs.app",
        "Origin": "http://app.avalonavs.com",
        "Referer": "http://app.avalonavs.com/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # -------------------- 1. 获取账号基本信息 --------------------
    log("PROCESS", "获取账号基本信息...")
    url_info = "https://app.avalonavs.com/api/app/api/customer_ext/personalDetails"
    headers_info = headers_base.copy()
    headers_info.update({
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Authorization": awl_token,
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    })
    res = make_request(url_info, headers_info, "GET", log_func=log, proxy=proxy)
    if res and res.status_code == 200:
        try:
            person_data = res.json()
            if person_data.get('code') == 0:
                data = person_data['data']
                log("SUCCESS", f"登录用户: {data.get('loginName', 'N/A')}")
                log("SUCCESS", f"总币数AVS: {data.get('coin', 'N/A')}")
                log("SUCCESS", f"总算力: {data.get('hashRate', 'N/A')}")
                log("SUCCESS", f"昨日收益: {data.get('yesterdayIncome', 'N/A')}")
            else:
                log("WARNING", f"获取信息失败: {person_data.get('msg', '未知错误')}")
        except Exception as e:
            log("ERROR", f"解析账号信息响应失败: {str(e)}")
    else:
        log("ERROR", "获取账号基本信息请求失败")

    # -------------------- 2. 执行签到 --------------------
    log("PROCESS", "执行签到...")
    url_sign = "https://app.avalonavs.com/api/app/api/signIn/keepSignIn"
    headers_sign = headers_base.copy()
    headers_sign.update({
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Authorization": awl_token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    })
    res = make_request(url_sign, headers_sign, "POST", log_func=log, proxy=proxy, data="")
    if res and res.status_code == 200:
        try:
            sign_data = res.json()
            if sign_data.get('code') == 0:
                log("SUCCESS", f"签到成功: {sign_data.get('msg', '成功')}")
            else:
                log("WARNING", f"签到失败: {sign_data.get('msg', '未知错误')}")
        except Exception as e:
            log("ERROR", f"解析签到响应失败: {str(e)}")
    else:
        log("ERROR", "签到请求失败")

    # -------------------- 3. 检查并收取币 --------------------
    log("PROCESS", "检查可收取的币...")
    url_income = "https://app.avalonavs.com/api/app/api/income/incomeList?balanceCapitalTyp=coin"
    headers_income = headers_base.copy()
    headers_income.update({
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Authorization": awl_token,
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    })
    res = make_request(url_income, headers_income, "GET", log_func=log, proxy=proxy)
    receive_count = 0
    if res and res.status_code == 200:
        try:
            income_data = res.json()
            if income_data.get('code') == 0:
                items = income_data.get('data', [])
                if items:
                    log("INFO", f"发现 {len(items)} 个可收取项")
                    for item in items:
                        income_id = item.get('id')
                        if income_id:
                            log("PROCESS", f"收取ID为 {income_id} 的收益...")
                            url_receive = f"https://app.avalonavs.com/api/app/api/income/receiveIncome/{income_id}"
                            headers_receive = headers_base.copy()
                            headers_receive.update({
                                "Accept": "application/json, text/plain, */*",
                                "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                                "sec-ch-ua-mobile": "?1",
                                "sec-ch-ua-platform": '"Android"',
                                "Authorization": awl_token,
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Sec-Fetch-Site": "cross-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty"
                            })
                            receive_res = make_request(url_receive, headers_receive, "POST", log_func=log, proxy=proxy, data=f"id={income_id}")
                            if receive_res and receive_res.status_code == 200:
                                receive_data = receive_res.json()
                                if receive_data.get('code') == 0:
                                    log("SUCCESS", f"收取ID {income_id} 成功")
                                    receive_count += 1
                                else:
                                    log("WARNING", f"收取ID {income_id} 失败: {receive_data.get('msg', '未知错误')}")
                            else:
                                log("ERROR", f"收取ID {income_id} 请求失败")
                else:
                    log("INFO", "当前没有可收取的币")
            else:
                log("WARNING", f"获取收益列表失败: {income_data.get('msg', '未知错误')}")
        except Exception as e:
            log("ERROR", f"解析收益列表响应失败: {str(e)}")
    else:
        log("ERROR", "获取收益列表请求失败")

    log("SUCCESS", f"账号流程执行完毕。成功收取 {receive_count} 个币。")
    return {"account_id": account_id, "receive_count": receive_count, "status": "completed"}

# == 主程序 ==
def main():
    # """主函数：打印横幅，读取令牌，并发执行"""
    print("=" * 70)
    print("🚀 AVALON 多账号并发自动签到收币脚本")
    print("📌 邀请地址: https://app.avalonavs.com/app/webapp/#/Register?code=52589129")
    print("=" * 70)
    art = """
    原神启动
    """
    print(art)
    print("=" * 70)
    print(f"⚙️ 配置：并发工作者数 = {CONCURRENT_WORKERS}, 调试模式 = {DEBUG}")
    print("=" * 70)
    # 从环境变量读取令牌
    awl_tokens = fetch_awl_tokens_from_env()
    token_count = len(awl_tokens)

    if token_count == 0:
        print("❌ 错误：未在环境变量中找到任何有效的 AWL_TOKEN (AWL_TOKEN1 - AWL_TOKEN999)。")
        print("💡 提示：请设置环境变量，例如：export AWL_TOKEN1='your_token_here'")
        return

    print(f"✅ 成功从环境变量中读取到 {token_count} 个账号令牌。")
    print(f"📋 账号ID列表: {list(awl_tokens.keys())}")
    print("-" * 70)

    # 使用线程池并发执行
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        # 提交所有任务
        future_to_account = {
            executor.submit(process_single_account, acc_id, acc_info): acc_id
            for acc_id, acc_info in awl_tokens.items()
        }

        # 处理完成的任务
        for future in concurrent.futures.as_completed(future_to_account):
            account_id = future_to_account[future]
            try:
                result = future.result(timeout=120)  # 每个任务最多等待120秒
                results.append(result)
            except concurrent.futures.TimeoutError:
                print(f"⏰ 超时：账号{account_id} 执行超时")
                results.append({"account_id": account_id, "status": "timeout"})
            except Exception as e:
                print(f"💥 异常：账号{account_id} 执行出错: {str(e)}")
                results.append({"account_id": account_id, "status": "error", "error": str(e)})

    # ====================== 执行结果汇总 ======================
    print("=" * 70)
    print("📊 所有账号任务执行完成！汇总报告：")
    print("-" * 70)

    status_count = {"completed": 0, "timeout": 0, "error": 0}
    total_received = 0

    for result in results:
        status = result.get("status", "unknown")
        status_count[status] = status_count.get(status, 0) + 1
        if status == "completed":
            total_received += result.get("receive_count", 0)

    print(f"✅ 成功完成: {status_count.get('completed', 0)} 个账号")
    print(f"⏰ 执行超时: {status_count.get('timeout', 0)} 个账号")
    print(f"❌ 执行错误: {status_count.get('error', 0)} 个账号")
    print(f"💰 总计收取: {total_received} 个AVS币")
    print("=" * 70)
    print("🎉 脚本执行结束！感谢使用。")
    print("=" * 70)

if __name__ == "__main__":
    main()

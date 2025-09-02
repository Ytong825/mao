import time
import os
import json
import numpy as np
import urllib3
import re
import subprocess
import socket
import traceback
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 日志颜色
COLOR_CODES = {
    "RED": "38;5;124",
    "GREEN": "38;5;22",
    "BLUE": "38;5;19",
    "YELLOW": "38;5;130",
    "PURPLE": "38;5;92",
    "BOLD": "1"
}

def color_text(text, color_code):
    """为文本添加颜色"""
    return f"\033[{color_code}m{text}\033[0m"

def log_base(msg, color, emoji):
    """基础日志函数"""
    time_str = datetime.now().strftime('%H:%M:%S')
    time_colored = color_text(time_str, color)
    print(f"{time_colored} {emoji} {msg}")

def log_info(msg, emoji="🌸"):
    log_base(msg, COLOR_CODES['BLUE'], emoji)

def log_success(msg, emoji="✨"):
    log_base(msg, COLOR_CODES['GREEN'], emoji)

def log_warning(msg, emoji="⚠️"):
    log_base(msg, COLOR_CODES['YELLOW'], emoji)

def log_error(msg, emoji="❌"):
    log_base(msg, COLOR_CODES['RED'], emoji)

def log_debug(data, emoji="🔍"):
    """调试日志"""
    time_str = datetime.now().strftime('%H:%M:%S')
    time_colored = color_text(time_str, COLOR_CODES['BLUE'])
    if isinstance(data, (dict, list)):
        print(f"{time_colored} {emoji} 调试数据:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"{time_colored} {emoji} {data}")

class AccountResult:
    """账号处理结果"""
    def __init__(self):
        self.total_accounts = 0
        self.success_count = 0
        self.fail_count = 0
        self.rewards = {}
        self.details = {}

    def add_success(self, wx_openid, remark, reward):
        self.success_count += 1
        self.rewards[wx_openid] = reward
        self.details[wx_openid] = {'remark': remark, 'reward': reward, 'status': '成功'}

    def add_fail(self, wx_openid, remark):
        self.fail_count += 1
        self.rewards[wx_openid] = 0.0
        self.details[wx_openid] = {'remark': remark, 'reward': 0.0, 'status': '失败'}

    def total_reward(self):
        return sum(self.rewards.values())

class Config:
    """配置类"""
    def __init__(self):
        self.XL_HOST = os.getenv("XL_HOST", "").strip()
        self.XL_ID = os.getenv("XL_ID", "").strip()
        self.XL_USER_LIST = [user.strip() for user in os.getenv("xlwy", "").split("&") if user.strip()]
        self.XL_MIN_SEGMENT = int(os.getenv("XL_MIN_SEGMENT", "300"))
        self.XL_MAX_SEGMENT = int(os.getenv("XL_MAX_SEGMENT", "1800"))
        self.XL_TIMEOUT = int(os.getenv("XL_TIMEOUT", "30"))
        self.XL_RETRY = int(os.getenv("XL_RETRY", "5"))
        self.XL_DELAY_MIN = int(os.getenv("XL_DELAY_MIN", "5"))
        self.XL_DELAY_MAX = int(os.getenv("XL_DELAY_MAX", "15"))

def validate_config(cfg):
    """验证配置"""
    errors = []
    if not cfg.XL_HOST: 
        errors.append("缺少域名(XL_HOST)")
    if not cfg.XL_ID: 
        errors.append("缺少课程ID(XL_ID)")
    if not cfg.XL_USER_LIST:
        errors.append("账号列表为空")
    elif any(len(u.split('#')) != 2 for u in cfg.XL_USER_LIST):
        errors.append("账号格式错误: 应为 wx_openid#备注")
    if cfg.XL_DELAY_MIN > cfg.XL_DELAY_MAX:
        errors.append("延迟时间设置错误")
    return errors

def random_delay(min_sec=0.5, max_sec=2.0):
    """生成随机延迟"""
    delay = np.random.uniform(min_sec, max_sec)
    actions = ["喝奶茶", "数星星", "和云朵聊天", "抓蝴蝶", "整理花园"]
    action = np.random.choice(actions)
    log_info(f"{action}中... ({delay:.2f}秒)")
    time.sleep(delay)
    return delay

def parse_video_time(time_str):
    """解析视频时长"""
    try:
        hms, _ = time_str.split('.')
        hours, mins, secs = hms.split(':')
        return int(hours)*3600 + int(mins)*60 + int(secs)
    except:
        log_warning("视频时长解析失败，使用默认值(3600秒)")
        return 3600

def curl_request(method, url, headers=None, data=None):
    """使用curl执行HTTP请求"""
    # 构建curl命令
    cmd = ["curl", "-s", "-i", "-X", method, "--http1.1", "--tlsv1.2", "--tls-max", "1.2", "-k"]
    
    # 添加请求头
    if headers:
        for key, value in headers.items():
            cmd.append("-H")
            cmd.append(f"{key}: {value}")
    
    # 添加请求体
    if data:
        cmd.append("-d")
        cmd.append(json.dumps(data))
    
    # 添加URL
    cmd.append(url)
    
    # 执行命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log_debug(f"curl命令失败: {' '.join(cmd)}")
            log_debug(f"错误信息: {result.stderr}")
            return {"error": f"curl错误: {result.returncode}", "stderr": result.stderr}
        
        # 解析响应
        response_text = result.stdout
        
        # 尝试多种方式查找头部结束位置
        header_end = -1
        possible_delimiters = ["\r\n\r\n", "\n\n", "\r\r"]
        
        for delimiter in possible_delimiters:
            header_end = response_text.find(delimiter)
            if header_end != -1:
                break
        
        if header_end == -1:
            # 如果找不到标准分隔符，尝试查找第一个空行
            lines = response_text.splitlines()
            for i, line in enumerate(lines):
                if not line.strip():  # 空行
                    header_end = sum(len(line) + 1 for line in lines[:i]) - 1
                    break
        
        if header_end == -1:
            # 如果还是找不到，返回整个响应
            return {"error": "无法解析响应头", "raw_response": response_text}
        
        headers_text = response_text[:header_end]
        body_text = response_text[header_end+len(delimiter):]
        
        # 解析状态码
        status_line = headers_text.splitlines()[0]
        try:
            status_code = int(status_line.split(" ")[1])
        except (IndexError, ValueError):
            status_code = 0
        
        # 解析JSON响应
        try:
            json_data = json.loads(body_text)
            return {"status_code": status_code, "data": json_data}
        except:
            return {"status_code": status_code, "data": body_text}
    
    except subprocess.TimeoutExpired:
        return {"error": "请求超时"}
    except Exception as e:
        return {"error": f"请求异常: {str(e)}"}

def simulate_watch_time(wx_openid, headers, user_activity_id, xlhost, cfg, video_time):
    """模拟观看视频时间"""
    log_info(f"视频时长: {video_time//60}分{video_time%60}秒")
    
    segments = []
    remaining = video_time
    
    # 分段逻辑
    while remaining > 0:
        max_seg = min(cfg.XL_MAX_SEGMENT, remaining)
        min_seg_candidate = max(cfg.XL_MIN_SEGMENT, remaining // 3)
        min_seg = min(min_seg_candidate, max_seg)
        
        if min_seg >= max_seg:
            segment = max_seg
        else:
            segment = np.random.randint(min_seg, max_seg + 1)
        
        segments.append(segment)
        remaining -= segment
        
        if len(segments) >=2 and remaining < cfg.XL_MIN_SEGMENT:
            segments[-1] += remaining
            remaining = 0
    
    if len(segments) > 1:
        first = segments.pop(0)
        np.random.shuffle(segments)
        segments.insert(0, first)
    
    # 学习描述词
    study_actions = ["听课", "学习", "吸收知识", "做笔记", "思考"]
    
    for idx, sec in enumerate(segments, 1):
        action = np.random.choice(study_actions)
        for attempt in range(cfg.XL_RETRY):
            try:
                if idx > 1:
                    random_delay(0.3, 1.2)
                
                # 使用curl发送请求
                url = f"https://{xlhost}/api-user/v1/activityWatchVideo"
                data = {"userActivityId": user_activity_id, "second": sec}
                response = curl_request("POST", url, headers, data)
                
                if "error" in response:
                    raise Exception(response["error"])
                    
                if response.get("data", {}).get("status") == "success":
                    total_sec = sum(segments[:idx])
                    minutes, seconds = divmod(total_sec, 60)
                    log_success(f"{action}中 | 第{idx}节 | 累计: {minutes}分{seconds}秒")
                    break
                else:
                    log_warning(f"请求失败 | 尝试{attempt+1}/{cfg.XL_RETRY}")
            except Exception as e:
                log_warning(f"错误: {str(e)} | 尝试{attempt+1}/{cfg.XL_RETRY}")
        time.sleep(np.random.uniform(0.5, 1.5))
    
    return video_time

def check_dns_resolution(host):
    """检查DNS解析"""
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False

def check_network_connection():
    """检查网络连接"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def parse_reward_amount(response):
    """解析奖励金额（增强版）"""
    # 1. 尝试从常见字段中解析
    reward_fields = ["red_money", "award", "money", "reward"]
    
    # 检查响应中的data字段
    data = response.get("data", {})
    if isinstance(data, dict):
        for field in reward_fields:
            if field in data:
                try:
                    return float(data[field])
                except (TypeError, ValueError):
                    pass
    
    # 2. 尝试从响应体中直接解析
    for field in reward_fields:
        if field in response:
            try:
                return float(response[field])
            except (TypeError, ValueError):
                pass
    
    # 3. 尝试从消息中解析金额
    message = response.get("message", "")
    if message:
        # 增强匹配模式：匹配各种金额格式
        patterns = [
            r'[\d.,]+元',  # 匹配"12.34元"
            r'[\d.,]+',    # 匹配纯数字
            r'¥([\d.,]+)'  # 匹配"¥12.34"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    # 移除逗号和小数点后的非数字字符
                    amount_str = match.group().replace(',', '').replace('元', '').replace('¥', '')
                    return float(amount_str)
                except ValueError:
                    continue
    
    # 4. 最后尝试从整个响应体中搜索
    if "data" in response and isinstance(response["data"], str):
        for pattern in patterns:
            match = re.search(pattern, response["data"])
            if match:
                try:
                    amount_str = match.group().replace(',', '').replace('元', '').replace('¥', '')
                    return float(amount_str)
                except ValueError:
                    continue
    
    return 0.0

def main():
    """主函数"""
    try:
        print(f"\n{color_text('🌈 小丽魔法教室启动', COLOR_CODES['PURPLE'])}")
        cfg = Config()
        
        # 配置信息
        log_info(f"域名: {cfg.XL_HOST}")
        log_info(f"课程ID: {cfg.XL_ID}")
        log_info(f"账号数: {len(cfg.XL_USER_LIST)}")
        
        # 验证配置
        if errors := validate_config(cfg):
            for err in errors: 
                log_error(err)
            exit(1)

        # 网络检查
        if not check_network_connection():
            log_error("网络连接失败")
            exit(1)
        else:
            log_success("网络正常")
        
        # DNS检查
        if not check_dns_resolution(cfg.XL_HOST):
            log_error(f"域名解析失败: {cfg.XL_HOST}")
            exit(1)
        else:
            log_success(f"域名解析成功: {cfg.XL_HOST}")

        result = AccountResult()
        result.total_accounts = len(cfg.XL_USER_LIST)

        log_info(f"{color_text('开始处理账号', COLOR_CODES['PURPLE'])}")
        log_info(f"延迟间隔: {cfg.XL_DELAY_MIN}-{cfg.XL_DELAY_MAX}秒")

        for idx, user in enumerate(cfg.XL_USER_LIST, 1):
            parts = user.split('#')
            if len(parts) != 2:
                log_error(f"账号格式错误: {user}")
                result.add_fail("", "")
                continue
                
            wx_openid, remark = parts
            current_reward = 0.0
            log_info(f"\n{color_text(f'处理账号 {idx}/{result.total_accounts}', COLOR_CODES['PURPLE'])}")
            log_info(f"ID尾号: {wx_openid[-4:]} | 备注: {remark}")

            try:
                headers = {
                    "Host": cfg.XL_HOST,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Content-Type": "application/json",
                    "Referer": f"https://{cfg.XL_HOST}/activity/index.html?id={cfg.XL_ID}&code=0&state=STATE"
                }

                # Token获取
                token = None
                for retry in range(cfg.XL_RETRY):
                    try:
                        url = f"https://{cfg.XL_HOST}/api-user/v2/getToken"
                        data = {"wx_openid": wx_openid, "id": cfg.XL_ID}
                        response = curl_request("POST", url, headers, data)
                        
                        if "error" in response:
                            raise Exception(response["error"])
                            
                        token_data = response.get("data", {})
                        if response.get("status_code") == 200 and token_data.get("status") == "success":
                            token = token_data["data"]["token"]
                            headers["Authorization"] = f"Bearer {token}"
                            log_success(f"Token获取成功 ({token[:6]}...)")
                            random_delay(1.0, 3.0)
                            break
                        else:
                            log_error(f"Token获取失败: {token_data.get('message', '未知错误')}")
                    except Exception as e:
                        log_warning(f"Token请求错误: {str(e)}")
                    if retry < cfg.XL_RETRY - 1:
                        time.sleep(2)
                if not token:
                    result.add_fail(wx_openid, remark)
                    continue

                # 获取活动详情
                random_delay(0.5, 1.5)
                url = f"https://{cfg.XL_HOST}/api-user/v2/activityDetatil?id={cfg.XL_ID}&withMaterial=1"
                response = curl_request("GET", url, headers)
                
                if "error" in response:
                    log_error(f"活动详情获取失败: {response['error']}")
                    result.add_fail(wx_openid, remark)
                    continue
                    
                detail_data = response.get("data", {})
                
                if response.get("status_code") != 200 or "data" not in detail_data:
                    log_error(f"活动详情错误: HTTP {response.get('status_code')}")
                    result.add_fail(wx_openid, remark)
                    continue

                # 检查是否已领取奖励
                join_info = detail_data.get("meta", {}).get("joinInfo", {})
                if join_info.get("is_receive_award", 0) == 1:
                    current_reward = float(join_info.get("red_money", 0))
                    result.add_success(wx_openid, remark, current_reward)
                    log_success(f"已领取奖励: ¥{current_reward:.2f}")
                    continue

                # 解析视频信息
                activity_data = detail_data.get("data", {})
                media_info = activity_data.get("media", {})
                video_time_str = media_info.get("media_v_time", "01:00:00.000")
                video_total_sec = parse_video_time(video_time_str)

                # 解析答案
                material_detail = activity_data.get("materialDetail", {})
                questions = material_detail.get("questions", [])
                answer_keys = []
                valid_questions = 0
                
                for q_idx, question in enumerate(questions):
                    answers = question.get("answer", [])
                    correct_index = None
                    
                    # 查找正确答案
                    for i, a in enumerate(answers):
                        if a.get("result") == "1":
                            correct_index = i
                            break
                    
                    if correct_index is None:
                        for i, a in enumerate(answers):
                            if "正确答案" in a.get("item", ""):
                                correct_index = i
                                break
                    
                    if correct_index is not None:
                        answer_keys.append(f"{q_idx}_{correct_index}")
                        valid_questions += 1
                        log_success(f"第{q_idx+1}题: 答案{correct_index}")
                    else:
                        log_warning(f"第{q_idx+1}题: 使用默认答案")
                        answer_keys.append(f"{q_idx}_0")
                        valid_questions += 1

                # 确保至少有一个有效答案
                if valid_questions == 0:
                    log_error("所有题目解析失败")
                    result.add_fail(wx_openid, remark)
                    continue

                # 上报观影时间
                user_activity_id = join_info.get("userActivityId")
                if not user_activity_id:
                    log_error("活动ID缺失")
                    result.add_fail(wx_openid, remark)
                    continue
                    
                total_time = simulate_watch_time(wx_openid, headers, user_activity_id, cfg.XL_HOST, cfg, video_total_sec)
                
                # 完成观影
                random_delay(0.5, 2.0)
                url = f"https://{cfg.XL_HOST}/api-user/v1/activityWatchVideoOver"
                data = {"userActivityId": user_activity_id}
                response = curl_request("POST", url, headers, data)
                log_success(f"学习完成! 时长: {total_time//60}分")

                # 领取奖励
                random_delay(1.0, 2.0)
                activity_id = activity_data.get("activity_id", cfg.XL_ID)
                
                try:
                    url = f"https://{cfg.XL_HOST}/api-user/v1/receiveAwardAndWatchOver"
                    data = {
                        "activity_id": activity_id,
                        "answers": answer_keys
                    }
                    response = curl_request("POST", url, headers, data)
                    
                    if "error" in response:
                        raise Exception(response["error"])
                        
                    reward_data = response.get("data", {})
                    
                    # 处理奖励结果
                    if response.get("status_code") == 200:
                        if reward_data.get("status") in ["success", "领取成功"]:
                            # 使用增强的奖励解析函数
                            current_reward = parse_reward_amount(reward_data)
                            
                            if current_reward > 0:
                                result.add_success(wx_openid, remark, current_reward)
                                log_success(f"获得奖励: ¥{current_reward:.2f}")
                            else:
                                # 如果还是解析失败，打印调试信息
                                log_warning("未能解析奖励金额")
                                log_debug(f"奖励响应数据: {reward_data}")
                                result.add_success(wx_openid, remark, 0.0)
                                log_success(f"奖励领取成功，但金额未知")
                        else:
                            result.add_fail(wx_openid, remark)
                            log_error(f"领取失败: {reward_data.get('message', '未知错误')}")
                    else:
                        result.add_fail(wx_openid, remark)
                        log_error(f"HTTP错误: {response.get('status_code')}")
                except Exception as e:
                    result.add_fail(wx_openid, remark)
                    log_error(f"领取异常: {str(e)}")

            except Exception as e:
                result.add_fail(wx_openid, remark)
                log_error(f"账号处理异常: {str(e)}")
                log_debug(traceback.format_exc())
            
            # 账号间随机延迟
            if idx < len(cfg.XL_USER_LIST):
                delay = np.random.randint(cfg.XL_DELAY_MIN, cfg.XL_DELAY_MAX + 1)
                log_info(f"等待 {delay}秒...")
                time.sleep(delay)

        # 结果汇总
        log_info(f"\n{color_text('处理结果', COLOR_CODES['PURPLE'])}")
        log_info(f"总账号: {result.total_accounts}")
        log_success(f"成功: {result.success_count}")
        if result.fail_count > 0:
            log_error(f"失败: {result.fail_count}")
        log_success(f"总奖励: ¥{result.total_reward():.2f}")

        # 详细结果
        log_info(f"\n{color_text('账号详情', COLOR_CODES['PURPLE'])}")
        for wx_openid, info in result.details.items():
            status = color_text(info['status'], COLOR_CODES['GREEN'] if info['status'] == '成功' else COLOR_CODES['RED'])
            reward_text = f"¥{info['reward']:.2f}" if info['reward'] > 0 else "未获取"
            log_info(f"ID尾号: {wx_openid[-4:]} | 备注: {info['remark']} | 状态: {status} | 奖励: {reward_text}")
            
        log_info(f"\n{color_text('🎉 处理完成', COLOR_CODES['PURPLE'])}")

    except Exception as e:
        log_error(f"系统错误: {str(e)}")
        log_debug(traceback.format_exc())

if __name__ == "__main__":
    main()

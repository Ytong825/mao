#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顺易充自动签到脚本
作者：奈斯
环境变量: SYC
格式: 备注#token#cookie，多账号换行
"""

import os
import sys
import json
import time
import hashlib
import requests
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 日志输出到青龙面板
def log(message: str):
    """输出日志到青龙面板"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    sys.stdout.flush()

def notify(title: str, content: str):
    """发送通知（兼容青龙面板通知）"""
    try:
        from notify import send as ql_send
        ql_send(title, content)
    except ImportError:
        log(f"未导入通知模块，跳过发送通知: {title}")
    except Exception as e:
        log(f"发送通知失败: {e}")

class ShunYiChongSign:
    """顺易充自动签到类"""
    
    def __init__(self, auth_token: str, cookies: str, remark: str = "未命名账号"):
        """
        初始化
        
        Args:
            auth_token: Bearer token
            cookies: Cookie字符串
            remark: 账号备注
        """
        self.base_url = "https://app.wodeev.com"
        self.remark = remark
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Site": "same-origin",
            "loginChannel": "15",
            "client-version": "5.5.2",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip",
            "Sec-Fetch-Mode": "cors",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://app.wodeev.com",
            "Referer": "https://app.wodeev.com/h5/pointsMall/",
            "lang": "1",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Cookie": cookies
        }
        
        # 用户信息（从token解析）
        self.user_info = self._parse_token(auth_token)
        
    def _parse_token(self, token: str) -> Dict:
        """从token中解析用户信息"""
        try:
            # JWT token格式: header.payload.signature
            parts = token.split('.')
            if len(parts) == 3:
                import base64
                import json as json_lib
                # 解码payload部分
                payload = parts[1]
                # 添加padding
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                payload_decoded = base64.urlsafe_b64decode(payload)
                payload_data = json_lib.loads(payload_decoded)
                
                return {
                    "custId": payload_data.get("custId", "未知"),
                    "phone": payload_data.get("sub", "未知"),
                    "exp": payload_data.get("exp", 0),
                    "clientType": payload_data.get("clientType", "未知")
                }
        except Exception as e:
            log(f"解析token失败: {e}")
        
        return {"custId": "未知", "phone": "未知", "exp": 0, "clientType": "未知"}
    
    def get_task_status(self) -> Optional[Dict]:
        """获取任务列表状态"""
        url = f"{self.base_url}/bil-front/v2.0/activity/getWelfareTask"
        params = {"taskNo": "20221231"}
        
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                log(f"获取任务失败，状态码: {response.status_code}")
                # 尝试重试一次
                time.sleep(2)
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params,
                    timeout=30,
                    verify=False
                )
                if response.status_code == 200:
                    return response.json()
                return None
                
        except requests.exceptions.Timeout:
            log("获取任务超时")
            return None
        except Exception as e:
            log(f"获取任务异常: {e}")
            return None
    
    def execute_sign_in(self) -> Dict:
        """执行签到"""
        # 1. 获取任务状态
        task_info = self.get_task_status()
        
        if not task_info:
            return {
                "success": False, 
                "message": "获取任务信息失败，请检查网络或token是否有效",
                "reward": "0",
                "status": "failed"
            }
        
        # 检查API返回状态
        if task_info.get("ret") != 200:
            return {
                "success": False,
                "message": f"获取任务失败: {task_info.get('msg', '未知错误')}",
                "reward": "0",
                "status": "api_error"
            }
        
        # 2. 查找签到任务
        sign_task = None
        all_tasks = []
        
        for task in task_info.get("taskList", []):
            all_tasks.append({
                "title": task.get("title", ""),
                "type": task.get("actType", ""),
                "reward": task.get("rewardValue", "0"),
                "status": task.get("rewardStatus", ""),
                "explain": task.get("explain", "")
            })
            
            if task.get("actType") == "1201":  # 签到任务
                sign_task = task
        
        if not sign_task:
            return {
                "success": False, 
                "message": "未找到签到任务",
                "reward": "0",
                "status": "not_found"
            }
        
        # 3. 检查是否已签到
        if sign_task.get("rewardStatus") == "02":
            return {
                "success": True, 
                "message": "今日已签到",
                "reward": sign_task.get("rewardValue", "0"),
                "status": "already_signed",
                "tasks": all_tasks
            }
        
        # 4. 执行签到
        sign_url = f"{self.base_url}/bil-front/v2.0/activity/getWelfare"
        sign_data = {
            "type": "1201",
            "taskNo": "20221231"
        }
        
        try:
            response = requests.post(
                sign_url,
                headers=self.headers,
                json=sign_data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ret") == 200:
                    return {
                        "success": True, 
                        "message": "签到成功",
                        "reward": sign_task.get("rewardValue", "0"),
                        "status": "signed",
                        "response": result,
                        "tasks": all_tasks
                    }
                else:
                    return {
                        "success": False, 
                        "message": f"签到失败: {result.get('msg', '未知错误')}",
                        "reward": "0",
                        "status": "api_error",
                        "response": result,
                        "tasks": all_tasks
                    }
            else:
                return {
                    "success": False, 
                    "message": f"请求失败，状态码: {response.status_code}",
                    "reward": "0",
                    "status": "http_error"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False, 
                "message": "签到请求超时",
                "reward": "0",
                "status": "timeout"
            }
        except Exception as e:
            return {
                "success": False, 
                "message": f"签到异常: {str(e)}",
                "reward": "0",
                "status": "exception"
            }
    
    def check_token_validity(self) -> bool:
        """检查token是否有效"""
        try:
            exp_time = self.user_info.get("exp", 0)
            if exp_time > 0:
                current_time = int(time.time())
                # 如果token在24小时内过期，则提示更新
                if exp_time - current_time < 86400:
                    log(f"Token将在 {(exp_time - current_time) // 3600} 小时后过期")
                return exp_time > current_time
            return True  # 如果无法解析exp，假定有效
        except:
            return True

def parse_environment_variable(env_value: str) -> List[Tuple[str, str, str]]:
    """
    解析环境变量
    
    格式: 备注#token#cookie
    多账号换行分隔
    
    Returns:
        List of (remark, token, cookie) tuples
    """
    accounts = []
    
    if not env_value:
        return accounts
    
    # 分割多个账户（按换行符分割）
    lines = env_value.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # 检查是否包含两个#号
        if line.count('#') < 2:
            log(f"第{line_num}行格式错误，需要 备注#token#cookie 格式: {line[:50]}...")
            continue
            
        parts = line.split('#', 2)  # 最多分割2次，得到3部分
        if len(parts) != 3:
            log(f"第{line_num}行格式错误，需要 备注#token#cookie 格式: {line[:50]}...")
            continue
            
        remark = parts[0].strip()
        token = parts[1].strip()
        cookie = parts[2].strip()
        
        if not remark:
            remark = f"账号{line_num}"
            
        if not token:
            log(f"第{line_num}行错误: token为空")
            continue
            
        if not cookie:
            log(f"第{line_num}行错误: cookie为空")
            continue
            
        accounts.append((remark, token, cookie))
    
    return accounts

def format_time(timestamp: int) -> str:
    """格式化时间戳为可读时间"""
    if timestamp == 0:
        return "未知"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "无效时间"

def main():
    """主函数"""
    log("=" * 60)
    log("顺易充自动签到脚本 v2.0")
    log("=" * 60)
    
    # 从环境变量获取配置
    env_value = os.environ.get("SYC", "")
    
    if not env_value:
        log("错误: 未找到环境变量 SYC")
        log("请在青龙面板环境变量中设置 SYC")
        log("")
        log("格式: 备注#token#cookie")
        log("多账号请换行，例如:")
        log("张三的账号#eyJhbGciOiJIUzI1NiJ9...xxx#_qddaz=QD.xxx;_qdda=3-1.1")
        log("李四的账号#eyJhbGciOiJIUzI1NiJ9...yyy#_qddaz=QD.yyy;_qdda=3-1.2")
        log("")
        log("如何获取token和cookie:")
        log("1. 打开顺易充网页版，登录")
        log("2. 按F12打开开发者工具")
        log("3. 找到网络请求中的Authorization头和Cookie头")
        return
    
    # 解析账户信息
    accounts = parse_environment_variable(env_value)
    
    if not accounts:
        log("错误: 未找到有效的账户配置")
        log("请检查环境变量 SYC 的格式是否正确")
        log("格式应为: 备注#token#cookie")
        return
    
    log(f"成功解析 {len(accounts)} 个账户")
    
    # 统计信息
    total_accounts = len(accounts)
    success_count = 0
    failed_count = 0
    already_signed = 0
    
    results = []
    total_points = 0
    
    # 遍历每个账户执行签到
    for idx, (remark, token, cookie) in enumerate(accounts, 1):
        log(f"\n{'='*40}")
        log(f"[账户 {idx}/{total_accounts}] {remark}")
        log(f"{'='*40}")
        
        try:
            # 创建签到实例
            sign_client = ShunYiChongSign(token, cookie, remark)
            
            # 显示用户信息
            user_info = sign_client.user_info
            phone = user_info.get("phone", "未知")
            cust_id = user_info.get("custId", "未知")
            client_type = user_info.get("clientType", "未知")
            exp_time = user_info.get("exp", 0)
            
            log(f"用户手机: {phone}")
            log(f"用户ID: {cust_id}")
            log(f"客户端类型: {client_type}")
            
            # 检查token有效期
            if sign_client.check_token_validity():
                log(f"Token状态: 有效 (过期时间: {format_time(exp_time)})")
            else:
                log(f"Token状态: ⚠️ 已过期或即将过期 (过期时间: {format_time(exp_time)})")
            
            # 执行签到
            result = sign_client.execute_sign_in()
            
            # 记录结果
            result_data = {
                "account": remark,
                "phone": phone,
                "result": result
            }
            results.append(result_data)
            
            # 输出结果
            if result["success"]:
                status = result.get("status", "")
                reward = result.get("reward", "0")
                
                if status == "already_signed":
                    log(f"📝 签到状态: 今日已签到")
                    log(f"💰 获得积分: {reward}")
                    already_signed += 1
                else:
                    log(f"✅ 签到状态: 签到成功")
                    log(f"💰 获得积分: {reward}")
                    success_count += 1
                    
                try:
                    total_points += float(reward)
                except:
                    pass
            else:
                log(f"❌ 签到状态: 签到失败")
                log(f"📋 失败原因: {result.get('message', '未知错误')}")
                failed_count += 1
            
            # 显示所有任务状态
            tasks = result.get("tasks", [])
            if tasks:
                log("📋 任务列表:")
                completed_tasks = 0
                for task in tasks:
                    title = task.get("title", "")
                    reward = task.get("reward", "0")
                    status = task.get("status", "")
                    status_text = "✅ 已完成" if status == "02" else "❌ 未完成"
                    if status == "02":
                        completed_tasks += 1
                    log(f"  {title}: {reward}积分 [{status_text}]")
                
                log(f"📊 任务完成度: {completed_tasks}/{len(tasks)}")
            
            # 避免请求过快
            if idx < total_accounts:
                time.sleep(3)
                
        except Exception as e:
            log(f"❌ 账户处理异常: {e}")
            traceback.print_exc()
            failed_count += 1
    
    # 生成汇总报告
    log("\n" + "=" * 60)
    log("🎉 签到汇总报告")
    log("=" * 60)
    log(f"📊 总账户数: {total_accounts}")
    log(f"✅ 成功签到: {success_count}")
    log(f"📝 今日已签: {already_signed}")
    log(f"❌ 签到失败: {failed_count}")
    log(f"💰 获得积分: {total_points}")
    
    # 生成通知消息
    notification_title = "顺易充签到结果"
    
    if success_count > 0 or already_signed > 0:
        notification_title = f"顺易充签到成功({success_count+already_signed}/{total_accounts})"
    
    notification_content = f"顺易充签到完成\n"
    notification_content += f"账户: {total_accounts}\n"
    notification_content += f"成功: {success_count}\n"
    notification_content += f"已签: {already_signed}\n"
    notification_content += f"失败: {failed_count}\n"
    notification_content += f"积分: {total_points}"
    
    # 添加详细信息
    if results:
        details = "\n详细结果:\n"
        for res in results:
            account = res["account"]
            phone = res["phone"]
            result_data = res["result"]
            
            if result_data["success"]:
                status = result_data.get("status", "")
                if status == "already_signed":
                    details += f"{account}({phone}): 已签到 ({result_data.get('reward', '0')}积分)\n"
                else:
                    details += f"{account}({phone}): ✅ 签到成功 ({result_data.get('reward', '0')}积分)\n"
            else:
                details += f"{account}({phone}): ❌ 失败 - {result_data.get('message', '未知')}\n"
        
        notification_content += details
    
    # 发送通知
    notify(notification_title, notification_content)
    
    log("\n顺易充自动签到脚本执行完成 🎉")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("脚本被用户中断")
    except Exception as e:
        log(f"脚本执行异常: {e}")
        traceback.print_exc()
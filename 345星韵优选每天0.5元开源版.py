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

# 此脚本为Python语言编写 运行请先安装好requests依赖！
# 脚本库http://2.345yun.cn
# 微信小程序
# 入口: #小程序://星韵优选/kt8xm5WOSI0Z6ri
# 环境变量配置（环境变量名: xyyx)(变量值：fb1f1efba29f93b14a0bf766xxxxxxxxxx)
# 抓包gzpengru.weimbo.com 请求里面的headers里的3rdsession的值
# 变量名：xyyx
# 变量值: fb1f1efba29f93b14a0bf766xxxxxxxxxx
# 多号换行或者&隔开变量值
import requests
import json
import time
import random
import datetime
import re
import os

def generate_bound_ua(token):
    rd = random.Random(token) 
    os_type = rd.choice(["Android", "iOS"])
    if os_type == "Android":
        android_ver = rd.choice(["10", "11", "12", "13", "14"])
        chrome_ver = f"{rd.randint(86, 120)}.0.{rd.randint(4000, 6000)}.{rd.randint(100, 200)}"
        phone_model = rd.choice(["SM-G9810", "V2055A", "M2012K11AC", "PADT00", "KB2000", "MI 10"])
        return (f"Mozilla/5.0 (Linux; Android {android_ver}; {phone_model} Build/QP1A.190711.020; wv) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_ver} "
                f"MicroMessenger/8.0.45.2400(0x28002B3D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64")
    else:
        ios_ver = rd.choice(["15_0", "16_2", "17_1"])
        return (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_ver} like Mac OS X) "
                f"AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
                f"MicroMessenger/8.0.46(0x18002e2f) NetType/WIFI Language/zh_CN")

class GzPengRu:
    def __init__(self, token, index):
        self.token = token
        self.index = index
        self.ua = generate_bound_ua(token)
        self.headers = {
            "Host": "gzpengru.weimbo.com",
            "Connection": "keep-alive",
            "3rdsession": self.token,
            "content-type": "application/json",
            "User-Agent": self.ua,
            "Referer": "https://servicewechat.com/wxc86c9aecdb67f876/9/page-frame.html"
        }
        self.base_url = "https://gzpengru.weimbo.com/api/index.php?ackey=GZYTAPPLET"
        self.next_run_time = 0 
        self.is_sign_completed = False
        self.is_video_completed = False
        self.is_all_done = False

    def log(self, content):
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] [账号{self.index}] {content}")

    def post_request(self, payload):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            self.log(f"请求异常: {e}")
            return None

    def get_user_info(self):
        payload = {"action": "userInfoData"}
        data = self.post_request(payload)
        if data and data.get("Status"):
            user_data = data.get("Data", {})
            user_name = user_data.get("user", {}).get("name", "未知")
            jifen = user_data.get("u_money", {}).get("jifen", 0)
            self.log(f"用户: {user_name} | 当前积分: {jifen}")
            return True
        else:
            self.log("Token失效")
            return False

    def check_task_progress(self):
        payload = {"action": "getIntegralInfo", "type": "jifen"}
        data = self.post_request(payload)
        
        sign_str = "未知"
        video_str = "0/3"
        
        if data and data.get("Status"):
            adv_arr = data.get("Data", {}).get("adv_arr", [])
            for task in adv_arr:
                title = task.get("title", "")
                if task.get("id") == 2:
                    match = re.search(r'\((\d+)/(\d+)\)', title)
                    if match:
                        curr, total = int(match.group(1)), int(match.group(2))
                        sign_str = f"{curr}/{total}"
                        if curr >= total:
                            self.is_sign_completed = True
                        else:
                            self.is_sign_completed = False
                
                elif task.get("id") == 3:
                    match = re.search(r'\((\d+)/(\d+)\)', title)
                    if match:
                        curr, total = int(match.group(1)), int(match.group(2))
                        video_str = f"{curr}/{total}"
                        if curr >= total:
                            self.is_video_completed = True
                        else:
                            self.is_video_completed = False

            if self.is_sign_completed and self.is_video_completed:
                self.log(f"🎉 今日所有任务已完成 (打卡:{sign_str} 视频:{video_str})")
                self.is_all_done = True
            else:
                self.log(f"📊 当前进度: 打卡[{sign_str}] 视频[{video_str}]")
            
            return True
        return False

    def execute_video_ad_task(self):
        if self.is_video_completed:
            self.log("🎬 视频任务: 今日已全部完成，跳过")
            return

        for i in range(3):
            payload_ad = {"action": "IntegralGiveReward"}
            res = self.post_request(payload_ad)
            
            if res and res.get("Status"):
                msg = res.get("Data", "")
                self.log(f"🎬 视频任务: ✅ {msg}")
            else:
                msg = res.get("Message", "未知错误") if res else "请求失败"
                if "上限" in msg or "完成" in msg:
                    self.log(f"🎬 视频任务: ❌ 今日已达上限")
                    self.is_video_completed = True
                    break
                else:
                    self.log(f"⚠️ 视频任务失败: {msg}")

    def process_cycle(self):
        if not self.check_task_progress():
            return 60

        if self.is_all_done:
            return -1

        if not self.is_video_completed:
            self.execute_video_ad_task()
            self.check_task_progress()

        if self.is_all_done:
            return -1

        if self.is_sign_completed:
            if self.is_video_completed:
                return -1
            else:
                return 60

        payload_status = {"action": "getIntegralInfo", "type": "sign"}
        data_status = self.post_request(payload_status)
        
        wait_seconds = 60 

        if data_status and data_status.get("Status"):
            status_data = data_status.get("Data", {})
            sign_time = status_data.get("sign_time", 0) 
            qiands = status_data.get("qiands", "未知")
            
            if sign_time > 0:
                self.log(f"📍 打卡状态: {qiands} | 冷却中: {sign_time}秒")
                wait_seconds = sign_time + 5 
            else:
                self.log("📍 冷却归零，执行打卡...")
                payload_sign = {"action": "userQiandao"}
                data_sign = self.post_request(payload_sign)
                
                if data_sign and data_sign.get("Status"):
                    res = data_sign.get("Data", {})
                    add_jf = res.get("add_jf", 0)
                    new_jf = res.get("user_jf", 0)
                    self.log(f"✅ 打卡成功! +{add_jf}分 | 总分: {new_jf}")
                    return 1 
                else:
                    msg = data_sign.get("Message", "未知") if data_sign else "无响应"
                    self.log(f"❌ 打卡失败: {msg}")
                    wait_seconds = 60 
        
        return wait_seconds

    def check_and_run(self):
        now = time.time()
        if now >= self.next_run_time:
            if self.get_user_info():
                wait_s = self.process_cycle()
                
                if wait_s == -1:
                    self.log("🏆 该账号今日任务全部完成，停止运行。")
                    return True
                
                self.next_run_time = now + wait_s
                next_str = datetime.datetime.fromtimestamp(self.next_run_time).strftime('%H:%M:%S')
                self.log(f"本轮结束，下次运行: {next_str}")
            else:
                self.next_run_time = now + 3600 
                self.log("账号Token异常，暂停1小时")
        return False

def main():
    print("-" * 30)
    print("脚本库 http://2.345yun.cn")
    print("脚本库 https://script.345yun.cn")
    print("-" * 30)
    print("=== 星韵优选脚本启动 ===")
    
    tokens_str = os.environ.get("xyyx")
    if not tokens_str:
        print("未找到环境变量名称: xyyx")
        return

    tokens = [t for t in tokens_str.replace("&", "\n").split("\n") if t.strip()]
    apps = [GzPengRu(token.strip(), i + 1) for i, token in enumerate(tokens) if token.strip()]
    
    if not apps:
        print("未配置有效 Token")
        return

    while True:
        try:
            now = time.time()
            min_next_run = float('inf')
            active_apps = []

            for app in apps:
                is_finished = False
                if now >= app.next_run_time:
                    is_finished = app.check_and_run()
                
                if not is_finished:
                    active_apps.append(app)
                    if app.next_run_time < min_next_run:
                        min_next_run = app.next_run_time
            
            apps = active_apps

            if not apps:
                print("\n" + "="*40)
                print("🎉 所有账号今日任务均已完成，脚本退出。")
                print("="*40)
                break

            sleep_time = min_next_run - time.time()
            if sleep_time < 0: 
                sleep_time = 0
            
            if sleep_time > 10:
                print(f"--- 系统待机: 等待 {int(sleep_time)} 秒 ---")
            
            time.sleep(max(1, sleep_time))
            
        except KeyboardInterrupt:
            print("\n用户手动停止脚本")
            break
        except Exception as e:
            print(f"主循环错误: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()

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
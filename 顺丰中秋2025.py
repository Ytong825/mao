# 当前脚本来自于http://script.345yun.cn脚本库下载！
import hashlib
import json
import os
import random
import time
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import unquote

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 全局消息变量
send_msg = ''
one_msg = ''

def Log(cont=''):
    """日志输出函数"""
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

def sunquote(sfurl):
    """双重URL解码函数"""
    decode = unquote(sfurl)
    if "3A//" in decode:
        decode = unquote(decode)
    return decode

# 邀请ID列表
inviteId = ['076CFC24BDE249BB8E7994DDE85E605F']

class SFRunner:
    def __init__(self, info, index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        url = split_info[0]
        self.index = index + 1
        Log(f"\n---------开始执行第{self.index}个账号>>>>>")
        
        # 初始化会话
        self.s = requests.session()
        self.s.verify = False
        
        # 请求头信息
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 15; 22061218C Build/AQ3A.241006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20250503 MMWEBID/6435 MicroMessenger/8.0.61.2861(0x28003D41) WeChat/arm64 Weixin GPVersion/1 NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxd4185d00bf7e08ac',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'platform': 'MINI_PROGRAM',
            'channel': '25zqappdb2',
        }
        
        # 登录并初始化用户信息
        self.login_res = self.login(url)
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.activity_code = 'MIDAUTUMN_2025'
        self.recommend_tasks = []

    def login(self, sfurl):
        """用户登录"""
        sfurl = sunquote(sfurl)
        ress = self.s.get(sfurl, headers=self.headers)
        cookies = self.s.cookies.get_dict()
        self.user_id = cookies.get('_login_user_id_', '')
        self.phone = cookies.get('_login_mobile_', '')
        
        if self.phone:
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:]
            Log(f'用户:【{self.mobile}】登陆成功')
            return True
        else:
            Log(f'获取用户信息失败')
            return False

    def get_sign(self):
        """生成签名信息"""
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sys_code = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sys_code}'
        signature = hashlib.md5(data.encode()).hexdigest()
        
        sign_data = {
            'sysCode': sys_code,
            'timestamp': timestamp,
            'signature': signature
        }
        self.headers.update(sign_data)
        return sign_data

    def do_request(self, url, data={}, req_type='post'):
        """通用请求处理"""
        self.get_sign()
        try:
            if req_type.lower() == 'get':
                response = self.s.get(url, headers=self.headers)
            else:
                response = self.s.post(url, headers=self.headers, json=data)
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            Log(f'请求错误: {str(e)}')
            return None

    def check_activity_status(self):
        """检查中秋活动状态"""
        Log('====== 查询中秋活动状态 ======')
        try:
            # 选择邀请ID
            invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
            payload = {"inviteUserId": invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~midAutumn2025IndexService~index'

            response = self.do_request(url, payload)
            if response and response.get('success'):
                obj = response.get('obj', {})
                ac_end_time = obj.get('acEndTime', '')
                
                if ac_end_time and datetime.now() < datetime.strptime(ac_end_time, "%Y-%m-%d %H:%M:%S"):
                    Log(f'2025中秋活动进行中，结束时间：{ac_end_time}')
                    self.activity_code = obj.get('actCode', 'MIDAUTUMN_2025')
                    self.recommend_tasks = obj.get('recommendTasks', [])
                    return True
                Log('2025中秋活动已结束')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'查询中秋活动失败: {error_msg}')
        except Exception as e:
            Log(f'活动状态查询错误: {str(e)}')
        return False

    def process_tasks(self):
        """处理中秋活动任务"""
        Log('====== 处理中秋活动任务 ======')
        try:
            payload = {
                "activityCode": self.activity_code,
                "channelType": "MINI_PROGRAM"
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'

            response = self.do_request(url, payload)
            if response and response.get('success'):
                task_list = response.get('obj', []) or self.recommend_tasks
                
                for task in task_list:
                    task_name = task.get('val', task.get('taskName', '未知任务'))
                    status = task.get('status', 0)
                    
                    if status == 3:
                        Log(f'> 中秋任务【{task_name}】已完成')
                        continue
                        
                    Log(f'> 开始完成中秋任务【{task_name}】')
                    task_code = task.get('key', task.get('taskCode'))
                    if task_code:
                        self.finish_task(task, task_code)
                        time.sleep(2)  # 任务间隔，避免请求过于频繁
                
                # 完成所有任务后尝试领取倒计时奖励
                self.receive_countdown_reward()
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'查询中秋任务失败: {error_msg}')
        except Exception as e:
            Log(f'任务处理错误: {str(e)}')

    def finish_task(self, task, task_code):
        """完成指定任务"""
        try:
            payload = {'taskCode': task_code}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            task_name = task.get('val', task.get('taskName', '未知任务'))
            
            if response and response.get('success'):
                Log(f'> 完成中秋任务【{task_name}】成功')
                self.receive_task_reward(task)
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'> 完成中秋任务【{task_name}】失败: {error_msg}')
        except Exception as e:
            Log(f'> 任务执行错误: {str(e)}')

    def receive_task_reward(self, task):
        """领取任务奖励"""
        try:
            payload = {
                'taskType': task.get('taskType', ''),
                'activityCode': self.activity_code,
                'channelType': 'MINI_PROGRAM'
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'

            response = self.do_request(url, payload)
            task_name = task.get('val', task.get('taskName', '未知任务'))
            
            if response and response.get('success'):
                Log(f'> 领取中秋任务【{task_name}】奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'> 领取中秋任务【{task_name}】奖励失败: {error_msg}')
        except Exception as e:
            Log(f'> 奖励领取错误: {str(e)}')

    def receive_countdown_reward(self):
        """领取倒计时奖励"""
        Log('====== 尝试领取倒计时奖励 ======')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~receiveCountdownReward'
            response = self.do_request(url, {})
            
            if response and response.get('success', False):
                Log(f'> 领取倒计时奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回信息') if response else '请求失败'
                Log(f'> 领取倒计时奖励失败: {error_msg}')
        except Exception as e:
            Log(f'> 倒计时奖励领取错误: {str(e)}')

    def run(self):
        """主运行函数"""
        # 随机等待避免风控
        time.sleep(random.randint(1000, 3000) / 1000.0)
        
        if not self.login_res: 
            return False
            
        # 执行活动任务
        if self.check_activity_status():
            self.process_tasks()
        
        self.send_msg()
        return True

    def send_msg(self, help=False):
        """消息推送功能（预留）"""
        pass

if __name__ == '__main__':
    APP_NAME = '顺丰速运2025中秋活动'
    ENV_NAME = 'sfsyUrl'
    
    print(f'''
    顺丰速运2025中秋活动自动化脚本
    变量名：sfsyUrl（多账号请换行）
    功能：自动完成中秋活动任务，包括领取倒计时奖励
    ''')
    
    token = os.getenv(ENV_NAME)
    if not token:
        print("请设置环境变量 sfsyUrl")
        exit(1)
        
    tokens = token.split('&')
    print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
    
    for index, info in enumerate(tokens):
        if info.strip():
            if not SFRunner(info, index).run():
                continue

# 当前脚本来自于http://script.345yun.cn脚本库下载！
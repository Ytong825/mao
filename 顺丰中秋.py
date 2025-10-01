import hashlib
import json
import os
import random
import time
from datetime import datetime
from urllib.parse import unquote
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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

# 邀请ID列表
inviteId = ['076CFC24BDE249BB8E7994DDE85E605F']

class SFRunner:
    def __init__(self, info, index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        self.url = split_info[0]
        self.index = index + 1
        Log(f"\n🚀 ========== 开始执行第{self.index}个账号 ==========")
        
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
        self.login_res = self.login()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.activity_code = 'MIDAUTUMN_2025'
        self.recommend_tasks = []

    def login(self):
        """用户登录"""
        ress = self.s.get(self.url, headers=self.headers)
        cookies = self.s.cookies.get_dict()
        self.user_id = cookies.get('_login_user_id_', '')
        self.phone = cookies.get('_login_mobile_', '')
        
        if self.phone:
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:]
            Log(f'✅ 用户【{self.mobile}】登录成功')
            return True
        else:
            Log(f'❌ 获取用户信息失败')
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
        Log('🌙 ====== 查询中秋活动状态 ======')
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
                    Log(f'🎉 2025中秋活动进行中，结束时间：{ac_end_time}')
                    self.activity_code = obj.get('actCode', 'MIDAUTUMN_2025')
                    self.recommend_tasks = obj.get('recommendTasks', [])
                    return True
                Log('⏰ 2025中秋活动已结束')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 查询中秋活动失败: {error_msg}')
        except Exception as e:
            Log(f'⚠️ 活动状态查询错误: {str(e)}')
        return False

    def play_game(self):
        """完成中秋游戏任务"""
        Log('🎮 ====== 完成中秋游戏任务 ======')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025GameService~win'

            # 请求4次，levelIndex从1到4
            for level in range(1, 5):
                payload = {"levelIndex": level}
                Log(f'🎯 开始游戏关卡 {level}')

                response = self.do_request(url, payload)
                if response and response.get('success'):
                    obj = response.get('obj', {})
                    pass_rank = obj.get('passRank', 0)
                    exceed_percent = obj.get('exceedPercent', 0)
                    current_award = obj.get('currentAward', {})
                    currency = current_award.get('currency', '')
                    amount = current_award.get('amount', 0)
                    Log(f'🎁 奖励: {currency} x{amount}')
                else:
                    error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                    Log(f'❌ 游戏关卡 {level} 完成失败: {error_msg}')

                # 关卡间隔，避免请求过于频繁
                time.sleep(random.randint(5, 15))
            Log(f'✅ 游戏关卡 {level} 完成成功')
            Log(f'📊 排名: {pass_rank}, 超越: {exceed_percent*100:.1f}%')

        except Exception as e:
            Log(f'⚠️ 游戏任务错误: {str(e)}')

    def process_tasks(self):
        """处理中秋活动任务"""
        Log('📋 ====== 处理中秋活动任务 ======')
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
                        Log(f'✅ 中秋任务【{task_name}】已完成')
                        continue

                    Log(f'🔄 开始完成中秋任务【{task_name}】')
                    if task_name == '玩一笔连兔游戏':
                        self.play_game()
                        continue
                    task_code = task.get('key', task.get('taskCode'))
                    if task_code:
                        self.finish_task(task, task_code)
                        time.sleep(2)  # 任务间隔，避免请求过于频繁
                
                # 完成所有任务后尝试领取倒计时奖励
                self.receive_countdown_reward()
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 查询中秋任务失败: {error_msg}')
        except Exception as e:
            Log(f'⚠️ 任务处理错误: {str(e)}')

    def finish_task(self, task, task_code):
        """完成指定任务"""
        try:
            payload = {'taskCode': task_code}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'

            response = self.do_request(url, payload)
            task_name = task.get('val', task.get('taskName', '未知任务'))
            
            if response and response.get('success'):
                Log(f'✅ 完成中秋任务【{task_name}】成功')
                self.receive_task_reward(task)
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 完成中秋任务【{task_name}】失败: {error_msg}')
        except Exception as e:
            Log(f'⚠️ 任务执行错误: {str(e)}')

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
                Log(f'🎁 领取中秋任务【{task_name}】奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 领取中秋任务【{task_name}】奖励失败: {error_msg}')
        except Exception as e:
            Log(f'⚠️ 奖励领取错误: {str(e)}')

    def receive_countdown_reward(self):
        """领取倒计时奖励"""
        Log('⏰ ====== 尝试领取倒计时奖励 ======')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~receiveCountdownReward'
            response = self.do_request(url, {})
            
            if response and response.get('success', False):
                Log(f'🎁 领取倒计时奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回信息') if response else '请求失败'
                Log(f'❌ 领取倒计时奖励失败: {error_msg}')
        except Exception as e:
            Log(f'⚠️ 倒计时奖励领取错误: {str(e)}')

    def unbox_mystery_boxes(self):
        """拆盲盒功能"""
        Log('📦 ====== 开始拆盲盒任务 ======')
        try:
            # 循环拆盲盒直到用完所有机会
            while True:
                # 获取当前盲盒状态
                box_status = self.get_box_status()
                if not box_status:
                    break

                remain_chance = box_status.get('remainBoxChance', 0)
                total_box_times = box_status.get('totalBoxTimes', 0)
                level_box_times = box_status.get('levelBoxTimes', 0)

                Log(f'📊 总拆盲盒次数: {total_box_times}, 当前关卡次数: {level_box_times}, 剩余机会: {remain_chance}')

                if remain_chance <= 0:
                    Log('✅ 所有拆盲盒机会已用完')
                    break

                # 获取当前关卡配置信息
                current_level_config = box_status.get('currentLevelConfig', {})
                current_level = current_level_config.get('level', 1)
                board_length = current_level_config.get('boardLength', 4)
                target_shape_num = current_level_config.get('targetShapeNum', 2)

                board_status = box_status.get('boardStatus', {})
                target_shapes = board_status.get('t', [])
                board_data = board_status.get('b', '')

                Log(f'🎯 当前关卡: {current_level}')
                Log(f'🎯 盲盒尺寸: {board_length}x{board_length}')
                Log(f'🎯 目标形状数量: {target_shape_num}')
                Log(f'🎯 需要开启的盲盒总数: {target_shape_num * 4}')

                # 解析当前盲盒状态
                try:
                    if board_data:
                        board_matrix = json.loads(board_data)
                    else:
                        # 初始状态，创建空白盲盒矩阵
                        Log('📋 检测到初始状态，创建空白盲盒矩阵')
                        board_matrix = []
                        for i in range(board_length):
                            row = []
                            for j in range(board_length):
                                row.append({"t": "", "s": "n"})
                            board_matrix.append(row)
                except Exception as e:
                    Log(f'❌ 解析盲盒状态失败: {str(e)}')
                    break

                # 开始拆当前关卡的盲盒
                level_completed = self.process_unboxing(board_matrix, target_shapes, target_shape_num, board_length)

                if level_completed:
                    Log(f'🎉 关卡 {current_level} 完成！')
                    # 等待一下再检查下一关
                    time.sleep(random.randint(3, 6))
                else:
                    Log(f'❌ 关卡 {current_level} 未完成，停止拆盲盒')
                    break

            # 所有拆盲盒完成后进行抽奖
            final_box_status = self.get_box_status()
            if final_box_status:
                passed_level_list = final_box_status.get('passedLevelList', [])
                self.process_lottery(passed_level_list)

        except Exception as e:
            Log(f'⚠️ 拆盲盒任务错误: {str(e)}')

    def get_box_status(self):
        """获取盲盒状态"""
        Log('📋 获取盲盒状态...')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~boxStatus'
            response = self.do_request(url, {})

            if response and response.get('success'):
                Log('✅ 获取盲盒状态成功')
                return response.get('obj', {})
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 获取盲盒状态失败: {error_msg}')
                return None
        except Exception as e:
            Log(f'⚠️ 获取盲盒状态错误: {str(e)}')
            return None

    def get_unbox_token(self):
        """获取拆盲盒token"""
        Log('🔑 获取拆盲盒token...')
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~unBox'
            response = self.do_request(url, {})

            if response and response.get('success'):
                obj = response.get('obj', {})
                token = obj.get('token', '')
                empty_box = obj.get('emptyBox', True)
                Log(f'✅ 获取token成功: {token[:8]}...')
                return token, empty_box
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 获取token失败: {error_msg}')
                return None, None
        except Exception as e:
            Log(f'⚠️ 获取token错误: {str(e)}')
            return None, None

    def process_unboxing(self, board_matrix, target_shapes, target_shape_num, board_length):
        """处理拆盲盒逻辑"""
        Log('🎮 开始拆盲盒流程...')

        # 统计每个形状需要开启的数量
        shape_counts = {}
        for shape in target_shapes:
            shape_type = shape.get('s', '')
            if shape_type:
                shape_counts[shape_type] = 0

        # 如果没有目标形状，说明是初始状态，需要根据配置创建
        if not shape_counts and target_shape_num > 0:
            Log('📋 初始状态，根据配置创建形状标记')
            # 常见的形状标记，可以根据实际情况调整
            common_shapes = ['O', 'I', 'T', 'L', 'S', 'Z', 'J']
            for i in range(min(target_shape_num, len(common_shapes))):
                shape_counts[common_shapes[i]] = 0

        # 先处理已经开启但未标记的盲盒
        for i in range(board_length):
            for j in range(board_length):
                cell = board_matrix[i][j]
                if cell.get('s') == 'y':
                    # 找到合适的形状标记
                    for shape_type in shape_counts:
                        if shape_counts[shape_type] < 4:
                            cell['t'] = shape_type
                            shape_counts[shape_type] += 1
                            break

        # 计算还需要开启的盲盒数量
        total_needed = target_shape_num * 4
        total_opened = sum(shape_counts.values())
        remaining_needed = total_needed - total_opened

        Log(f'📊 已开启: {total_opened}, 还需开启: {remaining_needed}')

        # 检查是否已经完成所有盲盒，如果完成则直接报告完成状态
        if total_opened >= total_needed:
            Log(f'🎉 检测到当前关卡已完成所有盲盒 ({total_opened}/{total_needed})，直接提交完成状态')
            success = self.report_unbox(board_matrix, target_shapes, is_final=True, shape_counts=shape_counts)
            if success:
                Log(f'✅ 当前关卡完成状态提交成功')
                return True
            else:
                Log(f'❌ 当前关卡完成状态提交失败')
                return False

        # 继续开启剩余的盲盒
        opened_count = 0
        for i in range(board_length):
            for j in range(board_length):
                if opened_count >= remaining_needed:
                    break

                cell = board_matrix[i][j]
                if cell.get('s') == 'n' and cell.get('t') == '':
                    # 找到需要开启的形状类型
                    for shape_type in shape_counts:
                        if shape_counts[shape_type] < 4:
                            cell['s'] = 'y'
                            cell['t'] = shape_type
                            shape_counts[shape_type] += 1
                            opened_count += 1

                            # 发送开盲盒请求
                            is_final = sum(shape_counts.values()) >= total_needed
                            success = self.report_unbox(board_matrix, target_shapes, is_final, shape_counts)
                            if not success:
                                Log('❌ 拆盲盒请求失败，停止当前关卡')
                                return False
                            time.sleep(random.randint(2, 5))

                            # 如果是最后一个盲盒，返回成功
                            if is_final:
                                return True
                            break
            if opened_count >= remaining_needed:
                break

        # 检查是否完成了所有需要的盲盒
        total_opened = sum(shape_counts.values())
        if total_opened >= total_needed:
            Log(f'✅ 当前关卡所有盲盒已完成 ({total_opened}/{total_needed})')
            return True
        else:
            Log(f'⚠️ 当前关卡未完成 ({total_opened}/{total_needed})')
            return False

    def report_unbox(self, board_matrix, target_shapes, is_final=False, shape_counts=None):
        """报告开盲盒结果"""
        try:
            # 获取token
            token, empty_box = self.get_unbox_token()
            if not token:
                return False

            # 构建target_shapes，如果原始为空且有shape_counts，则重新构建
            if not target_shapes and shape_counts:
                target_shapes = []
                for shape_type in shape_counts:
                    target_shapes.append({"s": shape_type, "p": "j"})  # p值可以是固定的

            # 构建请求数据
            board_data = json.dumps(board_matrix, separators=(',', ':'))
            payload = {
                "token": token,
                "boardStatus": {
                    "b": board_data,
                    "t": target_shapes
                },
                "levelPass": is_final,
                "emptyBox": empty_box,
                "taskType": ""
            }

            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~reportBox'
            response = self.do_request(url, payload)

            if response and response.get('success'):
                if is_final:
                    Log('🎉 完成所有盲盒拆解！')
                else:
                    Log('✅ 盲盒拆解成功')
                return True
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 盲盒拆解失败: {error_msg}')
                return False

        except Exception as e:
            Log(f'⚠️ 盲盒拆解错误: {str(e)}')
            return False

    def process_lottery(self, passed_level_list):
        """处理抽奖功能"""
        # 检查是否启用抽奖功能
        lottery_enabled = os.getenv('S_SFZQ_CJ', 'true').lower() == 'true'
        if not lottery_enabled:
            Log('🎰 ====== 抽奖功能已禁用 ======')
            Log('💡 如需启用抽奖功能，请设置环境变量 S_SFZQ_CJ=true')
            return
        
        Log('🎰 ====== 检查抽奖机会 ======')
        try:
            if not passed_level_list:
                Log('📋 没有已通过的关卡信息')
                return

            # 检查每个关卡的抽奖机会
            lottery_available = False
            for level_info in passed_level_list:
                currency = level_info.get('currency', '')
                balance = level_info.get('balance', 0)
                total_amount = level_info.get('totalAmount', 0)

                Log(f'📊 关卡【{currency}】- 总奖励: {total_amount}, 剩余抽奖机会: {balance}')

                if balance > 0:
                    lottery_available = True
                    # 进行抽奖
                    for i in range(balance):
                        Log(f'🎯 开始抽奖 - 关卡【{currency}】第{i+1}次')
                        self.draw_prize(currency)
                        time.sleep(random.randint(2, 4))  # 抽奖间隔

            if not lottery_available:
                Log('📋 没有可用的抽奖机会')

        except Exception as e:
            Log(f'⚠️ 抽奖处理错误: {str(e)}')

    def draw_prize(self, currency):
        """执行抽奖"""
        try:
            payload = {"currency": currency}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025LotteryService~prizeDraw'

            response = self.do_request(url, payload)
            if response and response.get('success'):
                obj = response.get('obj', {})
                gift_bag_name = obj.get('giftBagName', '未知奖品')
                gift_bag_worth = obj.get('giftBagWorth', 0)

                # 获取奖品详情
                product_list = obj.get('productDTOList', [])
                product_details = []
                for product in product_list:
                    product_name = product.get('productName', '')
                    amount = product.get('amount', 0)
                    if product_name:
                        product_details.append(f'{product_name} x{amount}')

                Log(f'🎉 抽奖成功！获得奖品：【{gift_bag_name}】')
                Log(f'💰 奖品价值：{gift_bag_worth}元')
                if product_details:
                    Log(f'📦 奖品详情：{", ".join(product_details)}')

            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'❌ 抽奖失败: {error_msg}')

        except Exception as e:
            Log(f'⚠️ 抽奖错误: {str(e)}')

    def run(self):
        """主运行函数"""
        # 随机等待避免风控
        time.sleep(random.randint(1000, 3000) / 1000.0)
        
        if not self.login_res: 
            return False
            
        # 执行活动任务
        if self.check_activity_status():
            self.process_tasks()
            # 完成任务后拆盲盒
            self.unbox_mystery_boxes()
        
        self.send_msg()
        return True

    def send_msg(self, help=False):
        """消息推送功能（预留）"""
        pass

if __name__ == '__main__':
    APP_NAME = '顺丰速运2025中秋活动'
    ENV_NAME = 'sfsyUrl'
    
    print(f'''
🌙 ========================================
    顺丰速运2025中秋活动自动化脚本
    变量名：sfsyUrl（多账号请换行）
    功能：自动完成中秋活动任务，包括领取倒计时奖励
    抽奖控制：S_SFZQ_CJ（true=抽奖，false=不抽奖，默认false）
🌙 ========================================
    ''')
    
    token = os.getenv(ENV_NAME)
    if not token:
        print("❌ 请设置环境变量 sfsyUrl")
        exit(1)

    # 检查抽奖控制环境变量
    lottery_control = os.getenv('S_SFZQ_CJ', 'false').lower()
    lottery_status = "启用" if lottery_control == 'true' else "禁用"
    print(f"🎰 抽奖功能状态：{lottery_status}")
    if lottery_control not in ['true', 'false']:
        print("⚠️ 环境变量 S_SFZQ_CJ 值无效，将使用默认值 false")

    # 分割账号信息并进行URL解码
    tokens = token.split('&')
    decoded_tokens = []

    for token_item in tokens:
        if token_item.strip():
            # 对每个账号信息进行URL解码
            decoded_token = unquote(token_item.strip())
            decoded_tokens.append(decoded_token)

    print(f"\n🎯 ========== 共获取到{len(decoded_tokens)}个账号 ==========")

    for index, info in enumerate(decoded_tokens):
        if info.strip():
            if not SFRunner(info, index).run():
                continue

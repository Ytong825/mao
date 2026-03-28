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

"""
脚本名称: 歌画东阳
作者：YSJohnson
功能：歌画东阳APP每日自动阅读文章、开红包抽奖、钱包余额查询
中奖概率好像不高 得挂浙江ip才高

【变量配置说明】
1. 账号变量 (ghdy):
   格式：X-SESSION-ID#X-ACCOUNT-ID
   多账号换行分隔
   示例：abc123XXXXX#abc123XXXXX
"""
import os
import sys
import time
import uuid
import json
import random
import hashlib
import logging
import signal
import threading
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

stop_event = threading.Event()

def signal_handler(signum, frame):
    print("\n 接收到退出信号，正在安全停止所有任务...")
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        account = getattr(record, 'account', None)
        if account and not account.startswith("账号_"):
            record.prefix = f"[{account}] "
        else:
            record.prefix = ""
        return super().format(record)

logger = logging.getLogger("Tmuyun")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter("%(asctime)s %(prefix)s%(message)s", "%H:%M:%S"))
logger.addHandler(handler)

class TmuyunClient:
    SALT = "FR*r!isE5W"

    def __init__(self, session_id, account_id):
        self.session_id = session_id
        self.account_id = account_id
        self.tenant_id = "49"
        self.account_name = f"账号_{account_id[-4:]}"

        self.device_id = str(uuid.uuid4())
        self.ua = f"5.0.9.0.3;{self.device_id};OnePlus PLC110;Android;16;Release;6.11.0"

        self.session = requests.Session()
        self.session.verify = False

        self.lottery_results = []
        self.wallet_info = {"total": "0.00", "balance": "0.00"}
        self.read_history = set()

    def log_info(self, msg):
        logger.info(msg, extra={'account': self.account_name})

    def log_warn(self, msg):
        logger.warning(msg, extra={'account': self.account_name})

    def _generate_signature(self, path, req_uuid, req_timestamp):
        parsed = urlparse(path)
        norm_path = parsed.path
        if norm_path.startswith('/api/v1'):
            norm_path = norm_path.replace('/api/v1', '', 1)

        raw_str = f"{norm_path}&&{self.session_id}&&{req_uuid}&&{req_timestamp}&&{self.SALT}&&{self.tenant_id}"
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest().lower()

    def _request(self, method, url, **kwargs):
        if stop_event.is_set():
            return None

        req_uuid = str(uuid.uuid4())
        req_timestamp = str(int(time.time() * 1000))

        signature = self._generate_signature(url, req_uuid, req_timestamp)

        headers = {
            "User-Agent": self.ua,
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": req_uuid,
            "X-TIMESTAMP": req_timestamp,
            "X-SIGNATURE": signature,
            "X-TENANT-ID": self.tenant_id,
            "Content-Type": "application/json;charset=UTF-8"
        }

        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        for attempt in range(3):
            if stop_event.is_set():
                break
            try:
                resp = self.session.request(method, url, headers=headers, timeout=10, **kwargs)
                res_json = resp.json()
                return res_json
            except Exception as e:
                if attempt == 2:
                    self.log_warn(f"请求失败 {url}: {e}")
                if stop_event.wait(2): return None
        return None

    def get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def init_account(self):
        self.log_info("开始初始化账号获取信息...")
        url = "https://vapp.tmuyun.com/api/user_mumber/account_detail"
        resp = self.get(url)

        if not resp or resp.get("code") != 0:
            self.log_warn(f"获取账号信息失败: {resp}")
            return False

        rst = resp.get("data", {}).get("rst", {})
        mobile = rst.get("mobile", "")
        nickname = rst.get("nick_name", "Unknown")
        total_integral = rst.get("total_integral", 0)

        if mobile and len(mobile) == 11:
            self.account_name = f"{mobile[:3]}****{mobile[7:]}"
        else:
            self.account_name = nickname

        self.log_info(f"登录成功 用户: {nickname} 积分: {total_integral}")
        return True

    def get_activity_info(self):
        if stop_event.wait(random.uniform(2, 4)): return -1, -1

        act_url = "https://fijdzpur.act.tmuact.com/activity/api.php"
        req_timestamp = str(int(time.time() * 1000))
        act_signature = hashlib.sha256(f"{self.device_id}&&{req_timestamp}&&MJ<?TH4&9w^".encode('utf-8')).hexdigest().lower()
        payload = f"m=front&subm=money&action=init&account_id={self.account_id}&session_id={self.session_id}&token=&q=YunSLfAkU&system=Android&signature={act_signature}&appName=%E6%AD%8C%E7%94%BB%E4%B8%9C%E9%98%B3&system_version=16&device_no={self.device_id}&device_type=OnePlus+PLC110&statusBarHeight=40&networkType=wifi&timestamp={req_timestamp}&version=5.0.9.0.3&detail=&client_code=xsb_dongyang"

        headers = {
            "Host": "fijdzpur.act.tmuact.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": f"Mozilla/5.0 (Linux; Android 16; PLC110 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/145.0.7632.159 Mobile Safari/537.36;xsb_dongyang;xsb_dongyang;5.0.9.0.3;native_app;6.11.0",
        }

        for attempt in range(3):
            if stop_event.is_set(): return -1, -1
            try:
                resp = self.session.post(act_url, headers=headers, data=payload, timeout=10)
                res_json = resp.json()

                if res_json.get("status") is True and res_json.get("code") == 3001:
                    data = res_json.get("data", {})
                    read_times = data.get("read_times", 0)
                    open_times = data.get("open_times", 0)
                    return read_times, open_times
            except Exception as e:
                if attempt == 2:
                    self.log_warn(f"请求活动接口失败: {e}")
            if stop_event.wait(2): return -1, -1
        return -1, -1

    def do_read_articles(self, need_read=5):
        if stop_event.is_set(): return
        self.log_info(f"开始获取文章列表，准备阅读 {need_read} 篇文章...")
        list_url = "https://vapp.tmuyun.com/api/article/channel_list?channel_id=6254f12dfe3fc10794f7b25c&isDiFangHao=false&is_new=true&list_count=0&size=20"
        resp = self.get(list_url)

        if stop_event.wait(random.uniform(2, 3)): return

        articles = []
        if resp and resp.get("code") == 0:
            for item in resp.get("data", {}).get("article_list", []):
                if item.get("doc_type") == 2 and item.get("id"):
                    articles.append((item["id"], item.get("list_title", "未命名文章")))
                for sub_item in item.get("column_news_list", []):
                    if sub_item.get("doc_type") == 2 and sub_item.get("id"):
                        articles.append((sub_item["id"], sub_item.get("list_title", "未命名文章")))

        if not articles:
            self.log_warn("未获取到文章列表")
            return

        unique_articles = []
        seen = set()
        for art in articles:
            art_id = art[0]
            if art_id not in seen and art_id not in self.read_history:
                seen.add(art_id)
                unique_articles.append(art)

        if not unique_articles:
            self.log_warn("无可读新文章，可能当前列表已全部阅读过")
            return

        if len(unique_articles) > need_read:
            selected_articles = random.sample(unique_articles, need_read)
        else:
            selected_articles = unique_articles

        self.log_info(f"成功获取并过滤历史文章，本次将阅读 {len(selected_articles)} 篇文章")

        for idx, (article_id, article_title) in enumerate(selected_articles, 1):
            if stop_event.is_set(): break
            self.log_info(f"开始阅读第 {idx} 篇:《{article_title}》...")

            start_time_ms = random.randint(3000, 6000)
            start_url = f"https://vapp.tmuyun.com/api/article/read_time?channel_article_id={article_id}&is_end=false&read_time={start_time_ms}"
            self.get(start_url)

            sleep_sec = random.uniform(7, 10)
            if stop_event.wait(sleep_sec): return

            end_time_ms = start_time_ms + int(sleep_sec * 1000) + random.randint(100, 1000)
            end_url = f"https://vapp.tmuyun.com/api/article/read_time?channel_article_id={article_id}&is_end=true&read_time={end_time_ms}"
            self.get(end_url)

            self.read_history.add(article_id)
            self.log_info(f"第 {idx} 篇文章阅读完成")

            if idx < len(selected_articles):
                if stop_event.wait(random.uniform(2, 3)): return

    def do_lottery(self):
        if stop_event.is_set(): return
        self.log_info("开始检查开红包次数...")

        try:
            self.session.get("https://fijdzpur.act.tmuact.com/money/index/index.html", timeout=10)
        except Exception:
            pass

        _, remain_times = self.get_activity_info()

        if remain_times == -1:
            self.log_warn("获取开红包次数失败")
            return

        self.log_info(f"准备开红包，当前剩余开红包次数: {remain_times}")

        while remain_times > 0 and not stop_event.is_set():
            act_url = "https://fijdzpur.act.tmuact.com/activity/api.php"
            req_timestamp = str(int(time.time() * 1000))
            act_signature = hashlib.sha256(f"{self.device_id}&&{req_timestamp}&&MJ<?TH4&9w^".encode('utf-8')).hexdigest().lower()
            payload = f"m=front&subm=money&action=open&account_id={self.account_id}&session_id={self.session_id}&token=68niVoe1Fx5BZlAQRUOS8xljS%2Fdde802&q=YunSLfAkU&system=Android&signature={act_signature}&appName=%E6%AD%8C%E7%94%BB%E4%B8%9C%E9%98%B3&system_version=16&device_no={self.device_id}&device_type=OnePlus+PLC110&statusBarHeight=40&networkType=wifi&timestamp={req_timestamp}&version=5.0.9.0.3&detail=&client_code=xsb_dongyang"

            headers = {
                "Host": "fijdzpur.act.tmuact.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 16; PLC110 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/145.0.7632.159 Mobile Safari/537.36;xsb_dongyang;xsb_dongyang;5.0.9.0.3;native_app;6.11.0",
            }

            try:
                resp = self.session.post(act_url, headers=headers, data=payload, timeout=10)
                res_json = resp.json()

                msg = res_json.get("msg", "未知结果")

                if res_json.get("status") is True:
                    award_name = res_json.get("data", {}).get("prize_name", msg)
                    self.log_info(f"拆红包成功: {award_name}")
                    self.lottery_results.append(f"中奖 {award_name}")
                else:
                    self.log_info(f"拆红包结果: {msg}")
                    self.lottery_results.append(msg)

            except Exception as e:
                self.log_warn(f"拆红包请求异常: {e}")
                self.lottery_results.append("请求异常")

            remain_times -= 1
            if remain_times > 0:
                if stop_event.wait(random.uniform(3, 5)): return

    def check_wallet(self):
        if stop_event.is_set(): return
        self.log_info("正在查询钱包资产...")

        wallet_url = "https://wallet.act.tmuact.com/activity/api.php"
        payload = f"m=front&subm=money_wallet&action=wallet&session_id={self.session_id}&account_id={self.account_id}&app=XSB_DONGYANG"

        headers = {
            "Host": "wallet.act.tmuact.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.ua,
        }

        try:
            resp = self.session.post(wallet_url, headers=headers, data=payload, timeout=10)
            res_json = resp.json()

            if res_json.get("status") is True and res_json.get("code") == 3001:
                data = res_json.get("data", {})
                total = data.get("total", "0.00")
                list_data = data.get("list", [])

                balance = "0.00"
                for item in list_data:
                    if item.get("name") == "通用钱包":
                        count_val = item.get("count", 0)
                        balance = f"{float(count_val):.2f}"
                        break

                self.wallet_info["total"] = total
                self.wallet_info["balance"] = balance

                self.log_info(f"钱包资产查询成功 - 累计收益: {total} | 账户余额: {balance}")
            else:
                msg = res_json.get("msg", "未知原因")
                self.log_warn(f"查询钱包资产失败: {msg}")

        except Exception as e:
            self.log_warn(f"请求钱包接口异常: {e}")

def process_account(account_data):
    if stop_event.is_set(): return ""

    try:
        session_id, account_id = account_data.split('#')
    except Exception:
        logger.warning(f"账号数据格式错误: {account_data}")
        return ""

    client = TmuyunClient(session_id, account_id)

    if client.init_account():
        if stop_event.is_set(): return ""
        if stop_event.wait(random.uniform(2, 5)): return ""

        read_times, open_times = client.get_activity_info()
        if read_times != -1:
            max_retries = 3
            current_retry = 0

            while read_times < 5 and current_retry < max_retries and not stop_event.is_set():
                need_read = 5 - read_times
                client.log_info(f"当前已阅读: {read_times}/5 篇，准备执行阅读 {need_read} 篇...")
                client.do_read_articles(need_read)

                if stop_event.wait(random.uniform(3, 5)): break

                client.log_info("验证最新阅读进度...")
                read_times, open_times = client.get_activity_info()
                current_retry += 1

            if read_times >= 5:
                client.log_info(f"今日阅读任务已完全达标，可开红包: {open_times} 次。")
            else:
                client.log_warn(f"阅读重试次数已达上限，当前进度: {read_times}/5，继续后续任务。")

            client.do_lottery()
            if stop_event.wait(random.uniform(2, 5)): return ""
        else:
            client.log_warn("获取活动信息失败，跳过阅读和抽奖环节")

        client.check_wallet()

        try:
            total_val = float(client.wallet_info["total"])
            bal_val = float(client.wallet_info["balance"])
            withdraw_val = total_val - bal_val
            if withdraw_val < 0: withdraw_val = 0.0
        except Exception:
            withdraw_val = 0.0

        lines = [f"账号: {client.account_name}"]
        if client.lottery_results:
            for idx, res in enumerate(client.lottery_results, 1):
                lines.append(f"第{idx}次: {res}")
        else:
            lines.append("第1次: 未执行抽奖或无次数")

        lines.append(f"累计: {client.wallet_info['total']}元 | 提现: {withdraw_val:.2f}元 | 余额: {client.wallet_info['balance']}元")
        return "\n".join(lines)
    return ""

def push_message(title, content):
    try:
        QLAPI.notify(title, content)
        print("\n 消息推送成功 (优先基于 QLAPI)")
    except NameError:
        try:
            from notify import send
            send(title, content)
            print("\n消息推送成功")
        except ImportError:
            print("\n未检测到推送模块，仅打印汇总输出:")
            print("\n" + content + "\n")
        except Exception as e:
            print(f"\n备用推送发生异常: {e}")
    except Exception as e:
        print(f"\nQLAPI 推送发生异常: {e}")
        print("\n" + content + "\n")

def main():
    env_data = os.getenv("ghdy")
    if not env_data:
        print("未获取到环境变量中的账号数据")
        return

    accounts = [acc.strip() for acc in env_data.split('\n') if acc.strip()]
    logger.info("=================================================")
    logger.info("          歌画东阳   | 作者: YSJohnson         ")
    logger.info("代码发布地址：https://github.com/YSJohnson/QingLongScripts-YSJ")
    logger.info("=================================================\n")
    logger.info(f"共加载到 {len(accounts)} 个账号")

    executor = ThreadPoolExecutor(max_workers=3)
    futures = []

    for account in accounts:
        if stop_event.is_set():
            break
        futures.append(executor.submit(process_account, account))
        if stop_event.wait(1): break

    while futures and not all(f.done() for f in futures):
        time.sleep(0.5)

    print("\n全部任务运行结束，开始汇总推送...")
    notify_list = []
    for f in futures:
        try:
            res = f.result()
            if res:
                notify_list.append(res)
        except Exception:
            pass

    if notify_list:
        push_content = "\n\n--------------------\n\n".join(notify_list)
        push_message("歌画东阳运行结果", push_content)

    try:
        executor.shutdown(wait=False, cancel_futures=True)
    except Exception:
        executor.shutdown(wait=False)

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
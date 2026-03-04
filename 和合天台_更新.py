# -*- coding: utf-8 -*-
"""
脚本名称: 和合天台 v2.2
作者：YSJohnson
功能：和合天台APP每日自动签到、阅读、评论、分享、发帖、抽奖及钱包余额查询 每日约0.15

【变量配置说明】
1. 账号变量 (hhtt):
   格式：手机号#密码
   多账号用 & 或换行隔开
   示例：18888888888#123456

2. 抽奖链接变量 (hhtt_link):
   格式：https://act.tmlyun.com/lottery/?q=************
   说明：每月更新一次，可在APP-阅读抽奖右上角复制获取。

3. 推送模式变量 (hhtt_push_mode):
   非必填 默认合并推送
   可选值："merge" (合并推送) 或 "single" (单独推送)

更新记录:
- [Add] 增加合并推送与单推模式选项，超长消息自动分段发送
- [Add] 抽奖activityId, prizeVersion动态获取
- [Add] 增加查询余额功能
- [Add] 增加手机号脱敏显示
- [Add] 聚合推送消息格式
- [Fix] 修复抽奖版本号不对的问题
- [Fix] 修复钱包查询鉴权失败的问题
- [Fix] 优化抽奖逻辑，支持多频次抽奖
- [Fix] 抽奖奖品查询
- [Fix] 日志输出优化
"""

import sys
import os
import re
import time
import json
import uuid
import base64
import hashlib
import random
import logging
from urllib.parse import quote, unquote, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Tuple, List, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

CONFIG = {
    "MAX_WORKERS": 3,
    "RETRY_COUNT": 3,
    "TIMEOUT": 15,
    "PROXY_ENABLED": os.getenv("IS_PROXY", "False").lower() == "true",
    "PROXY_URL": os.getenv("PROXY_API", ""),
    "ENV_VAR": "hhtt",
    "LINK_VAR": "hhtt_link",
    "SALT": "FR*r!isE5W",
    "TENANT_ID": "5",
    "PUSH_MODE": os.getenv("hhtt_push_mode", "merge").lower()
}

requests.packages.urllib3.disable_warnings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger("SkyT_Bot")


def send_notification(title: str, content: str):
    try:
        QLAPI.notify(title, content)
    except NameError:
        try:
            import notify
            notify.send(title, content)
        except ImportError:
            logger.info(f"\n未检测到推送模块，本地打印推送内容:\n【{title}】\n{content}\n")


class SecurityProvider:
    PUB_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXi
zPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXF
c+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlT
HMlluw4ZYmnOwg+thwIDAQAB
-----END PUBLIC KEY-----"""

    @staticmethod
    def rsa_encrypt(content: str) -> str:
        try:
            rsa_key = RSA.import_key(SecurityProvider.PUB_KEY_PEM)
            cipher = PKCS1_v1_5.new(rsa_key)
            encrypted_bytes = cipher.encrypt(content.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"❌ 加密过程发生错误: {e}")
            return ""

    @staticmethod
    def generate_signature(path: str, session_id: str, req_id: str, timestamp: str) -> str:
        clean_path = path.split('?')[0] if '?' in path else path
        raw_str = f"{clean_path}&&{session_id}&&{req_id}&&{timestamp}&&{CONFIG['SALT']}&&{CONFIG['TENANT_ID']}"
        return hashlib.sha256(raw_str.encode()).hexdigest()

    @staticmethod
    def deterministic_uuid(seed_key: str) -> str:
        m = hashlib.md5(seed_key.encode()).hexdigest()
        s = hashlib.sha256(seed_key.encode()).hexdigest()
        return f"00000000-{s[8:12]}-{s[20:24]}-ffff-{m[16:28]}"


class DeviceManager:
    POOLS = {
        0: ("xiaomi", ["23116PN5BC", "23127PN0CC", "24030PN60C", "23113RKC6C", "2311DRK48C"]),
        1: ("samsung", ["SM-S9280", "SM-S9210", "SM-S9180", "SM-F9460", "SM-S7110"]),
        2: ("huawei", ["ALN-AL00", "ALN-AL80", "HBP-AL00", "ALT-AL10", "BRA-AL00"]),
        3: ("oppo", ["PHY110", "PHZ110", "PJH110", "PJD110", "PHN110"]),
        4: ("vivo", ["V2309A", "V2324A", "V2307A", "V2337A", "V2302A"]),
        5: ("oneplus", ["PJD110", "PJE110", "PHP110", "PHB110", "PHK110"]),
    }

    @classmethod
    def get_ua(cls, phone: str) -> str:
        seed_int = int(hashlib.md5(phone.encode()).hexdigest()[:8], 16)
        uuid_val = SecurityProvider.deterministic_uuid(phone)

        last_num = int(phone[-1]) if phone[-1].isdigit() else 0
        brand_idx = last_num % len(cls.POOLS)
        brand_name, model_list = cls.POOLS[brand_idx]

        if len(phone) >= 6:
            mid_idx = int(phone[len(phone) // 2])
        else:
            mid_idx = seed_int

        model_idx = mid_idx % len(model_list)
        device_model = model_list[model_idx]

        phone_sum = sum(int(c) for c in phone if c.isdigit())
        if phone_sum % 10 < 2:
            os_sys = "iOS"
            ver_list = ["17.4.1", "17.3", "16.7.2", "18.0", "17.5"]
            ios_list = ["iPhone16,2", "iPhone15,3", "iPhone15,2", "iPhone14,3", "iPhone13,4"]
            device_model = ios_list[mid_idx % len(ios_list)]
            brand_name = "apple"
        else:
            os_sys = "Android"
            ver_list = ["14", "13", "12", "11", "15"]

        ver_offset = int(phone[-2:]) if len(phone) >= 2 else 0
        ver_idx = (seed_int + ver_offset) % len(ver_list)
        os_ver = ver_list[ver_idx]

        return f"4.5.6;{uuid_val};{device_model};{os_sys};{os_ver};{brand_name.lower()};6.8.0"


class SkyTClient:
    HOST = "vapp.tmuyun.com"
    AUTH_HOST = "passport.tmuyun.com"
    ACT_HOST = "act.tmlyun.com"
    MY_HOST = "my.tmlyun.com"
    HITOKOTO_API = "https://v1.hitokoto.cn/"

    def __init__(self, raw_data: str):
        parts = raw_data.split("#")
        self.phone = parts[0]
        self.pwd = parts[1]

        if len(self.phone) == 11:
            self.masked_phone = f"{self.phone[:3]}****{self.phone[7:]}"
        else:
            self.masked_phone = self.phone

        raw_q = ""
        if len(parts) >= 3:
            raw_q = parts[2]
        else:
            raw_q = os.getenv(CONFIG['LINK_VAR'], "")

        if raw_q:
            self.q = unquote(raw_q.replace("https://act.tmlyun.com/lottery/?q=", ""))
        else:
            self.q = ""
            logger.warning(f"⚠️ [{self.masked_phone}] 未检测到抽奖链接(hhtt_link)，将无法执行抽奖")

        self.ua = DeviceManager.get_ua(self.phone)
        self.sess = requests.Session()
        self.proxy_dict = None

        self.session_id = ""
        self.account_id = ""
        self.lottery_token = ""

        retries = Retry(total=CONFIG['RETRY_COUNT'], backoff_factor=0.5)
        self.sess.mount('https://', HTTPAdapter(max_retries=retries))

    def _refresh_proxy(self):
        if not CONFIG['PROXY_ENABLED'] or not CONFIG['PROXY_URL']:
            return
        try:
            resp = requests.get(CONFIG['PROXY_URL'], timeout=5)
            ip = resp.text.strip()
            if ":" in ip:
                self.proxy_dict = {"http": ip, "https": ip}
        except Exception:
            self.proxy_dict = None

    def _api_call(self, method: str, url: str, headers: Dict = None, data: Any = None, is_json: bool = False) -> Dict:
        attempts = 0
        while attempts < CONFIG['RETRY_COUNT']:
            try:
                if CONFIG['PROXY_ENABLED'] and not self.proxy_dict:
                    self._refresh_proxy()

                req_args = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "timeout": CONFIG['TIMEOUT'],
                    "proxies": self.proxy_dict,
                    "verify": False
                }

                if is_json:
                    req_args["json"] = data
                else:
                    req_args["data"] = data

                resp = self.sess.request(**req_args)
                resp.raise_for_status()
                return resp.json()

            except Exception as e:
                attempts += 1
                logger.debug(f"[{self.masked_phone}] 请求失败 (重试 {attempts}): {e}")
                if CONFIG['PROXY_ENABLED']:
                    time.sleep(1)
                    self._refresh_proxy()
        raise Exception("网络连接失败")

    def _build_headers(self, path: str, content_type: str = None) -> Dict:
        req_id = str(uuid.uuid4())
        ts = str(int(time.time() * 1000))
        sign = SecurityProvider.generate_signature(path, self.session_id, req_id, ts)

        h = {
            "User-Agent": self.ua,
            "Host": self.HOST,
            "X-TENANT-ID": CONFIG['TENANT_ID'],
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": req_id,
            "X-TIMESTAMP": ts,
            "X-SIGNATURE": sign,
            "X-ACCOUNT-ID": self.account_id,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        if content_type:
            h["Content-Type"] = content_type
        return h

    def fetch_comment_text(self) -> Tuple[str, str]:
        try:
            params = {
                "c": ["d", "i"],
                "encode": "json",
                "charset": "utf-8"
            }
            r = requests.get(self.HITOKOTO_API, params=params, verify=False, timeout=5)
            if r.status_code == 200:
                data = r.json()
                content = data.get("hitokoto", "")
                source = data.get("from", "") or data.get("from_who", "") or "随笔"

                if content:
                    return source, content
        except Exception as e:
            logger.warning(f"一言接口请求异常: {e}")

        fallback_quotes = [
            ("佚名", "俯仰不愧天地，褒贬自有春秋。"),
            ("佚名", "相思本是无凭语，莫向花笺费泪行"),
            ("随感", "庭院深深深几许，杨柳堆烟，帘幕无重数")
        ]
        return random.choice(fallback_quotes)

    def execute_login(self) -> bool:
        try:
            path_init = "/api/account/init"
            res = self._api_call("POST", f"https://{self.HOST}{path_init}",
                                 headers=self._build_headers(path_init,
                                                             "application/x-www-form-urlencoded;charset=utf-8"))
            self.session_id = (res.get("data") or {}).get("session", {}).get("id", "")

            enc_pwd = SecurityProvider.rsa_encrypt(self.pwd)
            cred_req_id = str(uuid.uuid4())
            cred_ts = str(int(time.time() * 1000))
            cred_path = "/web/oauth/credential_auth"
            cred_sign = SecurityProvider.generate_signature(cred_path, self.session_id, cred_req_id, cred_ts)

            auth_payload = {
                "client_id": "10",
                "password": enc_pwd,
                "phone_number": self.phone
            }
            auth_headers = {
                "User-Agent": self.ua,
                "X-REQUEST-ID": cred_req_id,
                "X-SIGNATURE": cred_sign,
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Host": self.AUTH_HOST
            }

            auth_res = self._api_call("POST", f"https://{self.AUTH_HOST}{cred_path}",
                                      headers=auth_headers, data=auth_payload)
            code = (auth_res.get("data") or {}).get("authorization_code", {}).get("code", "")

            login_path = "/api/zbtxz/login"
            login_body = f"check_token=&code={code}&token=&type=-1&union_id="
            login_res = self._api_call("POST", f"https://{self.HOST}{login_path}",
                                       headers=self._build_headers(login_path,
                                                                   "application/x-www-form-urlencoded;charset=utf-8"),
                                       data=login_body)

            if login_res.get("code") == 0:
                sess_data = (login_res.get("data") or {}).get("session", {})
                self.session_id = sess_data.get("id")
                self.account_id = sess_data.get("account_id")
                logger.info(f"[{self.masked_phone}] 🟢 登录成功")
                return True
            else:
                logger.error(f"[{self.masked_phone}] 🔴 登录失败: {login_res.get('message')}")
                return False
        except Exception as e:
            logger.error(f"[{self.masked_phone}] ❌ 登录过程异常: {e}")
            return False

    def run_daily_tasks(self):
        try:
            s_path = "/api/user_mumber/sign"
            s_res = self._api_call("GET", f"https://{self.HOST}{s_path}", headers=self._build_headers(s_path))
            if s_res.get("code") == 0:
                score = (s_res.get("data") or {}).get("signIntegral", 0)
                logger.info(f"[{self.masked_phone}] ✨ 签到成功: +{score} 分")
            else:
                logger.info(f"[{self.masked_phone}] ⚠️ 签到反馈: {s_res.get('message')}")
            time.sleep(random.uniform(2, 4))

            t_path = "/api/user_mumber/doTask"
            self._api_call("POST", f"https://{self.HOST}{t_path}",
                           headers=self._build_headers(t_path, "application/x-www-form-urlencoded;charset=utf-8"),
                           data="memberType=6&member_type=6")
            time.sleep(random.uniform(2, 4))

            l_path = "/api/article/channel_list?channel_id=5bf216941b011b0880b6e49f&isDiFangHao=false&is_new=true&list_count=0&size=40"
            art_res = self._api_call("GET", f"https://{self.HOST}{l_path}", headers=self._build_headers(l_path))
            art_list = (art_res.get("data") or {}).get("article_list", []) or []
            art_ids = [i.get("id") for i in art_list]
            random.shuffle(art_ids)

            bbs_path = "/api/bbs/api/post/list?categoryId=504"
            bbs_res = self._api_call("GET", f"https://{self.HOST}{bbs_path}", headers=self._build_headers(bbs_path))
            bbs_list = (bbs_res.get("data") or {}).get("records", []) or []
            bbs_ids = [i.get("id") for i in bbs_list]
            random.shuffle(bbs_ids)

            logger.info(f"[{self.masked_phone}] 📋 获取到文章 {len(art_ids)} 篇, 帖子 {len(bbs_ids)} 个")

            for i in range(5):
                if i < len(art_ids):
                    aid = art_ids[i]
                    r_path = f"/api/article/detail?id={aid}"
                    self._api_call("GET", f"https://{self.HOST}{r_path}", headers=self._build_headers(r_path))
                    time.sleep(random.uniform(8, 12))

                    lk_path = "/api/favorite/like"
                    self._api_call("POST", f"https://{self.HOST}{lk_path}",
                                   headers=self._build_headers(lk_path,
                                                               "application/x-www-form-urlencoded;charset=utf-8"),
                                   data=f"action=true&id={aid}")
                    time.sleep(random.uniform(2, 4))

                    _, c_txt = self.fetch_comment_text()
                    c_path = "/api/comment/create/v2"
                    self._api_call("POST", f"https://{self.HOST}{c_path}",
                                   headers=self._build_headers(c_path, "application/json;charset=utf-8"),
                                   data={"channel_article_id": aid, "content": c_txt}, is_json=True)
                    time.sleep(random.uniform(3, 5))

                    task_res = self._api_call("POST", f"https://{self.HOST}{t_path}",
                                              headers=self._build_headers(t_path,
                                                                          "application/x-www-form-urlencoded;charset=utf-8"),
                                              data=f"memberType=3&member_type=3&target_id={aid}")

                    if task_res.get("code") == 0:
                        logger.info(f"[{self.masked_phone}] 📖 文章 {i + 1}/5: 完成")
                    else:
                        logger.warning(f"[{self.masked_phone}] ⚠️ 文章 {i + 1}/5: 上报失败 ({task_res.get('message')})")

                    time.sleep(random.uniform(2, 4))

                if i < len(bbs_ids):
                    bid = bbs_ids[i]
                    self._api_call("GET", f"https://{self.HOST}/api/bbs/api/post/zan?id={bid}&status=0",
                                   headers=self._build_headers("/api/bbs/api/post/zan"))
                    time.sleep(0.5)

                    self._api_call("GET", f"https://{self.HOST}/api/bbs/api/post/zan?id={bid}&status=1",
                                   headers=self._build_headers("/api/bbs/api/post/zan"))
                    time.sleep(random.uniform(2, 4))

                    self._api_call("GET", f"https://{self.HOST}/api/bbs/api/post/share?id={bid}",
                                   headers=self._build_headers("/api/bbs/api/post/share"))
                    time.sleep(random.uniform(2, 4))

                    _, c_txt = self.fetch_comment_text()
                    rep_path = "/api/bbs/api/reply/edit"
                    self._api_call("POST", f"https://{self.HOST}{rep_path}",
                                   headers=self._build_headers(rep_path,
                                                               "application/x-www-form-urlencoded;charset=utf-8"),
                                   data=f"content={quote(c_txt)}&postId={bid}")

                    logger.info(f"[{self.masked_phone}] 💬 帖子 {i + 1}/5: 完成")
                    time.sleep(random.uniform(3, 6))

            for j in range(2):
                _, c_txt = self.fetch_comment_text()
                html_content = quote(f'<p style="margin:0px">{c_txt}</p>\n')
                pub_path = "/api/bbs/api/post/save"
                pub_res = self._api_call("POST", f"https://{self.HOST}{pub_path}",
                                         headers=self._build_headers(pub_path,
                                                                     "application/x-www-form-urlencoded;charset=utf-8"),
                                         data=f"auditStatus=0&categoryId=505&content={html_content}&postType=4&subjectId=227466&topicTitleList=&videoTime=0")

                if pub_res.get("code") == 0:
                    logger.info(f"[{self.masked_phone}] 🖊️ 灌水发帖 {j + 1}/2 成功")
                else:
                    logger.warning(f"[{self.masked_phone}] ⚠️ 发帖失败: {pub_res.get('message')}")

                time.sleep(random.uniform(8, 15))

            my_path = "/api/user_mumber/numberCenter?is_new=1"
            my_res = self._api_call("GET", f"https://{self.HOST}{my_path}", headers=self._build_headers(my_path))
            total = (my_res.get("data") or {}).get("rst", {}).get("total_integral", 0)
            logger.info(f"[{self.masked_phone}] 🔚 每日任务结束，当前总积分: {total}")

        except Exception as e:
            logger.error(f"[{self.masked_phone}] ❌ 任务执行异常: {e}")

    def get_jump_u_param(self) -> str:
        try:
            url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/jumpEquityWallet"
            headers = {
                'Authorization': self.lottery_token,
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                'User-Agent': self.ua
            }
            res = self._api_call("GET", url, headers=headers)
            if res.get("code") == 0:
                data_url = res.get("data", "")
                if data_url:
                    parsed = urlparse(data_url)
                    query = parse_qs(parsed.query)
                    return query.get('u', [''])[0]
            return ""
        except Exception as e:
            logger.warning(f"[{self.masked_phone}] 获取跳转参数异常: {e}")
            return ""

    def get_equity_token(self) -> str:
        try:
            u_val = self.get_jump_u_param()
            if not u_val:
                logger.warning(f"[{self.masked_phone}] 未能获取到u参数，跳过钱包鉴权")
                return ""

            url = f"https://{self.MY_HOST}/equity-api/user/auth/userLogin"
            headers = {
                'Content-Type': "application/json",
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                "User-Agent": self.ua,
            }
            payload = {
                "u": u_val,
                "accountId": self.account_id,
                "sessionId": self.session_id
            }
            res = self._api_call("POST", url, headers=headers, data=payload, is_json=True)
            if res.get("code") == 0:
                token = (res.get("data") or {}).get("token", "")
                if token:
                    return token

            logger.warning(f"[{self.masked_phone}] 获取钱包鉴权失败: {res.get('message')}")
            return ""
        except Exception as e:
            logger.error(f"[{self.masked_phone}] 获取钱包鉴权异常: {e}")
            return ""

    def get_wallet_info(self) -> str:
        try:
            token = self.get_equity_token()
            if not token:
                token = self.lottery_token

            if not token:
                return "未获取到Token，无法查询余额"

            device_id = SecurityProvider.deterministic_uuid(self.phone)
            url = f"https://{self.MY_HOST}/equity-api/redBag/getWalletInfo?device={device_id}"

            headers = {
                "User-Agent": self.ua,
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "com.zjonline.tiantai",
                "X-REQUEST-ID": str(uuid.uuid4()),
                "Authorization": token
            }

            res = self._api_call("GET", url, headers=headers)

            if res.get("code") == 0:
                data_list = res.get("data", [])
                if data_list and isinstance(data_list, list):
                    info = data_list[0]
                    total = info.get("totalPrice", 0)
                    withdrawn = info.get("totalTransPrice", 0)
                    alipay = info.get("aliPayTotalPrice", 0)
                    return f"💰 累计: {total}元 | 提现: {withdrawn}元 | 余额: {alipay}元"
            return ""

        except Exception as e:
            logger.debug(f"[{self.masked_phone}] 查询余额失败: {e}")
            return ""

    def get_prize_version(self, activity_id: int) -> int:
        try:
            client_id = self.ua.split(";")[1]
            url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/frontPage?activityId={activity_id}&clientId={client_id}"
            headers = {
                'Authorization': self.lottery_token,
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                'User-Agent': self.ua
            }
            res = self._api_call("GET", url, headers=headers)
            if res.get("code") == 0:
                data = res.get("data") or {}
                version = data.get("prizeVersion")
                if version is not None:
                    return int(version)
            return 2
        except Exception as e:
            logger.warning(f"[{self.masked_phone}] 获取prizeVersion失败，使用默认值2: {e}")
            return 2

    def run_lottery_module(self) -> str:
        try:
            if not self.q:
                logger.info(f"[{self.masked_phone}] ⏩ 跳过抽奖 (未配置抽奖链接)")
                return ""

            time.sleep(random.uniform(2, 5))
            logger.info("------ 开始检查抽奖 ------")

            l_url = f"https://{self.ACT_HOST}/activity-api/lottery/api/auth/userLogin"
            l_req_id = str(uuid.uuid4())
            l_payload = {
                "q": self.q, "accountId": self.account_id,
                "sessionId": self.session_id, "tenantCode": "xsb_tiantai"
            }
            l_headers = {
                'Content-Type': "application/json", 'X-REQUEST-ID': l_req_id,
                'X-Requested-With': "com.zjonline.tiantai"
            }

            res = self._api_call("POST", l_url, headers=l_headers, data=l_payload, is_json=True)

            third_id = 0

            if res.get("code") == 0:
                login_data = res.get("data") or {}
                self.lottery_token = login_data.get("token", "")
                third_id = login_data.get("thirdId", 0)
            else:
                logger.warning(f"[{self.masked_phone}] 🔴 抽奖系统登录失败: {res.get('message')}")
                return ""

            if not self.lottery_token:
                logger.warning(f"[{self.masked_phone}] ⚠️ Token获取为空，跳过抽奖")
                return ""

            if third_id:
                target_aid = third_id
            else:
                logger.warning(f"[{self.masked_phone}] ⚠️ 未找到有效活动ID(thirdId)，请等待作者更新脚本")
                return ""

            current_prize_version = self.get_prize_version(target_aid)
            logger.info(f"[{self.masked_phone}] ℹ️ 当前活动ID: {target_aid}, PrizeVersion: {current_prize_version}")

            auth_headers = {
                'Authorization': self.lottery_token, 'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai", 'Sec-Fetch-Site': "same-origin", 'Sec-Fetch-Mode': "cors"
            }

            chk_url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/frontPageNum?activityId={target_aid}"
            chk_res = self._api_call("GET", chk_url, headers=auth_headers)
            remain = (chk_res.get("data") or {}).get("remainPrizeNum", 0)

            lottery_msgs = []

            if remain > 0:
                logger.info(f"[{self.masked_phone}] 🎰 剩余抽奖次数: {remain}")

                for i in range(remain):
                    logger.info(f"[{self.masked_phone}] ⏳ 正在进行第 {i + 1} / {remain} 次抽奖...")

                    draw_url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/userActivityLottery"
                    draw_payload = {
                        "activityId": target_aid,
                        "clientId": self.ua.split(";")[1],
                        "prizeVersion": current_prize_version
                    }
                    draw_headers = {'Content-Type': "application/json", 'Authorization': self.lottery_token}

                    draw_res = self._api_call("POST", draw_url, headers=draw_headers, data=draw_payload, is_json=True)

                    if draw_res.get("code") == 0:
                        data_res = draw_res.get('data') or {}
                        is_prize = data_res.get('isPrize', 0)
                        prize_name = data_res.get('prizeName', '未知')

                        log_msg = ""
                        notify_line = ""

                        if str(is_prize) == "1" or is_prize is True or is_prize == 1:
                            log_msg = f"[{self.masked_phone}] 🎁 第{i + 1}次: 中奖 {prize_name}"
                            notify_line = f"🎁 第{i + 1}次: 中奖 {prize_name}"
                        else:
                            log_msg = f"[{self.masked_phone}] 💨 第{i + 1}次: 未中奖"
                            notify_line = f"💨 第{i + 1}次: 未中奖"

                        logger.info(log_msg)
                        lottery_msgs.append(notify_line)
                    else:
                        err_msg = f"⚠️ 第{i + 1}次: 请求失败"
                        logger.warning(f"[{self.masked_phone}] {err_msg}")
                        lottery_msgs.append(err_msg)

                    time.sleep(3)
            else:
                logger.info(f"[{self.masked_phone}] ❌ 今日无剩余抽奖次数")
                lottery_msgs.append("❌ 今日无剩余抽奖次数")

            logger.info(f"[{self.masked_phone}] 💳 正在查询钱包余额...")
            wallet_msg = self.get_wallet_info()
            if wallet_msg:
                logger.info(f"[{self.masked_phone}] {wallet_msg}")

            header = f"📱 账号: {self.masked_phone}"
            body = "\n".join(lottery_msgs) if lottery_msgs else "💨 今日无抽奖记录"
            footer = wallet_msg if wallet_msg else "⚠️ 未查询到余额信息"

            final_push = f"{header}\n{body}\n{footer}"

            if CONFIG["PUSH_MODE"] == "single":
                send_notification("和合天台运行结果", final_push)

            return final_push

        except Exception as e:
            logger.error(f"[{self.masked_phone}] ❌ 抽奖模块异常: {e}")
            return ""


def thread_handler(account_str: str) -> str:
    time.sleep(random.uniform(2, 12))

    if "#" not in account_str:
        return ""

    bot = SkyTClient(account_str)
    if bot.execute_login():
        bot.run_daily_tasks()
        push_res = bot.run_lottery_module()
        return push_res if push_res else ""
    return ""


def main():
    logger.info("=================================================")
    logger.info("          和合天台   | 作者: YSJohnson         ")
    logger.info("代码发布地址：https://github.com/YSJohnson/QingLongScripts-YSJ")
    logger.info("=================================================\n")

    env_data = os.getenv(CONFIG['ENV_VAR'], "")
    if CONFIG['PROXY_ENABLED'] and not CONFIG['PROXY_URL']:
        logger.critical("❌ 已启用代理模式，但未配置代理API地址！")
        return

    if not env_data:
        logger.critical(f"❌ 未找到环境变量 '{CONFIG['ENV_VAR']}'，请检查配置。")
        return

    accounts = [x for x in re.split(r'[&\n]', env_data) if x]
    logger.info(f"📋 成功加载 {len(accounts)} 个账号，并发线程数: {CONFIG['MAX_WORKERS']}")

    with ThreadPoolExecutor(max_workers=CONFIG['MAX_WORKERS']) as pool:
        results = list(pool.map(thread_handler, accounts))

    if CONFIG["PUSH_MODE"] == "merge":
        valid_results = [res for res in results if res.strip()]

        if valid_results:
            merged_content = "\n\n--------------------\n\n".join(valid_results)
            lines = merged_content.split("\n")

            if len(lines) <= 100:
                send_notification("和合天台运行结果", merged_content)
            else:
                logger.info("📝 消息内容较长，将进行分段推送...")
                chunk_size = 100
                for i in range(0, len(lines), chunk_size):
                    chunk = "\n".join(lines[i:i + chunk_size])
                    part_num = (i // chunk_size) + 1
                    send_notification(f"和合天台运行结果 (部分{part_num})", chunk)
                    time.sleep(2)

    logger.info("\n>>> ✅ 所有任务执行完毕 <<<")


if __name__ == "__main__":
    main()
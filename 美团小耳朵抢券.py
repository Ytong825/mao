#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   美团外卖 - 小耳朵限定 饮品专享券 自动抢券脚本
#   活动入口：美团/美团外卖App搜索"小耳朵"
#   活动时间：7月3日-7月12日 每日10/12/14/16/18/20点整点抢券
#   默认只抢: 满20减20 (2000张，秒光，需高并发)
#
#   环境变量：
#     mt_cookie     格式: 备注名#完整Cookie字符串#dj-token  多号用@或换行分隔
#     MT_FINGERPRINT mtFingerprint指纹(可选，有默认值)
#   可选环境变量：
#     MT_THREADS     每个账号线程数，默认30
#     MT_ADVANCE     整点延迟发射毫秒，默认0(整点发射)
#     MT_WARMUP      提前预热秒数，默认5
#     MT_INTERVAL    轮间隔毫秒，默认50
#     MT_COUPON_TARGET 目标券: 20=满20减20(默认), 40=满40减20, 0=两种都抢
#
#   命令行: --now 立即测试模式

import os, sys, time, uuid, threading, json
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from collections import defaultdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== 配置 ==========
INFO_URL = "https://rights-apigw.meituan.com/api/rights/activity/secKill/info"
GRAB_URL = "https://rights-apigw.meituan.com/api/rights/activity/secKill/grab"
COOKIE_ENV = "mt_cookie"
HTTP_TIMEOUT = 2
APP_VERSION = "12.60.402"
ACTIVITY_ID = "A2071918675363688470"
GD_ID = 1031755
PAGE_ID = 1036882

THREADS = int(os.getenv("MT_THREADS", "30"))
ADVANCE_MS = int(os.getenv("MT_ADVANCE", "0"))
WARMUP_SEC = int(os.getenv("MT_WARMUP", "5"))
INTERVAL_MS = int(os.getenv("MT_INTERVAL", "50"))
TARGET = int(os.getenv("MT_COUPON_TARGET", "20"))
DEBUG = os.getenv("MT_DEBUG", "0") == "1"

# mtFingerprint - 从抓包获取的设备指纹，也可通过环境变量 MT_FINGERPRINT 覆盖
DEFAULT_FINGERPRINT = os.getenv("MT_FINGERPRINT",
    "i2HKpOmsirDPavelVfQBZMqfPLIuJSYL3Lc1cBee7MqV9pfnJrr3Gw/Cvaij8YRUSiDnl8LtEdwr8bdMEHSEKMLm9t2HEVVohGWozL8sjAivtzcbL2SLegTgAscHbX3zkAzvRtaMlt6hrGLdp1pjwQZTq2kEfEO24W5kgMyWSRnWzA15UwRvj+IOoveeZN6Si5wT+1tLprHaDm+zQc9V3+DSdU262Mz8Axbl+GymO2zUQLmLfcaESws+wctqB5uW5uZ37txhl9Z1OVNimcFoiEsT18yMEXmZyN/xs4EfUrKnNku4ws9msM550zaGR4Hj4QP+Bq9q1erHbR35xMs8Ss5XLvs1Y7B/yes667eOcBJr3spED3gBaxYD7W8A9UQ8gJPWSigRhd/0JftfOkctGofiXb3V3BsbFw/l1+xLwTEHjoTp5SuHWLyiYulXl6u3fg2VFWJODlJtOtIHCZCdcgCYrqjMRYVmgaja8SPoxI581IyP5RVdgvTwTVE5jFZtNte8oTfic0an9AtWUt7MqkfHOUSksZcW2KFILCgSNX4EnGTjQd5QI9Du8CrORtMY0WqUZJv7UsErX8Z9tIgUng31S7A+AFX9muL/xGmUSBWwPT1eRgepS0uQUF2iAIgio7EHJ/bClehUL/c1C2sB8woR2dcoAjagquVC9c08y5YC1HlAKQ9sm6L6kgzURlpxrwOsaq8x7mcS47iMMMcRii1AHzGblbd6Vk2VOZjZWiMJTKKPzo85CIKxw8jPObRVw9J++n+NrGNWBxcH9ui3GsYyd+j1tLSIwI01I0dmHUkGtgSVRQ9CIi4MlTG3HYZE4WFUWSFDEAKIGPWtP09im7KmqrG1e00UcwMXhd3U+OxP3chwXAfUT4so9RgqWYn2fb7HVCkwOCNDz/XT6gTr3IysDnaHBL0gOlt8U98sbt5Er6hv9hMbYgTHgOdqx0f2+/1ZBsNsdODLXJ0lTgFf9ezKI73qPLqTQeHpFYcTCBIxy3eB0HclkW8VyXIMRr/YdBLR/ZIsjlAea6mTAnffSu7TBjK7y9AXkFnccstR9XB7Ln00087JVfCEZ/EOgSXRaEDJDzZZX7l07WGte1m5xBwU7DRzHmTePNq0leHOAwqcTQzFrd762YlqEKq8/LwsuTNlRiP+Ea+gBg8yCvvaTcfO+r/G14poaI7LKCkis52AFFDUUZvpO0vo1ehppAkbmsL2H960MXYjvJyVYItAYnFMFVL4fWB7TmPJXag1TrhFeiihYhy3stWJ7GtIvMt5PAJslV+mfclgz4eSgf6bbV/va/Kyj3C333evhdf/evsdqkR/ESL8VB/Vn8+JN3GumpPwoy9D0r8rqTBBlOYILaq54we1Y0O2FOJ+ApjEA90aABtTYZG29HHD760EBhTpbKH+oWOwuzB2ALQrGK2/6jqHBuktqyOb5PJOXoN2lH8="
)

DISCLAIMER = (
    "免责声明：本脚本仅供学习和技术研究使用，请遵守平台规则和相关法律法规；"
    "所发布的内容仅供学习，禁止用于其他用途，您必须在下载后的24小时内从计算机或手机中完全删除以上内容。"
    "严禁产生利益链！因使用本脚本产生的风险由使用者自行承担。"
)

# ========== 颜色 ==========
C = {"R":"\033[31m","G":"\033[32m","Y":"\033[33m","B":"\033[34m",
     "C":"\033[36m","M":"\033[35m","W":"\033[90m","D":"\033[2m","BOLD":"\033[1m","RST":"\033[0m"}
AC = ["B","M","C","G","R","Y"]
_print_lk = threading.Lock()

def P(*a, **kw):
    with _print_lk: print(*a, **kw)

def clr(t, *codes):
    p = "".join(C.get(c,"") for c in codes)
    return f"{p}{t}{C['RST']}" if p else t

# ========== 账号解析 ==========
class Account:
    __slots__ = ("cookie","dj_token","token","label","color","fingerprint")
    def __init__(self, s, idx, total):
        s = s.strip()
        # 清理误复制的 export mt_cookie=' 前缀和末尾的 '
        for prefix in ["export mt_cookie='", "export mt_cookie=\"", "mt_cookie='", "mt_cookie=\""]:
            if s.startswith(prefix):
                s = s[len(prefix):]
        s = s.rstrip("'\"; ")
        parts = s.split("#")
        if len(parts) < 3:
            raise ValueError(f"账号{idx}: 格式应为 备注#Cookie#dj-token")
        note, cookie, dj = parts[0], parts[1], parts[-1]
        token = ""
        for item in cookie.split(";"):
            item = item.strip()
            if item.startswith("token="):
                token = item[6:]; break
        if not token:
            for item in cookie.split(";"):
                item = item.strip()
                if item.startswith("mt_c_token="):
                    token = item[11:]; break
        if not token: raise ValueError(f"账号{idx}: Cookie中无token")
        if not dj or len(dj) < 20: raise ValueError(f"账号{idx}: dj-token无效")
        self.cookie = cookie
        self.dj_token = dj
        self.token = token
        self.label = note if note else (f"账号{idx}" if total<=1 else f"账号{idx}/{total}")
        self.color = AC[(idx-1)%len(AC)]
        self.fingerprint = DEFAULT_FINGERPRINT

    def headers(self):
        return {
            "Host":"rights-apigw.meituan.com","Accept":"*/*",
            "Content-Type":"application/json","Sec-Fetch-Site":"same-site",
            "Accept-Language":"zh-CN,zh-Hans;q=0.9","Sec-Fetch-Mode":"cors",
            "Accept-Encoding":"gzip, deflate, br",
            "Origin":"https://market.waimai.meituan.com",
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
                        "MT_WEB_UA/0.0.1 KNB/1.0.0 MeituanGroup/12.60.402 AppId/10/12.60.402 MSI/1.0.0",
            "Referer":"https://market.waimai.meituan.com/","Connection":"keep-alive",
            "dj-token":self.dj_token,"Cookie":self.cookie,
        }

def parse_accounts(text):
    raw = [c for c in text.replace("\n","@").split("@") if c.strip()]
    if not raw: raise ValueError("未找到有效cookie")
    return [Account(r, i+1, len(raw)) for i,r in enumerate(raw)]

# ========== HTTP ==========
def make_session():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(
        max_retries=Retry(total=2,connect=2,read=2,backoff_factor=0.03,
            status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET","POST"])),
        pool_connections=100,pool_maxsize=100))
    return s

def url_params(instance_id=""):
    p = {"cType":"mtiphone","fpPlatform":"5","wx_openid":"","appVersion":APP_VERSION,
         "gdBs":"0000","pageVersion":"364600","new_gundam":"1",
         "__gd_activid":str(GD_ID),"__gd_pageid":str(PAGE_ID),"__gd_pagev":"364600",
         "__gd_appv":APP_VERSION,"__gd_ctype":"mtiphone","yodaReady":"h5",
         "csecplatform":"4","csecversion":"4.2.4","activityId":ACTIVITY_ID}
    if instance_id: p["instanceId"] = instance_id
    return p

def get_info(sess, acc, round_code=None):
    p = url_params()
    if round_code: p["roundCode"] = round_code
    try:
        r = sess.get(INFO_URL, headers=acc.headers(), params=p, timeout=HTTP_TIMEOUT)
        return r.json()
    except: return None

def do_grab(sess, acc, iid, rc, rnd, gtoken):
    p = url_params(iid); p["roundCode"] = rnd
    body = {"activityId":ACTIVITY_ID,"gdId":GD_ID,"pageId":PAGE_ID,"instanceId":iid,
            "rightCode":rc,"roundCode":rnd,"grabToken":gtoken,"appVersion":APP_VERSION,
            "mtFingerprint":acc.fingerprint}
    try:
        r = sess.post(GRAB_URL, headers=acc.headers(), params=p, json=body, timeout=HTTP_TIMEOUT)
        j = r.json()
    except Exception as e:
        return False, f"网络异常", False, False
    code = j.get("code",-999); msg = str(j.get("msg","")); d = j.get("data",{})
    sub = d.get("subCode",0); cp = d.get("coupon",{}) or {}
    toast = str(cp.get("toastMsg","")); st = cp.get("status",0)
    ca = cp.get("couponAmount",0); cl = cp.get("couponAmountLimit",0)
    if st == 3:
        return True, toast or f"抢券成功!满{cl:.0f}减{ca:.0f}", False, False
    if sub == 9017 or any(k in toast for k in ["来晚了","抢完了","已抢光"]):
        return False, toast or f"抢完了(满{cl:.0f}减{ca:.0f})", True, False
    if code == 6 or "登录" in msg:
        return False, "未登录/Token失效", False, False
    if any(k in toast for k in ["已领取","已抢过","上限","明天","今日已领"]):
        return False, toast or msg, False, True
    txt = toast or msg or f"code={code}"
    return False, txt, False, False

def sync_time():
    try:
        t0=time.time(); s=make_session()
        r=s.get(INFO_URL,params=url_params(),timeout=5); el=time.time()-t0
        sd=r.headers.get("Date","")
        if sd:
            st=parsedate_to_datetime(sd).timestamp()
            return st-(t0+el/2), el
    except: pass
    return 0, 0.1

def now_cal(off): return time.time()+off

# ========== 查询场次 ==========
def find_round(acc):
    s = make_session()
    info = get_info(s, acc)
    if not info or info.get("code")!=1: return None
    d = info.get("data",{}); st = d.get("currentTime",int(time.time()))
    rounds = d.get("allGrabRounds",[])
    today = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    ts0 = int(today.timestamp())

    ci = d.get("currentGrabCouponInfo")
    if ci:
        rc = ci.get("roundCode")
        cr = next((r for r in rounds if r.get("roundCode")==rc), None)
        if cr:
            h,m,sec = map(int,cr["startTime"].split(":"))
            eh,em,es = map(int,cr["endTime"].split(":"))
            s_ts = ts0+h*3600+m*60+sec; e_ts = ts0+eh*3600+em*60+es
            if s_ts <= st <= e_ts:
                avail = []
                for c in ci.get("coupon",[]):
                    lim = c.get("couponAmountLimit",0); stock = c.get("residueStock",0)
                    cst = c.get("status",0)
                    if (TARGET==0 or lim==TARGET) and stock>0 and cst!=4:
                        avail.append({"rc":c.get("rightCode",""),"name":c.get("couponName","饮品专享券"),
                                     "amt":c.get("couponAmount",0),"lim":lim,"stock":stock})
                if avail:
                    return {"mode":"now","round":cr,"gtoken":ci.get("token",""),
                            "coupons":avail,"fire":time.time()+1.5,
                            "msg":f"当前场({cr['startTime']})有券，立即抢"}

    for r in rounds:
        h,m,sec = map(int,r["startTime"].split(":"))
        s_ts = ts0+h*3600+m*60+sec
        if s_ts > st:
            ri = get_info(s, acc, r.get("roundCode")); cs=[]; gt=""
            if ri and ri.get("code")==1:
                cci = ri.get("data",{}).get("currentGrabCouponInfo",{})
                gt = cci.get("token","")
                for c in cci.get("coupon",[]):
                    lim = c.get("couponAmountLimit",0)
                    if TARGET==0 or lim==TARGET:
                        cs.append({"rc":c.get("rightCode",""),"name":c.get("couponName",""),
                                   "amt":c.get("couponAmount",0),"lim":lim,
                                   "stock":c.get("residueStock",0)})
            return {"mode":"wait","round":r,"gtoken":gt,"coupons":cs,
                    "fire":s_ts+ADVANCE_MS/1000.0,"msg":f"等待 {r['startTime']} 开抢"}
    if rounds:
        r=rounds[0]; h,m,sec=map(int,r["startTime"].split(":"))
        tm = int((today+timedelta(days=1)).timestamp())+h*3600+m*60+sec
        return {"mode":"wait","round":r,"gtoken":"","coupons":[],
                "fire":tm+ADVANCE_MS/1000.0,"msg":f"今日已结束，等明天{r['startTime']}"}
    return None

# ========== 抢券执行器 ==========
class Grabber:
    def __init__(self, acc, n):
        self.acc = acc; self.n = min(n,80)
        self.iid = str(uuid.uuid4())
        self.results = []; self.rlk = threading.Lock()
        self.ok_rc = set(); self.gone_rc = set(); self.got_rc = set()
        self.warmup_s = []

    def log(self, *a):
        P(clr(f"[{self.acc.label}]",self.acc.color,"BOLD"), *a)

    def warmup(self, n=None):
        """并行预热连接，快速完成TCP/SSL握手"""
        if n is None: n = self.n
        self.log(f"并行预热 {n} 连接...")
        sessions = []
        sessions_lk = threading.Lock()
        errors = [0]
        def do_warmup():
            s = make_session()
            try:
                s.get(INFO_URL, headers=self.acc.headers(), params=url_params(), timeout=HTTP_TIMEOUT)
                with sessions_lk: sessions.append(s)
            except:
                errors[0]+=1
                with sessions_lk: sessions.append(s)
        ts = []
        for _ in range(n):
            t = threading.Thread(target=do_warmup, daemon=True)
            t.start(); ts.append(t)
        for t in ts: t.join(timeout=5)
        self.warmup_s = sessions
        self.log(clr(f"预热完成({len(sessions)}连接就绪, {errors[0]}个错误)","G"))

    def prepare_burst(self, coupons):
        """提前创建worker线程，到点调用fire()立即发射"""
        pending = [c for c in coupons if c["rc"] not in self.ok_rc
                   and c["rc"] not in self.gone_rc and c["rc"] not in self.got_rc]
        if not pending: return None
        nc = len(pending); tpc = max(1,self.n//max(nc,1)); total = tpc*nc
        evt = threading.Event()
        ready = [0]; rlk = threading.Lock()
        res_list = []; res_lk = threading.Lock()
        burst_sec = 3.0
        workers = []

        def run_w(tid, cp):
            sess = None
            if self.warmup_s:
                try: sess = self.warmup_s.pop(0)
                except: pass
            if sess is None: sess = make_session()
            rc = cp["rc"]; rnd = cp["rnd"]; gt = cp["gt"]; cl = cp["lim"]
            with rlk: ready[0]+=1
            evt.wait()
            end_t = time.time()+burst_sec
            best = None
            while time.time() < end_t:
                try:
                    t0=time.perf_counter()
                    ok,msg,gone,got = do_grab(sess,self.acc,self.iid,rc,rnd,gt)
                    el=(time.perf_counter()-t0)*1000
                    r = (tid,ok,msg,el,gone,got,cl,rc)
                    if ok:
                        self.ok_rc.add(rc); best=r; break
                    if gone or got:
                        if gone: self.gone_rc.add(rc)
                        if got: self.got_rc.add(rc)
                        best=r; break
                    if best is None or el < best[3]: best=r
                except Exception as e:
                    best = (tid,False,f"异常:{str(e)[:25]}",-1,False,False,cl,rc)
            if best:
                with res_lk: res_list.append(best)

        tid=0
        for c in pending:
            for _ in range(tpc):
                tid+=1
                w=threading.Thread(target=run_w,args=(tid,c),daemon=True)
                w.start(); workers.append(w)

        def fire_and_collect(rn):
            # 等所有worker就绪
            dl=time.time()+5
            while ready[0]<total and time.time()<dl:
                time.sleep(0.002)
            evt.set()  # 发射!
            for w in workers: w.join(timeout=burst_sec+3)
            with self.rlk: self.results.extend(res_list)
            return res_list, total

        return fire_and_collect

# ========== 主流程 ==========
def main_run():
    tw = THREADS*len(accs)
    P(clr("="*60,"C"))
    P(clr("  美团外卖·小耳朵饮品券 自动抢券","C","BOLD"))
    P(clr(f"  账号:{len(accs)} 线程/账号:{THREADS} 总线程:{tw}","C"))
    tstr = f"满{TARGET}减20" if TARGET else "全部"
    P(clr(f"  提前{WARMUP_SEC}s预热 整点+{ADVANCE_MS}ms 轮间隔{INTERVAL_MS}ms 目标:{tstr}","C"))
    P(clr("="*60,"C")); P()

    P(clr("┌─[1/5] 校准服务器时间","B","BOLD"))
    off, rtt = sync_time()
    P(f"│ 偏差:{off*1000:+.0f}ms RTT:{rtt*1000:.0f}ms")

    P(clr("├─[2/5] 查询场次","B","BOLD"))
    tinfo=None; ainfo={}
    gbs = [Grabber(a,THREADS) for a in accs]
    for gb in gbs:
        info = find_round(gb.acc)
        if not info: gb.log(clr("查询失败","R")); continue
        gb.log(info["msg"])
        for c in info["coupons"]:
            ss=f"剩余{c['stock']}张" if c['stock']>0 else "已抢完"
            gb.log(f"  {c['name']} 满{c['lim']:.0f}减{c['amt']:.0f} | {ss}")
        ainfo[gb.acc.label]=info
        if tinfo is None or info["fire"]<tinfo["fire"]: tinfo=info
    if tinfo is None: P(clr("无有效场次","R")); return

    mode=tinfo["mode"]; fts=tinfo["fire"]
    wts = fts-WARMUP_SEC if mode=="wait" else fts-1.5

    P(clr("├─[3/5] 时间","B","BOLD"))
    if mode=="now":
        P(f"│ 模式:{clr('立即抢','G','BOLD')}")
    else:
        P(f"│ 模式:{clr('定时抢','Y','BOLD')}")
        P(f"│ 场次:{tinfo['round']['startTime']}")
        P(f"│ 预热:{datetime.fromtimestamp(wts).strftime('%H:%M:%S')}")
        P(f"│ 发射:{datetime.fromtimestamp(fts).strftime('%H:%M:%S.%f')[:-3]}")

    P(clr("├─[4/5] 等待预热...","B","BOLD"))
    while True:
        n=now_cal(off); r=wts-n
        if r<=0: break
        if r>1:
            P(clr(f"│  距预热:{int(r)}秒","W"))
            time.sleep(min(r-0.5,5))
        else: time.sleep(0.05)

    P(clr("├─[5/5] 预热TCP连接 + 提前部署worker线程","B","BOLD"))
    fire_fns = {}
    for gb in gbs:
        gb.warmup(THREADS)
        ci = ainfo.get(gb.acc.label)
        if ci:
            cfr=[]
            for c in ci["coupons"]:
                rc=c["rc"]
                if rc in gb.ok_rc or rc in gb.gone_rc or rc in gb.got_rc: continue
                cc=dict(c); cc["rnd"]=ci["round"]["roundCode"]; cc["gt"]=ci["gtoken"]
                cfr.append(cc)
            if cfr:
                fn = gb.prepare_burst(cfr)
                if fn: fire_fns[gb.acc.label] = (gb, fn)
                gb.log(clr("worker线程已就绪，等待发射","G"))

    if mode=="wait":
        P(clr("  所有worker已就绪，等待精准发射时刻...","B"))
        # 高精度等待
        target_sec = int(fts)
        while True:
            n=now_cal(off); r=fts-n
            if r<=0: break
            if r>0.5:
                time.sleep(0.1)
            elif r>0.05:
                time.sleep(0.01)
            elif r>0.003:
                time.sleep(0.001)
            # <3ms 忙等
            # else 忙等

    P(); P(clr("  抢券开始!","R","BOLD"))
    P(clr(f"  {datetime.fromtimestamp(now_cal(off)).strftime('%H:%M:%S.%f')[:-3]}","R","BOLD")); P()

    rn=0; lats=[]; max_dur=30 if mode=="wait" else 10
    first_round = True
    while True:
        done=True
        for gb in gbs:
            ci=ainfo.get(gb.acc.label,{})
            for c in ci.get("coupons",[]):
                rc=c["rc"]
                if rc not in gb.ok_rc and rc not in gb.gone_rc and rc not in gb.got_rc:
                    done=False; break
        if done: break
        rn+=1
        ns=datetime.fromtimestamp(now_cal(off)).strftime("%H:%M:%S.%f")[:-3]
        P(clr(f"  ──第{rn}轮({ns})──","C"))

        if first_round and fire_fns:
            # 第一轮：直接发射已部署好的worker，零延迟
            for label,(gb,fire_fn) in fire_fns.items():
                res,total = fire_fn(rn)
                self = gb
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[1]]:
                    gb.log(clr(f"  T{tid:2d} {el:.0f}ms","G","BOLD")+f" {msg}")
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[4]]:
                    gb.log(clr(f"  {msg}","R"))
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[5]]:
                    gb.log(clr(f"  {msg}","Y"))
                other=[r for r in res if not r[1] and not r[4] and not r[5]]
                if other:
                    mg=defaultdict(list)
                    for r in other: mg[r[2]].append(r[0])
                    for i,(m,tsl) in enumerate(mg.items()):
                        if i>=2: break
                        gb.log(clr(f"  [{','.join(str(t) for t in tsl[:3])}]","Y")+f" {m}")
                lats.extend([r[3] for r in res if r[3]>0])
            first_round = False
        else:
            # 后续轮次：重新创建线程发射
            for gb in gbs:
                ci=ainfo.get(gb.acc.label)
                if not ci: continue
                cfr=[]
                for c in ci["coupons"]:
                    rc=c["rc"]
                    if rc in gb.ok_rc or rc in gb.gone_rc or rc in gb.got_rc: continue
                    cc=dict(c); cc["rnd"]=ci["round"]["roundCode"]; cc["gt"]=ci["gtoken"]
                    cfr.append(cc)
                if not cfr: continue
                fn = gb.prepare_burst(cfr)
                if fn:
                    res,total = fn(rn)
                else:
                    continue
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[1]]:
                    gb.log(clr(f"  T{tid:2d} {el:.0f}ms","G","BOLD")+f" {msg}")
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[4]]:
                    gb.log(clr(f"  {msg}","R"))
                for tid,ok,msg,el,gone,got,cl,rc in [(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7]) for r in res if r[5]]:
                    gb.log(clr(f"  {msg}","Y"))
                other=[r for r in res if not r[1] and not r[4] and not r[5]]
                if other:
                    mg=defaultdict(list)
                    for r in other: mg[r[2]].append(r[0])
                    for i,(m,tsl) in enumerate(mg.items()):
                        if i>=2: break
                        gb.log(clr(f"  [{','.join(str(t) for t in tsl[:3])}]","Y")+f" {m}")
                lats.extend([r[3] for r in res if r[3]>0])
        time.sleep(INTERVAL_MS/1000.0)
        if (now_cal(off)-fts)>max_dur:
            P(clr(f"  超时{max_dur}秒停止","Y")); break

    P(); P(clr("═"*60,"C")); P(clr("  结果汇总","C","BOLD"))
    P(clr(f"  共{rn}轮","C"))
    ok_n=0
    for gb in gbs:
        sc=len([r for r in gb.results if r[1]])
        if sc>0: ok_n+=1
        s=clr("成功!","G","BOLD") if sc>0 else clr("失败","R")
        d=f" 抢到{sc}张" if sc>0 else (" 已领过" if gb.got_rc else "")
        gb.log(f"{s} {len(gb.results)}次请求{d}")
    if lats:
        P(clr(f"  延迟:最快{min(lats):.0f}ms 最慢{max(lats):.0f}ms 平均{sum(lats)/len(lats):.0f}ms","W"))
    P(clr("═"*60,"C"))
    P(clr(f"  {ok_n}/{len(gbs)} 账号成功","G" if ok_n>0 else "R","BOLD"))

def test_run():
    ct=os.getenv(COOKIE_ENV,"").strip()
    if not ct: P(clr(f"请设置{COOKIE_ENV}","R")); return
    try: accs2=parse_accounts(ct)
    except ValueError as e: P(clr(f"解析失败:{e}","R")); return
    P(clr("="*60,"C")); P(clr(" 测试模式","C","BOLD")); P(clr("="*60,"C"))
    for acc in accs2:
        p=clr(f"[{acc.label}]",acc.color,"BOLD")
        P(p,clr("查询中...","B"))
        info=find_round(acc)
        if info:
            m="立即抢" if info["mode"]=="now" else "等待"
            P(p,clr(f"模式:{m} 场次:{info['round']['startTime']} 券:{len(info['coupons'])}","G"))
            for c in info["coupons"]:
                P(p,f"  {c['name']} 满{c['lim']:.0f}减{c['amt']:.0f} 库存{c['stock']}")
        else: P(p,clr("失败","R"))

def main():
    global accs
    P(clr("╔══════════════════════════════════════════════╗","C"))
    P(clr("║   美团外卖·小耳朵饮品券 自动抢券            ║","C","BOLD"))
    P(clr(f"║   默认抢满20减20 | 自动查场次 | 高并发      ║","C"))
    P(clr("╚══════════════════════════════════════════════╝","C")); P()
    P(clr(DISCLAIMER,"D")); P()
    ct=os.getenv(COOKIE_ENV,"").strip()
    if not ct:
        P(clr(f"请设置环境变量: {COOKIE_ENV}","R","BOLD"))
        P(clr("格式: export mt_cookie='备注#完整Cookie#dj-token'","Y"))
        P(clr("测试: python3 美团小耳朵抢券.py --now","G"))
        return
    try: accs=parse_accounts(ct)
    except ValueError as e: P(clr(f"解析失败:{e}","R")); sys.exit(1)
    if len(sys.argv)>1 and sys.argv[1]=="--now":
        test_run(); return
    try: main_run()
    except KeyboardInterrupt: P(clr("\n中断","Y"))
    except Exception as e:
        P(clr(f"异常:{e}","R"))
        if DEBUG: import traceback; traceback.print_exc()

if __name__=="__main__":
    accs=[]
    main()

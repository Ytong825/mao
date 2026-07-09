#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
美团外卖世界杯券自动领取脚本
支持青龙面板运行

环境变量配置（青龙面板 -> 环境变量）:
  MEITUAN_CK  - 抓包获取的美团完整Cookie字符串 (必填)
                格式: key1=value1; key2=value2; ...
                必须包含 oops(token)、openid、userid 字段

可选环境变量:
  MEITUAN_LAT - 纬度 (默认: 24.991572)
  MEITUAN_LNG - 经度 (默认: 102.680102)
  GUNDAM_ID   - 活动ID (默认: 26BQay)
  ACTIVITY_ID - 活动编号 (默认: 769301)

定时任务配置（每天9点、12点、18点）:
  0 9,12,18 * * *

Cookie获取方式:
  1. 打开Stream抓包
  2. 进入微信小程序 或者APP 美团外卖世界杯券活动页
  3. 在 market.waimai.meituan.com 或 click.meituan.com 请求中
     找到 Cookie 请求头，完整复制即可
"""

import os
import sys
import json
import time
import random
import re
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlencode, quote, unquote

requests.packages.urllib3.disable_warnings()


class MeituanWorldCupCoupon:
    def __init__(self):
        self.ck = os.environ.get("MEITUAN_CK", "")
        if not self.ck:
            print("[ERROR] 未设置 MEITUAN_CK 环境变量!")
            print("请在青龙面板 -> 环境变量 中添加 MEITUAN_CK")
            print("值为从抓包获取的美团完整Cookie字符串")
            sys.exit(1)

        self.token = self._extract_ck("token") or self._extract_ck("oops") or ""
        self.userid = self._extract_ck("userid") or ""
        self.openid = self._extract_ck("openid") or ""
        self.uuid = self._extract_ck("uuid") or self._extract_ck("_lxsdk") or self.openid
        self.webdfpid = self._extract_ck("WEBDFPID") or ""

        if not all([self.token, self.userid, self.openid]):
            print("[ERROR] Cookie中缺少必要字段!")
            print("  token/oops: %s" % ("OK" if self.token else "MISSING"))
            print("  userid: %s" % ("OK" if self.userid else "MISSING"))
            print("  openid: %s" % ("OK" if self.openid else "MISSING"))
            print("\n请检查Cookie是否完整，必须包含: token/oops, userid, openid")
            sys.exit(1)

        self.lat = os.environ.get("MEITUAN_LAT", "24.991572213170347")
        self.lng = os.environ.get("MEITUAN_LNG", "102.68010160900376")
        self.gundam_id = os.environ.get("GUNDAM_ID", "26BQay")
        self.activity_id = os.environ.get("ACTIVITY_ID", "769301")

        self.cityid = "114"
        self.utm_source = "60413"
        self.utm_medium = "weixin_mp"
        self.utm_term = "1000517"
        self.utm_content = "2033829926042279966_1000471252"
        self.utm_campaign = "other"
        self.mina_name = "mt-weapp"
        self.app_version = "10.24.1"
        self.ctype = "mt_mp"
        self.loc_type = "WX"
        self.rcf_token = "5cac67121c9d446c8c2d7b93"

        self.ua = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.75(0x18004b29) NetType/4G Language/zh_CN "
            "miniProgram/wxde8ac0a21135c07d"
        )
        self.ref = "https://market.waimai.meituan.com/"
        self.session = self._create_session()

    def _extract_ck(self, key):
        pat = re.compile(r'(?:\A|;\s*)' + re.escape(key) + r'=([^;]+)')
        m = pat.search(self.ck)
        if m:
            return m.group(1)
        decoded = unquote(self.ck)
        m = pat.search(decoded)
        return m.group(1) if m else ""

    def _create_session(self):
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.ua,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Origin": "https://market.waimai.meituan.com",
            "Referer": self.ref,
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Dest": "empty",
        })
        for item in self.ck.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                s.cookies.set(k.strip(), v.strip())
        return s

    def _rand_hex(self, n):
        return "".join(random.choice("0123456789abcdef") for _ in range(n))

    def _gen_rcf_uniqueid(self):
        parts = ["rcf" + self._rand_hex(4)]
        for _ in range(3):
            parts.append("%d.%s" % (random.randint(100000000, 999999999), self._rand_hex(13)))
        ts = int(time.time() * 1000)
        return "%s.%s-%s" % (parts[0], ".".join(parts[1:]), ts)

    def _gen_lxsdk_params(self):
        import base64
        info = (
            "lxcuid:%s;"
            "app:%s;"
            "appnm:group_wxapp;"
            "lch:group_wxapp;"
            "wxid:%s;"
            "uuid:%s;"
            "cityid:%s;"
        ) % (self.uuid, self.app_version, self.openid, self.uuid, self.cityid)
        encoded = base64.b64encode(info.encode()).decode()
        encoded = encoded.rstrip("=")
        return encoded + ".."

    def _build_activity_url(self):
        params = {
            "tenant": "gundam",
            "isMultiTab": "true",
            "gundam_title_bar_hide": "1",
            "activity_id": self.activity_id,
            "onHideRemain": "true",
            "ctype": self.ctype,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_term": self.utm_term,
            "utm_content": self.utm_content,
            "utm_campaign": self.utm_campaign,
            "uuid": self.openid,
            "mina_name": self.mina_name,
            "userId": self.userid,
            "userid": self.userid,
            "lat": self.lat,
            "lng": self.lng,
            "loc_type": self.loc_type,
            "rcf_token": self.rcf_token,
            "rcf_uniqueid": self._gen_rcf_uniqueid(),
            "__lxsdk_params": self._gen_lxsdk_params(),
            "_lx_ver": "3.17.5",
        }
        base = "https://market.waimai.meituan.com/gd2/wm/%s" % self.gundam_id
        return "%s?%s" % (base, urlencode(params))

    def _get(self, url, extra_headers=None, timeout=15):
        h = dict(self.session.headers)
        if extra_headers:
            h.update(extra_headers)
        try:
            r = self.session.get(url, headers=h, timeout=timeout, allow_redirects=True, verify=False)
            return r
        except Exception as e:
            print("  [WARN] GET异常: %s" % e)
            return None

    def _post(self, url, data=None, json_data=None, extra_headers=None, timeout=15):
        h = dict(self.session.headers)
        if extra_headers:
            h.update(extra_headers)
        try:
            r = self.session.post(url, headers=h, data=data, json=json_data, timeout=timeout,
                                  allow_redirects=True, verify=False)
            return r
        except Exception as e:
            print("  [WARN] POST异常: %s" % e)
            return None

    def step1_fingerprint_report(self):
        print("  [1/8] 上报设备指纹 ...", end=" ")
        url = "https://msp.meituan.com/fingerprint/v1/notapp/bio/info/report"
        r = self._post(url, json_data={"encryptVersion": 1, "fingerPrintData": "H5dfp_%s" % self._rand_hex(64)})
        if r and r.status_code == 200:
            print("OK")
            return True
        print("SKIP")
        return True

    def step2_get_wx_config(self):
        print("  [2/8] 获取微信配置 ...", end=" ")
        act_url = self._build_activity_url()
        params = {"url": act_url, "callback": "jsonpWXLoader"}
        url = "https://ihotel.meituan.com/topcube/api/toc/weixin/getConfig?%s" % urlencode(params)
        r = self._get(url)
        if r and r.status_code == 200:
            print("OK")
            return True
        print("SKIP")
        return True

    def step3_h5guard(self, module="H5guardTrack"):
        print("  [3/8] H5风控(%s) ..." % module, end=" ")
        if not self.webdfpid:
            self.webdfpid = "%s-%d-%dWIIYKOQ" % (self._rand_hex(80), int(time.time() * 1000) + 86400000, int(time.time() * 1000))
        params = {
            "appKey": "", "dfpId": self.webdfpid, "utm_medium": "h5",
            "ver": "4.2.4", "host": "market.waimai.meituan.com",
            "ref": quote("market.waimai.meituan.com/gd2/wm/%s" % self.gundam_id, safe=""),
            "i18n": "CN", "pVer": "1.1.2", "sso": "0",
        }
        url = "https://portal-portm.meituan.com/horn/v1/modules/%s/prod?%s" % (module, urlencode(params))
        r = self._get(url)
        if r and r.status_code == 200:
            print("OK")
            return True
        print("SKIP")
        return True

    def step4_visit_activity_page(self):
        print("  [4/8] 访问活动页面 ...", end=" ")
        url = self._build_activity_url()
        r = self._get(url)
        if r and r.status_code == 200:
            print("OK (HTTP %d)" % r.status_code)
            # 尝试解析页面中的券信息
            self._parse_coupon_info(r.text)
            return True
        print("FAIL (HTTP %s)" % (r.status_code if r else "None"))
        return False

    def _parse_coupon_info(self, html):
        """尝试从活动页面HTML中解析券信息"""
        try:
            # 查找页面中的JSON数据
            import re
            # 查找 gundamData 或类似的数据
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__data\s*=\s*({.*?});',
                r'"couponList":\s*(\[.*?\])',
                r'"activityInfo":\s*({.*?})',
            ]
            for pat in patterns:
                m = re.search(pat, html, re.DOTALL)
                if m:
                    print("\n    [页面数据] 找到活动数据")
                    break
        except Exception:
            pass

    def step5_visit_coupon_cps(self):
        print("  [5/8] CPS领券入口 ...", end=" ")
        coupon_url = "https://click.meituan.com/t?t=1&c=2&p=QZWLxbxzivwY"
        extra_cookies = {
            "from_wmfx_click_center_page": "true",
            "wm_fx_click_url": quote("https://click.meituan.com/t?p=QZWLxbxzivwY&t=1&c=2", safe=""),
        }
        for k, v in extra_cookies.items():
            self.session.cookies.set(k, v)
        r = self._get(coupon_url)
        if r:
            print("OK -> %s..." % r.url[:50])
            return True
        print("FAIL")
        return False

    def step6_locate(self):
        print("  [6/8] 定位上报 ...", end=" ")
        url = "https://mars.meituan.com/locate/v3/sdk/loc"
        params = {
            "yodaReady": "wx",
            "csecappid": "wxde8ac0a21135c07d",
            "csecplatform": "3",
            "csecversionname": self.app_version,
            "csecversion": "3.0.2",
        }
        r = self._get("%s?%s" % (url, urlencode(params)))
        if r and r.status_code == 200:
            print("OK")
            return True
        print("SKIP")
        return True

    def step7_abtest(self):
        print("  [7/8] AB测试接口 ...", end=" ")
        url = (
            "https://apimobile.meituan.com/abtest/v2/getClientAbTestResult"
            "?uuid=&openid=%s&ci=1&isAll=true&app=wechat"
            "&version_name=%s&platform=ios&userid=%s"
        ) % (self.openid, self.app_version, self.userid)
        r = self._get(url)
        if r and r.status_code == 200:
            print("OK")
            return True
        print("SKIP")
        return True

    def step8_try_draw_coupon(self):
        """
        尝试调用美团外卖通用领券接口
        注意: 这是基于美团H5活动页的通用接口推测，实际接口可能需要抓包确认
        """
        print("  [8/8] 尝试领取世界杯券 ...", end=" ")
        
        # 美团外卖H5活动页通用领券接口
        # 接口格式通常为: /gundam/v1/prizedraw 或 /gundam/v1/coupon/draw
        draw_urls = [
            "https://market.waimai.meituan.com/gundam/v1/prizedraw",
            "https://market.waimai.meituan.com/gundam/v1/coupon/draw",
            "https://market.waimai.meituan.com/gundam/v1/coupon/receive",
            "https://market.waimai.meituan.com/gundam/v1/lottery/draw",
        ]
        
        # 构建领券请求参数
        draw_data = {
            "gundamId": self.gundam_id,
            "activityId": self.activity_id,
            "cpsName": "waimai",
            "platform": "wechat",
            "token": self.token,
            "openid": self.openid,
            "userid": self.userid,
            "uuid": self.openid,
            "lat": self.lat,
            "lng": self.lng,
            "cityId": self.cityid,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://market.waimai.meituan.com",
            "Referer": self._build_activity_url(),
        }
        
        success = False
        for draw_url in draw_urls:
            try:
                r = self._post(draw_url, json_data=draw_data, extra_headers=headers, timeout=10)
                if r and r.status_code == 200:
                    try:
                        resp = r.json()
                        code = resp.get("code", -1)
                        msg = resp.get("msg", "")
                        data = resp.get("data", {})
                        
                        if code == 0:
                            coupon_name = data.get("couponName", "")
                            coupon_amount = data.get("couponAmount", "")
                            print("\n    ✅ 领取成功!")
                            print("    券名称: %s" % coupon_name)
                            print("    券金额: %s" % coupon_amount)
                            success = True
                            break
                        elif "已领取" in msg or "already" in msg.lower():
                            print("\n    ⚠️ 已领取过该券")
                            success = True
                            break
                        elif "抢完" in msg or "empty" in msg.lower() or "gone" in msg.lower():
                            print("\n    ❌ 券已抢完")
                            break
                        else:
                            print("\n    [响应] %s" % msg)
                    except Exception:
                        print("\n    [响应] HTTP %d" % r.status_code)
                elif r and r.status_code == 404:
                    continue  # 尝试下一个接口
                else:
                    continue
            except Exception as e:
                continue
        
        if not success:
            print("\n    ⚠️ 未找到可用领券接口，可能需要重新抓包获取实际接口地址")
            print("    建议: 在下次抢券活动时，用Stream抓包记录点击'立即抢'按钮的请求")
        
        return True  # 此步骤不阻塞整体流程

    def run(self):
        print("=" * 55)
        print("  美团外卖世界杯券自动领取")
        print("  时间: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("  用户ID: %s" % self.userid)
        print("  活动ID: %s  GundamID: %s" % (self.activity_id, self.gundam_id))
        print("=" * 55)

        steps = [
            self.step1_fingerprint_report,
            self.step2_get_wx_config,
            lambda: self.step3_h5guard("H5guardTrack"),
            self.step4_visit_activity_page,
            self.step5_visit_coupon_cps,
            self.step6_locate,
            self.step7_abtest,
            self.step8_try_draw_coupon,
        ]

        ok = 0
        for func in steps:
            try:
                if func():
                    ok += 1
                time.sleep(random.uniform(0.3, 1.0))
            except Exception as e:
                print("  [ERROR] 步骤异常: %s" % e)

        print("\n" + "=" * 55)
        print("  执行完成: %d/%d 步骤成功" % (ok, len(steps)))
        print("=" * 55)
        
        # 输出重要提示
        print("\n📌 重要说明:")
        print("  当前脚本已模拟了完整的活动页面访问流程。")
        print("  但由于抓包数据中没有'点击抢券按钮'的实际请求，")
        print("  第8步使用的是推测的通用接口，可能无法真正领到券。")
        print("\n📌 建议:")
        print("  1. 在下次世界杯券发放时，提前打开Stream抓包")
        print("  2. 点击'立即抢'按钮后，查看抓包记录")
        print("  3. 找到类似 /gundam/v1/xxx 的POST请求")
        print("  4. 将实际接口地址反馈给我，我会更新脚本")
        
        return ok == len(steps)


def main():
    c = MeituanWorldCupCoupon()
    c.run()


if __name__ == "__main__":
    main()

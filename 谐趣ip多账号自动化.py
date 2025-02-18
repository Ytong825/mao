#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: 0 */2 * * *
new Env('携趣IP检查');
"""
# 变量名：xqipck 需要的值：[uid,ukey,vkey]多账户用#隔开或者换行单账号格式用[uid,ukey,vkey]
#作者：偷豆豆的大舅哥
#版本：1.2
#更新时间：2025-02-18
#说明：本脚本用于检查携趣IP是否可用，自动添加或删除白名单ip查询ip剩余数量

import base64
import codecs
import time
import sys
import os
import requests
import json

def _O0O0(s): return codecs.encode(s, 'rot_13')
def _0O0O(s): return codecs.decode(s, 'rot_13')

_A1B2 = _O0O0("脚本由偷豆豆的大舅哥创作")
_C3D4 = _O0O0("475866384")

def _X1(content, end='\n'): return print(content, end=end) and sys.stdout.flush()

def _X4(url, params=None):
    _h = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://op.xiequ.cn/'
    }
    try:
        _r = requests.get(url, params=params, headers=_h, timeout=10)
        return _r.text if _r.status_code == 200 else None
    except: return None

def _X5():
    try:
        _r = requests.get('https://whois.pconline.com.cn/ipJson.jsp?json=true')
        _r.encoding = 'utf-8'
        _d = _r.json()
        return _d.get('ip', None)
    except: return None

def _X6():
    try:
        _c = os.getenv('xqipck')
        if not _c: return []
        _a = []
        for _i in _c.replace('\n', '#').split('#'):
            _i = _i.strip()
            if not _i or not (_i.startswith('[') and _i.endswith(']')): continue
            _p = _i[1:-1].split('&')
            if len(_p) != 3: continue
            _a.append({'uid': _p[0].strip(), 'ukey': _p[1].strip(), 'vkey': _p[2].strip()})
        return [_x for _x in _a if all(_x.values())]
    except: return []

def _X7(uid, ukey):
    _u = 'http://op.xiequ.cn/ApiUser.aspx'
    _p = {'act': 'suitdt', 'uid': uid, 'ukey': ukey}
    _r = _X4(_u, _p)
    if not _r: return {'success': False}
    try:
        _d = json.loads(_r)
        if _d.get('success') == 'true' and _d.get('data'):
            _i = _d['data'][0]
            return {
                'success': True,
                'package_type': _i.get('type', ''),
                'total_ips': int(_i.get('num', 0)),
                'used_ips': int(_i.get('use', 0)),
                'remaining_ips': int(_i.get('num', 0)) - int(_i.get('use', 0)),
                'end_date': _i.get('enddate', ''),
                'is_valid': _i.get('valid') == 'true'
            }
    except: pass
    return {'success': False}

def _X8(uid, ukey):
    _u = 'http://op.xiequ.cn/IpWhiteList.aspx'
    return _X4(_u, {'uid': uid, 'ukey': ukey, 'act': 'get'}) or ''

def _X9(uid, ukey, ip):
    _u = 'http://op.xiequ.cn/IpWhiteList.aspx'
    _r = _X4(_u, {'uid': uid, 'ukey': ukey, 'act': 'add', 'ip': ip})
    if not _r: return False
    if _r == 'Err:IpRep': return True
    if _r in ['success', 'OK']:
        time.sleep(1)
        return ip in (_X8(uid, ukey) or '').split('\n')
    return False

def _X10(uid, ukey):
    _u = 'http://op.xiequ.cn/IpWhiteList.aspx'
    _r = _X4(_u, {'uid': uid, 'ukey': ukey, 'act': 'del', 'ip': 'all'})
    return _r in ['success', 'OK'] if _r else False

def _X11(whitelist, ip):
    try: return ip in whitelist.split('\n') if whitelist.strip() else False
    except: return False

def main():
    _X1('==== 携趣IP检查任务开始 ====')
    _X1(f'任务开始时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    _a = _X6()
    _X1(f'已加载 {len(_a)} 个账号')
    
    _ip = _X5()
    if not _ip:
        _X1('获取IP失败')
        return
    _X1(f'当前IP：{_ip}')

    for _i, _acc in enumerate(_a, 1):
        _X1(f'\n检查账号 {_i} (uid: {_acc["uid"]})')
        _X1('-' * 30)

        _s = _X7(_acc['uid'], _acc['ukey'])
        if not _s['success']:
            _X1('获取账号状态失败')
            continue
            
        _X1(f'套餐：{_s["package_type"]} (到期：{_s["end_date"]})')
        _X1(f'IP：总{_s["total_ips"]}，已用{_s["used_ips"]}，剩余{_s["remaining_ips"]}')
        
        if not _s['is_valid'] or _s['remaining_ips'] <= 0:
            _X1('账号无效或无可用IP')
            continue

        _w = _X8(_acc['uid'], _acc['ukey'])
        
        if _X11(_w, _ip):
            if _w.strip().count('\n') > 0:
                if not _X10(_acc['uid'], _acc['ukey']) or not _X9(_acc['uid'], _acc['ukey'], _ip):
                    continue
            else: _X1('白名单正常')
        else:
            if _w.strip() and not _X10(_acc['uid'], _acc['ukey']): continue
            if not _X9(_acc['uid'], _acc['ukey'], _ip): continue

        if not _X11(_X8(_acc['uid'], _acc['ukey']), _ip):
            _X1('白名单更新失败')
            continue

        _X1(f'✓ 账号可用 (剩余IP：{_s["remaining_ips"]})')
        return

    _X1('\n==== 携趣IP检查任务结束 ====')
    _X1(f'任务结束时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: 0 */2 * * *
new Env('携趣IP检查');
"""
# 变量名：xqipck 需要的值：[uid&ukey&vkey]多账户用#隔开或者换行
#作者：偷豆豆的大舅哥
#版本：1.3
#更新时间：2025-02-18
#说明：本脚本用于检查携趣IP是否可用，自动添加或删除白名单ip查询ip剩余数量
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

def _verify():
    try:
        author = _0O0O(_A1B2)
        qq_group = _0O0O(_C3D4)
        if author != "脚本由偷豆豆的大舅哥创作" or qq_group != "475866384": return False
        print(f"\n{author}")
        print(f"QQ群：{qq_group}")
        return True
    except: return False

def _X1(content): print(content, flush=True)

def _X4(url, params=None):
    """发起GET请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://op.xiequ.cn/'
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        return r.text if r.status_code == 200 else None
    except: return None

def _X5():
    """获取当前IP"""
    try:
        r = requests.get('https://whois.pconline.com.cn/ipJson.jsp?json=true', timeout=5)
        r.encoding = 'utf-8'
        return r.json().get('ip')
    except: return None

def _X6():
    """加载配置"""
    try:
        config = os.getenv('xqipck')
        if not config: return []
        accounts = []
        for item in config.replace('\n', '#').split('#'):
            item = item.strip()
            if not (item.startswith('[') and item.endswith(']')): continue
            parts = item[1:-1].split('&')
            if len(parts) != 3: continue
            accounts.append({'uid': parts[0].strip(), 'ukey': parts[1].strip(), 'vkey': parts[2].strip()})
        return [acc for acc in accounts if all(acc.values())]
    except: return []

def _X7(uid, ukey):
    """检查账号状态"""
    r = _X4('http://op.xiequ.cn/ApiUser.aspx', {'act': 'suitdt', 'uid': uid, 'ukey': ukey})
    if not r: return {'success': False, 'error': '请求失败'}
    
    if r.startswith('ERR#'):
        return {
            'success': True,
            'package_type': '免费套餐',
            'total_ips': 1000,
            'used_ips': 1000,
            'remaining_ips': 0,
            'end_date': time.strftime('%Y/%m/%d %H:%M:%S'),
            'is_valid': True
        }
        
    try:
        data = json.loads(r)
        if data.get('success') == 'true' and data.get('data'):
            info = data['data'][0]
            return {
                'success': True,
                'package_type': info.get('type', ''),
                'total_ips': int(info.get('num', 0)),
                'used_ips': int(info.get('use', 0)),
                'remaining_ips': int(info.get('num', 0)) - int(info.get('use', 0)),
                'end_date': info.get('enddate', ''),
                'is_valid': info.get('valid') == 'true'
            }
    except: pass
    return {'success': False, 'error': f'解析失败: {r}'}

def _X8(uid, ukey):
    """获取白名单"""
    return _X4('http://op.xiequ.cn/IpWhiteList.aspx', {'uid': uid, 'ukey': ukey, 'act': 'get'}) or ''

def _X9(uid, ukey, ip):
    """添加IP到白名单"""
    r = _X4('http://op.xiequ.cn/IpWhiteList.aspx', {'uid': uid, 'ukey': ukey, 'act': 'add', 'ip': ip})
    if not r: return False
    
    if r == 'Err:IpRep':
        _X1('IP已存在于白名单中，尝试清理后重新添加...')
        time.sleep(30)
        if _X10(uid, ukey):
            time.sleep(2)
            r2 = _X4('http://op.xiequ.cn/IpWhiteList.aspx', {'uid': uid, 'ukey': ukey, 'act': 'add', 'ip': ip})
            if r2 in ['success', 'OK']:
                _X1('IP重新添加成功')
                return True
            _X1(f'IP重新添加失败，API返回：{r2}')
        return False
        
    if r in ['success', 'OK']:
        _X1('IP添加成功')
        return True
        
    _X1(f'添加IP失败，API返回：{r}')
    return False

def _X10(uid, ukey):
    """清理白名单"""
    r = _X4('http://op.xiequ.cn/IpWhiteList.aspx', {'uid': uid, 'ukey': ukey, 'act': 'del', 'ip': 'all'})
    if not r: return False
    if r in ['success', 'OK']:
        _X1('白名单清空成功')
        return True
    if '频率过快' in r:
        _X1('触发频率限制，等待30秒...')
        time.sleep(30)
        r2 = _X4('http://op.xiequ.cn/IpWhiteList.aspx', {'uid': uid, 'ukey': ukey, 'act': 'del', 'ip': 'all'})
        if r2 in ['success', 'OK']:
            _X1('白名单清空成功')
            return True
    _X1(f'清空白名单失败，响应：{r}')
    return False

def _X11(whitelist, ip):
    """检查IP是否在白名单中"""
    try: return ip in whitelist.split('\n') if whitelist.strip() else False
    except: return False

def main():
    if not _verify(): return
    
    _X1('==== 携趣IP检查任务开始 ====')
    _X1(f'任务开始时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')
    accounts = _X6()
    _X1(f'已加载 {len(accounts)} 个账号')
    
    current_ip = _X5()
    if not current_ip:
        _X1('获取IP失败')
        return
    _X1(f'当前IP：{current_ip}\n')

    for i, account in enumerate(accounts, 1):
        _X1(f'检查账号 {i} (uid: {account["uid"]})')
        _X1('-' * 30)

        status = _X7(account['uid'], account['ukey'])
        if not status['success']:
            _X1(f'获取账号状态失败: {status.get("error", "未知错误")}\n')
            continue
            
        _X1(f'套餐：{status["package_type"]} (到期：{status["end_date"]})')
        _X1(f'IP：总{status["total_ips"]}，已用{status["used_ips"]}，剩余{status["remaining_ips"]}')
        
        if status['remaining_ips'] <= 0:
            _X1('账号IP已用完')
            _X1('清理白名单...')
            _X10(account['uid'], account['ukey'])
            _X1('')
            continue
            
        if not status['is_valid']:
            _X1('账号无效\n')
            continue

        whitelist = _X8(account['uid'], account['ukey'])
        if _X11(whitelist, current_ip):
            _X1('当前IP已在白名单中')
            _X1(f'✓ 账号可用 (剩余IP：{status["remaining_ips"]})')
            return
            
        _X1('清理白名单...')
        if not _X10(account['uid'], account['ukey']):
            _X1('清理白名单失败\n')
            continue
            
        time.sleep(2)
        _X1('添加本机IP到白名单...')
        if not _X9(account['uid'], account['ukey'], current_ip):
            _X1('添加本机IP失败\n')
            continue
            
        time.sleep(2)
        whitelist = _X8(account['uid'], account['ukey'])
        if _X11(whitelist, current_ip):
            _X1('白名单更新成功')
            _X1(f'✓ 账号可用 (剩余IP：{status["remaining_ips"]})')
            return
        else:
            _X1(f'白名单验证失败，当前白名单：{whitelist}\n')
            continue

    _X1('==== 携趣IP检查任务结束 ====')
    _X1(f'任务结束时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: 0 */2 * * *
new Env('携趣IP检查');
"""
#环境变量：xqipck ，格式[uid&ukey&vkey]多账户用#号隔开或者换行vky在提前代理api的时候里面会有
#脚本推荐定时每2个小时运行一次

import base64, codecs, time, sys, os, requests, json


def _0O0O(s): return codecs.encode(s, 'rot_13')
def _0OO0(s): return codecs.decode(s, 'rot_13')


_A1B2 = _0O0O("脚本由偷豆豆的大舅哥创作")
_C3D4 = _0O0O("475866384")
_X0X0 = _0O0O("cnm")  # 加密的错误提示

def _verify():
    try:
        
        author = _0OO0(_A1B2)
        qq_group = _0OO0(_C3D4)
        
        
        if author != "脚本由偷豆豆的大舅哥创作" or qq_group != "475866384":
            while True:
                print(_0OO0(_X0X0))
                time.sleep(1)
            return False
            
        
        print(f"\n{author}")
        print(f"QQ群：{qq_group}\n")
        return True
        
    except:
        
        while True:
            print(_0OO0(_X0X0))
            time.sleep(1)
        return False


def _X1(content, end='\n'): return print(content, end=end) and sys.stdout.flush()
def _X2(): return requests.get('https://whois.pconline.com.cn/ipJson.jsp?json=true')
def _X3(): return os.getenv('xqipck')
def _X4(uid, ukey): return requests.get(f'http://op.xiequ.cn/IpWhiteList.aspx', params={'uid':uid,'ukey':ukey,'act':'get'})

def log(content, end='\n'):
    """统一的日志输出"""
    print(content, end=end)
    sys.stdout.flush()  

def get_current_ip():
    """获取当前机器的公网IPv4地址"""
    try:
        response = requests.get('https://whois.pconline.com.cn/ipJson.jsp?json=true')
        response.encoding = 'utf-8'  
        data = response.json()
        if 'ip' in data:
            return data['ip']
        else:
            log('获取IP地址失败：API返回数据格式不正确')
            sys.exit(1)
    except Exception as e:
        log(f'获取IP地址时发生错误：{str(e)}')
        sys.exit(1)

def load_config():
    """从环境变量加载配置"""
    import os
    accounts = []
    
    try:
        
        config_str = os.getenv('xqipck')
        if not config_str:
            print('未找到环境变量 xqipck')
            sys.exit(1)
            
        
        account_configs = config_str.replace('\n', '#').split('#')
        
        for config in account_configs:
            config = config.strip()
            if not config:
                continue
                
            
            if not (config.startswith('[') and config.endswith(']')):
                print(f'账号配置格式错误: {config}')
                continue
                
            
            config = config[1:-1]  
            parts = config.split('&')
            
            if len(parts) != 3:
                print(f'账号配置项数量错误: {config}')
                continue
                
            account = {
                'uid': parts[0].strip(),
                'ukey': parts[1].strip(),
                'vkey': parts[2].strip()
            }
            
            
            if all(account.values()):
                accounts.append(account)
            else:
                print(f'账号配置项不能为空: {config}')
        
        if not accounts:
            print('未找到有效账号配置')
            sys.exit(1)
            
        return accounts
        
    except Exception as e:
        print(f'读取配置时发生错误：{str(e)}')
        sys.exit(1)

def get_whitelist(uid, ukey):
    """获取白名单列表"""
    try:
        url = f'http://op.xiequ.cn/IpWhiteList.aspx'
        params = {
            'uid': uid,
            'ukey': ukey,
            'act': 'get'
        }
        response = requests.get(url, params=params)
        return response.text
    except Exception as e:
        log(f'获取白名单时发生错误：{str(e)}')
        sys.exit(1)

def add_ip_to_whitelist(uid, ukey, ip):
    """添加IP到白名单"""
    try:
        url = f'http://op.xiequ.cn/IpWhiteList.aspx'
        params = {
            'uid': uid,
            'ukey': ukey,
            'act': 'add',
            'ip': ip
        }
        response = requests.get(url, params=params)
        response_text = response.text
        log(f'添加IP到白名单的响应：{response_text}')
        
        
        if response_text == 'Err:IpRep':
            log('IP已存在于白名单中，无需重复添加')
            return True  
        elif response_text == 'success' or response_text == 'OK':
            log('IP添加成功')
            
            time.sleep(1)  
            current_whitelist = get_whitelist(uid, ukey)
            if is_ip_in_whitelist(current_whitelist, ip):
                log('已确认IP成功添加到白名单')
                return True
            else:
                log('IP未能成功添加到白名单')
                return False
        else:
            log(f'添加IP失败，未知响应：{response_text}')
            return False
            
    except Exception as e:
        log(f'添加IP到白名单时发生错误：{str(e)}')
        return False

def delete_all_ips(uid, ukey):
    """删除所有白名单IP"""
    try:
        url = f'http://op.xiequ.cn/IpWhiteList.aspx'
        params = {
            'uid': uid,
            'ukey': ukey,
            'act': 'del',
            'ip': 'all'
        }
        response = requests.get(url, params=params)
        response_text = response.text
        log(f'删除所有IP的响应：{response_text}')
        
        
        if response_text == 'success' or response_text == 'OK':
            return True
        else:
            log(f'删除IP失败，未知响应：{response_text}')
            return False
            
    except Exception as e:
        log(f'删除IP时发生错误：{str(e)}')
        return False

def check_ip_availability(uid, vkey):
    """检查账号是否有可用的IP"""
    try:
        url = 'http://api.xiequ.cn/VAD/GetIp.aspx'
        params = {
            'act': 'get',
            'uid': uid,
            'vkey': vkey,
            'num': '1',
            'time': '30',
            'plat': '1',
            're': '0',
            'type': '0',
            'so': '1',
            'ow': '1',
            'spl': '1',
            'addr': '',
            'db': '1'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'http://api.xiequ.cn/',
            'Host': 'api.xiequ.cn'
        }
        
        response = requests.get(url, params=params, headers=headers)
        print(f'API响应内容：{response.text}')
        
        
        if ':' in response.text and any(c.isdigit() for c in response.text):
            print('账号状态：有IP可用')
            print(f'返回的代理IP信息：{response.text}')
            return True
        
       
        if "不是白名单" in response.text or "请先添加白名单" in response.text:
            print('需要先设置白名单')
            return 'need_whitelist'
        elif "没有可用的代理IP" in response.text:
            print('账号状态：无IP可用')
            print(f"错误信息：{response.text}")
            return False
        else:
            print(f'未知的API响应格式：{response.text}')
            return False
            
    except Exception as e:
        print(f'检查IP可用性时发生错误：{str(e)}')
        return False

def is_ip_in_whitelist(whitelist, ip):
    """检查IP是否在白名单列表中"""
    try:
        
        if not whitelist.strip():
            return False
        
        return ip in whitelist.split('\n')
    except Exception as e:
        print(f'检查IP是否在白名单时发生错误：{str(e)}')
        return False

def _main():
    if not _verify():
        return
    
    log('==== 携趣IP检查任务开始 ====')
    log(f'任务开始时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    
    log('正在读取配置...')
    accounts = load_config()
    log(f'成功加载 {len(accounts)} 个账号')

    
    log('正在获取当前IP地址...')
    current_ip = get_current_ip()
    log(f'当前IP地址：{current_ip}')

    
    for i, account in enumerate(accounts, 1):
        log(f'\n正在测试第 {i} 个账号 (uid: {account["uid"]})...')
        log('-' * 50)

        
        log('正在检查白名单状态...')
        whitelist = get_whitelist(account['uid'], account['ukey'])
        log('当前白名单列表：')
        log(whitelist)

        
        if is_ip_in_whitelist(whitelist, current_ip):
            if whitelist.strip().count('\n') > 0:  
                log('白名单中除了本机IP外还有其他IP，需要清理...')
                if delete_all_ips(account['uid'], account['ukey']):
                    log('白名单已清空，准备添加本机IP...')
                    if not add_ip_to_whitelist(account['uid'], account['ukey'], current_ip):
                        log('添加本机IP失败，切换到下一个账号')
                        continue
                else:
                    log('清空白名单失败，切换到下一个账号')
                    continue
            else:
                log('白名单状态正确，仅包含本机IP')
        else:
            log('本机IP不在白名单中，需要更新白名单...')
            if whitelist.strip():  
                if not delete_all_ips(account['uid'], account['ukey']):
                    log('清空白名单失败，切换到下一个账号')
                    continue
                log('白名单已清空')
            log('添加本机IP到白名单...')
            if not add_ip_to_whitelist(account['uid'], account['ukey'], current_ip):
                log('添加本机IP失败，切换到下一个账号')
                continue

        
        updated_whitelist = get_whitelist(account['uid'], account['ukey'])
        if not is_ip_in_whitelist(updated_whitelist, current_ip):
            log('白名单更新失败，切换到下一个账号')
            continue

        log('白名单配置正确，开始检查账号IP可用性...')
        
        account_usable = False
        for attempt in range(3):
            log(f'正在进行第 {attempt + 1} 次检查...')
            if attempt > 0:
                log(f'等待10秒后重试...')
                time.sleep(10)
            
            if check_ip_availability(account['uid'], account['vkey']):
                log(f'账号 {account["uid"]} 有可用IP，使用该账号')
                account_usable = True
                return  
            else:
                log(f'第 {attempt + 1} 次检查无可用IP')
                if attempt < 2:  
                    continue

        
        if not account_usable:
            log(f'账号 {account["uid"]} IP不可用，清空白名单')
            delete_all_ips(account['uid'], account['ukey'])
            if i < len(accounts):
                log(f'准备切换到下一个账号...\n')
                continue
            else:
                log('所有账号均已测试完毕')
                break

    log('\n==== 携趣IP检查任务结束 ====')
    log(f'任务结束时间：{time.strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == '__main__':
    _main() 
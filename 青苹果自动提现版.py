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

import requests
import json
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
#================================ 青苹果自动提现脚本 ===============================#
# 邀请链接如下
# https://api.zhenghui.xyz/user/#/register?inviteCode=LlefhltH
# 此脚本仅为了方便多账户提现，仅供学习交流使用，请勿用于商业用途，由此引发的一切后果与作者无关
# 如有问题请联系作者+v:xcv2160
#================================ 自定义设置 ===============================#
# 18 19 * * * 建议每天一次即可
Datafile = "UserConfig.json" # 账号配置文件，默认为当前目录下的 UserConfig.json
Goal=50 # 自动提现额度，设置为0则不自动提现
Type=1 # 提现类型，1为全提，2为仅提现Goal的额度
Account_Info = {
    1: {"账号": "xxx", "密码": "xxx"},
    2: {"账号": "xxx", "密码": "xxx"},
    3: {"账号": "xxx", "密码": "xxx"},
}# 账号信息 格式 {1：{"账号":"xxx","密码":"xxx"},2:{"账号":"xxx","密码":"xxx"}}
#================================ 自定义设置 ===============================#

Login = "https://api.zhenghui.xyz/api/web/v1/auth/passwordLogin"
Balance = "https://api.zhenghui.xyz/api/web/v1/user/wallet/balance/getInfo"
Withdraw = "https://api.zhenghui.xyz/api/web/v1/user/wallet/balance/withdraw"

header={
    "host": "api.zhenghui.xyz",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua-platform": "Windows",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    "accept": "application/json",
    "content-type": "application/json",
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "origin": "https://api.zhenghui.xyz",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://api.zhenghui.xyz/user/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i",
}

def login(acc,pas):
    data={
        "mobile": acc,
        "password": pas
    }
    try:
        resp=requests.post(Login,json=data,headers=header,verify=False,timeout=10).json()
        if resp['code']==0:
            token=resp['data']['token']
            print(f"账号 {acc} 登录成功")
            return token
        else:
            print(f"账号 {acc} 登录失败，原因：{resp['message']}")
            return None
    except Exception as e:
        print(f"账号 {acc} 登录异常，原因：{e}")
        return None

def getBalance(token):
    header_info=header.copy()
    header_info.pop('origin')
    header_info.pop('content-type')
    header_info['authorization']=f"bearer {token}"
    header_info['cookie']=f"vue_admin_template_token={token}"
    try:
        resp=requests.get(Balance,headers=header_info,verify=False,timeout=10).json()
        if resp['code']==0:
            balance=resp['data']['balance']
            print(f"获取余额成功：{balance} 元")
            balance = float(balance)
            if(Goal>0 and balance>=Goal):
                if Type==1:
                    money=balance
                elif Type==2:
                    money=Goal
                withdraw_data={
                    "amount":money,
                }
                withdraw_resp=requests.post(Withdraw,json=withdraw_data,headers=header_info,verify=False,timeout=10).json()
                if withdraw_resp['code']==0:
                    print(f"余额达到 {Goal} 元，自动提现成功，提现金额：{money} 元")
                else:
                    print(f"余额达到 {Goal} 元，自动提现失败，原因：{withdraw_resp['message']}")
            return balance
        else:
            print(f"获取余额失败，原因：{resp['message']}")
            return None
    except Exception as e:
        print(f"获取余额异常，原因：{e}")
        return None

def read_json(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        return FileNotFoundError(f"配置文件不存在：{file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
            print("成功获取到", config_dict.__len__(), "个账号配置")
        return config_dict
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误，解析失败：{e}")
    except PermissionError:
        raise PermissionError(f"没有读取配置文件的权限：{file_path}")
    except Exception as e:
        raise Exception(f"读取配置文件异常：{e}")

def write_json(file_name, data, indent=4):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    def serialize_obj(obj):
        if isinstance(obj, Exception):
            return str(obj)
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            raise TypeError(f"无法序列化的类型：{type(obj)}")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
                default=serialize_obj
            )
        print(f"✅ 成功写入：{file_path}")
    except Exception as e:
        print(f"❌ 写入失败：{type(e).__name__} - {e}")

if __name__ == "__main__":
    config = read_json(Datafile)
    if "配置文件不存在" in str(config):
        print('配置文件不存在，开始创建新配置文件')
        config={}
        if Account_Info.__len__():
            print("存在账号信息,创建配置文件")
            for i in Account_Info:
                token=login(Account_Info[i]['账号'],Account_Info[i]['密码'])
                if token:
                    config[i]={
                        "账号": Account_Info[i]['账号'],
                        "密码": Account_Info[i]['密码'],
                        "token": token
                    }
            write_json(Datafile, config)
    for i in config:
        balance=getBalance(config[i]['token'])
        config[i]['余额']=balance
    write_json(Datafile, config)


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
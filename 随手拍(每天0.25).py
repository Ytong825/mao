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

#注册地址http://www.lgdov.com?masterid=26fadfa2e0a2ec253cda9b1cc270663e&ptnum=125209
#变量名qc 格式unionid@token
import requests
import json
import os

qc = os.getenv("qc", "")
if not qc:
    print("未设置环境变量 qc，请添加 unionid@token")
    exit()

accounts = []
for line in qc.replace("&", "\n").split("\n"):
    line = line.strip()
    if line and "@" in line:
        unionid, token = line.split("@", 1)
        accounts.append((unionid, token))

if not accounts:
    print("账号格式错误，正确格式：unionid@token")
    exit()

url = "http://www.lgdov.com/user/activeone"

headers_base = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 15; 23013RK75C Build/AQ3A.250226.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36 (Immersed/39.61905) Html5Plus/1.0",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/json",
}

for idx, (unionid, token) in enumerate(accounts, 1):
    print(f"\n===== 第 {idx} 个账号 =====")
    
    payload = {"unionid": unionid}
    
    headers = headers_base.copy()
    headers['unionid'] = unionid
    headers['token'] = token

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        res = response.json()
        print(res.get("content", ""))
    except Exception as e:
        print(f"请求失败：{e}")

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
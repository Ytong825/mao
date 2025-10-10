# 当前脚本来自于http://script.345yun.cn脚本库下载！
"""
KSP_JBDH  # True或False  金币是否自动兑换为余额
KSP_JBSU # 写数字   检测到金币低于多少会自动切换did
KSP_DID # True或False  检测到金币过低是否自动切换did
KSP_YC # 20,30 每次任务延迟多少到多少秒
KSP_JBMAX # 写数字  最高金币数量
KSP_BF # True或False  是否开启并发
KSP_BFMS # 1或者2   并发模式
KSP_YXCS # 运行次数  每个账号最多看多少次广告停止
KSP_Card # 快手卡密  卡密设置为Yzyxmm 免费使用！！！！！
ksck # 备注#ck#salt#任务id#ip|port|username|password
# 任务id详解： 0饭补  1我不知道  2 200广  3 宝箱广告 4 混合模式（每次随机）
# socket5地址http://www.gzsk5.com/#/register?invitation=Yzyxmm&shareid=436（5r/月）
# 一键取ck https://www.123912.com/s/VKFJjv-z7anA
"""
import sys
import requests
import base64
import os
if not os.path.exists('kspt.so'):
    print('正在加载so文件.....')
    version_str = sys.version.split()[0]
    
    if version_str.startswith("3.10"):
        v = '310'
        print(f'当前python版本为3.10')
    elif version_str.startswith("3.11"):
        v = '311'
        print(f'当前python版本为3.11')
    else:
        print(f"当前python版本不受支持！")
        exit(0)
    url = 'http://yi100.top:3029/ks'
    data = {
        'type': v
    }
    response = requests.post(url, json=data)
    print(response.text)
    file_data = base64.b64decode(response.text.encode('utf-8'))
    
    # 写入目标文件
    with open('kspt.so', 'wb') as file:
        file.write(file_data)
    print('so文件加载成功！')
import kspt

# 当前脚本来自于http://script.345yun.cn脚本库下载！
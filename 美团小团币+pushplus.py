emoji_list = ["😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃", "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙", "🥲", "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😶‍🌫️", "😏", "😒", "🙄", "😬", "😮‍💨", "🤥", "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕", "🤢", "🤮", "🤧", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳", "🥸", "😎", "🤓", "🧐", "😕", "😟", "🙁", "😮", "😯", "😲", "🥺", "😦", "😧", "😨", "😰", "😥", "😢", "😭", "😱", "😖", "😣", "😞", "😓", "😩", "😫", "🥱", "😤", "😡", "😠", "🤬", "😈", "👿", ]  
usage_count = 0
markdown = ""
from functools import partial
import requests, time, base64, random, string, datetime, json, os


# 使用说明：
# 脚本使用usage_log.txt文件来记录运行信息，一般情况下脚本会自动创建，如果没有创建就是权限不够，请自己在同目录下创建一个usage_log.txt文件，青龙则在脚本管理下创建usage_log.txt文件，否则无法推送。 

# 变量说明：
# max_usage_per_day：一天运行几次后推送？ 默认6次，自己定好时 
# pushplus_url：加上pushplus的token 
# topic：填pushplus群组编码 
# delay：完成任务后延时多久进行下一个任务（秒） 
# cookies：按格式添加token，不够位置自己加 

max_usage_per_day = 6 
topic = "填自己的" 
pushplus_url = 'http://www.pushplus.plus/send/?token=填自己的'
delay = 3 

cookies = [

            "token=xxx",
            "token=xxx",
            "token=xxx",

]

# -------------------------------------------------------------------- ↓ 下面的不懂就不用看了 ↓

class Mttb:
    def __init__(self, ck):
        self.ck = ck
        self.name = None
        self.name = None
        self.usid = None
        self.actoken = None
        self.xtb = None
        self.wcxtb = None
        self.ids = [323, 324, 325, 326, 327, 329, 330, 331, 332, 333, 383, 386, 393, 394, 395, 397, 420, 421, 422, 423, 424, 507, 509, 510, 511, 525, 526, 527, 528, 529, 672, 768, 15169, 15170, 15171, 15172, 15173, 15177, 15224, 15282, 15287, 15293, 15302, 15324, 15326, 15400, 15457, 15458, 15602, 15603, 15604, 15605, 15606, 15607, 15608, 15609, 15610, 15618, 15768, 15810, 15812, 15813, 15837]
        self.id = None
        self.tid = None
        self.ua = "Mozilla/5.0 (Linux; Android 10; YAL-AL10 Build/HUAWEIYAL-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5223 MMWEBSDK/20230202 MMWEBID/3114 MicroMessenger/8.0.35.2360(0x2800235D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
        self.t_h = None

    def main(self):
        global markdown
        if self.login():
            self.act()
            self.cxtb()
            markdown += ('~ 运行任务中...') + "\n"
            print('~ 尝试获取任务中 ~')
            self.get_id()

    def login(self):
        global markdown
        markdown += str("-------------------------------------") + "\n"
        print("-------------------------------------")
        markdown += random.choice(emoji_list) + "第" + str(i) + "个账号, 开始!" + "\n"
        print(random.choice(emoji_list),"第"+str(i)+"个账号, 开始!")
        try:
            url = "https://open.meituan.com/user/v1/info/auditting?fields=auditAvatarUrl%2CauditUsername"
            h = {
                'Connection': 'keep-alive',
                'Origin': 'https://mtaccount.meituan.com',
                'User-Agent': self.ua,
                'token': self.ck,
                'Referer': 'https://mtaccount.meituan.com/user/',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.9',
                'X-Requested-With': 'com.sankuai.meituan',
            }
            r = requests.get(url, headers=h)

            if 'username' in r.text:
                rj = r.json()
                self.name = rj["user"]["username"]
                self.usid = rj["user"]["id"]
                xx = "~ 账号：<"+self.name+"> → 登录成功 !" + "\n"
                markdown += "~ 账号：<"+self.name+"> → 登录成功 !" + "\n"
                print(xx)
                return True
            else:
                markdown += "~ 登录失败, 账号已过期..." + "\n"
                print('~ 登录失败, 账号已过期...')
                markdown += ""+random.choice(emoji_list)+" 账号ck为: "+cookie+" ~" + "\n"
                print(random.choice(emoji_list),"账号ck为: "+cookie+" ~")
        except Exception as e:
            markdown += "登录异常："+{e}+"" + "\n"
            print(f'登录异常：{e}')
            # exit(0)

    def act(self):
        global markdown
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login'
            h = {
                'Accept': 'application/json, text/plain, */*',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': self.ua,
                'Content-Type': 'application/json;charset=UTF-8',
                'cookie': f'token={self.ck}'
            }
            sing = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            data = {
                "mtToken": self.ck,
                "deviceUUID": '0000000000000A3467823460D436CAB51202F336236F6A167191373531985811',
                "mtUserId": self.usid,
                "idempotentString": sing
            }
            r = requests.post(url, headers=h, json=data)
            if r.json()['data']['loginInfo']['accessToken'] is not None:
                self.actoken = r.json()['data']['loginInfo']['accessToken']
                # print(f'{self.name}>>>获取token成功！')
            else:
                markdown += ""+r.json()+"" + "\n"
                print(r.json())
        except Exception as e:
            markdown += "获取token异常："+(e)+"" + "\n"
            print(f'获取token异常：{e}')
            # exit(0)

    def cxtb(self):
        global markdown
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/skuExchange/resource/counts?sceneId=3&gameId=10102'
            self.t_h = {
                'Accept': 'application/json, text/plain, */*',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': self.ua,
                'Content-Type': 'application/json;charset=UTF-8',
                'mtgsig': '',
                'actoken': self.actoken,
                'mtoken': self.ck,
                'cookie': f'token={self.ck}'
            }
            r = requests.get(url, headers=self.t_h)
            rj = r.json()
            if rj['msg'] == 'ok':
                data = rj['data']
                for d in data:
                    if self.xtb is not None:
                        self.wcxtb = d['count']
                        xx = f'第二次查询小团币: {self.wcxtb}' + "\n"
                        markdown += ""+random.choice(emoji_list)+" 查询小团币: "+(self.wcxtb)+"" + "\n"
                        print(random.choice(emoji_list),xx)
                    else:
                        self.xtb = d['count']
                        xx = f'第一次查询小团币: {self.xtb}' + "\n"
                        print(random.choice(emoji_list),xx)
        except Exception as e:
            markdown += "查询团币异常："+(e)+"" + "\n"
            print(f'查询团币异常：{e}')
            # exit(0)

    def get_id(self):
        global markdown
        for i in self.ids:
            self.id = i
            if self.get_game():
                self.post_id()
        markdown += "~ 全部任务完成 ~" + "\n"
        print('~ 全部任务完成 ~')
        self.cxtb()
        # markdown += "" + random.choice(emoji_list) + " 账号：<" + self.name + "> → 本次获得小团币: " + str(int(self.wcxtb) - int(self.xtb)) + " ~" + "\n"
        print(random.choice(emoji_list) + f'账号：<{self.name}> → 本次获得小团币: {int(self.wcxtb) - int(self.xtb)} ~')

    def b64(self):
        y_bytes = base64.b64encode(self.tid.encode('utf-8'))
        y_bytes = y_bytes.decode('utf-8')
        return y_bytes

    def get_game(self):
        global markdown
        try:
            self.tid = f'mgc-gamecenter{self.id}'
            self.tid = self.b64()
            url = f'https://game.meituan.com/mgc/gamecenter/common/mtUser/mgcUser/task/finishV2?taskId={self.tid}'
            r = requests.get(url, headers=self.t_h)
            # print(r.json())
            if r.status_code == 200:
                if r.json()['msg'] == 'ok':
                    time.sleep(delay)
                    return True
                elif '完成过' in r.text:
                    pass
                else:
                    print(f'🌚任务状态: {r.text}')
            else:
                print('请求错误: ', r.status_code)
        except Exception as e:
            print(f'获取任务异常：{e}')
            # exit(0)

    def post_id(self):
        global markdown
        try:
            url = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/mgcUser/task/receiveMgcTaskReward?yodaReady=h5&csecplatform=4&csecversion=2.1.0&mtgsig={}'
            data = {
                "taskId": self.id,
                "externalStr": "",
                "riskParams": {}
            }
            r = requests.post(url, headers=self.t_h, json=data)
            # print(r.json())
            if r.status_code == 200:
                if r.json()['msg'] == 'ok':
                    print(random.choice(emoji_list),f' 任务完成 !')
                    time.sleep(delay)
                elif '异常' in r.text:
                    print(random.choice(emoji_list),f' 任务失败...')
                    time.sleep(delay)
                else:
                    print(f'账号：{self.name}>>>{r.text}')
                    time.sleep(delay)
            else:
                print('请求错误!')
        except Exception as e:
            print(f'完成任务异常：{e}')
            # exit(0)
            
def log_usage(log_filename, usage_count, max_usage_per_day):
    today = datetime.date.today()
    with open(log_filename, 'a') as log_file:
        log_file.write(f"{today}: {usage_count}/{max_usage_per_day} used\n")

def pushplus():
    pushplus_data = {
                    'title': '今日团币结果报告~',
                    'content': markdown,
                    "template": "txt",
                    "topic": topic
                }
    response = requests.post(pushplus_url, json=pushplus_data)
    if response .status_code ==200 :
        data =json.loads (response .text )
        print (data)
    else :
        print (response .status_code)

def usage_check():
    global usage_count 
    current_date = datetime.date.today()
    if os.path.isfile("usage_log.txt"):
        with open("usage_log.txt", 'r') as log_file:
            lines = log_file.readlines()
            if lines:
                last_entry = lines[-1].split(":")
                last_date = datetime.date.fromisoformat(last_entry[0].strip())
                if last_date == current_date:
                    usage_count = int(last_entry[1].split("/")[0])
    usage_count += 1

def header():
    global markdown
    markdown = str("-------------------------------------") + "\n"
    print("-------------------------------------")
    markdown += str(random.choice(emoji_list)) + str(random.choice(emoji_list)) + str(random.choice(emoji_list)) + " 哥们又来跑团币啦 ? " + str(random.choice(emoji_list)) + str(random.choice(emoji_list)) + str(random.choice(emoji_list)) + "\n"
    print(random.choice(emoji_list),random.choice(emoji_list),random.choice(emoji_list)," 哥们又来跑团币啦 ? ",random.choice(emoji_list),random.choice(emoji_list),random.choice(emoji_list))
    markdown += str("-------------------------------------") + "\n"
    print("-------------------------------------")
    markdown += f'      ~ 本次共获取到{len(cookies)}个账号 ~' + "\n"
    print(f'      ~ 本次共获取到{len(cookies)}个账号 ~')



if __name__ == '__main__':
    print = partial(print, flush=True)
    usage_check()
    log_usage("usage_log.txt", usage_count, max_usage_per_day)
    print("这是今天第"+str(usage_count)+"次运行")

    if usage_count == max_usage_per_day:
        header()
        i = 0
        for cookie in cookies:
            i = i + 1
            token_value = cookie.split('=')[1]
            run = Mttb(token_value)
            run.main()
        markdown += str("-------------------------------------") + "\n"
        pushplus()

    else:
        header()
        i = 0
        for cookie in cookies:
            i = i + 1
            token_value = cookie.split('=')[1]
            run = Mttb(token_value)
            run.main()
        markdown += str("-------------------------------------") + "\n"


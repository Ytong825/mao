# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 脚本库官方QQ群: 1077801222
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。


# 项目名称：金麟阅读V至尊版(无需抓包新增通知)
# 作者:YSJohnson | 更新：铁铁   优化：佚名
# 环境变量：JL_Token 多账号以换行符或 & 分隔 参数：code=
#无需抓包，进入程序点击阅读获取链接如http://t17.yzvnixio.icu/v8/?cnn=1&srd=1&code=XXXXXXXXXXX
#code=XXX,就是token
#微信收到通知请马上进行阅读第一篇，这是所有阅读的老规矩了，懂的都懂
# 阅读入口 （复制到浏览器打开）： http://t5.kyfcsipt.icu/auth/?cnn=1&srd=1&pud=1603
# 当前版本：v3.0
# 更新时间：2025-12-30

# 一句话：鲁迅《故乡》（1921 年，收录于《呐喊》）的结尾原文：我想：希望本是无所谓有，无所谓无的。这正如地上的路；其实地上本没有路，走的人多了，也便成了路。

import os
import requests
import time
import random
import re

# ANSI 颜色代码
class Colors:
    # 基本颜色
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

version = "3.3"  # 版本升级
ACCOUNTS_STR = os.getenv("JL_Token")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")  # 新增：PUSHPLUS推送token
try:
    MIN_DELAY = int(os.getenv("READ_DELAY_MIN", 7))
except ValueError:
    MIN_DELAY = 7
try:
    MAX_DELAY = int(os.getenv("READ_DELAY_MAX", 8))
except ValueError:
    MAX_DELAY = 8

# 拆分Header：阅读接口Header + 校验接口Header（适配抓包信息）
READ_HEADERS = {
  "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004241) NetType/WIFI Language/zh_CN",
  "Connection": "keep-alive",
  "Accept": "*/*",
  "Accept-Encoding": "gzip, deflate, br",
  "Sec-Fetch-Site": "cross-site",
  "Sec-Fetch-Mode": "no-cors",
  "Referer": "http://t19.oddqwspx.icu/",
  "Sec-Fetch-Dest": "script",
  "Accept-Language": "zh-CN,zh-Hans;q=0.9"
}

# 新增：校验接口专用Header（完全匹配抓包信息）
CHECK_HEADERS = {
  "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.68(0x18004241) NetType/WIFI Language/zh_CN",
  "Connection": "keep-alive",
  "Accept": "application/json, text/plain, */*",
  "Accept-Encoding": "gzip, deflate, br",
  "Origin": "http://t5.khtalkzr.icu",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "cross-site",
  "Referer": "http://t19.oddqwspx.icu/",
  "Sec-Fetch-Dest": "empty",
  "Accept-Language": "zh-CN,zh-Hans;q=0.9"
}


def log_print(msg, level="info", color=None):
    """
    带颜色和时间戳的日志打印
    level: info, success, warning, error, system, title, highlight
    """
    now = time.strftime("[%H:%M:%S]", time.localtime())
    
    # 根据级别选择颜色
    if color:
        # 如果指定了颜色，直接使用
        color_code = color
    elif level == "success":
        color_code = Colors.BRIGHT_GREEN
    elif level == "warning":
        color_code = Colors.BRIGHT_YELLOW
    elif level == "error":
        color_code = Colors.BRIGHT_RED
    elif level == "system":
        color_code = Colors.BRIGHT_CYAN
    elif level == "title":
        color_code = Colors.BRIGHT_MAGENTA + Colors.BOLD
    elif level == "highlight":
        color_code = Colors.BRIGHT_BLUE
    elif level == "info":
        color_code = Colors.WHITE
    else:
        color_code = Colors.RESET
    
    # 时间戳颜色
    time_color = Colors.BRIGHT_BLACK
    
    # 根据不同级别添加前缀
    if level == "success":
        prefix = "✅ "
    elif level == "warning":
        prefix = "⚠️ "
    elif level == "error":
        prefix = "❌ "
    elif level == "system":
        prefix = "🔧 "
    elif level == "title":
        prefix = "🎯 "
    else:
        prefix = ""
    
    print(f"{time_color}{now}{Colors.RESET} | {color_code}{prefix}{msg}{Colors.RESET}")


def print_banner():
    """打印彩色横幅"""
    banner = f"""
{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}
{Colors.BRIGHT_MAGENTA}{Colors.BOLD}          金鳞阅读自动脚本 v{version}{Colors.RESET}
{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}
{Colors.BRIGHT_YELLOW}作者: YSJohnson | 更新: 铁铁{Colors.RESET}
{Colors.BRIGHT_GREEN}环境变量: JL_Token (多账号分隔){Colors.RESET}
{Colors.BRIGHT_BLUE}阅读延迟: {MIN_DELAY}-{MAX_DELAY}秒{Colors.RESET}
{Colors.BRIGHT_CYAN}{'='*60}{Colors.RESET}
"""
    print(banner)


def get_timestamp_ms():
    """获取毫秒级时间戳字符串"""
    return str(int(time.time() * 1000))


def pushplus_notify(title, content):
    """
    发送PUSHPLUS推送
    参数：
        title: 推送标题
        content: 推送内容
    返回：布尔值，表示是否成功
    """
    if not PUSHPLUS_TOKEN:
        return False
    
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "txt"
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                log_print(f"PUSHPLUS推送成功", "success")
                return True
            else:
                log_print(f"PUSHPLUS推送失败: {result.get('msg', '未知错误')}", "error")
                return False
        else:
            log_print(f"PUSHPLUS推送HTTP错误: {response.status_code}", "error")
            return False
    except Exception as e:
        log_print(f"PUSHPLUS推送异常: {str(e)}", "error")
        return False


def notify_all(title, content):
    """
    多重通知方式：优先青龙通知，其次PUSHPLUS
    参数：
        title: 通知标题
        content: 通知内容
    """
    # 尝试青龙通知
    try:
        QLAPI.notify(title, content)
        log_print(f"青龙通知已发送", "success")
        return True
    except NameError:
        # 青龙环境不存在，尝试PUSHPLUS
        pass
    except Exception as e:
        log_print(f"青龙通知失败: {str(e)}", "error")
    
    # 尝试PUSHPLUS
    if PUSHPLUS_TOKEN:
        return pushplus_notify(title, content)
    else:
        log_print("无推送渠道，请检查PUSHPLUS_TOKEN环境变量", "warning")
        return False


def check_account_validity(user_code):
    """
    运行前账户有效性校验（修复Header问题）
    调用指定接口：https://api.hxehn.com/inter/task/user/read/url?userCode=xxx&spreadId=1
    使用抓包匹配的专用Header
    """
    check_url = f"https://api.hxehn.com/inter/task/user/read/url?userCode={user_code}&spreadId=1"
    short_code = user_code[-6:]
    log_print(f"校验账号 {short_code}（隐藏部分字符）有效性...", "system")
    try:
        # 发送校验请求（使用专用CHECK_HEADERS）
        resp = requests.get(check_url, headers=CHECK_HEADERS, timeout=15)
        # 打印响应状态码（调试用）
        log_print(f"账号 {short_code} 校验接口响应码：{resp.status_code}", "info")
        resp.raise_for_status()  # 4xx/5xx状态码会触发异常

        # 解析JSON响应
        try:
            check_data = resp.json()
        except json.JSONDecodeError:
            log_print(f"账号 {short_code} 校验失败：接口返回非JSON内容，响应片段：{resp.text[:50]}", "error")
            return False, "响应格式异常"

        # 解析响应状态
        success_status = check_data.get("success", False)
        code = check_data.get("code", 0)
        msg = check_data.get("msg", "未知信息")

        if not success_status:
            log_print(f"账号 {short_code} 校验不通过：{msg}", "error")
            return False, msg

        # 处理code=102的情况（无法执行任务）
        if code == 102:
            log_print(f"账号 {short_code} 不可执行任务：{msg}", "warning")
            return False, msg

        # 其他成功状态（可执行任务）
        log_print(f"账号 {short_code} 校验通过：可正常执行阅读任务", "success")
        return True, "账号有效"

    except requests.exceptions.HTTPError as e:
        # 捕获4xx/5xx错误，打印响应内容
        error_msg = f"HTTP错误 {e.response.status_code}，响应内容：{e.response.text[:100]}"
        log_print(f"账号 {short_code} 校验HTTP异常：{error_msg}", "error")
        return False, error_msg
    except requests.exceptions.RequestException as e:
        log_print(f"账号 {short_code} 校验网络异常：{str(e)}", "error")
        return False, f"网络异常：{str(e)}"
    except Exception as e:
        log_print(f"账号 {short_code} 校验未知异常：{str(e)}", "error")
        return False, f"未知错误：{str(e)}"


def parse_response(temp):
    """统一解析接口响应的工具函数（提取l、url、rw）"""
    result = {
        "l": None,
        "url": None,
        "rw": 0
    }
    # 提取l参数（兼容纯数字/10000前缀）
    match_l = re.search(r'"l":(\d+)', temp)
    if match_l:
        l_val = match_l.group(1)
        result["l"] = "10000" + l_val if len(l_val) < 8 else l_val  # 自动补前缀
    # 提取文章链接
    match_url = re.search(r'https://mp\.weixin\.qq\.com/s\?[^#]+#wechat_redirect', temp)
    if match_url:
        result["url"] = match_url.group(0)
    # 提取金币
    match_rw = re.search(r'"rw":(\d+)', temp)
    if match_rw:
        result["rw"] = int(match_rw.group(1))
    return result


def main_task(user_code, account_num):
    """单个账号的核心任务执行函数（使用阅读接口Header）"""
    account_tag = f"账号-{account_num}"
    log_print(f"=== {account_tag} 开始执行任务 ===", "title")
    log_print(f"=== CODE: {user_code} ===", "highlight")

    # 1. 初始化请求（获取检测文章，使用READ_HEADERS）
    try:
        init_url = f"https://api.hxehn.com/inter/h5/taskgac/?cnn=1&srd=1&code={user_code}&l=-1&t={get_timestamp_ms()}"
        log_print(f"{account_tag} 正在获取检测文章...", "system")
        resp = requests.get(init_url, headers=READ_HEADERS, timeout=12)
        resp.raise_for_status()
        resp_data = parse_response(resp.text)
    except Exception as e:
        log_print(f"{account_tag} 初始化请求失败：{str(e)}", "error")
        return

    # 校验初始化结果
    if not resp_data["l"]:
        log_print(f"{account_tag} 未获取到l参数，UserCode无效", "error")
        return
    if not resp_data["url"]:
        log_print(f"{account_tag} 未获取到文章链接，任务终止", "error")
        return

    # 2. 推送通知并等待用户阅读
    article_url = resp_data['url']
    log_print(f"{account_tag} 检测文章链接：{article_url}", "highlight")
    
    # 创建推送内容
    push_title = f"金鳞阅读-{account_tag}"
    push_content = f"请30秒内阅读检测文章：\n\n{article_url}\n\n账号：{user_code}\n时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # 发送通知（优先青龙，其次PUSHPLUS）
    notify_all(push_title, push_content)
    
    log_print(f"{account_tag} 等待30秒（请手动阅读文章）...", "warning")
    time.sleep(30)

    # 3. 循环执行阅读任务
    total_gold = 0
    current_l = resp_data["l"]
    success_count = 0
    for i in range(1, 31):
        try:
            loop_url = f"https://api.hxehn.com/inter/h5/taskgac/?cnn=1&srd=1&code={user_code}&l={current_l}&t={get_timestamp_ms()}"
            resp = requests.get(loop_url, headers=READ_HEADERS, timeout=12)
            resp.raise_for_status()
            loop_data = parse_response(resp.text)
        except Exception as e:
            log_print(f"{account_tag} 第{i}次请求失败：{str(e)}", "error")
            break

        # 校验本次阅读结果
        if not loop_data["l"] or not loop_data["url"]:
            log_print(f"{account_tag} 第{i}次阅读失败，响应异常", "error")
            break
        if loop_data["rw"] <= 0:
            log_print(f"{account_tag} 第{i}次阅读无金币，任务终止", "warning")
            break

        # 更新数据
        total_gold += loop_data["rw"]
        current_l = loop_data["l"]
        success_count = i
        
        # 金币显示颜色根据数量变化
        if loop_data["rw"] >= 500:
            gold_color = Colors.BRIGHT_GREEN
        elif loop_data["rw"] >= 200:
            gold_color = Colors.BRIGHT_YELLOW
        else:
            gold_color = Colors.BRIGHT_BLUE
            
        log_print(f"{account_tag} 第{i}次阅读成功 | 本次{gold_color}+{loop_data['rw']}{Colors.RESET} | 累计{Colors.BRIGHT_GREEN}{total_gold}{Colors.RESET}金币", "success")

        # 随机延迟
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        log_print(f"{account_tag} 等待{Colors.BRIGHT_YELLOW}{delay}{Colors.RESET}秒后继续...", "info")
        time.sleep(delay)

    # 任务总结
    summary = f"{account_tag} 任务结束 | 成功阅读{success_count}次 | 累计{total_gold}金币"
    
    # 根据成功次数选择颜色
    if success_count >= 20:
        summary_color = Colors.BRIGHT_GREEN + Colors.BOLD
    elif success_count >= 10:
        summary_color = Colors.BRIGHT_YELLOW
    else:
        summary_color = Colors.BRIGHT_RED
        
    log_print(f"=== {summary_color}{summary}{Colors.RESET} ===", "title")
    
    # 可选：任务完成时发送总结通知
    if success_count > 0:
        summary_title = f"金鳞阅读任务完成-{account_tag}"
        summary_content = f"任务完成情况：\n\n成功阅读次数：{success_count}次\n累计获得金币：{total_gold}\n完成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        notify_all(summary_title, summary_content)


def get_remote_notice():
    """本地通知（不使用远程获取）"""
    local_text = """代码发布地址: https://gitee.com/ysjohnson6/qinglong
阅读入口：http://t5.kyfcsipt.icu/auth/?cnn=1&srd=1&pud=1603
源码采用MIT许可证 欢迎二改修复 保留作者与许可声明即可"""
    
    print(f"\n{Colors.BRIGHT_CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BRIGHT_GREEN}📢 通知：{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}{local_text}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'='*50}{Colors.RESET}\n")

def main():
    """主函数（新增账户前置校验，优化流程）"""
    # 打印彩色横幅
    print_banner()
    
    get_remote_notice()
    log_print(f"金鳞阅读 v{version} 启动", "title")

    # 检查PUSHPLUS_TOKEN是否配置
    if PUSHPLUS_TOKEN:
        log_print("PUSHPLUS推送已启用", "success")
    else:
        log_print("如需推送检测文章，请配置PUSHPLUS_TOKEN环境变量", "warning")

    # 校验环境变量
    if not ACCOUNTS_STR:
        log_print("错误：环境变量JL_Token未设置", "error")
        return

    # 解析多账号（支持换行、&、逗号分隔）
    user_codes = [
        code.strip()
        for code in re.split(r'[\n&,]', ACCOUNTS_STR)
        if code.strip()
    ]
    if not user_codes:
        log_print("错误：JL_Token中无有效账号", "error")
        return
    log_print(f"共读取到{Colors.BRIGHT_CYAN}{len(user_codes)}{Colors.RESET}个账号，开始批量校验...", "system")
    log_print(f"阅读延迟范围：{Colors.BRIGHT_YELLOW}{MIN_DELAY}-{MAX_DELAY}{Colors.RESET}秒", "info")

    # 前置批量校验账号，筛选有效账号
    valid_accounts = []
    for idx, code in enumerate(user_codes, 1):
        is_valid, msg = check_account_validity(code)
        if is_valid:
            valid_accounts.append((idx, code))
        else:
            log_print(f"账号-{idx} 无效，跳过执行：{msg}", "error")
        # 校验间隔，避免接口限流
        time.sleep(2)  # 延长间隔到2秒，降低限流风险

    if not valid_accounts:
        log_print("所有账号均无效，任务终止", "error")
        return
        
    # 有效账号统计
    success_count = len(valid_accounts)
    fail_count = len(user_codes) - success_count
    
    log_print(f"账号校验完成，共{Colors.BRIGHT_GREEN}{success_count}{Colors.RESET}个有效账号将执行任务", "success")
    if fail_count > 0:
        log_print(f"有{Colors.BRIGHT_RED}{fail_count}{Colors.RESET}个账号无效", "warning")
    print()

    # 执行有效账号的阅读任务
    for account_idx, (original_idx, code) in enumerate(valid_accounts, 1):
        # 显示账号进度条
        progress_bar = f"[{account_idx}/{len(valid_accounts)}]"
        log_print(f"开始执行有效账号 {progress_bar}（原账号-{original_idx}）", "title")
        main_task(code, original_idx)
        # 多账号间隔
        if account_idx < len(valid_accounts):
            interval = random.randint(3, 6)
            log_print(f"\n{Colors.BRIGHT_CYAN}{'-'*40}{Colors.RESET}", "info")
            log_print(f"等待{interval}秒后执行下一个有效账号", "warning")
            log_print(f"{Colors.BRIGHT_CYAN}{'-'*40}{Colors.RESET}\n", "info")
            time.sleep(interval)

    # 最终统计
    print(f"\n{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")
    log_print(f"所有有效账号任务执行完毕！", "success")
    log_print(f"总账号数: {len(user_codes)}", "info")
    log_print(f"有效账号: {Colors.BRIGHT_GREEN}{success_count}{Colors.RESET}", "success")
    if fail_count > 0:
        log_print(f"无效账号: {Colors.BRIGHT_RED}{fail_count}{Colors.RESET}", "warning")
    print(f"{Colors.BRIGHT_GREEN}{'='*60}{Colors.RESET}")


if __name__ == "__main__":
    # 导入json模块（用于账户校验时解析响应）
    import json
    main()



# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 脚本库官方QQ群: 1077801222
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。
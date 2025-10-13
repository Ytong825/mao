import urllib3
import sys
import os
import requests
import platform
import re

# 禁用SSL证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 版本文件名称
VERSION_FILE = "so_version.txt"
# 服务器版本号获取地址
VERSION_CHECK_URL = "http://43.143.175.165:8888/down/sZeEcKNcJRhe.txt"  # 服务器应返回简单版本号如"1.2"
# 首次运行的初始版本
INITIAL_VERSION = "1.1"
# 本地备用Python文件名称
LOCAL_BACKUP_FILE = "kuaishou_so.py"


def check_python_version():
    """检查Python版本是否符合 3.10.x ~ 3.11.x 要求"""
    version = sys.version_info
    if not (version >= (3, 10) and version < (3, 12)):
        current_version = f"{version.major}.{version.minor}.{version.micro}"
        print(f"\n【❌ Python版本检查失败】")
        print(f"当前版本：{current_version}")
        print(f"必须版本：3.10.x ~ 3.11.x")
        sys.exit(1)
    print(f"【✅ Python版本检查通过】当前版本：{version.major}.{version.minor}.{version.micro}")


def check_system_architecture():
    """检查系统架构是否为支持的 x86_64 或 arm64"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    supported_arch = ["x86_64", "amd64", "arm64", "aarch64"]
    arch_map = {"amd64": "x86_64", "aarch64": "arm64"}
    arch = arch_map.get(machine, machine)

    if machine not in supported_arch:
        print(f"\n【❌ 系统架构检查失败】")
        print(f"当前环境：{system.capitalize()} 系统 | 架构：{machine}（映射后：{arch}）")
        print(f"支持架构：x86_64（含amd64）、arm64（含aarch64）")
        sys.exit(1)

    print(f"\n【✅ 系统架构检查通过】")
    print(f"操作系统：{platform.system()} {platform.release()}")
    print(f"CPU架构：{machine}（标准映射：{arch}）")
    return arch


def get_local_version():
    """获取本地so文件版本"""
    if not os.path.exists(VERSION_FILE):
        # 首次运行，设置初始版本
        with open(VERSION_FILE, "w") as f:
            f.write(INITIAL_VERSION)
        return INITIAL_VERSION
    
    try:
        with open(VERSION_FILE, "r") as f:
            version = f.read().strip()
            # 简单验证版本格式
            if re.match(r"^\d+\.\d+$", version):
                return version
            # 格式不正确，使用初始版本
            return INITIAL_VERSION
    except Exception:
        return INITIAL_VERSION


def get_server_version():
    """从服务器获取最新版本号"""
    try:
        response = requests.get(
            VERSION_CHECK_URL,
            timeout=10,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()
        
        version = response.text.strip()
        # 验证版本格式
        if re.match(r"^\d+\.\d+$", version):
            return version
        else:
            print(f"【⚠️ 服务器版本格式不正确：{version}】")
            return None
    except Exception as e:
        print(f"【⚠️ 获取服务器版本失败：{str(e)}】")
        return None


def version_needs_update(local_ver, server_ver):
    """比较版本号，判断是否需要更新"""
    if not server_ver:
        return False
        
    try:
        local_parts = list(map(int, local_ver.split('.')))
        server_parts = list(map(int, server_ver.split('.')))
        
        # 比较主版本号
        if server_parts[0] > local_parts[0]:
            return True
        # 主版本号相同，比较次版本号
        if server_parts[0] == local_parts[0] and server_parts[1] > local_parts[1]:
            return True
            
        return False
    except Exception:
        return False


def update_local_version(new_version):
    """更新本地版本记录"""
    try:
        with open(VERSION_FILE, "w") as f:
            f.write(new_version)
        return True
    except Exception as e:
        print(f"【⚠️ 更新本地版本记录失败：{str(e)}】")
        return False


def download_so_file(url, target_path):
    """从指定URL下载so文件，支持进度显示与失败清理"""
    try:
        print(f"\n【📥 开始下载so文件】")
        print(f"源地址：{url}")
        print(f"保存路径：{os.path.abspath(target_path)}")

        response = requests.get(
            url,
            stream=True,
            timeout=60,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )
        response.raise_for_status()

        total_size = int(response.headers.get("Content-Length", 0))
        downloaded_size = 0
        chunk_size = 8192

        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"下载进度：{progress:.1f}% | {downloaded_size}/{total_size} 字节", end="\r")

        if total_size > 0:
            print(f"下载进度：100.0% | {downloaded_size}/{total_size} 字节")
        print(f"【✅ so文件下载完成】已保存为：{target_path}")
        return True

    except Exception as e:
        # 捕获所有异常，准备使用本地备份
        error_msg = str(e)
        if isinstance(e, requests.exceptions.HTTPError):
            error_msg = f"HTTP错误：{e.response.status_code} {e.response.reason}"
            if e.response.status_code == 403:
                error_msg += "（可能是链接权限不足）"
            elif e.response.status_code == 404:
                error_msg += "（文件不存在，链接可能已失效）"
        elif isinstance(e, requests.exceptions.ConnectionError):
            error_msg = "网络连接失败"
        elif isinstance(e, requests.exceptions.Timeout):
            error_msg = "下载超时"

        print(f"\n【❌ so文件下载失败】")
        print(f"错误详情：{error_msg}")
        
        # 清理可能的不完整文件
        if os.path.exists(target_path):
            os.remove(target_path)
            
        # 检查本地备份是否存在
        if os.path.exists(LOCAL_BACKUP_FILE):
            print(f"【ℹ️ 发现本地备用文件 {LOCAL_BACKUP_FILE}，将使用该文件执行任务】")
            return False
        else:
            print(f"【❌ 未找到本地备用文件 {LOCAL_BACKUP_FILE}，无法继续执行】")
            print(f"请加群获取帮助：https://t.me/+pGksv96SJjVjZTQ1")
            sys.exit(1)


def main():
    # 终端颜色配置
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    # 1. 打印加群提示
    print(f"{GREEN}="*50)
    print(f"        加群获取白嫖卡密 | 问题反馈")
    print(f"{BLUE}        交流群链接：https://t.me/+pGksv96SJjVjZTQ1")
    print(f"{GREEN}="*50 + RESET)

    # 2. 执行环境检查
    print(f"\n{YELLOW}【🔍 开始环境兼容性检查】{RESET}")
    check_python_version()
    check_system_architecture()
    print(f"\n{YELLOW}【✅ 所有环境检查通过】{RESET}")

    # 3. 版本检查与更新逻辑
    target_so_name = "kuaishou_task.so"
    remote_so_url = "http://43.143.175.165:8888/down/REJLjrxQI1zg.so"
    
    local_version = get_local_version()
    
    server_version = get_server_version()
    download_success = True  # 标记下载是否成功
    
    # 处理版本比较结果
    if not server_version:
        print("【⚠️ 无法获取服务器版本，将使用本地版本（如存在）】")
        if not os.path.exists(target_so_name):
            print("【ℹ️ 未发现本地so文件，将进行下载】")
            download_success = download_so_file(remote_so_url, target_so_name)
            if download_success:  # 只有下载成功才更新版本
                update_local_version(local_version)
    else:
        if version_needs_update(local_version, server_version):
            print(f"【🔄 发现新版本 {server_version}，正在更新...】")
            # 下载并替换文件
            if os.path.exists(target_so_name):
                os.remove(target_so_name)
            download_success = download_so_file(remote_so_url, target_so_name)
            # 只有下载成功才更新版本
            if download_success:
                update_local_version(server_version)
        else:
            print(f"【✅ 本地版本 {local_version} 已是最新，无需更新】")
            # 如果本地文件不存在，即使版本相同也下载
            if not os.path.exists(target_so_name):
                print("【ℹ️ 未发现本地so文件，将下载当前版本】")
                download_success = download_so_file(remote_so_url, target_so_name)

    # 4. 导入并执行快手任务（优先使用so文件，失败则使用本地Python文件）
    try:
        print(f"\n{YELLOW}【🚀 开始执行快手任务】{RESET}")
        
        # 根据下载情况选择导入方式
        if download_success and os.path.exists(target_so_name):
            print(f"【ℹ️ 使用so文件执行任务】")
            import kuaishou_task
            result = kuaishou_task.run_main()
        else:
            print(f"【ℹ️ 使用本地备用文件 {LOCAL_BACKUP_FILE} 执行任务】")
            import kuaishou_so
            result = kuaishou_so.run_main()

        print(f"\n{GREEN}【🎉 任务执行完成】{RESET}")
        print(f"任务执行结果：{result}")

    except ImportError as e:
        print(f"\n{RED}【❌ 模块导入失败】{RESET}")
        print(f"错误详情：{str(e)}")
        print("可能原因及解决方案：")
        print(f"  1. {target_so_name}与系统架构不兼容")
        print(f"  2. {LOCAL_BACKUP_FILE}文件不存在或有语法错误")
        print(f"  3. 尝试重新运行脚本或获取最新版本")
        sys.exit(1)

    except Exception as e:
        print(f"\n{RED}【❌ 执行快手任务失败】{RESET}")
        print(f"错误详情：{str(e)}")
        print("建议：加群反馈错误信息，获取技术支持")
        sys.exit(1)


if __name__ == "__main__":
    main()

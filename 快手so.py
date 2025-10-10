# 当前脚本来自于http://script.345yun.cn脚本库下载！
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
# 服务器版本号获取地址(这里使用示例地址，实际应替换为真实地址)
VERSION_CHECK_URL = "http://43.143.175.165:8888/down/j8cKIDC0gB6E.txt"  # 服务器应返回简单版本号如"1.2"
# 首次运行的初始版本
INITIAL_VERSION = "1.1"


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
        # print("\n【🔍 检查服务器版本...】")
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
            # print(f"服务器最新版本：{version}")
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

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP错误：{e.response.status_code} {e.response.reason}"
        if e.response.status_code == 403:
            error_msg += "（可能是链接权限不足，建议加群获取最新链接）"
        elif e.response.status_code == 404:
            error_msg += "（文件不存在，链接可能已失效）"
    except requests.exceptions.ConnectionError:
        error_msg = "网络连接失败"
    except requests.exceptions.Timeout:
        error_msg = "下载超时"
    except Exception as e:
        error_msg = f"未知错误：{str(e)}"

    print(f"\n【❌ so文件下载失败】")
    print(f"错误详情：{error_msg}")
    print(f"请加群获取帮助：https://t.me/+pGksv96SJjVjZTQ1")
    if os.path.exists(target_path):
        os.remove(target_path)
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
    # remote_so_url = "http://43.143.175.165:8888/down/AYcHZSpwaLax.so"
    remote_so_url = "http://43.143.175.165:8888/down/nouh4Neo1IjV.so"
    
    local_version = get_local_version()
    # print(f"\n【📌 本地so版本：{local_version}】")
    
    server_version = get_server_version()
    
    # 处理版本比较结果
    if not server_version:
        print("【⚠️ 无法获取服务器版本，将使用本地版本（如存在）】")
        if not os.path.exists(target_so_name):
            print("【ℹ️ 未发现本地so文件，将进行下载】")
            download_so_file(remote_so_url, target_so_name)
            update_local_version(local_version)  # 使用当前本地版本
    else:
        if version_needs_update(local_version, server_version):
            print(f"【🔄 发现新版本 {server_version}，正在更新...】")
            # 下载并替换文件
            if os.path.exists(target_so_name):
                os.remove(target_so_name)
            download_so_file(remote_so_url, target_so_name)
            # 更新版本记录
            update_local_version(server_version)
        else:
            print(f"【✅ 本地版本 {local_version} 已是最新，无需更新】")
            # 如果本地文件不存在，即使版本相同也下载
            if not os.path.exists(target_so_name):
                print("【ℹ️ 未发现本地so文件，将下载当前版本】")
                download_so_file(remote_so_url, target_so_name)

    # 4. 导入并执行快手任务
    try:
        print(f"\n{YELLOW}【🚀 开始执行快手任务】{RESET}")
        import kuaishou_task
        result = kuaishou_task.run_main()
        print(f"\n{GREEN}【🎉 任务执行完成】{RESET}")
        print(f"任务执行结果：{result}")

    except ImportError as e:
        print(f"\n{RED}【❌ 导入kuaishou_task失败】{RESET}")
        print(f"错误详情：{str(e)}")
        print("可能原因及解决方案：")
        print("  1. so文件与系统架构不兼容")
        print("  2. so文件损坏（重新运行脚本尝试下载）")
        sys.exit(1)

    except Exception as e:
        print(f"\n{RED}【❌ 执行快手任务失败】{RESET}")
        print(f"错误详情：{str(e)}")
        print("建议：加群反馈错误信息，获取技术支持")
        sys.exit(1)


if __name__ == "__main__":
    main()

# 当前脚本来自于http://script.345yun.cn脚本库下载！
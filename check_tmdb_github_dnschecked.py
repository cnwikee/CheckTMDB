# 标准库导入
import os
import re
import sys
import platform
import time
import random
import socket
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from time import sleep
from typing import List, Optional
import ipaddress

# 第三方库导入
from ping3 import ping
import requests
from retry import retry

HOSTS_FILE_PATH = '' #全局HOSTS文件路径

DOMAINS = [
    'tmdb.org',
    'api.tmdb.org',
    'files.tmdb.org',
    'themoviedb.org',
    'api.themoviedb.org',
    'www.themoviedb.org',
    'auth.themoviedb.org',
    'image.tmdb.org',
    'images.tmdb.org',
    'imdb.com',
    'www.imdb.com',
    'secure.imdb.com',
    's.media-imdb.com',
    'us.dd.imdb.com',
    'www.imdb.to',
    'imdb-webservice.amazon.com',
    'origin-www.imdb.com',
    'ia.media-imdb.com',
    'thetvdb.com',
    'api.thetvdb.com',
    'm.media-amazon.com',
    'ia.media-imdb.com',
    'imdb-video.media-imdb.com'
]

Tmdb_Host_TEMPLATE = """# Tmdb Hosts Start
{content}
# Update time: {update_time}
# Update url: https://github.com/cnwikee/CheckTMDB/blob/main/Tmdb_host
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End\n"""

Github_Host_TEMPLATE = """# Github Hosts Start
{content}
# Update time: {update_time}
# Github Hosts End\n"""

Cloudflare_Host_TEMPLATE = """# Cloudflare Hosts Start
{content}
# Update time: {update_time}
# Cloudflare Hosts End\n"""

UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"

# -------------------- 公共功能模块 -------------------- #
class Utils:
    @staticmethod
    def get_hosts_file_path() -> str:
        """根据当前操作系统，返回hosts路径"""
        os_type = platform.system().lower()

        if os_type == "windows":
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]操作系统: Windows")
            return r"C:\Windows\System32\drivers\etc\hosts"
        elif os_type == "linux":
            if os.path.exists('/etc/openwrt_release'):
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]操作系统: OpenWrt")
                return "/etc/myhosts"
            else:
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]操作系统: Linux")
                return "/etc/hosts"
        elif os_type == "darwin":
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]操作系统: macOS")
            return "/etc/hosts"
        else:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:脚本不支持的操作系统~")
            sys.exit(1)

    @staticmethod
    def execute_dns_command():
        """根据操作系统类型执行刷新DNS缓存的命令"""
        os_type = platform.system().lower()
        if os_type == "windows":
            command = "ipconfig /flushdns"
            result = os.system(command)
            if result == 0:
                print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Windows 系统中 DNS 刷新成功。")
            else:
                print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:执行 Windows 刷新 DNS 命令时出错。")
        elif os_type == "linux":
            if os.path.exists('/etc/openwrt_release'):
                # OpenWrt 系统
                command = "/etc/init.d/dnsmasq restart"
                result = os.system(command)
                if result == 0:
                    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:执行重启 Dnsmasq 服务成功。")
                else:
                    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:Dnsmasq 服务重启时出错。")
            else:
                # 其他 Linux 系统
                command = "systemctl restart systemd-resolved"
                result = os.system(command)
                if result == 0:
                    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:执行重启 systemd-resolved 服务成功。")
                else:
                    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:执行重启 systemd-resolved 服务命令时出错。")
        elif os_type == "darwin":
            command = "dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
            result = os.system(command)
            if result == 0:
                print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:执行 macOS DNS 刷新成功。")
            else:
                print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:执行 macOS 刷新 DNS 命令时出错。")   
        else:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:刷新DNS失败，{os_type} 为脚本不支持的操作系统~")
    
    @staticmethod
    def check_environment(file_path: str) -> bool:
        """检查运行环境是否满足要求"""
        # 检查Python版本
        if sys.version_info < (3, 6):
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:需要 Python 3.6 或更高版本")
            return False

        # 检查必要的目录权限
        if not os.access(file_path, os.W_OK):
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:需要 {file_path} 目录的写入权限,脚本无法正常执行!")
            return False
            
        return True

    @staticmethod
    def is_ci_environment() -> bool:
        """检查是否为Github Aciton环境"""
        ci_environment_vars = {
            'GITHUB_ACTIONS': 'true',
            'TRAVIS': 'true',
            'CIRCLECI': 'true'
        }
        for env_var, expected_value in ci_environment_vars.items():
            env_value = os.getenv(env_var)
            if env_value is not None and str(env_value).lower() == expected_value.lower():
                return True
        return False
    
    @staticmethod
    def is_valid_ipv4(ip) -> bool:
        """检查是否为合法的IPv4地址"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        return all(0 <= int(num) <= 255 for num in ip.split('.'))

    @staticmethod
    def bak_myhosts(file_path: str):
        """备份指定的文件"""
        if not os.path.exists(file_path):
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:指定的文件 {file_path} 不存在，无法进行备份操作。")
            return

        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            backup_text = f"# Bak Time {current_time}"

            with open(file_path, 'r', encoding='utf-8') as original_file:
                content = original_file.read()

            backup_file_path = file_path + ".bak"
            with open(backup_file_path, 'w', encoding='utf-8') as backup_file:
                backup_file.write(content + "\n" + backup_text)
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]已成功备份文件 {file_path} 为 {backup_file_path}")
        except Exception as e:
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:备份hosts源文件 {file_path} 时出现错误: {str(e)}")

def ping_ip(ip, port=80):
    # 添加超时处理
    socket.setdefaulttimeout(2)
    try:
        start_time = time.time()
        with socket.create_connection((ip, port)) as sock:
            latency = (time.time() - start_time) * 1000
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:IP {ip} 的平均延迟: {latency:.2f}ms")  # 格式化保留2位小数
            return latency
    except (socket.timeout, socket.error) as e:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Ping {ip} 时发生错误: {str(e)}")
        return float('inf')
    except Exception as e:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Ping {ip} 时发生错误: {str(e)}")
        return float('inf')
    
def ping3_ip(ip):
    try:
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:使用ping3库 ping {ip}...")
        latency = ping(ip, timeout=2)  # 使用ping3库进行ping操作
        
        if latency is None:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]IP: {ip} ping 超时")
            return float('inf')
        
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]IP: {ip} 的平均延迟: {latency * 1000}ms")  # 转换为毫秒
        return latency * 1000  # 返回延迟，转换为毫秒
    except Exception as e:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Ping {ip} 时发生错误: {str(e)}")
        return float('inf')

def find_fastest_ip(ips: List[str]) -> Optional[str]:
    """找出延迟最低的IP地址"""
    if not ips:
        return None
    
    fastest_ip = None
    min_latency = float('inf')
    ip_latencies = []  # 存储所有IP及其延迟
    
    for ip in ips:
        ip = ip.strip()
        if not ip:
            continue
            
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始检测 IP: {ip}")
        latency = ping_ip(ip)
        ip_latencies.append((ip, latency))
        
        if latency < min_latency:
            min_latency = latency
            fastest_ip = ip
            
        sleep(0.5) 
    
    return fastest_ip

def update_file(FILE_PATH: str, Start_Str: str, End_Str: str, new_content: str) -> bool:
    """
    在文件中查找并替换指定的文本块
    
    Args:
        FILE_PATH: 文件路径
        Start_Str: 起始特征字符串
        End_Str: 结束特征字符串
        new_content: 要替换的新内容
    
    Returns:
        bool: 更新成功返回True，失败返回False
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(FILE_PATH):
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 更新文件内容时发生错误：文件 {FILE_PATH} 不存在！")
            return False
            
        # 读取文件内容
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # 查找特征字符串的位置
        start_pos = content.find(Start_Str)
        if start_pos == -1:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 在文件 {FILE_PATH} 中，未找到起始特征字符串: {Start_Str}")
            return False
            
        end_pos = content.find(End_Str, start_pos)
        if end_pos == -1:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 在文件 {FILE_PATH} 中，未找到结束特征字符串: {End_Str}")
            return False
            
        # 计算结束位置（包含End_Str的长度）
        end_pos += len(End_Str)
        
        # 构建新的文件内容
        new_file_content = content[:start_pos] + new_content + content[end_pos:]
        
        # 写入文件
        with open(FILE_PATH, 'w', encoding='utf-8') as file:
            file.write(new_file_content)
        
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:更新 {FILE_PATH} 指定块成功！")
        return True
        
    except Exception as e:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 更新文件 {FILE_PATH} 时发生错误: {str(e)}")
        return False

def write_Tmdb_host_file(hosts_content: str) -> None:
    output_file_path = os.path.join('/tmp', 'Tmdb_host')
    with open(output_file_path, "w", encoding='utf-8') as output_fb:
        output_fb.write(hosts_content)
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]~最新TMDB IP已更新~")

def write_myhosts(hosts_content: str) -> None:
    global HOSTS_FILE_PATH
    if not hosts_content:
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Error:没有内容需要写入,hosts_content 为空~")
        return
        
    try:
        # 备份旧文件
        Utils.bak_myhosts(HOSTS_FILE_PATH)

        with open(HOSTS_FILE_PATH, "w", encoding='utf-8') as output_fb:
            output_fb.write(hosts_content)
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:已成功获取Hosts信息并写出新 {HOSTS_FILE_PATH} 文件！")
        # 刷新DNS缓存
        Utils.execute_dns_command()
    except PermissionError:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:无权写入文件 {HOSTS_FILE_PATH}，请使用sudo运行")
    except Exception as e:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:写入 {HOSTS_FILE_PATH} 文件时发生错误: {str(e)}")

# 生成最快tmdb ip
def get_tmdb_ips(parameter: Optional[str] = None) -> Optional[str]:
    print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始检测TMDB相关域名的最快IP...")

    
    # 初始化 查询类型 为默认值 "-4"
    parameter = int(-4) if parameter is None or parameter not in ["-4", "-6", "-10"] else int(parameter)

    results = []
    for domain in DOMAINS:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:正在处理域名: {domain}")
        
        # 初始化变量
        ipv4_ips, ipv6_ips = [], []

        # 根据参数获取不同类型的IP地址
        if parameter == -4:
            ipv4_ips = get_domain_ips(domain, "A")
        elif parameter == -6:
            ipv6_ips = get_domain_ips(domain, "AAAA")
        elif parameter == -10:
            ipv4_ips = get_domain_ips(domain, "A")
            ipv6_ips = get_domain_ips(domain, "AAAA")
        
        # 分别查找最快的 IPv4 和 IPv6 地址
        if not ipv4_ips and not ipv6_ips:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:无法获取 {domain} 的IP列表，跳过该域名")
            continue
               
        # 处理 IPv6 地址
        if ipv6_ips:
            fastest_ipv6 = find_fastest_ip(ipv6_ips)
            if fastest_ipv6:
                results.append([fastest_ipv6, domain])
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:域名 {domain} 的最快IPv6是: {fastest_ipv6}")
            else:
                # 兜底：可能存在无法正确获取 fastest_ipv6 的情况，则将第一个IP赋值
                results.append([ipv6_ips[0], domain])

        # 处理 IPv4 地址
        if ipv4_ips:
            fastest_ipv4 = find_fastest_ip(ipv4_ips)
            if fastest_ipv4:
                results.append([fastest_ipv4, domain])
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:域名 {domain} 的最快IPv4是: {fastest_ipv4}")
            else:
                results.append([ipv4_ips[0], domain])
        
        sleep(1)  # 避免请求过于频繁
    
    # 返回内容
    if results:              
        update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
        hosts_content = Tmdb_Host_TEMPLATE.format(content="\n".join(f"{ip:<40} {domain}" for ip, domain in results), update_time=update_time) if results else ""
        return hosts_content
    else:
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 未能正确获取TMDB解析结果。")
        return None

@retry(tries=3)
def get_domain_ips(domain, record_type):
    """
    从Google DNS获取域名的A/AAAA记录IP列表
    :param domain: 目标域名（如 tmdb.org）
    :param record_type: 记录类型（A/AAAA，或数字1/28）
    :return: 去重后的IP列表
    """
    all_ips = []  # 存储所有DNS服务器返回的IP
    
    print(f"正在从Google DNS获取 {domain} 的{record_type}记录...")
    url = f'https://dns.google/resolve'
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json; charset=UTF-8",  # 关键：指定JSON格式负载
        "referer": f"https://dns.google/query?name={domain}&rr_type={record_type}&ecs=",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
    }

    params = {
        'name': domain,
        'type': record_type
    }

    # 初始化IP列表（默认空列表，确保后续使用安全）
    ips_str = []

    try:
        # 改用GET请求（Google DNS resolve接口标准用法）
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # 主动抛出HTTP错误（如4xx/5xx）

        # 解析JSON响应
        data = response.json()
        if not isinstance(data, dict):
            print("返回数据不是字典格式，无法解析")
            return all_ips

        # 核心：提取Answer数组中的data字段（IP地址）
        answer_list = data.get("Answer", [])
        if not answer_list:
            print(f"未找到 {domain} 的{record_type}记录（Answer字段为空）")
            return all_ips

        # 遍历Answer数组，提取每个条目的data值（IP）
        for answer in answer_list:
            ip = answer.get("data")
            if ip:  # 过滤空值
                all_ips.append(ip)
                print(f"提取到IP：{ip}")

    except requests.exceptions.RequestException as e:
        # 捕获所有网络/请求异常
        print(f"请求Google DNS失败：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"响应内容：{e.response.text[:500]}")  # 打印前500字符避免过长
    except ValueError:
        # JSON解析失败
        print(f"响应内容不是有效的JSON格式：{response.text[:500]}")
    
    # 去重并返回（保持列表格式）
    unique_ips = list(set(all_ips))
    print(f"最终提取到 {domain} 的{record_type}记录IP（去重后）：{unique_ips}")
    return unique_ips

# 通过ipv4\ipv6同源json数据包，获取最快的Cloudflare IP IPv4 及 IPv6
def get_CloudflareIP():
    """获取最快的Cloudflare IP IPv4 及 IPv6"""
    url = "https://api.vvhan.com/tool/cf_ip"
    headers = {
        "Sec-Ch-Ua-Platform": "Windows",
        "User-Agent": UserAgent
    }

    cf_domains = [
        'cloudflare.com',
        'hdtime.org'
    ]
    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始从：{url} 获取最优CloudFlare IP地址~")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        v4_ct = data["data"]["v4"]["CT"]
        v6_ct = data["data"]["v6"]["CT"]

        try:
            min_latency_v4 = min(v4_ct, key=lambda x: x["latency"])["ip"]
            # 验证 IPv4 地址的有效性
            ipaddress.IPv4Address(min_latency_v4)
        except (ValueError, IndexError):
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 未找到有效的 IPv4 地址。")
            min_latency_v4 = None

        try:
            min_latency_v6 = min(v6_ct, key=lambda x: x["latency"])["ip"]
            # 验证 IPv6 地址的有效性
            ipaddress.IPv6Address(min_latency_v6)
        except (ValueError, IndexError):
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 未找到有效的 IPv6 地址。")
            min_latency_v6 = None

        if min_latency_v4 is not None:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:data.v4.CT 节点下 latency 最低的 ip: {min_latency_v4}")
        if min_latency_v6 is not None:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:data.v6.CT 节点下 latency 最低的 ip: {min_latency_v6}")

        # 构建 hosts 文件内容
        lines = []
        for domain in cf_domains:
            if min_latency_v6 is not None:
                lines.append(f"{min_latency_v6:<40} {domain}")
            if min_latency_v4 is not None:
                lines.append(f"{min_latency_v4:<40} {domain}")

        # 返回内容
        update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
        hosts_content = Cloudflare_Host_TEMPLATE.format(content="\n".join(lines), update_time=update_time) if lines else ""
        return hosts_content
    else:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 从 {url} 网址获取 Cloudflare最优IP结果失败。: {response.status_code}")
        return ""

# 通过 ipv4\ipv6 异源 单行单IP 数据，获取最快的Cloudflare IP IPv4 及 IPv6
def get_bestcf_ipv4v6(use_ipv6=False):
    """
    获取最快的CloudFlare IPv4和IPv6地址
    
    Args:
        use_ipv6 (bool): 是否获取IPv6地址，默认为False
    """
    ipv4_urls = [
        'https://ip.164746.xyz/ipTop.html',
        'https://ipdb.api.030101.xyz/?type=bestcfv4',
        'https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestcf.txt'
    ]
    ipv6_urls = [
        'https://ipdb.api.030101.xyz/?type=bestcfv6'
    ]

    cf_domains = [
        'cloudflare.com',
        'hdtime.org'
    ]

    headers = {
        "Sec-Ch-Ua-Platform": "Windows",
        "User-Agent": UserAgent
    }

    valid_ipv4s = []
    valid_ipv6s = []

    # 获取有效的 IPv4 地址
    for url in ipv4_urls:
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始从：{url} 获取CloudFlare IPv4地址~")
        try:
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                ips = [ip.strip() for part in response.text.split('\n') for ip in part.split(',') if ip.strip()]
                for ip in ips:
                    try:
                        ipaddress.IPv4Address(ip)
                        valid_ipv4s.append(ip)
                    except ipaddress.AddressValueError:
                        pass
                if valid_ipv4s:
                    print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 成功获取到 {len(valid_ipv4s)} 个有效IPv4地址")
                    break
                else:
                    print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取的IP地址列表中没有有效的IPv4地址")
        except Exception as e:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取IPv4列表时发生错误: {str(e)}")

    # 仅当 use_ipv6 为 True 时，获取有效的 IPv6 地址
    if use_ipv6:
        for url in ipv6_urls:
            print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始从：{url} 获取CloudFlare IPv6地址~")
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    ips = [ip.strip() for part in response.text.split('\n') for ip in part.split(',') if ip.strip()]
                    for ip in ips:
                        try:
                            ipaddress.IPv6Address(ip)
                            valid_ipv6s.append(ip)
                        except ipaddress.AddressValueError:
                            pass
                    if valid_ipv6s:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 成功获取到 {len(valid_ipv6s)} 个有效IPv6地址")
                        break
                    else:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取的IP地址列表中没有有效的IPv6地址")
            except Exception as e:
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取IPv6列表时发生错误: {str(e)}")

    fastest_ipv4 = find_fastest_ip(valid_ipv4s) if valid_ipv4s else None
    fastest_ipv6 = find_fastest_ip(valid_ipv6s) if use_ipv6 and valid_ipv6s else None

    if fastest_ipv4 or fastest_ipv6:
        if fastest_ipv4:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:检测出 cloudflare 最快 IPv4 是{fastest_ipv4}")
        if fastest_ipv6:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:检测出 cloudflare 最快 IPv6 是{fastest_ipv6}")

        # 生成 hosts 文件内容
        lines = []
        for domain in cf_domains:
            if fastest_ipv6:
                lines.append(f"{fastest_ipv6:<40} {domain}")
            if fastest_ipv4:
                lines.append(f"{fastest_ipv4:<40} {domain}")

        update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
        hosts_content = Cloudflare_Host_TEMPLATE.format(content="\n".join(lines), update_time=update_time) if lines else ""
        return hosts_content
    else:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: 未能正确获取Cloudflare最优IP结果。")
        return None

# 获取GitHub ips
def get_github_ips() -> None:
    github_hosts_urls = [
        "https://raw.githubusercontent.com/521xueweihan/GitHub520/refs/heads/main/hosts",
        "https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts",
        "https://github-hosts.tinsfox.com/hosts",
        "https://raw.githubusercontent.com/ittuann/GitHub-IP-hosts/refs/heads/main/hosts_single"
    ]
    all_failed = True
    for url in github_hosts_urls:
        print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:开始从：{url} 获取Github hosts~")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:成功获取到GitHub hosts~")
                # 去掉所有以 # 开头的注释行
                lines = response.text.split('\n')
                non_comment_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]
                non_comment_lines.insert(0, '# GitHun Data From: ' + url)
                non_comment_content = '\n'.join(non_comment_lines).strip()
                update_time = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
                hosts_content = Github_Host_TEMPLATE.format(content=non_comment_content, update_time=update_time)
                return hosts_content
            else:
                print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取GitHub hosts失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:从 {url} 获取GitHub hosts时发生错误: {str(e)}")
    if all_failed:
        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:获取GitHub hosts失败: 所有Url全部失效！")
        return None

def main():  
    print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:update_myhosts 脚本执行开始...")
    global HOSTS_FILE_PATH
    HOSTS_FILE_PATH = Utils.get_hosts_file_path()

    if not Utils.check_environment(HOSTS_FILE_PATH):
        sys.exit(1)

    parameters = list(OrderedDict.fromkeys(sys.argv)) #获取去重后的参数

    # 根据参数数量执行不同的操作
    if len(parameters) == 1:
        # 无参数执行
        tmdb_hosts = get_tmdb_ips("-4")
        if tmdb_hosts:
            write_myhosts(tmdb_hosts)
    else:
        if '-flush' in parameters:
            """部分更新方式更新hosts"""
            for paramet in parameters[1:]:
                if paramet.upper() == '-4':
                    tmdb_hosts = get_tmdb_ips("-4")
                    if tmdb_hosts:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:TMDB Hosts 更新成功。" if update_file(HOSTS_FILE_PATH, "# Tmdb Hosts Start", "# Tmdb Hosts End\n", tmdb_hosts) else f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:TMDB Hosts 更新失败！")
                elif paramet.upper() == '-10':
                    tmdb_hosts = get_tmdb_ips("-10")
                    if tmdb_hosts:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:TMDB Hosts 更新成功。" if update_file(HOSTS_FILE_PATH, "# Tmdb Hosts Start", "# Tmdb Hosts End\n", tmdb_hosts) else f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:TMDB Hosts 更新失败！")
                elif paramet.upper() == '-G':
                    github_hosts = get_github_ips()
                    if github_hosts:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Github Hosts 更新成功。" if update_file(HOSTS_FILE_PATH, "# Github Hosts Start", "# Github Hosts End\n", github_hosts) else f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:Github Hosts 更新失败!")
                elif paramet.upper() == '-CF':
                    cf_hosts = get_CloudflareIP() # 优先使用 get_CloudflareIP() 获取
                    if not cf_hosts:
                        # 如果 get_CloudflareIP() 未获取到有效 IP，改用 get_bestcf_ipv4v6()
                        cf_hosts = get_bestcf_ipv4v6()
                    if cf_hosts:
                        print(f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:Cloudflare 最优IP 更新成功。" if update_file(HOSTS_FILE_PATH, "# Cloudflare Hosts Start", "# Cloudflare Hosts End\n", cf_hosts) else f"[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error:Cloudflare Hosts 更新失败!")
                else:
                    pass
            # 改为此处刷新DNS缓存，避免同时更新多个块时，反复刷新DNS
            sleep(1)
            Utils.execute_dns_command()
        else:
            myhosts_content = ""
            for paramet in parameters[1:]:
                if paramet.upper() == '-4':
                    tmdb_hosts = get_tmdb_ips("-4")
                    if tmdb_hosts:
                        myhosts_content += tmdb_hosts
                elif paramet.upper() == '-10':
                    tmdb_hosts = get_tmdb_ips("-10")
                    if tmdb_hosts:
                        myhosts_content += "\n" + tmdb_hosts
                elif paramet.upper() == '-G':
                    github_hosts = get_github_ips()
                    if github_hosts:
                        myhosts_content += "\n" + github_hosts + "\n"
                elif paramet.upper() == '-CF':
                    cf_hosts = get_CloudflareIP() # 优先使用 get_CloudflareIP() 获取
                    if not cf_hosts:
                        # 如果 get_CloudflareIP() 未获取到有效 IP，改用 get_bestcf_ipv4v6()
                        cf_hosts = get_bestcf_ipv4v6()
                    if cf_hosts:
                        myhosts_content += "\n" + cf_hosts
                else:
                    print(f"\n[update_myhosts {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Error: '{paramet}' 非脚本支持的参数，抛弃~")
    
            # 写出hosts文档
            if myhosts_content:
                write_myhosts(myhosts_content)

if __name__ == "__main__":
    main()

import sqlite3
import threading
import requests
import time
from czdb查询.find_ip import find_map
def get_myip():
    response = requests.get('http://httpbin.org/ip')
    if response.status_code == 200:
        return response.json()['origin']
    else:
        return None
MYIP = get_myip()
# 数据库文件路径
db_path = r'C:\Users\Administrator\Desktop\工作\ip\proxies.db'

# 连接到 SQLite 数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 修改表结构，添加新的字段
try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN anonymity TEXT')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN latency REAL')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN is_working INTEGER')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN country TEXT')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN region TEXT')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN city TEXT')
except sqlite3.OperationalError:
    pass  # 字段已存在

try:
    cursor.execute('ALTER TABLE proxies ADD COLUMN isp_domain TEXT')
except sqlite3.OperationalError:
    pass  # 字段已存在

# 查询所有代理 IP
cursor.execute('SELECT ip, port FROM proxies')
proxies = cursor.fetchall()

# 关闭数据库连接
conn.close()

# 创建一个线程锁
lock = threading.Lock()

# 测试 IP 连接性和匿名程度的函数
def test_proxy(ip, port):
    proxy = f"http://{ip}:{port}"
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    try:
        start_time = time.time()
        response = requests.get('http://www.baidu.com', proxies=proxies, timeout=5)
        latency = time.time() - start_time
        latency = round(latency, 3)
        if response.status_code == 200:
            print(f"Proxy {ip}:{port} is working")
            # 测试匿名程度
            anonymity_response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            if anonymity_response.status_code == 200:
                origin_ip = anonymity_response.json()['origin']
                origin_ips = origin_ip.split(", ")
                if MYIP in origin_ips:
                    anonymity = "透明代理"
                elif len(origin_ips) > 1:
                    anonymity = "匿名代理"
                else:
                    anonymity = "高匿名代理"
            else:
                anonymity = "未知"
            is_working = 1
        else:
            print(f"Proxy {ip}:{port} is not working")
            anonymity = "未知"
            latency = None
            is_working = 0
    except Exception as e:
        print(f"Proxy {ip}:{port} failed: {e}")
        anonymity = "未知"
        latency = None
        is_working = 0
    # 获取地址信息
    address_info = find_map(ip)
    if address_info is not None:
        
        country = address_info.get('country', '未知')
        region = address_info.get('region', '未知')
        city = address_info.get('city', '未知')
        isp_domain = address_info.get('isp_domain', '未知')

    # 使用线程锁来更新数据库中的代理信息
    with lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE proxies
            SET anonymity = ?, latency = ?, is_working = ?, country = ?, region = ?, city = ?, isp_domain = ?
            WHERE ip = ? AND port = ?
        ''', (anonymity, latency, is_working, country, region, city, isp_domain, ip, port))
        conn.commit()
        conn.close()

# 创建线程列表
threads = []

# 为每个代理 IP 创建一个线程
for proxy in proxies:
    ip, port = proxy
    thread = threading.Thread(target=test_proxy, args=(ip, port))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

print("All proxy tests completed.")
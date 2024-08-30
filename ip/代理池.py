from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import re
import requests
import json
import sqlite3
# 创建或连接到 SQLite 数据库
conn = sqlite3.connect(r'C:\Users\Administrator\Desktop\工作\ip\proxies.db')
cursor = conn.cursor()

# 创建表（如果表不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    port TEXT NOT NULL
)
''')
#这是一个修改

# 插入代理信息到数据库的函数
def insert_proxy(ip, port):
    cursor.execute('INSERT INTO proxies (ip, port) VALUES (?, ?)', (ip, port))
    conn.commit()
# 设置 ChromeDriver 路径和下载目录
chrome_driver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
download_dir = r"C:\Users\Administrator\Downloads"
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--headless")
# 创建 Service 对象并指定 ChromeDriver 的路径
service = Service(executable_path=chrome_driver_path)

# 初始化全局变量
ips = []

def get_站大爷代理():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = 'https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=2&cunhuo=&dengji=1&nadr=&https=1&yys=&post=&px='
    driver.get(url)
    trs = driver.find_elements(By.XPATH, '//*[@id="ipc"]/tbody/tr')
    for tr in trs:
        tds = tr.find_elements(By.XPATH, './td')
        ip = tds[0].text
        port = tds[1].text
        print(ip, port)
        ips.append({'ip': ip, 'port': port})        
def get_free_proxy_list():
    url = 'https://free-proxy-list.net/'
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    trs = driver.find_elements(By.XPATH, '//*[@id="list"]/div/div[2]/div/table/tbody/tr')
    for tr in trs:
        tds = tr.find_elements(By.XPATH, './td')
        ip = tds[0].text
        port = tds[1].text
        print(ip, port)
        ips.append({'ip': ip, 'port': port})
def get_proxy_list():
    def get_ips(response):
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'LISTA' in data:
                    for ip in data['LISTA']:
                        ip_lower = {k.lower(): v for k, v in ip.items()}
                        print(ip_lower['ip'], ip_lower['port'])
                        ips.append({'ip': ip_lower['ip'], 'port': ip_lower['port']})
                else:
                    print("JSON response does not contain 'LISTA'")
            except requests.exceptions.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        else:
            print(f"Failed to retrieve proxy list, status code: {response.status_code}")
    url = 'https://www.proxy-list.download/api/v2/get?l=en&t=http'
    url1 = 'https://www.proxy-list.download/api/v2/get?l=en&t=https'
    for url in [url, url1]:
        response = requests.get(url)
        get_ips(response)
    
def get_快代理():
    url = 'https://www.kuaidaili.com/free/inha/1/'
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    trs = driver.find_elements(By.XPATH, '//*[@id="table__free-proxy"]/div/table/tbody/tr')
    for tr in trs:
        tds = tr.find_elements(By.XPATH, './td')
        ip = tds[0].text
        port = tds[1].text
        print(ip, port)
        ips.append({'ip': ip, 'port': port})
        
def get_西刺代理():
    url = 'https://www.xicidaili.com/nn/1'
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    trs = driver.find_elements(By.XPATH, '//*[@id="ip_list"]/tbody/tr')
    for tr in trs:
        tds = tr.find_elements(By.XPATH, './td')
        ip = tds[1].text
        port = tds[2].text
        print(ip, port)
        ips.append({'ip': ip, 'port': port})
        
def get_66代理():
    url = 'http://www.66ip.cn/1.html'
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    trs = driver.find_elements(By.XPATH, '//*[@id="table__free-proxy"]/div/table/tbody/tr')
    for tr in trs:
        tds = tr.find_elements(By.XPATH, './td')
        ip = tds[0].text
        port = tds[1].text
        print(ip, port)
        ips.append({'ip': ip, 'port': port})


get_free_proxy_list()
get_站大爷代理()
get_proxy_list()
get_快代理()
for ip in ips:
    insert_proxy(ip['ip'], ip['port'])
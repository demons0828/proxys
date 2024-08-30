import threading
import subprocess
import os
import requests


#加入请求头为了防止被封
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

ipgood = []


def test_ip(ip, port=80):
    proxies = {
        'http': f'http://{ip}:{port}',
        'https': f'http://{ip}:{port}'
    }
    try:
        # response = requests.get('http://httpbin.org/ip', headers=headers, timeout=3, proxies=proxies)
        # response = requests.get('https://v26-web.douyinvod.com/', headers=headers, timeout=3, proxies=proxies)
        response = requests.get('http://www.baidu.com', headers=headers, timeout=3, proxies=proxies)
        # response = requests.get('http://ucdl.25pp.com/fs08/2024/06/18/11/110_0d963d4584cb5f7053c9b30aaa9490c0.apk', headers=headers, timeout=1, proxies=proxies,stream=True)
    except Exception as e:
        # print(e)
        return False
    if response.status_code in [200, 301, 302] and '百度' in response.text:
        # ipgood.append(str(ip) + ':' + str(port))
        # print(response.text)
        if port==80:
            ipgood.append(ip)
        # print(proxies)
        # print(response.text)
        return True
    else:
        # print(response.status_code)
        # print(response.text)
        print(response.status_code)
        return False


    
    # Print the result

def main():
    """
    从文本文件中读取IP地址，并为每个IP地址创建一个线程并启动它们。
    等待所有线程完成后结束。
    """
    # Read IP addresses from the text file
    with open(r'c:\Users\Administrator\Desktop\工作\ip\ip1.txt', 'r') as file:
        ip_addresses = file.read().splitlines()

    # Create a thread for each IP address and start them
    threads = []
    for ip in ip_addresses:
        port=80
        if ':' in ip:     
            port=ip.split(':')[-1]
            ip=ip.split(':')[0]
        thread = threading.Thread(target=test_ip, args=(ip,port))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    print(ipgood)
    print(len(ipgood))

if __name__ == '__main__':
    # with open('ip\ip.txt', 'r') as file:
    #     ip_addresses = file.read().splitlines()
    # for ip in ip_addresses:
    #     test_ip(ip)
    main()
    # with open(r'工作\ip\ipgood.txt', 'r') as file:
    #     ip_addresses = file.read().splitlines()
#     iplist=['125.111.163.214', '190.103.177.131', '222.66.202.6', '121.40.170.252', '23.152.40.14', '40.114.147.106', '153.101.67.170', '180.167.238.98', '121.43.101.253', '23.226.117.85', '212.127.93.185', '220.248.70.237', '199.19.103.162', '51.15.242.202', '103.118.46.174', '50.62.183.223', '176.98.81.85', '119.23.72.21', '182.253.181.10', '103.118.46.176', '80.89.198.229', '60.12.168.114', '121.40.98.50', '198.59.147.146', '159.65.77.168', '91.189.177.189', '133.18.234.13', '183.100.14.134', '103.216.49.151', '116.203.28.43', '103.49.202.252', '158.255.212.55', '212.108.145.195', '200.201.223.164', '146.59.202.70', 
# '183.215.23.242', '121.40.118.246', '103.133.24.50', '112.51.96.118', '211.45.175.45', '122.116.150.2', '150.136.4.250', '91.202.230.219', '61.160.223.141', '46.17.63.166', '91.189.177.186', '101.37.18.160', '111.177.63.86', '168.197.182.159', '58.214.243.91', '62.3.30.135', '138.91.159.185', '13.81.217.201', '49.228.131.169', '156.67.214.232', '115.127.31.66']
#     for ip in iplist:
#         test_ip(ip)

    #     test_ip(ip=ip)
    # import requests

    # proxies = {
    #     'http': 'http://171.83.191.99:5529',
    #     'https': 'http://171.83.191.99:5529',
    # }

    # try:
    #     response = requests.get('https://r.inews.qq.com/api/ip2city?ip=', proxies=proxies, timeout=5)  # timeout 设置为 5 秒
    #     print(response.text)
    # except requests.exceptions.ProxyError as e:
    #     print(f"无法连接到代理: {e}")
    # except requests.exceptions.ConnectTimeout as e:
    #     print(f"连接超时: {e}")
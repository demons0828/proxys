
# import requests
# import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
# ipgood = ['112.90.48.12']

# def test_ip(ip, port=80):
#     proxies = {
#         'http': f'http://{ip}:{port}',
#         'https': f'http://{ip}:443'  
#     }
#     try:
#         response = requests.get('http://httpbin.org/ip', headers=headers, timeout=3, proxies=proxies)
#         # response = requests.get('https://v26-web.douyinvod.com/', headers=headers, timeout=3, proxies=proxies,verify=False)
#         # response = requests.get('http://www.baidu.com', headers=headers, timeout=3, proxies=proxies)
#         # response = requests.get('http://ucdl.25pp.com/fs08/2024/06/18/11/110_0d963d4584cb5f7053c9b30aaa9490c0.apk', headers=headers, timeout=1, proxies=proxies,stream=True)
#     except Exception as e:
#         print(e)
#         print('出错：'+ip)
#         return False
#     if response.status_code in [200, 301, 302,403]:
#         print(response.status_code)
#         print(response.headers)
#         print(proxies)
#         print(response.text)
#         # print(response.text)
#         return True
#     else:
#         print(ip)
#         # print(response.status_code)
#         # print(response.text)
#         return False

# if __name__ == '__main__':
#     for ip in ipgood:
#         port=80
#         if ':' in ip:     
#             port=ip.split(':')[-1]
#             ip=ip.split(':')[0]
#         test_ip(ip)
#




import requests
import json

# 配置的代理IP地址
ipgood = ['202.110.112.168']

# 定义头信息
headers = {
    'User-Agent': 'Mozilla/5.0'
}

def test_ip(ip, port=80):
    proxies = {
        'http': f'http://{ip}:{port}',
        'https': f'http://{ip}:443'  
    }
    try:
        # response = requests.get('http://httpbin.org/ip', headers=headers, timeout=3, proxies=proxies)
        response = requests.get('https://api.proxychecker.yccd.cc:8443/',timeout=3)
        print(response.status_code)
        response_data = response.json()  # 解析返回的JSON数据
        origin_ip = response_data.get('origin')  # 获取返回的IP地址
        if origin_ip == ip:
            print(f"请求通过了代理 {ip}")
            return True
        else:
            print(f"请求没有通过代理，返回的IP是 {origin_ip}")
            return False
    except Exception as e:
        print(e)
        print('出错：'+ip)
        return False

if __name__ == '__main__':
    for ip in ipgood:
        port = 80
        if ':' in ip:     
            port = ip.split(':')[-1]
            ip = ip.split(':')[0]
        test_ip(ip)

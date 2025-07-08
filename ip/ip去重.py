import re

# 打开文件
with open(r'工作\ip\ipgood.txt', 'r') as file:
    content = file.read()

# 正则表达式匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ips = re.findall(ip_pattern, content)

# 去重
ips = list(set(ips))
# 写入文件
with open(r'工作\ip\ipgood.txt', 'w') as file:
    for ip in ips:
        file.write(ip + '\n')
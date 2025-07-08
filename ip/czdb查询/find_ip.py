import ipdb
from flask import Flask, request, jsonify
import ipaddress
import json

# 加载 IPDB 文件
db_path = r'ip\czdb查询\qqwry.ipdb'
db = ipdb.City(db_path)

app = Flask(__name__)

def find_map(ip_address):
    # 检查是否为 IPv6 地址
    try:
        ip = ipaddress.ip_address(ip_address)
        if ip.version == 6:
            return {"error": "数据库不支持 IPv6 地址"}
    except ValueError:
        return {"error": "无效的 IP 地址"}

    try:
        # 查询 IP 地址信息
        info = db.find_map(ip_address, "CN")
    except UnicodeDecodeError as e:
        return {"error": f"编码错误: {str(e)}"}

    if info is None:
        return None

    # 返回查询结果
    return {
        "ip_address": ip_address,
        "country": info['country_name'],
        "region": info['region_name'],
        "city": info['city_name'],
        "isp_domain": info['isp_domain']
    }

@app.route('/query_ip', methods=['GET'])
def query_ip():
    ip_address = request.args.get('ip')
    if not ip_address:
        return jsonify({"error": "缺少 IP 地址参数"}), 400

    result = find_map(ip_address)
    if result is None:
        return jsonify({"error": f"未找到 IP 地址 {ip_address} 的信息"}), 404

    return jsonify(result)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, threaded=True)
    ips = []
    with open(r'C:\Users\Administrator\Desktop\工作\随机联通ip\移动ip.txt', 'r') as f:
        for line in f:
            ip = line.strip()
            test = find_map(ip)
            ipstr = ip
            if test is None or 'error' in test:
                continue
            area = test['region'] + test['city']
            type = 3
            if '移动' in test['isp_domain']:
                ips.append({'ip_str': ipstr, 'area': area, 'type': type})
    with open(r'C:\Users\Administrator\Desktop\工作\随机联通ip\移动ip.json', 'w',encoding='utf-8') as f:
        f.write(json.dumps(ips, ensure_ascii=False, indent=4))
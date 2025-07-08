import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from models import LocationInfo
from config import settings
import logging

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.ipdb_path = settings.QQWRY_IPDB_PATH
        self.ipdb_instance = None
        self.fallback_mode = False
    
    async def download_ipdb(self) -> bool:
        """下载IP地理位置数据库"""
        try:
            if os.path.exists(self.ipdb_path):
                logger.info(f"IP数据库已存在: {self.ipdb_path}")
                return True
            
            logger.info(f"正在下载IP数据库: {settings.QQWRY_IPDB_URL}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.QQWRY_IPDB_URL) as response:
                    if response.status == 200:
                        with open(self.ipdb_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        logger.info(f"IP数据库下载完成: {self.ipdb_path}")
                        return True
                    else:
                        logger.error(f"下载失败，状态码: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"下载IP数据库失败: {e}")
            return False
    
    async def load_ipdb(self) -> bool:
        """加载IP地理位置数据库"""
        try:
            # 尝试导入ipdb库
            try:
                import ipdb
                logger.info("成功导入ipdb库")
            except ImportError:
                logger.warning("ipdb库未安装，使用内置IP段映射")
                self.fallback_mode = True
                return True
            
            # 如果数据库文件不存在，先下载
            if not os.path.exists(self.ipdb_path):
                logger.info("IP数据库不存在，正在下载...")
                if not await self.download_ipdb():
                    logger.warning("下载失败，使用内置IP段映射")
                    self.fallback_mode = True
                    return True
            
            # 尝试加载ipdb数据库
            try:
                self.ipdb_instance = ipdb.City(self.ipdb_path)
                logger.info(f"IP数据库加载完成")
                logger.info(f"支持语言: {self.ipdb_instance.languages()}")
                logger.info(f"数据字段: {self.ipdb_instance.fields()}")
                logger.info(f"构建时间: {self.ipdb_instance.build_time()}")
                return True
            except Exception as e:
                logger.error(f"加载ipdb数据库失败: {e}")
                logger.info("回退到内置IP段映射")
                self.fallback_mode = True
                return True
                
        except Exception as e:
            logger.error(f"初始化IP数据库失败: {e}")
            self.fallback_mode = True
            return True
    
    async def get_location(self, ip: str) -> Optional[LocationInfo]:
        """获取IP地理位置信息"""
        try:
            # 确保数据库已加载
            if self.ipdb_instance is None and not self.fallback_mode:
                if not await self.load_ipdb():
                    return None
            
            # 使用ipdb库查询
            if not self.fallback_mode and self.ipdb_instance:
                try:
                    result = self.ipdb_instance.find_map(ip, "CN")
                    if result:
                        return LocationInfo(
                            country=result.get('country_name', '未知'),
                            region=result.get('region_name', '未知'),
                            city=result.get('city_name', '未知'),
                            isp=result.get('isp_domain', '未知'),
                            country_code=result.get('country_code', 'UN'),
                            continent_code=result.get('continent_code', 'UN')
                        )
                except Exception as e:
                    logger.warning(f"ipdb查询失败，使用内置映射: {e}")
                    # 回退到内置映射
                    pass
            
            # 使用内置IP段映射
            location_info = self._get_basic_location(ip)
            return LocationInfo(
                country=location_info.get('country', '未知'),
                region=location_info.get('region', '未知'),
                city=location_info.get('city', '未知'),
                isp=location_info.get('isp', '未知'),
                country_code=location_info.get('country_code', 'UN'),
                continent_code=location_info.get('continent_code', 'UN')
            )
        except Exception as e:
            logger.error(f"获取IP地理位置失败 {ip}: {e}")
            return None
    
    def ip_to_int(self, ip: str) -> int:
        """将IP地址转换为整数"""
        try:
            parts = ip.split('.')
            return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
        except:
            return 0
    
    def _get_basic_location(self, ip: str) -> Dict[str, str]:
        """基本的IP地理位置映射（内置备用方案）"""
        ip_int = self.ip_to_int(ip)
        
        # 定义IP段范围和对应的地理位置信息
        ip_ranges = [
            # 中国大陆IP段
            {
                'ranges': [
                    ('1.0.0.0', '1.255.255.255'),
                    ('14.0.0.0', '14.255.255.255'),
                    ('27.0.0.0', '27.255.255.255'),
                    ('36.0.0.0', '36.255.255.255'),
                    ('39.0.0.0', '39.255.255.255'),
                    ('42.0.0.0', '42.255.255.255'),
                    ('58.0.0.0', '61.255.255.255'),
                    ('101.0.0.0', '101.255.255.255'),
                    ('106.0.0.0', '106.255.255.255'),
                    ('110.0.0.0', '125.255.255.255'),
                    ('180.0.0.0', '183.255.255.255'),
                    ('202.0.0.0', '203.255.255.255'),
                    ('210.0.0.0', '211.255.255.255'),
                    ('218.0.0.0', '223.255.255.255'),
                ],
                'location': {
                    'country': '中国',
                    'region': '大陆地区',
                    'city': '未知城市',
                    'isp': '中国电信/联通/移动',
                    'country_code': 'CN',
                    'continent_code': 'AS'
                }
            },
            # 美国IP段
            {
                'ranges': [
                    ('3.0.0.0', '4.255.255.255'),
                    ('8.0.0.0', '8.255.255.255'),
                    ('12.0.0.0', '20.255.255.255'),
                    ('23.0.0.0', '24.255.255.255'),
                    ('50.0.0.0', '50.255.255.255'),
                    ('64.0.0.0', '76.255.255.255'),
                    ('96.0.0.0', '99.255.255.255'),
                    ('104.0.0.0', '108.255.255.255'),
                    ('173.0.0.0', '174.255.255.255'),
                    ('184.0.0.0', '184.255.255.255'),
                    ('192.0.0.0', '192.255.255.255'),
                    ('198.0.0.0', '199.255.255.255'),
                    ('204.0.0.0', '209.255.255.255'),
                ],
                'location': {
                    'country': '美国',
                    'region': '未知州',
                    'city': '未知城市',
                    'isp': 'Unknown ISP',
                    'country_code': 'US',
                    'continent_code': 'NA'
                }
            },
            # 日本IP段
            {
                'ranges': [
                    ('126.0.0.0', '126.255.255.255'),
                    ('133.0.0.0', '133.255.255.255'),
                    ('150.0.0.0', '150.255.255.255'),
                    ('153.0.0.0', '153.255.255.255'),
                    ('163.0.0.0', '163.255.255.255'),
                    ('202.11.0.0', '202.11.255.255'),
                    ('210.128.0.0', '210.255.255.255'),
                ],
                'location': {
                    'country': '日本',
                    'region': '关东地区',
                    'city': '东京',
                    'isp': 'NTT/KDDI',
                    'country_code': 'JP',
                    'continent_code': 'AS'
                }
            },
            # 韩国IP段
            {
                'ranges': [
                    ('114.0.0.0', '114.255.255.255'),
                    ('175.0.0.0', '175.255.255.255'),
                    ('211.104.0.0', '211.119.255.255'),
                    ('220.0.0.0', '220.255.255.255'),
                ],
                'location': {
                    'country': '韩国',
                    'region': '首尔特别市',
                    'city': '首尔',
                    'isp': 'KT/SK Telecom',
                    'country_code': 'KR',
                    'continent_code': 'AS'
                }
            },
            # 英国IP段
            {
                'ranges': [
                    ('80.0.0.0', '80.255.255.255'),
                    ('81.0.0.0', '81.255.255.255'),
                    ('82.0.0.0', '82.255.255.255'),
                    ('86.0.0.0', '86.255.255.255'),
                    ('87.0.0.0', '87.255.255.255'),
                    ('90.0.0.0', '90.255.255.255'),
                    ('92.0.0.0', '92.255.255.255'),
                ],
                'location': {
                    'country': '英国',
                    'region': '英格兰',
                    'city': '伦敦',
                    'isp': 'BT/Virgin Media',
                    'country_code': 'GB',
                    'continent_code': 'EU'
                }
            },
            # 德国IP段
            {
                'ranges': [
                    ('84.0.0.0', '84.255.255.255'),
                    ('85.0.0.0', '85.255.255.255'),
                    ('88.0.0.0', '88.255.255.255'),
                    ('89.0.0.0', '89.255.255.255'),
                    ('93.0.0.0', '93.255.255.255'),
                    ('217.0.0.0', '217.255.255.255'),
                ],
                'location': {
                    'country': '德国',
                    'region': '巴伐利亚州',
                    'city': '柏林',
                    'isp': 'Deutsche Telekom',
                    'country_code': 'DE',
                    'continent_code': 'EU'
                }
            },
            # 新加坡IP段
            {
                'ranges': [
                    ('103.0.0.0', '103.255.255.255'),
                    ('152.0.0.0', '152.255.255.255'),
                    ('165.0.0.0', '165.255.255.255'),
                    ('202.156.0.0', '202.156.255.255'),
                ],
                'location': {
                    'country': '新加坡',
                    'region': '新加坡',
                    'city': '新加坡',
                    'isp': 'Singtel/StarHub',
                    'country_code': 'SG',
                    'continent_code': 'AS'
                }
            },
            # 俄罗斯IP段
            {
                'ranges': [
                    ('77.0.0.0', '77.255.255.255'),
                    ('78.0.0.0', '78.255.255.255'),
                    ('79.0.0.0', '79.255.255.255'),
                    ('95.0.0.0', '95.255.255.255'),
                    ('178.0.0.0', '178.255.255.255'),
                ],
                'location': {
                    'country': '俄罗斯',
                    'region': '莫斯科州',
                    'city': '莫斯科',
                    'isp': 'Rostelecom',
                    'country_code': 'RU',
                    'continent_code': 'EU'
                }
            },
        ]
        
        # 检查IP是否属于任何已知范围
        for country_data in ip_ranges:
            for start_ip, end_ip in country_data['ranges']:
                if self.ip_to_int(start_ip) <= ip_int <= self.ip_to_int(end_ip):
                    return country_data['location']
        
        # 本地和私有IP段
        if ip.startswith(('127.', '192.168.', '10.')):
            return {
                'country': '本地网络',
                'region': '局域网',
                'city': '本地',
                'isp': '本地ISP',
                'country_code': 'LOCAL',
                'continent_code': 'LOCAL'
            }
        
        # 私有IP段 172.16.0.0/12
        if ip.startswith('172.'):
            parts = ip.split('.')
            if len(parts) >= 2 and 16 <= int(parts[1]) <= 31:
                return {
                    'country': '本地网络',
                    'region': '局域网',
                    'city': '本地',
                    'isp': '本地ISP',
                    'country_code': 'LOCAL',
                    'continent_code': 'LOCAL'
                }
        
        # 默认返回
        return {
            'country': '未知国家',
            'region': '未知地区',
            'city': '未知城市',
            'isp': '未知运营商',
            'country_code': 'UN',
            'continent_code': 'UN'
        }
    
    async def batch_get_location(self, ips: list) -> dict:
        """批量获取IP地理位置信息"""
        results = {}
        
        # 限制并发数
        semaphore = asyncio.Semaphore(20)
        
        async def get_single_location(ip):
            async with semaphore:
                return await self.get_location(ip)
        
        # 批量处理
        tasks = [get_single_location(ip) for ip in ips]
        locations = await asyncio.gather(*tasks, return_exceptions=True)
        
        for ip, location in zip(ips, locations):
            if isinstance(location, Exception):
                logger.error(f"获取IP地理位置失败 {ip}: {location}")
                results[ip] = None
            else:
                results[ip] = location
        
        return results

# 全局地理位置服务实例
location_service = LocationService() 
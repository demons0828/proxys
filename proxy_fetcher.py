import aiohttp
import asyncio
import re
import ssl
from typing import List, Optional, Dict, Any
from models import ProxyInfo, ProxyProtocol, ProxyStatus
from config import settings
import logging

logger = logging.getLogger(__name__)

class ProxyFetcher:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        # 创建更宽松的SSL上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def __aenter__(self):
        # 创建连接器，禁用SSL验证
        connector = aiohttp.TCPConnector(
            ssl=self.ssl_context,
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        # 设置用户代理和其他headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_proxy_list(self, url: str) -> List[str]:
        """从URL获取代理列表"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content.strip().split('\n')
                else:
                    logger.error(f"获取代理列表失败，状态码: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"获取代理列表失败 {url}: {e}")
            return []
    
    def parse_proxy_line(self, line: str, protocol: ProxyProtocol) -> Optional[ProxyInfo]:
        """解析代理行"""
        try:
            line = line.strip()
            if not line or line.startswith('#'):
                return None
            
            # 支持多种格式
            # 格式1: ip:port
            # 格式2: ip:port:username:password
            # 格式3: protocol://ip:port
            # 格式4: protocol://username:password@ip:port
            
            # 去掉协议前缀
            if '://' in line:
                parts = line.split('://', 1)
                line = parts[1]
            
            # 检查是否有认证信息
            username = None
            password = None
            
            if '@' in line:
                auth_part, server_part = line.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                line = server_part
            
            # 解析IP和端口
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    host = parts[0]
                    port = int(parts[1])
                    
                    # 如果还有更多部分，可能是用户名和密码
                    if len(parts) >= 4 and not username:
                        username = parts[2]
                        password = parts[3]
                    
                    # 验证IP地址格式
                    if self._is_valid_ip(host) and 1 <= port <= 65535:
                        return ProxyInfo(
                            protocol=protocol,
                            host=host,
                            port=port,
                            username=username,
                            password=password,
                            status=ProxyStatus.ACTIVE
                        )
            
            return None
        except Exception as e:
            logger.debug(f"解析代理行失败 {line}: {e}")
            return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
    
    async def fetch_http_proxies(self) -> List[ProxyInfo]:
        """获取HTTP代理列表"""
        logger.info("开始获取HTTP代理...")
        url = settings.PROXY_SOURCES["http"]
        proxy_lines = await self.fetch_proxy_list(url)
        
        proxies = []
        for line in proxy_lines:
            proxy = self.parse_proxy_line(line, ProxyProtocol.HTTP)
            if proxy:
                proxies.append(proxy)
        
        logger.info(f"获取到 {len(proxies)} 个HTTP代理")
        return proxies
    
    async def fetch_https_proxies(self) -> List[ProxyInfo]:
        """获取HTTPS代理列表"""
        logger.info("开始获取HTTPS代理...")
        url = settings.PROXY_SOURCES["https"]
        proxy_lines = await self.fetch_proxy_list(url)
        
        proxies = []
        for line in proxy_lines:
            proxy = self.parse_proxy_line(line, ProxyProtocol.HTTPS)
            if proxy:
                proxies.append(proxy)
        
        logger.info(f"获取到 {len(proxies)} 个HTTPS代理")
        return proxies
    
    async def fetch_socks5_proxies(self) -> List[ProxyInfo]:
        """获取SOCKS5代理列表"""
        logger.info("开始获取SOCKS5代理...")
        url = settings.PROXY_SOURCES["socks5"]
        proxy_lines = await self.fetch_proxy_list(url)
        
        proxies = []
        for line in proxy_lines:
            proxy = self.parse_proxy_line(line, ProxyProtocol.SOCKS5)
            if proxy:
                proxies.append(proxy)
        
        logger.info(f"获取到 {len(proxies)} 个SOCKS5代理")
        return proxies
    
    async def fetch_all_proxies(self) -> List[ProxyInfo]:
        """获取所有类型的代理"""
        logger.info("开始获取所有代理...")
        
        # 并发获取所有类型的代理
        tasks = [
            self.fetch_http_proxies(),
            self.fetch_https_proxies(),
            self.fetch_socks5_proxies()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_proxies = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"获取代理失败: {result}")
            else:
                all_proxies.extend(result)
        
        logger.info(f"总共获取到 {len(all_proxies)} 个代理")
        return all_proxies
    
    async def fetch_proxies_from_custom_urls(self, urls: Dict[str, str]) -> List[ProxyInfo]:
        """从自定义URL获取代理"""
        logger.info("开始从自定义URL获取代理...")
        
        all_proxies = []
        
        for protocol_name, url in urls.items():
            try:
                # 确定协议类型
                if protocol_name.lower() == 'http':
                    protocol = ProxyProtocol.HTTP
                elif protocol_name.lower() == 'https':
                    protocol = ProxyProtocol.HTTPS
                elif protocol_name.lower() == 'socks5':
                    protocol = ProxyProtocol.SOCKS5
                elif protocol_name.lower() == 'socks4':
                    protocol = ProxyProtocol.SOCKS4
                else:
                    logger.warning(f"未知协议类型: {protocol_name}")
                    continue
                
                proxy_lines = await self.fetch_proxy_list(url)
                
                for line in proxy_lines:
                    proxy = self.parse_proxy_line(line, protocol)
                    if proxy:
                        all_proxies.append(proxy)
                
                logger.info(f"从 {url} 获取到 {len([p for p in all_proxies if p.protocol == protocol])} 个 {protocol_name} 代理")
                
            except Exception as e:
                logger.error(f"从 {url} 获取代理失败: {e}")
        
        logger.info(f"从自定义URL总共获取到 {len(all_proxies)} 个代理")
        return all_proxies
    
    def deduplicate_proxies(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """去重代理"""
        seen = set()
        unique_proxies = []
        
        for proxy in proxies:
            key = (proxy.protocol, proxy.host, proxy.port)
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        logger.info(f"去重后剩余 {len(unique_proxies)} 个代理")
        return unique_proxies
    
    async def validate_proxy_format(self, proxy_str: str) -> Optional[ProxyInfo]:
        """验证并解析代理格式"""
        try:
            # 尝试所有协议类型
            for protocol in [ProxyProtocol.HTTP, ProxyProtocol.HTTPS, ProxyProtocol.SOCKS5, ProxyProtocol.SOCKS4]:
                proxy = self.parse_proxy_line(proxy_str, protocol)
                if proxy:
                    return proxy
            return None
        except Exception as e:
            logger.error(f"验证代理格式失败 {proxy_str}: {e}")
            return None

# 全局代理获取器实例
proxy_fetcher = ProxyFetcher() 
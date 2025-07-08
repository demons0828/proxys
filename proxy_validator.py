import aiohttp
import asyncio
import time
import socket
from typing import List, Optional, Dict, Any
from models import ProxyInfo, TestResult, ProxyStatus, ProxyProtocol
from config import settings
from location_service import location_service
import logging

logger = logging.getLogger(__name__)

class ProxyValidator:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
    
    async def __aenter__(self):
        # 配置连接器
        connector = aiohttp.TCPConnector(
            limit=settings.MAX_CONCURRENT_TESTS,
            limit_per_host=50,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_proxy_url(self, proxy: ProxyInfo) -> str:
        """构建代理URL"""
        if proxy.username and proxy.password:
            if proxy.protocol in [ProxyProtocol.HTTP, ProxyProtocol.HTTPS]:
                return f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
            else:
                return f"socks5://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
        else:
            if proxy.protocol in [ProxyProtocol.HTTP, ProxyProtocol.HTTPS]:
                return f"http://{proxy.host}:{proxy.port}"
            else:
                return f"socks5://{proxy.host}:{proxy.port}"
    
    async def validate_proxy(self, proxy: ProxyInfo, target_url: str = None) -> TestResult:
        """验证单个代理"""
        if not target_url:
            target_url = settings.DEFAULT_TEST_URL
        
        start_time = time.time()
        
        try:
            if not self.session:
                await self.__aenter__()
            
            proxy_url = self._get_proxy_url(proxy)
            
            # 根据协议类型选择验证方式
            if proxy.protocol in [ProxyProtocol.HTTP, ProxyProtocol.HTTPS]:
                return await self._validate_http_proxy(proxy, proxy_url, target_url, start_time)
            elif proxy.protocol in [ProxyProtocol.SOCKS5, ProxyProtocol.SOCKS4]:
                return await self._validate_socks_proxy(proxy, proxy_url, target_url, start_time)
            else:
                return TestResult(
                    proxy_id=proxy.id or 0,
                    target_url=target_url,
                    success=False,
                    error_message=f"不支持的协议类型: {proxy.protocol}"
                )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"验证代理失败 {proxy.host}:{proxy.port}: {e}")
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    async def _validate_http_proxy(self, proxy: ProxyInfo, proxy_url: str, 
                                 target_url: str, start_time: float) -> TestResult:
        """验证HTTP/HTTPS代理"""
        try:
            async with self.session.get(
                target_url,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    # 验证响应内容
                    content = await response.text()
                    if len(content) > 0:  # 基本验证
                        return TestResult(
                            proxy_id=proxy.id or 0,
                            target_url=target_url,
                            response_time=response_time,
                            status_code=response.status,
                            success=True
                        )
                
                return TestResult(
                    proxy_id=proxy.id or 0,
                    target_url=target_url,
                    response_time=response_time,
                    status_code=response.status,
                    success=False,
                    error_message=f"HTTP状态码: {response.status}"
                )
        
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=False,
                error_message="连接超时"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    async def _validate_socks_proxy(self, proxy: ProxyInfo, proxy_url: str, 
                                  target_url: str, start_time: float) -> TestResult:
        """验证SOCKS代理"""
        try:
            # 使用aiohttp-socks或直接测试连接
            # 这里简化实现，实际可能需要aiohttp-socks库
            async with self.session.get(
                target_url,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    content = await response.text()
                    if len(content) > 0:
                        return TestResult(
                            proxy_id=proxy.id or 0,
                            target_url=target_url,
                            response_time=response_time,
                            status_code=response.status,
                            success=True
                        )
                
                return TestResult(
                    proxy_id=proxy.id or 0,
                    target_url=target_url,
                    response_time=response_time,
                    status_code=response.status,
                    success=False,
                    error_message=f"SOCKS代理响应异常: {response.status}"
                )
        
        except Exception as e:
            # 对于SOCKS代理，也可以尝试基本的socket连接测试
            return await self._test_socket_connection(proxy, target_url, start_time)
    
    async def _test_socket_connection(self, proxy: ProxyInfo, target_url: str, 
                                    start_time: float) -> TestResult:
        """测试Socket连接"""
        try:
            # 简单的socket连接测试
            future = asyncio.get_event_loop().run_in_executor(
                None, 
                self._sync_socket_test, 
                proxy.host, 
                proxy.port
            )
            
            await asyncio.wait_for(future, timeout=settings.REQUEST_TIMEOUT)
            response_time = (time.time() - start_time) * 1000
            
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=True
            )
        
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=False,
                error_message="Socket连接超时"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return TestResult(
                proxy_id=proxy.id or 0,
                target_url=target_url,
                response_time=response_time,
                success=False,
                error_message=f"Socket连接失败: {str(e)}"
            )
    
    def _sync_socket_test(self, host: str, port: int) -> bool:
        """同步Socket测试"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(settings.REQUEST_TIMEOUT)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def batch_validate(self, proxies: List[ProxyInfo], 
                           target_url: str = None) -> List[TestResult]:
        """批量验证代理"""
        if not target_url:
            target_url = settings.DEFAULT_TEST_URL
        
        logger.info(f"开始批量验证 {len(proxies)} 个代理")
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TESTS)
        
        async def validate_with_semaphore(proxy):
            async with semaphore:
                return await self.validate_proxy(proxy, target_url)
        
        # 创建任务列表
        tasks = [validate_with_semaphore(proxy) for proxy in proxies]
        
        # 执行批量验证
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        test_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"验证代理异常 {proxies[i].host}:{proxies[i].port}: {result}")
                test_results.append(TestResult(
                    proxy_id=proxies[i].id or 0,
                    target_url=target_url,
                    success=False,
                    error_message=str(result)
                ))
            else:
                test_results.append(result)
        
        # 统计结果
        successful = sum(1 for r in test_results if r.success)
        logger.info(f"批量验证完成，成功: {successful}/{len(test_results)}")
        
        return test_results
    
    async def validate_proxy_with_multiple_urls(self, proxy: ProxyInfo, 
                                              urls: List[str]) -> List[TestResult]:
        """使用多个URL验证代理"""
        logger.info(f"使用多个URL验证代理 {proxy.host}:{proxy.port}")
        
        results = []
        for url in urls:
            result = await self.validate_proxy(proxy, url)
            results.append(result)
        
        return results
    
    async def get_proxy_location(self, proxy: ProxyInfo) -> Optional[Dict[str, Any]]:
        """获取代理地理位置信息"""
        try:
            location = await location_service.get_location(proxy.host)
            if location:
                return {
                    'country': location.country,
                    'region': location.region,
                    'city': location.city,
                    'isp': location.isp,
                    'country_code': location.country_code,
                    'continent_code': location.continent_code
                }
            return None
        except Exception as e:
            logger.error(f"获取代理地理位置失败 {proxy.host}: {e}")
            return None
    
    async def validate_and_update_location(self, proxy: ProxyInfo, 
                                         target_url: str = None) -> TestResult:
        """验证代理并更新地理位置信息"""
        # 先验证代理
        test_result = await self.validate_proxy(proxy, target_url)
        
        # 如果验证成功，获取地理位置信息
        if test_result.success:
            location_info = await self.get_proxy_location(proxy)
            if location_info:
                # 更新代理的地理位置信息
                proxy.country = location_info['country']
                proxy.region = location_info['region']
                proxy.city = location_info['city']
                proxy.isp = location_info['isp']
        
        return test_result
    
    async def calculate_success_rate(self, proxy: ProxyInfo, 
                                   test_count: int = 5) -> float:
        """计算代理成功率"""
        results = []
        
        for i in range(test_count):
            result = await self.validate_proxy(proxy)
            results.append(result.success)
            
            # 添加小延迟避免过于频繁的请求
            await asyncio.sleep(0.1)
        
        success_rate = sum(results) / len(results)
        logger.info(f"代理 {proxy.host}:{proxy.port} 成功率: {success_rate:.2%}")
        
        return success_rate
    
    async def benchmark_proxy_speed(self, proxy: ProxyInfo, 
                                  target_urls: List[str] = None) -> Dict[str, float]:
        """基准测试代理速度"""
        if not target_urls:
            target_urls = [
                settings.DEFAULT_TEST_URL,
                "http://httpbin.org/json",
                "http://httpbin.org/html",
                "http://httpbin.org/bytes/1024"
            ]
        
        results = {}
        
        for url in target_urls:
            test_result = await self.validate_proxy(proxy, url)
            results[url] = test_result.response_time if test_result.success else None
        
        # 计算平均速度
        valid_times = [t for t in results.values() if t is not None]
        avg_time = sum(valid_times) / len(valid_times) if valid_times else None
        
        results['average'] = avg_time
        
        return results

# 全局代理验证器实例
proxy_validator = ProxyValidator() 
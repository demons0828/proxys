#!/usr/bin/env python3
"""
代理池系统测试脚本
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class ProxyPoolTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self) -> Dict[str, Any]:
        """测试健康检查"""
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_add_proxy(self) -> Dict[str, Any]:
        """测试添加代理"""
        try:
            proxy_data = {
                "protocol": "HTTP",
                "host": "127.0.0.1",
                "port": 8080
            }
            
            async with self.session.post(
                f"{self.base_url}/api/proxies",
                json=proxy_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_get_proxies(self) -> Dict[str, Any]:
        """测试获取代理列表"""
        try:
            async with self.session.get(f"{self.base_url}/api/proxies") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "count": len(data), "data": data[:3]}  # 只显示前3个
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_get_statistics(self) -> Dict[str, Any]:
        """测试获取统计信息"""
        try:
            async with self.session.get(f"{self.base_url}/api/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_manual_update(self) -> Dict[str, Any]:
        """测试手动更新"""
        try:
            update_data = {"action": "fetch_new"}
            
            async with self.session.post(
                f"{self.base_url}/api/update",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_task_status(self) -> Dict[str, Any]:
        """测试任务状态"""
        try:
            async with self.session.get(f"{self.base_url}/api/tasks") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_random_proxy(self) -> Dict[str, Any]:
        """测试获取随机代理"""
        try:
            async with self.session.get(f"{self.base_url}/api/proxies/random") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "data": data}
                elif response.status == 404:
                    return {"status": "⚠️ 无代理", "message": "没有可用的代理"}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def test_countries(self) -> Dict[str, Any]:
        """测试获取国家列表"""
        try:
            async with self.session.get(f"{self.base_url}/api/proxies/countries") as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "✅ 通过", "count": len(data), "data": data}
                else:
                    return {"status": "❌ 失败", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "❌ 失败", "error": str(e)}
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("代理池系统测试")
        print("=" * 60)
        
        tests = [
            ("健康检查", self.test_health),
            ("添加代理", self.test_add_proxy),
            ("获取代理列表", self.test_get_proxies),
            ("获取统计信息", self.test_get_statistics),
            ("手动更新", self.test_manual_update),
            ("任务状态", self.test_task_status),
            ("随机代理", self.test_random_proxy),
            ("国家列表", self.test_countries),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔍 测试: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                print(f"   状态: {result['status']}")
                
                if 'data' in result:
                    if test_name == "获取代理列表":
                        print(f"   数量: {result.get('count', 0)}")
                        if result.get('data'):
                            print(f"   示例: {result['data'][0]['host']}:{result['data'][0]['port']}")
                    elif test_name == "获取统计信息":
                        stats = result['data']
                        print(f"   总代理数: {stats.get('total_proxies', 0)}")
                        print(f"   活跃代理数: {stats.get('active_proxies', 0)}")
                    elif test_name == "国家列表":
                        print(f"   国家数量: {result.get('count', 0)}")
                        if result.get('data'):
                            print(f"   国家列表: {', '.join(result['data'][:5])}")
                    elif test_name == "随机代理":
                        if result['status'] == "✅ 通过":
                            proxy = result['data']
                            print(f"   代理: {proxy['host']}:{proxy['port']} ({proxy['protocol']})")
                
                if 'error' in result:
                    print(f"   错误: {result['error']}")
                
                if 'message' in result:
                    print(f"   信息: {result['message']}")
                    
            except Exception as e:
                print(f"   状态: ❌ 异常")
                print(f"   错误: {str(e)}")
                results[test_name] = {"status": "❌ 异常", "error": str(e)}
        
        # 测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        passed = sum(1 for r in results.values() if r['status'] == "✅ 通过")
        total = len(results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"成功率: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！代理池系统运行正常。")
        else:
            print("\n⚠️ 部分测试失败，请检查服务状态。")
        
        return results

async def main():
    """主函数"""
    print("等待服务启动...")
    await asyncio.sleep(2)
    
    try:
        async with ProxyPoolTester() as tester:
            await tester.run_all_tests()
    except Exception as e:
        print(f"测试运行失败: {e}")
        print("\n请确保代理池服务正在运行:")
        print("python main.py")

if __name__ == "__main__":
    asyncio.run(main()) 
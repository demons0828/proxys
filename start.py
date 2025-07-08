#!/usr/bin/env python3
"""
代理池系统快速启动脚本
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import aiosqlite
        import apscheduler
        import pydantic
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_files():
    """检查必要文件"""
    print("📁 检查文件...")
    
    required_files = [
        "main.py",
        "api.py", 
        "config.py",
        "models.py",
        "database.py",
        "proxy_fetcher.py",
        "proxy_validator.py",
        "location_service.py",
        "scheduler.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必要文件存在")
        return True

def show_banner():
    """显示欢迎横幅"""
    print("=" * 60)
    print("🚀 代理池管理系统")
    print("=" * 60)
    print("功能特性:")
    print("  ✅ 支持 HTTP/HTTPS/SOCKS5/SOCKS4 代理")
    print("  ✅ 自动获取和验证代理")
    print("  ✅ 地理位置信息补充")
    print("  ✅ RESTful API 接口")
    print("  ✅ 定时任务调度")
    print("  ✅ Web 管理界面")
    print("=" * 60)

def show_urls():
    """显示访问地址"""
    print("\n🌐 访问地址:")
    print("  主页:     http://localhost:8000")
    print("  API文档:  http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/api/health")
    print("  代理列表: http://localhost:8000/api/proxies")
    print("  统计信息: http://localhost:8000/api/statistics")
    print("\n📝 日志文件: proxy_pool.log")
    print("💾 数据库:   proxy_pool.db")

def show_help():
    """显示帮助信息"""
    print("\n📚 快速使用指南:")
    print("\n1. 获取代理列表:")
    print("   curl http://localhost:8000/api/proxies")
    
    print("\n2. 添加代理:")
    print('   curl -X POST http://localhost:8000/api/proxies \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"protocol": "HTTP", "host": "1.2.3.4", "port": 8080}\'')
    
    print("\n3. 手动更新代理:")
    print('   curl -X POST http://localhost:8000/api/update \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"action": "fetch_new"}\'')
    
    print("\n4. 获取统计信息:")
    print("   curl http://localhost:8000/api/statistics")

async def start_system():
    """启动系统"""
    show_banner()
    
    # 检查环境
    if not check_dependencies():
        return False
    
    if not check_files():
        return False
    
    print("\n🔧 系统配置:")
    
    # 显示配置信息
    try:
        from config import settings
        print(f"  数据库: {settings.DATABASE_URL}")
        print(f"  更新间隔: {settings.UPDATE_INTERVAL}秒")
        print(f"  验证间隔: {settings.VALIDATION_INTERVAL}秒")
        print(f"  最大并发: {settings.MAX_CONCURRENT_TESTS}")
        print(f"  日志级别: {settings.LOG_LEVEL}")
    except Exception as e:
        print(f"⚠️ 配置读取失败: {e}")
    
    show_urls()
    show_help()
    
    print("\n" + "=" * 60)
    print("🚀 正在启动代理池系统...")
    print("💡 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        # 启动主程序
        from main import main
        await main()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 7):
            print("❌ 需要Python 3.7或更高版本")
            return
        
        # 检查是否在正确的目录
        if not Path("main.py").exists():
            print("❌ 请在项目根目录运行此脚本")
            return
        
        # 启动系统
        asyncio.run(start_system())
        
    except KeyboardInterrupt:
        print("\n👋 启动被用户取消")
    except Exception as e:
        print(f"\n❌ 启动脚本异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
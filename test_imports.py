#!/usr/bin/env python3
"""
导入测试脚本 - 诊断模块导入问题
"""

import sys
import traceback

def test_import(module_name, description=""):
    """测试模块导入"""
    try:
        if module_name == "pydantic_settings":
            from pydantic_settings import BaseSettings
            print(f"✅ {description or module_name} - 导入成功")
            return True
        elif module_name == "config":
            import config
            print(f"✅ {description or module_name} - 导入成功")
            print(f"   配置实例: {config.settings}")
            return True
        else:
            __import__(module_name)
            print(f"✅ {description or module_name} - 导入成功")
            return True
    except Exception as e:
        print(f"❌ {description or module_name} - 导入失败: {e}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print(f"""
{'='*60}
🧪 模块导入测试
{'='*60}
Python版本: {sys.version}
{'='*60}
""")
    
    # 测试基础模块
    modules_to_test = [
        ("typing", "类型提示"),
        ("typing_extensions", "类型扩展"),
        ("pydantic", "Pydantic数据验证"),
        ("pydantic_settings", "Pydantic设置"),
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "Uvicorn服务器"),
        ("aiohttp", "AioHTTP客户端"),
        ("aiosqlite", "AioSQLite数据库"),
        ("apscheduler", "APScheduler任务调度"),
        ("requests", "Requests HTTP库"),
        ("sqlite3", "SQLite数据库"),
        ("asyncio", "异步IO"),
        ("json", "JSON处理"),
        ("datetime", "日期时间"),
        ("logging", "日志"),
        ("os", "操作系统"),
        ("sys", "系统"),
    ]
    
    failed_count = 0
    
    for module_name, description in modules_to_test:
        if not test_import(module_name, description):
            failed_count += 1
    
    print(f"\n{'='*60}")
    print("🧪 测试项目相关模块")
    print(f"{'='*60}")
    
    # 测试项目模块
    project_modules = [
        ("config", "项目配置"),
        ("models", "数据模型"),
        ("database", "数据库模块"),
        ("location_service", "地理位置服务"),
        ("proxy_fetcher", "代理获取"),
        ("proxy_validator", "代理验证"),
        ("scheduler", "任务调度"),
        ("api", "API接口"),
    ]
    
    for module_name, description in project_modules:
        if not test_import(module_name, description):
            failed_count += 1
    
    print(f"\n{'='*60}")
    if failed_count == 0:
        print("🎉 所有模块导入成功！")
        print("现在可以启动系统了: python main.py")
    else:
        print(f"❌ {failed_count} 个模块导入失败")
        print("请运行修复脚本: python fix_dependencies.py")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 
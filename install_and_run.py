#!/usr/bin/env python3
"""
代理池系统安装和启动脚本
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"🔧 命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print(f"✅ 输出:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️  错误信息:\n{result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {description} 完成")
            return True
        else:
            print(f"❌ {description} 失败 (返回码: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装依赖包...")
    
    # 升级pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip")
    
    # 安装项目依赖
    if run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装项目依赖"):
        print("✅ 所有依赖安装完成")
        return True
    else:
        print("❌ 依赖安装失败")
        return False

def test_imports():
    """测试关键模块导入"""
    print("\n🧪 测试关键模块...")
    
    modules = [
        ('fastapi', 'FastAPI框架'),
        ('uvicorn', 'ASGI服务器'),
        ('aiohttp', 'HTTP客户端'),
        ('aiosqlite', 'SQLite异步库'),
        ('apscheduler', '任务调度器'),
        ('pydantic', '数据验证'),
    ]
    
    failed_modules = []
    
    for module, desc in modules:
        try:
            __import__(module)
            print(f"✅ {desc} ({module})")
        except ImportError as e:
            print(f"❌ {desc} ({module}): {e}")
            failed_modules.append(module)
    
    # 测试ipdb（可选）
    try:
        import ipdb
        print("✅ IPDB地理位置库 (ipdb) - 将使用精确的IP地理位置查询")
    except ImportError:
        print("⚠️  IPDB地理位置库 (ipdb) - 将使用内置IP段映射（功能正常）")
    
    if failed_modules:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed_modules)}")
        return False
    
    print("\n✅ 所有关键模块测试通过")
    return True

def start_system():
    """启动系统"""
    print("\n🚀 启动代理池系统...")
    print("💡 按 Ctrl+C 停止服务")
    print("🌐 服务将在 http://localhost:8000 启动")
    
    try:
        # 启动系统
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 启动失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 启动异常: {e}")
        return False
    
    return True

def show_quick_start():
    """显示快速开始指南"""
    print(f"""
{'='*60}
🎉 安装完成！快速开始指南
{'='*60}

🌐 访问地址:
   主页:     http://localhost:8000
   API文档:  http://localhost:8000/docs
   健康检查: http://localhost:8000/api/health

📝 常用API:
   获取代理: GET  /api/proxies
   添加代理: POST /api/proxies
   统计信息: GET  /api/statistics
   手动更新: POST /api/update

💡 使用示例:
   # Windows PowerShell
   Invoke-RestMethod -Uri "http://localhost:8000/api/health"
   
   # Linux/Mac curl
   curl http://localhost:8000/api/health

📚 更多信息请查看 README.md

""")

def main():
    """主函数"""
    print("""
{'='*60}
🚀 代理池管理系统 - 安装和启动脚本
{'='*60}
功能特性:
  ✅ 支持 HTTP/HTTPS/SOCKS5/SOCKS4 代理
  ✅ 自动获取和验证代理
  ✅ 地理位置信息补充 (支持IPDB精确查询)
  ✅ RESTful API 接口
  ✅ 定时任务调度
  ✅ Web 管理界面
{'='*60}
""")
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查是否在正确目录
    if not os.path.exists("main.py"):
        print("❌ 请在项目根目录运行此脚本")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请检查网络连接")
        return
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块测试失败，请检查安装")
        return
    
    # 显示快速开始
    show_quick_start()
    
    # 询问是否启动
    try:
        choice = input("是否现在启动系统? (y/N): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            start_system()
        else:
            print(f"""
✅ 安装完成！

手动启动命令:
   python main.py

或使用快速启动:
   python start.py
""")
    except KeyboardInterrupt:
        print("\n👋 安装完成，您可以稍后手动启动系统")

if __name__ == "__main__":
    main() 
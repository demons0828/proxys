#!/usr/bin/env python3
"""
依赖修复脚本 - 解决pydantic版本兼容性问题
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """运行命令"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print(f"✅ 输出:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️  错误信息:\n{result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def fix_pydantic_issues():
    """修复pydantic相关问题"""
    
    print("🔧 正在修复pydantic依赖问题...")
    
    # 1. 卸载可能冲突的包
    print("\n步骤1: 卸载可能冲突的包")
    packages_to_remove = [
        'pydantic',
        'pydantic-settings', 
        'fastapi',
        'uvicorn'
    ]
    
    for package in packages_to_remove:
        run_command(f"{sys.executable} -m pip uninstall {package} -y", f"卸载 {package}")
    
    # 2. 清理pip缓存
    print("\n步骤2: 清理pip缓存")
    run_command(f"{sys.executable} -m pip cache purge", "清理pip缓存")
    
    # 3. 升级pip
    print("\n步骤3: 升级pip")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip")
    
    # 4. 安装兼容的版本
    print("\n步骤4: 安装兼容的依赖包")
    compatible_packages = [
        "typing-extensions>=4.8.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    
    for package in compatible_packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"安装 {package}"):
            print(f"❌ 安装 {package} 失败")
            return False
    
    # 5. 安装其他依赖
    print("\n步骤5: 安装其他依赖")
    run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装所有依赖")
    
    return True

def test_imports():
    """测试关键模块导入"""
    print("\n🧪 测试关键模块导入...")
    
    modules_to_test = [
        ('pydantic', 'Pydantic数据验证'),
        ('pydantic_settings', 'Pydantic设置'),
        ('fastapi', 'FastAPI框架'),
        ('uvicorn', 'Uvicorn服务器'),
        ('aiohttp', 'AioHTTP客户端'),
        ('aiosqlite', 'AioSQLite数据库'),
        ('apscheduler', 'APScheduler任务调度')
    ]
    
    failed_modules = []
    
    for module_name, description in modules_to_test:
        try:
            if module_name == 'pydantic_settings':
                from pydantic_settings import BaseSettings
                print(f"✅ {description}")
            else:
                __import__(module_name)
                print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            failed_modules.append(module_name)
    
    if failed_modules:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed_modules)}")
        return False
    
    print("\n✅ 所有模块导入成功")
    return True

def test_config_import():
    """测试配置模块导入"""
    print("\n🧪 测试配置模块...")
    
    try:
        # 测试我们的config模块
        import config
        print("✅ 配置模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("""
{'='*60}
🔧 代理池系统 - 依赖修复脚本
{'='*60}
这个脚本将修复pydantic版本兼容性问题
{'='*60}
""")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt文件不存在")
        return
    
    # 修复pydantic问题
    if not fix_pydantic_issues():
        print("❌ 依赖修复失败")
        return
    
    # 测试模块导入
    if not test_imports():
        print("❌ 模块测试失败")
        return
    
    # 测试配置导入
    if not test_config_import():
        print("❌ 配置测试失败")
        return
    
    print(f"""
{'='*60}
🎉 依赖修复完成！
{'='*60}

现在可以启动系统了:
  python main.py

或使用快速启动:
  python start.py
""")

if __name__ == "__main__":
    main() 
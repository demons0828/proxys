#!/usr/bin/env python3
"""
代理池管理系统主程序
"""

import logging
import asyncio
import uvicorn
from pathlib import Path

from api import app
from config import settings

# 配置日志
def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO)

async def main():
    """主程序入口"""
    print("=" * 60)
    print("代理池管理系统")
    print("=" * 60)
    print(f"配置文件: {settings}")
    print(f"日志文件: {settings.LOG_FILE}")
    print(f"数据库: {settings.DATABASE_URL}")
    print(f"更新间隔: {settings.UPDATE_INTERVAL}秒")
    print(f"验证间隔: {settings.VALIDATION_INTERVAL}秒")
    print("=" * 60)
    
    # 配置日志
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("代理池管理系统启动")
    
    # 启动Web服务器
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0", 
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务运行异常: {e}")
    finally:
        logger.info("代理池管理系统已关闭")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc() 
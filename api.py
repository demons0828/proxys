from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Optional, List
import logging

from models import (
    ProxyInfo, ProxyCreateRequest, ProxyQueryParams, ProxyUpdateRequest,
    ProxyStatistics, APIResponse, ProxyProtocol, ProxyStatus
)
from database import db_manager
from proxy_validator import proxy_validator
from scheduler import task_scheduler
from config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="代理池管理系统",
    description="高性能代理池管理系统，支持HTTP/HTTPS/SOCKS5/SOCKS4代理",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    return """
    <html>
        <head>
            <title>代理池管理系统</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .method { font-weight: bold; color: #007bff; }
                .path { font-family: monospace; background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
                .description { color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>代理池管理系统 API</h1>
                <p>欢迎使用代理池管理系统！以下是可用的API接口：</p>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="path">/api/proxies</span></div>
                    <div class="description">获取代理列表，支持按协议、国家、速度筛选</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="path">/api/proxies/{proxy_id}</span></div>
                    <div class="description">获取指定代理详情</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">POST</span> <span class="path">/api/proxies</span></div>
                    <div class="description">添加新代理</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="path">/api/statistics</span></div>
                    <div class="description">获取代理统计信息</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">POST</span> <span class="path">/api/update</span></div>
                    <div class="description">手动触发更新任务</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="path">/api/health</span></div>
                    <div class="description">健康检查</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="path">/docs</span></div>
                    <div class="description">查看详细的API文档</div>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "代理池服务运行正常"}

@app.get("/api/proxies", response_model=List[ProxyInfo])
async def get_proxies(
    protocol: Optional[ProxyProtocol] = Query(None, description="代理协议"),
    country: Optional[str] = Query(None, description="国家筛选"),
    min_speed: Optional[float] = Query(None, description="最小速度要求(ms)"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量限制"),
    status: Optional[ProxyStatus] = Query(None, description="代理状态")
):
    """获取代理列表"""
    try:
        # 转换参数
        protocol_str = protocol.value if protocol else None
        status_str = status.value if status else None
        
        proxies = await db_manager.get_proxies(
            protocol=protocol_str,
            status=status_str,
            country=country,
            min_speed=min_speed,
            limit=limit
        )
        
        return proxies
        
    except Exception as e:
        logger.error(f"获取代理列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取代理列表失败")

@app.get("/api/proxies/{proxy_id}", response_model=ProxyInfo)
async def get_proxy_by_id(proxy_id: int):
    """获取指定代理详情"""
    try:
        proxy = await db_manager.get_proxy_by_id(proxy_id)
        if not proxy:
            raise HTTPException(status_code=404, detail="代理不存在")
        
        return proxy
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取代理详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取代理详情失败")

@app.post("/api/proxies", response_model=APIResponse)
async def create_proxy(proxy_request: ProxyCreateRequest):
    """添加新代理"""
    try:
        # 创建代理对象
        proxy = ProxyInfo(
            protocol=proxy_request.protocol,
            host=proxy_request.host,
            port=proxy_request.port,
            username=proxy_request.username,
            password=proxy_request.password,
            status=ProxyStatus.ACTIVE
        )
        
        # 保存到数据库
        proxy_id = await db_manager.save_proxy(proxy)
        
        return APIResponse(
            success=True,
            message="代理添加成功",
            data={"proxy_id": proxy_id}
        )
        
    except Exception as e:
        logger.error(f"添加代理失败: {e}")
        raise HTTPException(status_code=500, detail="添加代理失败")

@app.delete("/api/proxies/{proxy_id}", response_model=APIResponse)
async def delete_proxy(proxy_id: int):
    """删除代理"""
    try:
        # 检查代理是否存在
        proxy = await db_manager.get_proxy_by_id(proxy_id)
        if not proxy:
            raise HTTPException(status_code=404, detail="代理不存在")
        
        # 删除代理
        success = await db_manager.delete_proxy(proxy_id)
        
        if success:
            return APIResponse(
                success=True,
                message="代理删除成功"
            )
        else:
            raise HTTPException(status_code=500, detail="代理删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除代理失败: {e}")
        raise HTTPException(status_code=500, detail="删除代理失败")

@app.post("/api/proxies/{proxy_id}/validate", response_model=APIResponse)
async def validate_proxy(proxy_id: int, target_url: Optional[str] = None):
    """验证指定代理"""
    try:
        # 获取代理
        proxy = await db_manager.get_proxy_by_id(proxy_id)
        if not proxy:
            raise HTTPException(status_code=404, detail="代理不存在")
        
        # 验证代理
        async with proxy_validator as validator:
            test_result = await validator.validate_proxy(proxy, target_url)
        
        # 更新代理状态
        status = 'active' if test_result.success else 'inactive'
        await db_manager.update_proxy_status(
            proxy_id,
            response_time=test_result.response_time,
            status=status
        )
        
        # 保存测试记录
        await db_manager.save_test_record(test_result)
        
        return APIResponse(
            success=True,
            message="代理验证完成",
            data={
                "proxy_id": proxy_id,
                "success": test_result.success,
                "response_time": test_result.response_time,
                "error_message": test_result.error_message
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证代理失败: {e}")
        raise HTTPException(status_code=500, detail="验证代理失败")

@app.get("/api/statistics", response_model=ProxyStatistics)
async def get_proxy_statistics():
    """获取代理统计信息"""
    try:
        stats = await db_manager.get_proxy_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")

@app.post("/api/update", response_model=APIResponse)
async def manual_update(
    update_request: ProxyUpdateRequest, 
    background_tasks: BackgroundTasks
):
    """手动触发更新任务"""
    try:
        action = update_request.action
        
        if action == "fetch_new":
            background_tasks.add_task(task_scheduler.manual_fetch_proxies)
            message = "开始获取新代理"
        elif action == "validate_existing":
            background_tasks.add_task(task_scheduler.manual_validate_proxies)
            message = "开始验证现有代理"
        elif action == "update_location":
            background_tasks.add_task(task_scheduler.manual_update_locations)
            message = "开始更新地理位置"
        else:
            raise HTTPException(status_code=400, detail="无效的更新操作")
        
        return APIResponse(
            success=True,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手动更新失败: {e}")
        raise HTTPException(status_code=500, detail="手动更新失败")

@app.get("/api/tasks", response_model=dict)
async def get_task_status():
    """获取任务状态"""
    try:
        task_status = task_scheduler.get_job_status()
        return task_status
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取任务状态失败")

@app.post("/api/tasks/{task_id}/reschedule", response_model=APIResponse)
async def reschedule_task(task_id: str, interval_seconds: int):
    """重新调度任务"""
    try:
        await task_scheduler.reschedule_job(task_id, interval_seconds)
        
        return APIResponse(
            success=True,
            message=f"任务 {task_id} 重新调度成功"
        )
        
    except Exception as e:
        logger.error(f"重新调度任务失败: {e}")
        raise HTTPException(status_code=500, detail="重新调度任务失败")

@app.get("/api/proxies/random", response_model=ProxyInfo)
async def get_random_proxy(
    protocol: Optional[ProxyProtocol] = Query(None, description="代理协议"),
    country: Optional[str] = Query(None, description="国家筛选")
):
    """获取随机代理"""
    try:
        # 转换参数
        protocol_str = protocol.value if protocol else None
        
        proxies = await db_manager.get_proxies(
            protocol=protocol_str,
            status='active',
            country=country,
            limit=10
        )
        
        if not proxies:
            raise HTTPException(status_code=404, detail="没有可用的代理")
        
        # 返回第一个代理（已按响应时间排序）
        return proxies[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取随机代理失败: {e}")
        raise HTTPException(status_code=500, detail="获取随机代理失败")

@app.get("/api/proxies/countries", response_model=List[str])
async def get_available_countries():
    """获取可用国家列表"""
    try:
        stats = await db_manager.get_proxy_statistics()
        countries = list(stats.countries.keys())
        return countries
        
    except Exception as e:
        logger.error(f"获取国家列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取国家列表失败")

@app.post("/api/proxies/batch-validate", response_model=APIResponse)
async def batch_validate_proxies(
    proxy_ids: List[int],
    background_tasks: BackgroundTasks,
    target_url: Optional[str] = None
):
    """批量验证代理"""
    try:
        if len(proxy_ids) > 100:
            raise HTTPException(status_code=400, detail="批量验证代理数量不能超过100个")
        
        # 添加后台任务
        background_tasks.add_task(
            task_scheduler.manual_validate_proxies,
            proxy_ids
        )
        
        return APIResponse(
            success=True,
            message=f"开始批量验证 {len(proxy_ids)} 个代理"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量验证代理失败: {e}")
        raise HTTPException(status_code=500, detail="批量验证代理失败")

# 错误处理
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "资源不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"服务器内部错误: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误"}
    )

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("代理池服务启动中...")
    
    # 初始化数据库
    await db_manager.init_database()
    
    # 启动任务调度器
    await task_scheduler.start()
    
    logger.info("代理池服务启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("代理池服务关闭中...")
    
    # 停止任务调度器
    await task_scheduler.stop()
    
    logger.info("代理池服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
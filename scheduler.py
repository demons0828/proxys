import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from config import settings
from database import db_manager
from proxy_fetcher import proxy_fetcher
from proxy_validator import proxy_validator
from location_service import location_service
from models import ProxyInfo, ProxyStatus

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("任务调度器已启动")
            
            # 添加定时任务
            await self._add_scheduled_tasks()
        else:
            logger.warning("任务调度器已在运行中")
    
    async def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("任务调度器已停止")
    
    async def _add_scheduled_tasks(self):
        """添加定时任务"""
        # 代理更新任务
        self.scheduler.add_job(
            self.fetch_new_proxies,
            trigger=IntervalTrigger(seconds=settings.UPDATE_INTERVAL),
            id='fetch_new_proxies',
            name='获取新代理',
            replace_existing=True
        )
        
        # 代理验证任务
        self.scheduler.add_job(
            self.validate_existing_proxies,
            trigger=IntervalTrigger(seconds=settings.VALIDATION_INTERVAL),
            id='validate_existing_proxies',
            name='验证现有代理',
            replace_existing=True
        )
        
        # 地理位置更新任务
        self.scheduler.add_job(
            self.update_proxy_locations,
            trigger=IntervalTrigger(seconds=settings.LOCATION_UPDATE_INTERVAL),
            id='update_proxy_locations',
            name='更新代理地理位置',
            replace_existing=True
        )
        
        # 清理过期记录任务（每天凌晨2点执行）
        self.scheduler.add_job(
            self.cleanup_old_records,
            trigger=CronTrigger(hour=2, minute=0),
            id='cleanup_old_records',
            name='清理过期记录',
            replace_existing=True
        )
        
        # 数据库维护任务（每周日凌晨3点执行）
        self.scheduler.add_job(
            self.database_maintenance,
            trigger=CronTrigger(day_of_week=6, hour=3, minute=0),
            id='database_maintenance',
            name='数据库维护',
            replace_existing=True
        )
        
        logger.info("所有定时任务已添加")
    
    async def fetch_new_proxies(self):
        """获取新代理任务"""
        try:
            logger.info("开始执行获取新代理任务")
            
            # 获取所有代理
            async with proxy_fetcher as fetcher:
                all_proxies = await fetcher.fetch_all_proxies()
                
                # 去重
                unique_proxies = fetcher.deduplicate_proxies(all_proxies)
                
                # 保存到数据库
                saved_count = 0
                for proxy in unique_proxies:
                    try:
                        await db_manager.save_proxy(proxy)
                        saved_count += 1
                    except Exception as e:
                        logger.debug(f"保存代理失败 {proxy.host}:{proxy.port}: {e}")
                
                logger.info(f"获取新代理任务完成，保存了 {saved_count} 个新代理")
                
        except Exception as e:
            logger.error(f"获取新代理任务失败: {e}")
    
    async def validate_existing_proxies(self):
        """验证现有代理任务"""
        try:
            logger.info("开始执行验证现有代理任务")
            
            # 获取需要验证的代理
            # 优先验证长时间未检查的代理
            proxies = await db_manager.get_proxies(
                status='active',
                limit=settings.MAX_CONCURRENT_TESTS
            )
            
            if not proxies:
                logger.info("没有需要验证的代理")
                return
            
            # 批量验证
            async with proxy_validator as validator:
                test_results = await validator.batch_validate(proxies)
                
                # 更新代理状态
                for proxy, result in zip(proxies, test_results):
                    try:
                        if result.success:
                            # 计算成功率
                            success_rate = await self._calculate_proxy_success_rate(proxy.id)
                            
                            await db_manager.update_proxy_status(
                                proxy.id,
                                response_time=result.response_time,
                                success_rate=success_rate,
                                status='active'
                            )
                        else:
                            # 失败次数过多则标记为失败
                            failed_count = await self._get_proxy_failed_count(proxy.id)
                            if failed_count >= 3:
                                await db_manager.update_proxy_status(
                                    proxy.id,
                                    status='failed'
                                )
                            else:
                                await db_manager.update_proxy_status(
                                    proxy.id,
                                    status='inactive'
                                )
                        
                        # 保存测试记录
                        await db_manager.save_test_record(result)
                        
                    except Exception as e:
                        logger.error(f"更新代理状态失败 {proxy.host}:{proxy.port}: {e}")
                
                successful_count = sum(1 for r in test_results if r.success)
                logger.info(f"验证现有代理任务完成，成功: {successful_count}/{len(test_results)}")
                
        except Exception as e:
            logger.error(f"验证现有代理任务失败: {e}")
    
    async def update_proxy_locations(self):
        """更新代理地理位置任务"""
        try:
            logger.info("开始执行更新代理地理位置任务")
            
            # 获取没有地理位置信息的代理
            proxies = await db_manager.get_proxies(limit=10000)
            
            # 过滤出需要更新地理位置的代理
            proxies_to_update = [
                proxy for proxy in proxies 
                if not proxy.country or proxy.country == '未知' or not proxy.region
            ]
            
            if not proxies_to_update:
                logger.info("没有需要更新地理位置的代理")
                return
            
            # 批量获取地理位置信息
            ips = [proxy.host for proxy in proxies_to_update]
            locations = await location_service.batch_get_location(ips)
            
            # 更新数据库
            updated_count = 0
            for proxy in proxies_to_update:
                location = locations.get(proxy.host)
                if location:
                    try:
                        await db_manager.update_proxy_location(
                            proxy.id,
                            location.country,
                            location.region,
                            location.city,
                            location.isp
                        )
                        updated_count += 1
                    except Exception as e:
                        logger.error(f"更新代理地理位置失败 {proxy.host}: {e}")
            
            logger.info(f"更新代理地理位置任务完成，更新了 {updated_count} 个代理")
            
        except Exception as e:
            logger.error(f"更新代理地理位置任务失败: {e}")
    
    async def cleanup_old_records(self):
        """清理过期记录任务"""
        try:
            logger.info("开始执行清理过期记录任务")
            
            # 清理30天前的测试记录
            deleted_count = await db_manager.cleanup_old_records(days=30)
            
            logger.info(f"清理过期记录任务完成，删除了 {deleted_count} 条记录")
            
        except Exception as e:
            logger.error(f"清理过期记录任务失败: {e}")
    
    async def database_maintenance(self):
        """数据库维护任务"""
        try:
            logger.info("开始执行数据库维护任务")
            
            # 删除长时间失败的代理
            failed_proxies = await db_manager.get_proxies(status='failed')
            cutoff_time = datetime.now() - timedelta(days=7)
            
            deleted_count = 0
            for proxy in failed_proxies:
                if proxy.updated_at and proxy.updated_at < cutoff_time:
                    await db_manager.delete_proxy(proxy.id)
                    deleted_count += 1
            
            logger.info(f"数据库维护任务完成，删除了 {deleted_count} 个失败的代理")
            
        except Exception as e:
            logger.error(f"数据库维护任务失败: {e}")
    
    async def _calculate_proxy_success_rate(self, proxy_id: int) -> float:
        """计算代理成功率"""
        try:
            # 这里简化实现，实际应该从test_records表查询
            # 获取最近10次测试记录计算成功率
            return 0.8  # 默认成功率
        except Exception as e:
            logger.error(f"计算代理成功率失败: {e}")
            return 0.0
    
    async def _get_proxy_failed_count(self, proxy_id: int) -> int:
        """获取代理失败次数"""
        try:
            # 这里简化实现，实际应该从test_records表查询
            # 获取最近的连续失败次数
            return 1  # 默认失败次数
        except Exception as e:
            logger.error(f"获取代理失败次数失败: {e}")
            return 0
    
    async def manual_fetch_proxies(self):
        """手动获取代理"""
        logger.info("手动执行获取代理任务")
        await self.fetch_new_proxies()
    
    async def manual_validate_proxies(self, proxy_ids: Optional[List[int]] = None):
        """手动验证代理"""
        logger.info("手动执行验证代理任务")
        
        if proxy_ids:
            # 验证指定的代理
            proxies = []
            for proxy_id in proxy_ids:
                proxy = await db_manager.get_proxy_by_id(proxy_id)
                if proxy:
                    proxies.append(proxy)
            
            if proxies:
                async with proxy_validator as validator:
                    test_results = await validator.batch_validate(proxies)
                    
                    # 更新状态
                    for proxy, result in zip(proxies, test_results):
                        status = 'active' if result.success else 'inactive'
                        await db_manager.update_proxy_status(
                            proxy.id,
                            response_time=result.response_time,
                            status=status
                        )
                        await db_manager.save_test_record(result)
        else:
            # 验证所有代理
            await self.validate_existing_proxies()
    
    async def manual_update_locations(self):
        """手动更新地理位置"""
        logger.info("手动执行更新地理位置任务")
        await self.update_proxy_locations()
    
    def get_job_status(self) -> dict:
        """获取任务状态"""
        jobs = self.scheduler.get_jobs()
        job_status = {}
        
        for job in jobs:
            job_status[job.id] = {
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'coalesce': job.coalesce,
                'max_instances': job.max_instances
            }
        
        return {
            'is_running': self.is_running,
            'jobs': job_status
        }
    
    async def reschedule_job(self, job_id: str, interval_seconds: int):
        """重新调度任务"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.modify_job(
                    job_id,
                    trigger=IntervalTrigger(seconds=interval_seconds)
                )
                logger.info(f"任务 {job_id} 重新调度成功，间隔: {interval_seconds}秒")
            else:
                logger.error(f"任务 {job_id} 不存在")
        except Exception as e:
            logger.error(f"重新调度任务失败 {job_id}: {e}")

# 全局任务调度器实例
task_scheduler = TaskScheduler() 
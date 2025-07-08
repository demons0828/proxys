import aiosqlite
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import ProxyInfo, TestResult, ProxyStatus, ProxyProtocol, ProxyStatistics
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "proxy_pool.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """初始化数据库表"""
        async with aiosqlite.connect(self.db_path) as db:
            # 创建代理表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol TEXT NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT,
                    password TEXT,
                    country TEXT,
                    region TEXT,
                    city TEXT,
                    isp TEXT,
                    response_time REAL,
                    success_rate REAL,
                    last_check TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(protocol, host, port)
                )
            """)
            
            # 创建测试记录表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy_id INTEGER,
                    target_url TEXT,
                    response_time REAL,
                    status_code INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proxy_id) REFERENCES proxies (id)
                )
            """)
            
            # 创建索引
            await db.execute("CREATE INDEX IF NOT EXISTS idx_proxies_protocol ON proxies(protocol)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_proxies_status ON proxies(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_proxies_country ON proxies(country)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_test_records_proxy_id ON test_records(proxy_id)")
            
            await db.commit()
            logger.info("数据库初始化完成")
    
    async def save_proxy(self, proxy: ProxyInfo) -> int:
        """保存代理信息"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                cursor = await db.execute("""
                    INSERT OR REPLACE INTO proxies 
                    (protocol, host, port, username, password, country, region, city, isp, 
                     response_time, success_rate, last_check, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    proxy.protocol.value,
                    proxy.host,
                    proxy.port,
                    proxy.username,
                    proxy.password,
                    proxy.country,
                    proxy.region,
                    proxy.city,
                    proxy.isp,
                    proxy.response_time,
                    proxy.success_rate,
                    proxy.last_check,
                    proxy.status.value,
                    datetime.now()
                ))
                await db.commit()
                return cursor.lastrowid
            except Exception as e:
                logger.error(f"保存代理失败: {e}")
                raise
    
    async def get_proxies(self, protocol: Optional[str] = None, 
                         status: Optional[str] = None,
                         country: Optional[str] = None,
                         min_speed: Optional[float] = None,
                         limit: int = 50) -> List[ProxyInfo]:
        """获取代理列表"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM proxies WHERE 1=1"
            params = []
            
            if protocol:
                query += " AND protocol = ?"
                params.append(protocol)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if country:
                query += " AND country = ?"
                params.append(country)
            
            if min_speed:
                query += " AND response_time <= ?"
                params.append(min_speed)
            
            query += " ORDER BY response_time ASC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            proxies = []
            for row in rows:
                proxy = ProxyInfo(
                    id=row['id'],
                    protocol=ProxyProtocol(row['protocol']),
                    host=row['host'],
                    port=row['port'],
                    username=row['username'],
                    password=row['password'],
                    country=row['country'],
                    region=row['region'],
                    city=row['city'],
                    isp=row['isp'],
                    response_time=row['response_time'],
                    success_rate=row['success_rate'],
                    last_check=row['last_check'],
                    status=ProxyStatus(row['status']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                proxies.append(proxy)
            
            return proxies
    
    async def get_proxy_by_id(self, proxy_id: int) -> Optional[ProxyInfo]:
        """根据ID获取代理"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM proxies WHERE id = ?", (proxy_id,))
            row = await cursor.fetchone()
            
            if row:
                return ProxyInfo(
                    id=row['id'],
                    protocol=ProxyProtocol(row['protocol']),
                    host=row['host'],
                    port=row['port'],
                    username=row['username'],
                    password=row['password'],
                    country=row['country'],
                    region=row['region'],
                    city=row['city'],
                    isp=row['isp'],
                    response_time=row['response_time'],
                    success_rate=row['success_rate'],
                    last_check=row['last_check'],
                    status=ProxyStatus(row['status']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
    
    async def update_proxy_status(self, proxy_id: int, response_time: Optional[float] = None,
                                 success_rate: Optional[float] = None, 
                                 status: Optional[str] = None) -> bool:
        """更新代理状态"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                updates = []
                params = []
                
                if response_time is not None:
                    updates.append("response_time = ?")
                    params.append(response_time)
                
                if success_rate is not None:
                    updates.append("success_rate = ?")
                    params.append(success_rate)
                
                if status is not None:
                    updates.append("status = ?")
                    params.append(status)
                
                updates.append("last_check = ?")
                params.append(datetime.now())
                
                updates.append("updated_at = ?")
                params.append(datetime.now())
                
                params.append(proxy_id)
                
                query = f"UPDATE proxies SET {', '.join(updates)} WHERE id = ?"
                await db.execute(query, params)
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"更新代理状态失败: {e}")
                return False
    
    async def update_proxy_location(self, proxy_id: int, country: str, region: str, 
                                   city: str, isp: str) -> bool:
        """更新代理地理位置信息"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    UPDATE proxies 
                    SET country = ?, region = ?, city = ?, isp = ?, updated_at = ?
                    WHERE id = ?
                """, (country, region, city, isp, datetime.now(), proxy_id))
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"更新代理地理位置失败: {e}")
                return False
    
    async def save_test_record(self, test_result: TestResult) -> bool:
        """保存测试记录"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO test_records 
                    (proxy_id, target_url, response_time, status_code, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    test_result.proxy_id,
                    test_result.target_url,
                    test_result.response_time,
                    test_result.status_code,
                    test_result.success,
                    test_result.error_message
                ))
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"保存测试记录失败: {e}")
                return False
    
    async def get_proxy_statistics(self) -> ProxyStatistics:
        """获取代理统计信息"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 总体统计
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive,
                    SUM(CASE WHEN status = 'testing' THEN 1 ELSE 0 END) as testing,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(response_time) as avg_response_time,
                    AVG(success_rate) as avg_success_rate
                FROM proxies
            """)
            stats = await cursor.fetchone()
            
            # 按协议统计
            cursor = await db.execute("""
                SELECT protocol, COUNT(*) as count
                FROM proxies
                GROUP BY protocol
            """)
            protocols = {row['protocol']: row['count'] for row in await cursor.fetchall()}
            
            # 按国家统计
            cursor = await db.execute("""
                SELECT country, COUNT(*) as count
                FROM proxies
                WHERE country IS NOT NULL
                GROUP BY country
                ORDER BY count DESC
                LIMIT 10
            """)
            countries = {row['country']: row['count'] for row in await cursor.fetchall()}
            
            return ProxyStatistics(
                total_proxies=stats['total'],
                active_proxies=stats['active'],
                inactive_proxies=stats['inactive'],
                testing_proxies=stats['testing'],
                failed_proxies=stats['failed'],
                avg_response_time=stats['avg_response_time'],
                success_rate=stats['avg_success_rate'],
                protocols=protocols,
                countries=countries
            )
    
    async def delete_proxy(self, proxy_id: int) -> bool:
        """删除代理"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("DELETE FROM proxies WHERE id = ?", (proxy_id,))
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"删除代理失败: {e}")
                return False
    
    async def cleanup_old_records(self, days: int = 30) -> int:
        """清理旧的测试记录"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                cursor = await db.execute("""
                    DELETE FROM test_records 
                    WHERE tested_at < datetime('now', '-{} days')
                """.format(days))
                await db.commit()
                return cursor.rowcount
            except Exception as e:
                logger.error(f"清理旧记录失败: {e}")
                return 0

# 全局数据库管理器实例
db_manager = DatabaseManager() 
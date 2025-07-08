from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///proxy_pool.db"
    
    # 更新间隔配置（秒）
    UPDATE_INTERVAL: int = 3600  # 1小时
    VALIDATION_INTERVAL: int = 1800  # 30分钟
    LOCATION_UPDATE_INTERVAL: int = 7200  # 2小时
    
    # 测试配置
    MAX_CONCURRENT_TESTS: int = 10000
    REQUEST_TIMEOUT: int = 10
    DEFAULT_TEST_URL: str = "http://httpbin.org/ip"
    
    # 代理源配置
    PROXY_SOURCES: dict = {
        "http": "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/http.txt",
        "https": "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/https.txt",
        "socks5": "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list/socks5.txt",
        "all" : "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt"
    }
    
    # IP地理位置数据库
    QQWRY_IPDB_URL: str = "https://raw.gitmirror.com/nmgliangwei/qqwry.ipdb/main/qqwry.ipdb"
    QQWRY_IPDB_PATH: str = "qqwry.ipdb"
    
    # API配置
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "proxy_pool.log"
    
    class Config:
        env_file = ".env"

# 全局配置实例
settings = Settings() 
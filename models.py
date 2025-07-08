from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProxyProtocol(str, Enum):
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SOCKS5 = "SOCKS5"
    SOCKS4 = "SOCKS4"

class ProxyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    FAILED = "failed"

class ProxyInfo(BaseModel):
    id: Optional[int] = None
    protocol: ProxyProtocol
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    response_time: Optional[float] = None
    success_rate: Optional[float] = None
    last_check: Optional[datetime] = None
    status: ProxyStatus = ProxyStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LocationInfo(BaseModel):
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    isp: Optional[str] = None
    country_code: Optional[str] = None
    continent_code: Optional[str] = None

class TestResult(BaseModel):
    proxy_id: int
    target_url: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    tested_at: datetime = Field(default_factory=datetime.now)

class ProxyCreateRequest(BaseModel):
    protocol: ProxyProtocol
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

class ProxyQueryParams(BaseModel):
    protocol: Optional[ProxyProtocol] = None
    country: Optional[str] = None
    min_speed: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=1000)
    status: Optional[ProxyStatus] = None

class ProxyUpdateRequest(BaseModel):
    action: str = Field(..., pattern="^(fetch_new|validate_existing|update_location)$")

class ProxyStatistics(BaseModel):
    total_proxies: int
    active_proxies: int
    inactive_proxies: int
    testing_proxies: int
    failed_proxies: int
    avg_response_time: Optional[float] = None
    success_rate: Optional[float] = None
    protocols: dict
    countries: dict

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    count: Optional[int] = None 
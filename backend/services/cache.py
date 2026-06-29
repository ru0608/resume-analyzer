"""Redis 缓存服务模块

对已解析和评分的简历进行缓存，避免重复计算。
使用 Redis 实现，当 Redis 不可用时降级为内存缓存。
"""
import json
import time
from typing import Optional, Any
from config import settings


class CacheService:
    """缓存服务，优先使用 Redis，不可用时使用内存缓存"""

    def __init__(self):
        self._redis = None
        self._redis_available = False
        self._memory_cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expire_time)
        self._init_redis()

    def _init_redis(self):
        """尝试初始化 Redis 连接"""
        if not settings.redis_host:
            print("[Cache] Redis 未配置，使用内存缓存")
            return

        try:
            import redis
            self._redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis.ping()
            self._redis_available = True
            print(f"[Cache] Redis 连接成功: {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            print(f"[Cache] Redis 连接失败 ({e})，降级至内存缓存")
            self._redis = None
            self._redis_available = False

    def _make_key(self, prefix: str, identifier: str) -> str:
        """生成缓存键"""
        return f"resume:{prefix}:{identifier}"

    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """获取缓存

        Args:
            prefix: 缓存前缀（如 parse, match）
            identifier: 标识符（如 resume_id）

        Returns:
            缓存的数据，不存在时返回 None
        """
        key = self._make_key(prefix, identifier)

        if self._redis_available:
            try:
                data = self._redis.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                print(f"[Cache] Redis 读取失败: {e}")
                return None
        else:
            # 内存缓存
            if key in self._memory_cache:
                value, expire = self._memory_cache[key]
                if expire > time.time():
                    return value
                else:
                    del self._memory_cache[key]
            return None

    async def set(
        self, prefix: str, identifier: str, value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """设置缓存

        Args:
            prefix: 缓存前缀
            identifier: 标识符
            value: 要缓存的数据
            ttl: 过期时间（秒），默认使用配置值

        Returns:
            是否成功
        """
        key = self._make_key(prefix, identifier)
        expire = ttl or settings.cache_ttl

        if self._redis_available:
            try:
                serialized = json.dumps(value, ensure_ascii=False, default=str)
                return bool(self._redis.setex(key, expire, serialized))
            except Exception as e:
                print(f"[Cache] Redis 写入失败: {e}")
                return False
        else:
            self._memory_cache[key] = (value, time.time() + expire)
            return True

    async def delete(self, prefix: str, identifier: str) -> bool:
        """删除缓存"""
        key = self._make_key(prefix, identifier)

        if self._redis_available:
            try:
                return bool(self._redis.delete(key))
            except Exception:
                return False
        else:
            return self._memory_cache.pop(key, None) is not None

    async def exists(self, prefix: str, identifier: str) -> bool:
        """检查缓存是否存在"""
        key = self._make_key(prefix, identifier)

        if self._redis_available:
            try:
                return bool(self._redis.exists(key))
            except Exception:
                return False
        else:
            if key in self._memory_cache:
                value, expire = self._memory_cache[key]
                if expire > time.time():
                    return True
                del self._memory_cache[key]
            return False


# 全局缓存服务实例
cache_service = CacheService()

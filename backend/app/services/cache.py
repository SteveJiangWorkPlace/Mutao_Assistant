import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from app.models.schemas import ResearchOption

class ResearchCache:
    """调研结果缓存服务"""

    def __init__(self, ttl_hours: int = 24, max_entries: int = 1000):
        """
        初始化缓存

        Args:
            ttl_hours: 缓存存活时间（小时）
            max_entries: 最大缓存条目数
        """
        self.cache: Dict[str, dict] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.max_entries = max_entries
        self.access_count: Dict[str, int] = {}

    def _generate_cache_key(self, school: str, major: str, courses: str, extracurricular: str) -> str:
        """
        生成缓存键

        Args:
            school: 目标学校
            major: 申请专业
            courses: 相关课程描述
            extracurricular: 课外经历描述

        Returns:
            缓存键字符串
        """
        # 创建输入数据的JSON字符串
        input_data = {
            'school': school,
            'major': major,
            'courses': courses,
            'extracurricular': extracurricular
        }
        input_str = json.dumps(input_data, sort_keys=True, ensure_ascii=False)

        # 使用SHA256生成哈希
        return hashlib.sha256(input_str.encode('utf-8')).hexdigest()[:32]

    def get_cached_research(self, school: str, major: str, courses: str, extracurricular: str) -> Optional[List[ResearchOption]]:
        """
        获取缓存的调研结果

        Args:
            school: 目标学校
            major: 申请专业
            courses: 相关课程描述
            extracurricular: 课外经历描述

        Returns:
            缓存的ResearchOption列表，如果未找到或过期则返回None
        """
        cache_key = self._generate_cache_key(school, major, courses, extracurricular)

        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]

            # 检查是否过期
            created_at = cache_entry['created_at']
            if datetime.now() - created_at < self.ttl:
                # 更新访问计数
                self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1

                # 返回缓存的调研结果
                research_data = cache_entry['research_options']
                return [ResearchOption(**item) for item in research_data]
            else:
                # 缓存过期，删除
                self._remove_from_cache(cache_key)

        return None

    def cache_research(self, school: str, major: str, courses: str, extracurricular: str, research_options: List[ResearchOption]) -> str:
        """
        缓存调研结果

        Args:
            school: 目标学校
            major: 申请专业
            courses: 相关课程描述
            extracurricular: 课外经历描述
            research_options: 调研结果列表

        Returns:
            缓存键
        """
        cache_key = self._generate_cache_key(school, major, courses, extracurricular)

        # 检查缓存是否已满
        if len(self.cache) >= self.max_entries:
            self._evict_least_used()

        # 缓存数据
        self.cache[cache_key] = {
            'school': school,
            'major': major,
            'courses': courses,
            'extracurricular': extracurricular,
            'research_options': [opt.dict() for opt in research_options],
            'created_at': datetime.now(),
            'access_count': 0
        }

        self.access_count[cache_key] = 0

        # 清理过期缓存
        self._cleanup_expired()

        return cache_key

    def _remove_from_cache(self, cache_key: str):
        """从缓存中移除条目"""
        if cache_key in self.cache:
            del self.cache[cache_key]
        if cache_key in self.access_count:
            del self.access_count[cache_key]

    def _evict_least_used(self):
        """驱逐最少使用的缓存条目"""
        if not self.access_count:
            # 如果没有访问记录，移除第一个条目
            if self.cache:
                first_key = next(iter(self.cache))
                self._remove_from_cache(first_key)
            return

        # 找到访问次数最少的条目
        min_access_key = min(self.access_count.items(), key=lambda x: x[1])[0]
        self._remove_from_cache(min_access_key)

    def _cleanup_expired(self):
        """清理过期缓存"""
        current_time = datetime.now()
        expired_keys = []

        for key, entry in self.cache.items():
            if current_time - entry['created_at'] >= self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_from_cache(key)

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        current_time = datetime.now()
        expired_count = 0
        total_size = 0

        for entry in self.cache.values():
            if current_time - entry['created_at'] >= self.ttl:
                expired_count += 1
            total_size += len(json.dumps(entry))

        return {
            'total_entries': len(self.cache),
            'expired_entries': expired_count,
            'max_entries': self.max_entries,
            'ttl_hours': self.ttl.total_seconds() / 3600,
            'total_size_bytes': total_size,
            'access_counts': len(self.access_count)
        }

    def clear_cache(self):
        """清空所有缓存"""
        self.cache.clear()
        self.access_count.clear()
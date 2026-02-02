"""
城市级别映射表

建立"城市级别"的映射表，确保地址替换时保持法律效力一致性。
例如：如果原文是"北京市"，假数据也必须是"北京市"或同级别的一线城市。
"""

import random
from typing import Dict, List
from faker import Faker


class LocationMapper:
    """
    位置映射器：保持城市级别一致性
    """

    def __init__(self):
        """初始化位置映射器"""
        self.fake = Faker("zh_CN")
        self.city_mapping: Dict[str, str] = {}
        self.city_tiers = self._init_city_tiers()

    def _init_city_tiers(self) -> Dict[str, List[str]]:
        """
        初始化城市分级

        Returns:
            城市分级字典，key 为城市级别，value 为该级别的城市列表
        """
        return {
            "tier1": [
                "北京市",
                "上海市",
                "广州市",
                "深圳市",
            ],
            "tier2": [
                "杭州市",
                "南京市",
                "成都市",
                "武汉市",
                "西安市",
                "重庆市",
                "天津市",
            ],
            "tier3": [
                "苏州市",
                "无锡市",
                "宁波市",
                "青岛市",
                "大连市",
                "长沙市",
                "郑州市",
            ],
        }

    def _get_city_tier(self, city: str) -> str | None:
        """
        获取城市所属级别

        Args:
            city: 城市名

        Returns:
            城市级别，如果无法确定则返回 None
        """
        for tier, cities in self.city_tiers.items():
            for tier_city in cities:
                if tier_city in city or city in tier_city:
                    return tier
        return None

    def map_location(self, original_location: str) -> str:
        """
        映射位置，保持城市级别一致性

        Args:
            original_location: 原始位置文本，如"北京市朝阳区"或"深圳市南山区"

        Returns:
            映射后的位置，保持相同的城市级别
        """
        # 如果已有映射，直接返回
        if original_location in self.city_mapping:
            return self.city_mapping[original_location]

        # 确定原始城市的级别
        original_tier = self._get_city_tier(original_location)

        if original_tier:
            # 从同级别的城市中随机选择
            tier_cities = self.city_tiers[original_tier]
            mapped_city = random.choice(tier_cities)

            # 提取原始位置的区/县信息（如果有）
            district = self._extract_district(original_location)

            # 生成新的位置
            if district:
                # 保持区/县结构，但使用新城市
                mapped_location = mapped_city + district
            else:
                mapped_location = mapped_city
        else:
            # 如果无法确定级别，使用 Faker 生成
            mapped_location = self.fake.address()

        # 保存映射
        self.city_mapping[original_location] = mapped_location

        return mapped_location

    def _extract_district(self, location: str) -> str:
        """
        提取区/县信息

        Args:
            location: 位置文本，如"北京市朝阳区"

        Returns:
            区/县部分，如"朝阳区"
        """
        # 简单的区/县提取逻辑
        # 匹配"XX区"或"XX县"
        import re

        match = re.search(r"([^市省]+[区县])", location)
        if match:
            return match.group(1)
        return ""

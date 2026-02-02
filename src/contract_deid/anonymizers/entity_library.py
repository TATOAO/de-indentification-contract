"""
行业实体库

维护 1000+ 假公司名、人名等实体库，用于替换识别到的实体
"""

import random
from typing import List


class EntityLibrary:
    """
    行业实体库：提供预定义的虚拟实体名称
    """

    def __init__(self):
        """初始化实体库"""
        self.companies = self._load_company_names()
        self.persons = self._load_person_names()

    def _load_company_names(self) -> List[str]:
        """
        加载公司名称库

        Returns:
            公司名称列表
        """
        # TODO: 可以从文件或数据库加载更多公司名
        # 这里先提供一些示例
        company_types = ["科技", "贸易", "置业", "投资", "咨询", "服务", "制造", "物流"]
        company_suffixes = ["有限公司", "股份有限公司", "集团", "企业", "公司"]

        companies = []
        for _ in range(1000):
            type_name = random.choice(company_types)
            suffix = random.choice(company_suffixes)
            # 生成随机公司名
            name_parts = [
                random.choice(["海蓝", "大山", "绿水", "蓝天", "星辰", "阳光", "智慧", "创新"]),
                random.choice(["科技", "贸易", "投资", "发展", "实业"]),
            ]
            company_name = "".join(name_parts) + suffix
            companies.append(company_name)

        return companies

    def _load_person_names(self) -> List[str]:
        """
        加载人名库

        Returns:
            人名列表
        """
        # TODO: 可以从文件或数据库加载更多人名
        # 这里先提供一些示例
        surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        given_names = [
            "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
            "洋", "勇", "艳", "杰", "涛", "明", "超", "秀兰", "霞", "平",
        ]

        persons = []
        for surname in surnames:
            for given_name in given_names:
                persons.append(surname + given_name)

        return persons

    def get_random_company(self) -> str:
        """
        随机获取一个公司名

        Returns:
            随机公司名
        """
        return random.choice(self.companies)

    def get_random_person(self) -> str:
        """
        随机获取一个人名

        Returns:
            随机人名
        """
        return random.choice(self.persons)

    def add_company(self, company_name: str):
        """
        添加公司名到库中

        Args:
            company_name: 公司名
        """
        if company_name not in self.companies:
            self.companies.append(company_name)

    def add_person(self, person_name: str):
        """
        添加人名到库中

        Args:
            person_name: 人名
        """
        if person_name not in self.persons:
            self.persons.append(person_name)

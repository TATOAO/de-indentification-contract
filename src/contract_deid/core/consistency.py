"""
第三层：上下文一致性映射（Context Consistency Map）

对每一份合同，在内存中维护一个 Session Mapping Dictionary。
确保同一实体在整个文档中始终映射到同一个虚拟值。
"""

from typing import Dict, List
from presidio_analyzer.entities import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from contract_deid.anonymizers.faker_provider import FakerProvider
from contract_deid.anonymizers.entity_library import EntityLibrary
from contract_deid.utils.location_mapper import LocationMapper
from contract_deid.utils.mapping_export import DeidentificationConfig


class ConsistencyProvider:
    """
    一致性映射提供者：确保同一实体在整个文档中映射一致
    """

    def __init__(self):
        """初始化一致性映射提供者"""
        # Session Mapping Dictionary
        # 格式: {entity_type: {original_value: anonymized_value}}
        self.mapping: Dict[str, Dict[str, str]] = {}

        # 初始化数据生成器
        self.faker_provider = FakerProvider()
        self.entity_library = EntityLibrary()
        self.location_mapper = LocationMapper()

        # 初始化 Presidio Anonymizer
        self.anonymizer = AnonymizerEngine()

    def anonymize(
        self,
        text: str,
        analyzer_results: List[RecognizerResult],
        config: DeidentificationConfig,
    ) -> tuple[str, Dict[str, Dict[str, str]]]:
        """
        使用一致性映射进行匿名化

        Args:
            text: 原始文本
            analyzer_results: 识别结果列表
            config: 脱敏配置

        Returns:
            tuple: (匿名化后的文本, 映射表字典)
        """
        # 构建自定义操作符字典
        operators = {}

        for entity_type in set(r.entity_type for r in analyzer_results):
            operators[entity_type] = OperatorConfig(
                "custom",
                {
                    "lambda": lambda x, et=entity_type: self._get_consistent_value(
                        x.entity_text, et, config
                    )
                },
            )

        # 执行匿名化
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )

        return anonymized_result.text, self.mapping

    def _get_consistent_value(
        self, original_value: str, entity_type: str, config: DeidentificationConfig
    ) -> str:
        """
        获取一致性映射值

        Args:
            original_value: 原始值
            entity_type: 实体类型
            config: 脱敏配置

        Returns:
            映射后的值
        """
        # 初始化该实体类型的映射字典
        if entity_type not in self.mapping:
            self.mapping[entity_type] = {}

        # 如果已存在映射，直接返回
        if original_value in self.mapping[entity_type]:
            return self.mapping[entity_type][original_value]

        # 生成新的映射值
        anonymized_value = self._generate_anonymized_value(
            original_value, entity_type, config
        )

        # 保存映射
        self.mapping[entity_type][original_value] = anonymized_value

        return anonymized_value

    def _generate_anonymized_value(
        self, original_value: str, entity_type: str, config: DeidentificationConfig
    ) -> str:
        """
        生成匿名化值

        Args:
            original_value: 原始值
            entity_type: 实体类型
            config: 脱敏配置

        Returns:
            匿名化后的值
        """
        if entity_type == "ORGANIZATION":
            # 从实体库中随机选择
            return self.entity_library.get_random_company()

        elif entity_type == "PERSON":
            # 使用 Faker 生成人名
            return self.faker_provider.generate_name()

        elif entity_type == "LOCATION":
            # 根据配置决定是否保持城市级别一致性
            if config.location_preserve_level:
                return self.location_mapper.map_location(original_value)
            else:
                return self.faker_provider.generate_address()

        elif entity_type == "CREDIT_CODE":
            return self.faker_provider.generate_credit_code()

        elif entity_type == "ID_CARD":
            return self.faker_provider.generate_id_card()

        elif entity_type == "PHONE_NUMBER":
            return self.faker_provider.generate_phone()

        elif entity_type == "EMAIL":
            return self.faker_provider.generate_email()

        elif entity_type == "BANK_ACCOUNT":
            return self.faker_provider.generate_bank_account()

        elif entity_type == "AMOUNT":
            # 金额处理在 AmountRecognizer 中完成，这里直接返回
            return original_value

        else:
            # 默认使用 Faker 生成
            return self.faker_provider.generate_default(original_value)

    def clear(self):
        """清空映射表（处理完一份合同后调用）"""
        self.mapping.clear()

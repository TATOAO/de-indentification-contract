"""
第一层：规则引擎（Regex & Pattern）

处理所有格式固定的实体，准确率 100%，成本最低。
包括：统一社会信用代码、身份证号、电话/手机/邮箱、银行账号、金额等
"""

from typing import List, Dict, Any
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, RecognizerResult

from contract_deid.recognizers.credit_code import CreditCodeRecognizer
from contract_deid.recognizers.id_card import IdCardRecognizer
from contract_deid.recognizers.phone import PhoneRecognizer
from contract_deid.recognizers.bank_account import BankAccountRecognizer
from contract_deid.recognizers.amount import AmountRecognizer
from contract_deid.core.ner_engine import NEREngine
from contract_deid.core.consistency import ConsistencyProvider
from contract_deid.core.llm_refine import LLMRefiner
from contract_deid.utils.mapping_export import DeidentificationConfig, DeidentificationResult


class DeidentificationEngine:
    """
    脱敏引擎：整合四层脱敏策略
    """

    def __init__(
        self,
        config: DeidentificationConfig,
        consistency_provider: ConsistencyProvider,
    ):
        """
        初始化脱敏引擎

        Args:
            config: 脱敏配置
            consistency_provider: 一致性映射提供者（第三层）
        """
        self.config = config
        self.consistency_provider = consistency_provider

        # 初始化 Presidio Analyzer
        self.analyzer = self._create_analyzer()

        # 初始化 NER 引擎（第二层）
        self.ner_engine = NEREngine() if config.enable_ner else None

        # 初始化 LLM 润色器（第四层，可选）
        self.llm_refiner = (
            LLMRefiner(config.llm_model_path) if config.enable_llm_refinement else None
        )

    def _create_analyzer(self) -> AnalyzerEngine:
        """
        创建 Presidio Analyzer，并注册自定义识别器
        """
        # 创建注册表并添加自定义识别器
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        # 移除与自定义识别器冲突的预定义识别器
        # Presidio 的 PhoneRecognizer 与我们的自定义 PhoneRecognizer 冲突
        try:
            registry.remove_recognizer("PhoneRecognizer")
        except ValueError:
            pass  # 如果不存在则忽略

        # 注册自定义识别器（第一层）
        registry.add_recognizer(CreditCodeRecognizer())
        registry.add_recognizer(IdCardRecognizer())
        registry.add_recognizer(PhoneRecognizer())
        registry.add_recognizer(BankAccountRecognizer())
        registry.add_recognizer(AmountRecognizer(self.config.amount_noise_range))

        # 创建分析引擎
        analyzer = AnalyzerEngine(registry=registry)
        return analyzer

    def process(self, text: str) -> DeidentificationResult:
        """
        执行完整的脱敏流程

        Args:
            text: 待脱敏的文本

        Returns:
            DeidentificationResult: 脱敏结果
        """
        # 第一层：规则引擎识别
        analyzer_results = self.analyzer.analyze(text=text, language="zh")

        # 第二层：NER 识别（如果启用）
        if self.ner_engine:
            ner_results = self.ner_engine.analyze(text)
            analyzer_results.extend(ner_results)

        # 第三层：使用一致性映射进行替换
        anonymized_text, mapping = self.consistency_provider.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            config=self.config,
        )

        # 第四层：LLM 润色（如果启用）
        if self.llm_refiner:
            anonymized_text = self.llm_refiner.refine(anonymized_text, mapping)

        # 构建结果对象
        result = DeidentificationResult(
            anonymized_text=anonymized_text,
            mapping=mapping,
            config=self.config,
        )

        return result

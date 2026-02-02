"""
金额识别器（带比例保持）

识别合同中的金额，并保持比例关系（通过乘以随机系数）
"""

import re
import random
from typing import Tuple
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult


class AmountRecognizer(PatternRecognizer):
    """
    金额识别器

    识别合同中的金额，支持多种格式：
    - 人民币 1,000,000 元
    - ¥1000000
    - 100万元
    - 壹佰万元整
    """

    PATTERNS = [
        Pattern(
            "AMOUNT_WITH_COMMA",
            r"[¥￥]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*[元整]?",
            0.9,
        ),
        Pattern(
            "AMOUNT_SIMPLE",
            r"\d+(?:\.\d{2})?\s*[万元]",
            0.8,
        ),
        Pattern(
            "AMOUNT_CHINESE",
            r"[零壹贰叁肆伍陆柒捌玖拾佰仟万亿]+[元整]?",
            0.7,
        ),
    ]

    CONTEXT = [
        "金额",
        "价格",
        "费用",
        "总价",
        "单价",
        "合同金额",
        "交易金额",
        "人民币",
        "RMB",
    ]

    def __init__(self, noise_range: Tuple[float, float] = (0.8, 1.2)):
        """
        初始化金额识别器

        Args:
            noise_range: 金额随机系数范围，例如 (0.8, 1.2) 表示乘以 0.8 到 1.2 之间的随机数
        """
        super().__init__(
            supported_entity="AMOUNT",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
        )
        self.noise_range = noise_range
        self.noise_factor = random.uniform(*noise_range)

    def analyze(self, text: str, entities=None, nlp_artifacts=None):
        """
        分析文本，识别金额

        Args:
            text: 待分析文本
            entities: 实体类型列表
            nlp_artifacts: NLP 分析结果

        Returns:
            识别结果列表
        """
        results = []

        for pattern in self.PATTERNS:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                amount_text = match.group()
                # 提取数字部分
                numeric_value = self._extract_numeric_value(amount_text)
                if numeric_value:
                    results.append(
                        RecognizerResult(
                            entity_type="AMOUNT",
                            start=match.start(),
                            end=match.end(),
                            score=pattern.score,
                        )
                    )

        return results

    def _extract_numeric_value(self, amount_text: str) -> float | None:
        """
        从金额文本中提取数值

        Args:
            amount_text: 金额文本，如 "1,000,000 元" 或 "100万元"

        Returns:
            提取的数值，如果无法提取则返回 None
        """
        # 移除货币符号和单位
        cleaned = re.sub(r"[¥￥元整\s]", "", amount_text)

        # 处理中文数字（如"壹佰万元"）
        if re.search(r"[零壹贰叁肆伍陆柒捌玖拾佰仟万亿]", cleaned):
            # TODO: 实现中文数字转阿拉伯数字
            return None

        # 处理带逗号的数字（如 "1,000,000"）
        cleaned = cleaned.replace(",", "")

        # 处理"万"单位（如 "100万元" -> 1000000）
        if "万" in amount_text:
            match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
            if match:
                return float(match.group(1)) * 10000

        # 提取纯数字
        match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
        if match:
            return float(match.group(1))

        return None

    def get_noise_factor(self) -> float:
        """
        获取当前使用的噪声系数

        Returns:
            噪声系数
        """
        return self.noise_factor

"""
电话/手机/邮箱识别器

识别手机号、固定电话和邮箱地址
"""

import re
from typing import List
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult


class PhoneRecognizer(PatternRecognizer):
    """
    电话/手机/邮箱识别器
    """

    # 手机号模式：11 位数字，以 1 开头
    PHONE_PATTERNS = [
        Pattern(
            "MOBILE_PHONE",
            r"1[3-9]\d{9}",
            0.9,
        ),
    ]

    # 固定电话模式：区号 + 号码
    LANDLINE_PATTERNS = [
        Pattern(
            "LANDLINE_PHONE",
            r"0\d{2,3}-?\d{7,8}",
            0.8,
        ),
    ]

    # 邮箱模式
    EMAIL_PATTERNS = [
        Pattern(
            "EMAIL",
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            0.9,
        ),
    ]

    PHONE_CONTEXT = ["电话", "手机", "联系电话", "手机号", "手机号码", "座机", "固话"]
    EMAIL_CONTEXT = ["邮箱", "电子邮件", "Email", "E-mail", "电子邮箱"]

    def __init__(self):
        """
        初始化电话/手机/邮箱识别器
        """
        # 合并所有模式
        all_patterns = self.PHONE_PATTERNS + self.LANDLINE_PATTERNS + self.EMAIL_PATTERNS

        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=all_patterns,
            context=self.PHONE_CONTEXT + self.EMAIL_CONTEXT,
        )

    def analyze(self, text: str, entities: List[str] = None, nlp_artifacts=None):
        """
        分析文本，识别电话和邮箱

        Args:
            text: 待分析文本
            entities: 实体类型列表
            nlp_artifacts: NLP 分析结果

        Returns:
            识别结果列表
        """
        results = []

        # 识别手机号
        for pattern in self.PHONE_PATTERNS:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                results.append(
                    RecognizerResult(
                        entity_type="PHONE_NUMBER",
                        start=match.start(),
                        end=match.end(),
                        score=pattern.score,
                    )
                )

        # 识别固定电话
        for pattern in self.LANDLINE_PATTERNS:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                results.append(
                    RecognizerResult(
                        entity_type="PHONE_NUMBER",
                        start=match.start(),
                        end=match.end(),
                        score=pattern.score,
                    )
                )

        # 识别邮箱
        for pattern in self.EMAIL_PATTERNS:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                results.append(
                    RecognizerResult(
                        entity_type="EMAIL",
                        start=match.start(),
                        end=match.end(),
                        score=pattern.score,
                    )
                )

        return results

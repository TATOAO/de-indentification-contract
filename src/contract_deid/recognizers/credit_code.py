"""
统一社会信用代码识别器

识别 18 位统一社会信用代码，需要符合校验规则
"""

import re
from typing import List, Pattern
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult


class CreditCodeRecognizer(PatternRecognizer):
    """
    统一社会信用代码识别器

    统一社会信用代码格式：18 位，由数字和大写字母组成
    前两位：登记管理部门代码
    第3-8位：机构类别代码
    第9-17位：主体标识码
    第18位：校验码
    """

    PATTERNS = [
        Pattern(
            "CREDIT_CODE",
            r"[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}",
            0.9,
        ),
    ]

    CONTEXT = ["统一社会信用代码", "信用代码", "社会信用代码", "信用代码证"]

    def __init__(self):
        """
        初始化统一社会信用代码识别器
        """
        super().__init__(
            supported_entity="CREDIT_CODE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        验证识别结果是否符合统一社会信用代码的校验规则

        Args:
            pattern_text: 识别到的文本

        Returns:
            是否符合校验规则
        """
        if len(pattern_text) != 18:
            return False

        # TODO: 实现完整的校验位算法
        # 统一社会信用代码的校验算法较为复杂，这里先做基本格式验证
        return bool(re.match(r"^[0-9A-HJ-NPQRTUWXY]{18}$", pattern_text))

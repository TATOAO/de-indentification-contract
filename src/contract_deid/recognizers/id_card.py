"""
身份证号识别器

识别 15 位或 18 位身份证号，需要符合校验位算法
"""

import re
from typing import List
from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult


class IdCardRecognizer(PatternRecognizer):
    """
    身份证号识别器

    支持 15 位（旧版）和 18 位（新版）身份证号
    18 位身份证最后一位是校验码，需要验证
    """

    PATTERNS = [
        Pattern(
            "ID_CARD_18",
            r"\d{17}[\dXx]",
            0.9,
        ),
        Pattern(
            "ID_CARD_15",
            r"\d{15}",
            0.8,
        ),
    ]

    CONTEXT = ["身份证", "身份证号", "身份证号码", "身份证明", "证件号码"]

    def __init__(self):
        """
        初始化身份证号识别器
        """
        super().__init__(
            supported_entity="ID_CARD",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        验证识别结果是否符合身份证号的校验规则

        Args:
            pattern_text: 识别到的文本

        Returns:
            是否符合校验规则
        """
        # 15 位身份证（旧版）
        if len(pattern_text) == 15:
            return bool(re.match(r"^\d{15}$", pattern_text))

        # 18 位身份证（新版）
        if len(pattern_text) == 18:
            # 基本格式验证
            if not re.match(r"^\d{17}[\dXx]$", pattern_text):
                return False

            # 校验位验证
            return self._validate_check_digit(pattern_text)

        return False

    @staticmethod
    def _validate_check_digit(id_card: str) -> bool:
        """
        验证 18 位身份证的校验位

        Args:
            id_card: 18 位身份证号

        Returns:
            校验位是否正确
        """
        # 加权因子
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验码对应值
        check_codes = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]

        # 计算校验位
        sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
        check_digit = check_codes[sum_value % 11]

        # 验证最后一位
        return id_card[17].upper() == check_digit

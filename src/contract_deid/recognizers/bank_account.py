"""
银行账号识别器

识别常见的银行卡号格式（16-19 位数字）
"""

import re
from presidio_analyzer import PatternRecognizer, Pattern


class BankAccountRecognizer(PatternRecognizer):
    """
    银行账号识别器

    银行卡号通常为 16-19 位数字
    """

    PATTERNS = [
        Pattern(
            "BANK_ACCOUNT_16",
            r"\d{16}",
            0.8,
        ),
        Pattern(
            "BANK_ACCOUNT_17",
            r"\d{17}",
            0.8,
        ),
        Pattern(
            "BANK_ACCOUNT_18",
            r"\d{18}",
            0.8,
        ),
        Pattern(
            "BANK_ACCOUNT_19",
            r"\d{19}",
            0.8,
        ),
    ]

    CONTEXT = [
        "银行账号",
        "银行卡号",
        "账户",
        "账号",
        "卡号",
        "银行账户",
        "开户行",
        "收款账户",
    ]

    def __init__(self):
        """
        初始化银行账号识别器
        """
        super().__init__(
            supported_entity="BANK_ACCOUNT",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        验证识别结果是否符合银行卡号的格式

        Args:
            pattern_text: 识别到的文本

        Returns:
            是否符合格式要求
        """
        # 银行卡号通常是 16-19 位数字
        if not re.match(r"^\d{16,19}$", pattern_text):
            return False

        # TODO: 可以添加 Luhn 算法验证（银行卡校验算法）
        return True

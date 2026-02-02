"""
Faker 数据生成器

使用 Python Faker 库生成虚拟数据，用于替换敏感信息
"""

import random
import string
from faker import Faker


class FakerProvider:
    """
    Faker 数据生成器：提供各种类型的虚拟数据
    """

    def __init__(self, locale: str = "zh_CN"):
        """
        初始化 Faker 提供者

        Args:
            locale: 语言环境，默认为中文
        """
        self.fake = Faker(locale)

    def generate_name(self) -> str:
        """
        生成虚拟人名

        Returns:
            虚拟人名
        """
        return self.fake.name()

    def generate_company(self) -> str:
        """
        生成虚拟公司名

        Returns:
            虚拟公司名
        """
        return self.fake.company()

    def generate_address(self) -> str:
        """
        生成虚拟地址

        Returns:
            虚拟地址
        """
        return self.fake.address()

    def generate_phone(self) -> str:
        """
        生成虚拟手机号

        Returns:
            虚拟手机号（11位）
        """
        return self.fake.phone_number()

    def generate_email(self) -> str:
        """
        生成虚拟邮箱

        Returns:
            虚拟邮箱地址
        """
        return self.fake.email()

    def generate_credit_code(self) -> str:
        """
        生成虚拟统一社会信用代码（18位）

        Returns:
            虚拟统一社会信用代码
        """
        # 生成符合格式的 18 位代码
        # 前两位：登记管理部门代码（随机选择）
        dept_codes = ["91", "92", "93", "94", "95", "96", "97", "98", "99"]
        dept_code = random.choice(dept_codes)

        # 第3-8位：机构类别代码（6位数字）
        org_code = "".join(random.choices(string.digits, k=6))

        # 第9-17位：主体标识码（9位，数字或字母）
        valid_chars = "0123456789ABCDEFGHJKLMNPQRTUWXY"
        subject_code = "".join(random.choices(valid_chars, k=9))

        # 第18位：校验码（需要计算，这里先随机生成）
        check_code = random.choice(valid_chars)

        credit_code = dept_code + org_code + subject_code + check_code

        # TODO: 实现完整的校验位算法，确保生成的代码符合校验规则
        return credit_code

    def generate_id_card(self) -> str:
        """
        生成虚拟身份证号（18位，符合校验规则）

        Returns:
            虚拟身份证号
        """
        # 生成地区码（前6位）
        area_code = "".join(random.choices(string.digits, k=6))

        # 生成出生日期（7-14位，YYYYMMDD格式）
        year = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 避免日期无效
        birth_date = f"{year:04d}{month:02d}{day:02d}"

        # 生成顺序码（15-17位）
        sequence_code = "".join(random.choices(string.digits, k=3))

        # 计算校验位（第18位）
        id_17 = area_code + birth_date + sequence_code
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]

        sum_value = sum(int(id_17[i]) * weights[i] for i in range(17))
        check_digit = check_codes[sum_value % 11]

        return id_17 + check_digit

    def generate_bank_account(self) -> str:
        """
        生成虚拟银行账号（16-19位）

        Returns:
            虚拟银行账号
        """
        length = random.choice([16, 17, 18, 19])
        return "".join(random.choices(string.digits, k=length))

    def generate_default(self, original_value: str) -> str:
        """
        生成默认虚拟值（用于未知类型的实体）

        Args:
            original_value: 原始值

        Returns:
            虚拟值
        """
        # 保持相同长度，使用随机字符
        if original_value.isdigit():
            return "".join(random.choices(string.digits, k=len(original_value)))
        else:
            return "".join(random.choices(string.ascii_letters + string.digits, k=len(original_value)))

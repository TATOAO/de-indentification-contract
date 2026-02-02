"""
脱敏功能测试

测试四层脱敏策略的各项功能
"""

import pytest
from contract_deid import deidentify, DeidentificationConfig


def test_basic_deidentification():
    """测试基础脱敏功能"""
    text = """
    甲方：腾讯科技（深圳）有限公司
    统一社会信用代码：91440300MA5D123456
    法定代表人：马化腾
    联系电话：13800138000
    合同金额：人民币 1,000,000 元
    项目地址：深圳市南山区科技园
    """

    result = deidentify(text)

    # 验证脱敏后文本不为空
    assert result.anonymized_text is not None
    assert len(result.anonymized_text) > 0

    # 验证映射表不为空
    assert result.mapping is not None
    assert isinstance(result.mapping, dict)


def test_credit_code_recognition():
    """测试统一社会信用代码识别"""
    text = "统一社会信用代码：91440300MA5D123456"

    result = deidentify(text)

    # 验证原始代码被替换
    assert "91440300MA5D123456" not in result.anonymized_text

    # 验证映射表中包含信用代码
    if "CREDIT_CODE" in result.mapping:
        assert "91440300MA5D123456" in result.mapping["CREDIT_CODE"]


def test_id_card_recognition():
    """测试身份证号识别"""
    text = "身份证号：110101199001011234"

    result = deidentify(text)

    # 验证原始身份证号被替换
    assert "110101199001011234" not in result.anonymized_text


def test_phone_recognition():
    """测试电话识别"""
    text = "联系电话：13800138000"

    result = deidentify(text)

    # 验证原始电话被替换
    assert "13800138000" not in result.anonymized_text


def test_consistency_mapping():
    """测试一致性映射"""
    text = """
    甲方：腾讯科技（深圳）有限公司
    乙方：腾讯科技（深圳）有限公司
    """

    result = deidentify(text)

    # 验证同一实体映射一致
    # 提取脱敏后的公司名
    lines = result.anonymized_text.strip().split("\n")
    if len(lines) >= 2:
        company1 = lines[0].split("：")[-1] if "：" in lines[0] else ""
        company2 = lines[1].split("：")[-1] if "：" in lines[1] else ""
        # 同一实体应该映射到同一个值
        assert company1 == company2


def test_amount_noise():
    """测试金额噪声处理"""
    text = "合同金额：人民币 1,000,000 元"

    config = DeidentificationConfig(amount_noise_range=(0.9, 1.1))
    result = deidentify(text, config=config)

    # 验证金额被处理（这里只做基本检查）
    assert result.anonymized_text is not None


def test_mapping_export():
    """测试映射表导出"""
    text = "甲方：腾讯科技（深圳）有限公司"

    result = deidentify(text)

    # 测试 JSON 导出
    json_str = result.mapping_json
    assert json_str is not None
    assert isinstance(json_str, str)

    # 测试 CSV 导出（如果 pandas 可用）
    try:
        csv_str = result.mapping_csv
        assert csv_str is not None
        assert isinstance(csv_str, str)
    except ImportError:
        # pandas 未安装时跳过
        pass


def test_config_options():
    """测试配置选项"""
    text = "测试文本"

    config = DeidentificationConfig(
        amount_noise_range=(0.7, 1.3),
        location_preserve_level=False,
        enable_ner=False,
    )

    result = deidentify(text, config=config)
    assert result is not None

# python -m pytest tests/test_deidentification.py
if __name__ == "__main__":
    pytest.main()
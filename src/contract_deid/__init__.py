"""
合同脱敏工具主模块

提供简洁的 API 接口，支持四层脱敏策略：
1. 规则引擎（Regex & Pattern）
2. NLP 实体识别（NER）
3. 上下文一致性映射
4. LLM 润色与逻辑修复（可选）
"""

from contract_deid.utils.mapping_export import DeidentificationResult, DeidentificationConfig

# 延迟导入，避免循环依赖
def _get_engine_and_provider():
    from contract_deid.core.analyzer import DeidentificationEngine
    from contract_deid.core.consistency import ConsistencyProvider
    return DeidentificationEngine, ConsistencyProvider

__version__ = "0.1.0"
__all__ = ["deidentify", "DeidentificationConfig", "DeidentificationResult"]


def deidentify(
    text: str,
    config: DeidentificationConfig | None = None,
) -> DeidentificationResult:
    """
    对合同文本进行脱敏处理

    Args:
        text: 待脱敏的合同文本
        config: 脱敏配置选项，如果为 None 则使用默认配置

    Returns:
        DeidentificationResult: 包含脱敏后文本和映射表的结果对象

    Example:
        >>> from contract_deid import deidentify
        >>> result = deidentify("甲方：腾讯科技（深圳）有限公司...")
        >>> print(result.anonymized_text)
        >>> print(result.mapping)
    """
    if config is None:
        config = DeidentificationConfig()

    # 延迟导入
    DeidentificationEngine, ConsistencyProvider = _get_engine_and_provider()

    # 创建一致性映射提供者（第三层）
    consistency_provider = ConsistencyProvider()

    # 创建脱敏引擎
    engine = DeidentificationEngine(config=config, consistency_provider=consistency_provider)

    # 执行脱敏
    result = engine.process(text)

    return result

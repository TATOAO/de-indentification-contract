"""
NER 适配器模块

提供统一的 NER 模型接口，支持多种后端：
- ModelScope（推荐）
- PaddleNLP（向后兼容）
- LLM（用于实体抽取）
"""

from contract_deid.core.ner_adapters.base import BaseNERAdapter
from contract_deid.core.ner_adapters.modelscope_adapter import ModelScopeNERAdapter
from contract_deid.core.ner_adapters.paddlenlp_adapter import PaddleNLPAdapter
from contract_deid.core.ner_adapters.llm_adapter import LLMNERAdapter

__all__ = [
    "BaseNERAdapter",
    "ModelScopeNERAdapter",
    "PaddleNLPAdapter",
    "LLMNERAdapter",
]

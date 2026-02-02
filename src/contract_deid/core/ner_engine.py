"""
第二层：NLP 实体识别（NER）

使用适配器模式支持多种 NER 后端：
- ModelScope（推荐）
- PaddleNLP（向后兼容）
- LLM（用于实体抽取）

识别中文法律实体：
- ORG（组织机构）：甲方、乙方、关联公司
- PER（人名）：法人代表、授权签字人
- LOC（地点）：项目地址、管辖法院地
"""

from typing import List, Optional, Literal, Union
from presidio_analyzer import RecognizerResult

from contract_deid.config import NERConfig
from contract_deid.core.ner_adapters import (
    BaseNERAdapter,
    ModelScopeNERAdapter,
    PaddleNLPAdapter,
    LLMNERAdapter,
)


class NEREngine:
    """
    NER 引擎：使用适配器模式支持多种 NER 后端
    
    默认使用 ModelScope，但可以通过 adapter_type 参数切换后端。
    """

    # 支持的适配器类型
    ADAPTER_TYPES = Literal["modelscope", "paddlenlp", "llm"]

    def __init__(
        self,
        adapter_type: Optional[ADAPTER_TYPES] = None,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        schema: Optional[List[str]] = None,
        **kwargs
    ):
        """
        初始化 NER 引擎

        Args:
            adapter_type: 适配器类型，可选 "modelscope"（默认）、"paddlenlp"、"llm"
                        如果为 None，将从环境变量 NER_ADAPTER_TYPE 读取
            model_name: 模型名称（根据适配器类型不同而不同）
                       如果为 None，将从环境变量 NER_MODEL_NAME 读取
            model_path: 本地模型路径（如果指定则从本地加载）
                       如果为 None，将从环境变量 NER_MODEL_PATH 读取
            schema: 实体类型列表，如 ["组织机构", "人名", "地点"]
                   如果为 None，将从环境变量 NER_SCHEMA 读取
            **kwargs: 其他适配器特定参数
        """
        # 从环境变量读取默认值
        self.adapter_type = adapter_type or NERConfig.get_adapter_type()
        self.model_name = model_name or NERConfig.get_model_name()
        self.model_path = model_path or NERConfig.get_model_path()
        self.schema = schema or NERConfig.get_schema() or ["组织机构", "人名", "地点"]
        
        # 创建适配器实例
        self._adapter: BaseNERAdapter = self._create_adapter(**kwargs)

    def _create_adapter(self, **kwargs) -> BaseNERAdapter:
        """
        根据 adapter_type 创建相应的适配器实例
        
        Args:
            **kwargs: 适配器特定参数
            
        Returns:
            BaseNERAdapter: 适配器实例
        """
        adapter_kwargs = {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "schema": self.schema,
            **kwargs
        }
        
        if self.adapter_type == "modelscope":
            try:
                return ModelScopeNERAdapter(**adapter_kwargs)
            except ImportError:
                print("Warning: ModelScope not available, falling back to PaddleNLP")
                return PaddleNLPAdapter(**adapter_kwargs)
        
        elif self.adapter_type == "paddlenlp":
            return PaddleNLPAdapter(**adapter_kwargs)
        
        elif self.adapter_type == "llm":
            return LLMNERAdapter(**adapter_kwargs)
        
        else:
            raise ValueError(
                f"Unknown adapter_type: {self.adapter_type}. "
                f"Supported types: {', '.join(['modelscope', 'paddlenlp', 'llm'])}"
            )

    def analyze(self, text: str) -> List[RecognizerResult]:
        """
        识别文本中的实体（统一接口）

        Args:
            text: 待识别的文本

        Returns:
            List[RecognizerResult]: Presidio 格式的识别结果列表
        """
        return self._adapter.analyze(text)

    @property
    def adapter(self) -> BaseNERAdapter:
        """
        获取当前使用的适配器实例
        
        Returns:
            BaseNERAdapter: 适配器实例
        """
        return self._adapter

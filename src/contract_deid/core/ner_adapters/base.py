"""
NER 适配器抽象基类

定义统一的 NER 模型接口，所有具体的 NER 实现都需要继承此基类。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from presidio_analyzer import RecognizerResult


class BaseNERAdapter(ABC):
    """
    NER 适配器抽象基类
    
    定义统一的输入输出接口：
    - 输入：文本字符串
    - 输出：List[RecognizerResult]（Presidio 格式）
    """

    def __init__(self, model_name: Optional[str] = None, model_path: Optional[str] = None, **kwargs):
        """
        初始化适配器
        
        Args:
            model_name: 模型名称（可选）
            model_path: 本地模型路径（可选）
            **kwargs: 其他模型特定参数
        """
        self.model_name = model_name
        self.model_path = model_path
        self._model = None

    @abstractmethod
    def _load_model(self) -> Any:
        """
        加载模型（懒加载）
        
        Returns:
            模型对象（类型取决于具体实现）
        """
        pass

    @property
    def model(self) -> Any:
        """
        获取模型实例（懒加载）
        
        Returns:
            模型对象
        """
        if self._model is None:
            self._model = self._load_model()
        return self._model

    @abstractmethod
    def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        从文本中提取实体（内部方法，返回原始格式）
        
        Args:
            text: 待识别的文本
            
        Returns:
            Dict[str, List[Dict]]: 实体字典，格式为 {entity_type: [{"text": "...", "start": 0, "end": 10, ...}]}
        """
        pass

    @abstractmethod
    def _map_entity_type(self, raw_type: str) -> Optional[str]:
        """
        将原始实体类型映射到 Presidio 标准类型
        
        Args:
            raw_type: 原始实体类型（如 "组织机构"、"人名" 等）
            
        Returns:
            Presidio 实体类型（如 "ORGANIZATION"、"PERSON" 等），如果无法映射则返回 None
        """
        pass

    def analyze(self, text: str) -> List[RecognizerResult]:
        """
        识别文本中的实体（统一接口）
        
        Args:
            text: 待识别的文本
            
        Returns:
            List[RecognizerResult]: Presidio 格式的识别结果列表
        """
        results = []
        
        try:
            # 调用具体实现提取实体
            ner_results = self._extract_entities(text)
            
            # 转换为 Presidio 格式
            for entity_type, entities in ner_results.items():
                presidio_type = self._map_entity_type(entity_type)
                if presidio_type:
                    for entity in entities:
                        if "text" in entity and "start" in entity and "end" in entity:
                            result = RecognizerResult(
                                entity_type=presidio_type,
                                start=entity["start"],
                                end=entity["end"],
                                score=entity.get("probability", entity.get("score", 0.9)),
                            )
                            results.append(result)
        except Exception as e:
            # 如果 NER 失败，记录错误但不中断流程
            print(f"Warning: NER analysis failed: {e}")
            return []
        
        return results

    def __repr__(self) -> str:
        """返回适配器的字符串表示"""
        return f"{self.__class__.__name__}(model_name={self.model_name}, model_path={self.model_path})"

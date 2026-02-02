"""
第二层：NLP 实体识别（NER）

使用 PaddleNLP 或 ModelScope 识别中文法律实体：
- ORG（组织机构）：甲方、乙方、关联公司
- PER（人名）：法人代表、授权签字人
- LOC（地点）：项目地址、管辖法院地
"""

from typing import List
from presidio_analyzer.entities import RecognizerResult

try:
    from paddlenlp import Taskflow
except ImportError:
    Taskflow = None


class NEREngine:
    """
    NER 引擎：使用 PaddleNLP 进行中文实体识别
    """

    def __init__(self, model_name: str = "uie-base"):
        """
        初始化 NER 引擎

        Args:
            model_name: PaddleNLP 模型名称，默认为 "uie-base"
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """懒加载模型"""
        if self._model is None:
            if Taskflow is None:
                raise ImportError(
                    "PaddleNLP is not installed. Please install it with: pip install paddlenlp"
                )
            # 初始化 PaddleNLP 的 NER 任务流
            self._model = Taskflow(
                "information_extraction",
                schema=["组织机构", "人名", "地点"],
                model=self.model_name,
            )
        return self._model

    def analyze(self, text: str) -> List[RecognizerResult]:
        """
        识别文本中的实体

        Args:
            text: 待识别的文本

        Returns:
            List[RecognizerResult]: Presidio 格式的识别结果列表
        """
        results = []

        try:
            # 调用 PaddleNLP 进行实体识别
            ner_results = self.model(text)

            # 将 PaddleNLP 结果转换为 Presidio 格式
            for entity_type, entities in ner_results.items():
                presidio_type = self._map_entity_type(entity_type)
                if presidio_type:
                    for entity in entities:
                        if "text" in entity and "start" in entity and "end" in entity:
                            result = RecognizerResult(
                                entity_type=presidio_type,
                                start=entity["start"],
                                end=entity["end"],
                                score=entity.get("probability", 0.9),
                            )
                            results.append(result)
        except Exception as e:
            # 如果 NER 失败，记录错误但不中断流程
            print(f"Warning: NER analysis failed: {e}")
            return []

        return results

    @staticmethod
    def _map_entity_type(paddlenlp_type: str) -> str | None:
        """
        将 PaddleNLP 的实体类型映射到 Presidio 的实体类型

        Args:
            paddlenlp_type: PaddleNLP 的实体类型

        Returns:
            Presidio 实体类型，如果无法映射则返回 None
        """
        mapping = {
            "组织机构": "ORGANIZATION",
            "人名": "PERSON",
            "地点": "LOCATION",
        }
        return mapping.get(paddlenlp_type)

"""
ModelScope NER 适配器

使用 ModelScope 的模型进行实体识别。
推荐使用，因为 ModelScope 的模型下载更稳定。
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import os

try:
    from modelscope import snapshot_download, AutoModel, AutoTokenizer
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks
    MODEL_SCOPE_AVAILABLE = True
except ImportError:
    MODEL_SCOPE_AVAILABLE = False

from contract_deid.config import NERConfig, ModelConfig
from contract_deid.core.ner_adapters.base import BaseNERAdapter


class ModelScopeNERAdapter(BaseNERAdapter):
    """
    ModelScope NER 适配器
    
    支持使用 ModelScope Hub 上的 NER 模型，例如：
    - damo/nlp_structbert_named-entity-recognition_chinese-base-ecommerce
    - damo/nlp_raner_named-entity-recognition_chinese-base-ecommerce
    - 或其他 UIE 模型
    """

    # 默认模型配置
    DEFAULT_MODEL_NAME = "damo/nlp_structbert_named-entity-recognition_chinese-base-ecommerce"
    
    # 实体类型映射（根据具体模型调整）
    ENTITY_TYPE_MAPPING = {
        "组织机构": "ORGANIZATION",
        "人名": "PERSON",
        "地点": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
        "LOC": "LOCATION",
        "MISC": "MISC",
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        schema: Optional[List[str]] = None,
        **kwargs
    ):
        """
        初始化 ModelScope 适配器
        
        Args:
            model_name: ModelScope 模型名称，默认为 DEFAULT_MODEL_NAME
            model_path: 本地模型路径（如果已下载）
            schema: 实体类型列表（对于 UIE 类模型），如 ["组织机构", "人名", "地点"]
            **kwargs: 其他参数
        """
        if not MODEL_SCOPE_AVAILABLE:
            raise ImportError(
                "ModelScope is not installed. Please install it with: "
                "uv pip install modelscope"
            )
        
        super().__init__(
            model_name=model_name or self.DEFAULT_MODEL_NAME,
            model_path=model_path,
            **kwargs
        )
        self.schema = schema or ["组织机构", "人名", "地点"]
        self._pipeline = None

    def _load_model(self):
        """加载 ModelScope 模型"""
        if self.model_path:
            # 使用本地模型路径
            model_path = Path(self.model_path).resolve()
            if not model_path.exists():
                raise FileNotFoundError(f"Model path not found: {model_path}")
            model_dir = str(model_path)
        else:
            # 从 ModelScope Hub 下载或使用缓存
            # 优先使用环境变量配置的缓存目录
            cache_dir = NERConfig.get_modelscope_cache_dir()
            if cache_dir:
                models_dir = Path(cache_dir)
            else:
                # 使用项目 models 目录
                models_dir = ModelConfig.get_models_dir() / "modelscope"
            
            # 设置 ModelScope 缓存目录
            os.environ.setdefault("MODELSCOPE_CACHE", str(models_dir.resolve()))
            
            # 下载或加载模型
            model_dir = snapshot_download(
                self.model_name,
                cache_dir=str(models_dir.resolve())
            )
        
        # 创建 pipeline
        # 根据模型类型选择不同的 pipeline
        if "uie" in self.model_name.lower() or "information_extraction" in self.model_name.lower():
            # UIE 类模型
            self._pipeline = pipeline(
                Tasks.information_extraction,
                model=model_dir,
                schema=self.schema,
            )
        else:
            # 标准 NER 模型
            self._pipeline = pipeline(
                Tasks.named_entity_recognition,
                model=model_dir,
            )
        
        return self._pipeline

    def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用 ModelScope 模型提取实体
        
        Args:
            text: 待识别的文本
            
        Returns:
            Dict[str, List[Dict]]: 实体字典
        """
        pipeline = self.model
        
        # 调用 pipeline
        results = pipeline(text)
        
        # 标准化结果格式
        entities = {}
        
        if isinstance(results, dict):
            # UIE 类模型返回格式：{"组织机构": [{"text": "...", "start": 0, "end": 10, ...}], ...}
            for entity_type, entity_list in results.items():
                entities[entity_type] = entity_list
        elif isinstance(results, list):
            # 标准 NER 模型返回格式：[{"type": "ORG", "start": 0, "end": 10, "text": "...", ...}, ...]
            for item in results:
                entity_type = item.get("type", item.get("label", "MISC"))
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append({
                    "text": item.get("text", text[item.get("start", 0):item.get("end", 0)]),
                    "start": item.get("start", 0),
                    "end": item.get("end", 0),
                    "probability": item.get("score", item.get("probability", 0.9)),
                })
        
        return entities

    def _map_entity_type(self, raw_type: str) -> Optional[str]:
        """
        将 ModelScope 实体类型映射到 Presidio 类型
        
        Args:
            raw_type: 原始实体类型
            
        Returns:
            Presidio 实体类型
        """
        return self.ENTITY_TYPE_MAPPING.get(raw_type)

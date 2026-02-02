"""
PaddleNLP NER 适配器

保留对 PaddleNLP 的支持，用于向后兼容。
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import os

# 修复 aistudio_sdk 导入问题（必须在导入 PaddleNLP 之前）
def _fix_aistudio_sdk_import():
    """修复 aistudio_sdk.hub 的导入问题"""
    try:
        import aistudio_sdk.hub as hub_module
        if not hasattr(hub_module, 'download'):
            def download_dummy(*args, **kwargs):
                """占位符函数，实际下载由 PaddleNLP 内部处理"""
                raise NotImplementedError(
                    "aistudio_sdk download is not available. "
                    "PaddleNLP will use alternative download methods."
                )
            hub_module.download = download_dummy
    except Exception:
        pass

# 在导入 PaddleNLP 之前修复导入问题
_fix_aistudio_sdk_import()

try:
    from paddlenlp import Taskflow
    PADDLE_NLP_AVAILABLE = True
except ImportError:
    PADDLE_NLP_AVAILABLE = False
    Taskflow = None

from contract_deid.config import NERConfig, ModelConfig
from contract_deid.core.ner_adapters.base import BaseNERAdapter


class PaddleNLPAdapter(BaseNERAdapter):
    """
    PaddleNLP NER 适配器
    
    使用 PaddleNLP 的 Taskflow 进行实体识别。
    主要用于向后兼容。
    """

    DEFAULT_MODEL_NAME = "uie-base"
    
    ENTITY_TYPE_MAPPING = {
        "组织机构": "ORGANIZATION",
        "人名": "PERSON",
        "地点": "LOCATION",
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        schema: Optional[List[str]] = None,
        **kwargs
    ):
        """
        初始化 PaddleNLP 适配器
        
        Args:
            model_name: PaddleNLP 模型名称，默认为 "uie-base"
            model_path: 本地模型路径
            schema: 实体类型列表，如 ["组织机构", "人名", "地点"]
            **kwargs: 其他参数
        """
        if not PADDLE_NLP_AVAILABLE:
            raise ImportError(
                "PaddleNLP is not installed. Please install it with: "
                "uv pip install paddlenlp"
            )
        
        super().__init__(
            model_name=model_name or self.DEFAULT_MODEL_NAME,
            model_path=model_path,
            **kwargs
        )
        self.schema = schema or ["组织机构", "人名", "地点"]

    def _load_model(self):
        """加载 PaddleNLP 模型"""
        # 如果指定了本地模型路径，优先使用本地模型
        if self.model_path:
            model_path = Path(self.model_path).resolve()
            if model_path.exists():
                os.environ["PADDLE_HOME"] = str(model_path.parent)
                task_path = str(model_path)
            else:
                print(f"Warning: 指定的模型路径不存在: {model_path}，将使用默认模型")
                task_path = None
        else:
            # 优先使用环境变量配置的 PADDLE_HOME
            paddle_home = NERConfig.get_paddle_home()
            if paddle_home:
                models_dir = Path(paddle_home)
            else:
                # 使用项目 models 目录
                models_dir = ModelConfig.get_models_dir()
            
            model_cache_dir = models_dir / "taskflow" / "information_extraction" / self.model_name
            
            if model_cache_dir.exists() and (model_cache_dir / "model_state.pdparams").exists():
                os.environ["PADDLE_HOME"] = str(models_dir.resolve())
                task_path = None
            else:
                # 检查默认缓存目录
                default_cache = Path.home() / ".paddlenlp" / "taskflow" / "information_extraction" / self.model_name
                if default_cache.exists() and (default_cache / "model_state.pdparams").exists():
                    os.environ["PADDLE_HOME"] = str(Path.home() / ".paddlenlp")
                    task_path = None
                else:
                    # 设置项目 models 目录，让模型下载到这里
                    os.environ["PADDLE_HOME"] = str(models_dir.resolve())
                    task_path = None
        
        # 初始化 PaddleNLP 的 NER 任务流
        taskflow_kwargs = {
            "schema": self.schema,
            "model": self.model_name,
        }
        if task_path:
            taskflow_kwargs["task_path"] = task_path
        
        return Taskflow("information_extraction", **taskflow_kwargs)

    def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用 PaddleNLP 模型提取实体
        
        Args:
            text: 待识别的文本
            
        Returns:
            Dict[str, List[Dict]]: 实体字典
        """
        taskflow = self.model
        results = taskflow(text)
        
        # PaddleNLP 返回格式已经是标准格式：{"组织机构": [{"text": "...", "start": 0, "end": 10, ...}], ...}
        return results

    def _map_entity_type(self, raw_type: str) -> Optional[str]:
        """
        将 PaddleNLP 实体类型映射到 Presidio 类型
        
        Args:
            raw_type: 原始实体类型
            
        Returns:
            Presidio 实体类型
        """
        return self.ENTITY_TYPE_MAPPING.get(raw_type)

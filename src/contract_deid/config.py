"""
配置模块

从环境变量和 .env 文件读取配置。
"""

import os
from pathlib import Path
from typing import List, Optional
import json

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def _load_env_file():
    """加载 .env 文件"""
    if DOTENV_AVAILABLE:
        # 查找项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)


# 在模块加载时自动加载 .env 文件
_load_env_file()


class NERConfig:
    """NER 相关配置"""
    
    @staticmethod
    def get_adapter_type() -> str:
        """
        获取适配器类型
        
        Returns:
            适配器类型，默认为 "modelscope"
        """
        return os.getenv("NER_ADAPTER_TYPE", "modelscope")
    
    @staticmethod
    def get_model_name() -> Optional[str]:
        """
        获取模型名称
        
        Returns:
            模型名称，如果未设置则返回 None
        """
        return os.getenv("NER_MODEL_NAME") or None
    
    @staticmethod
    def get_model_path() -> Optional[str]:
        """
        获取本地模型路径
        
        Returns:
            模型路径，如果未设置则返回 None
        """
        path = os.getenv("NER_MODEL_PATH")
        if path:
            return str(Path(path).expanduser().resolve())
        return None
    
    @staticmethod
    def get_schema() -> Optional[List[str]]:
        """
        获取实体类型列表
        
        Returns:
            实体类型列表，如果未设置则返回 None
        """
        schema_str = os.getenv("NER_SCHEMA")
        if schema_str:
            try:
                # 尝试解析 JSON 格式
                schema = json.loads(schema_str)
                if isinstance(schema, list):
                    return schema
            except json.JSONDecodeError:
                # 如果不是 JSON，尝试按逗号分割
                return [s.strip() for s in schema_str.split(",") if s.strip()]
        return None
    
    @staticmethod
    def get_modelscope_cache_dir() -> Optional[str]:
        """
        获取 ModelScope 缓存目录
        
        Returns:
            缓存目录路径，如果未设置则返回 None
        """
        path = os.getenv("MODEL_SCOPE_CACHE_DIR")
        if path:
            return str(Path(path).expanduser().resolve())
        return None
    
    @staticmethod
    def get_paddle_home() -> Optional[str]:
        """
        获取 PaddleNLP 模型目录
        
        Returns:
            PADDLE_HOME 路径，如果未设置则返回 None
        """
        path = os.getenv("PADDLE_HOME")
        if path:
            return str(Path(path).expanduser().resolve())
        return None
    
    @staticmethod
    def get_llm_call_func_module() -> Optional[str]:
        """
        获取 LLM 调用函数的模块路径（用于动态导入）
        
        Returns:
            模块路径，格式如 "module.path:function_name"
        """
        return os.getenv("LLM_CALL_FUNC_MODULE") or None


class ModelConfig:
    """模型相关配置"""
    
    @staticmethod
    def get_models_dir() -> Path:
        """
        获取项目 models 目录
        
        Returns:
            models 目录路径
        """
        custom_dir = os.getenv("MODELS_DIR")
        if custom_dir:
            return Path(custom_dir).expanduser().resolve()
        
        # 默认使用项目根目录下的 models 目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        return project_root / "models"

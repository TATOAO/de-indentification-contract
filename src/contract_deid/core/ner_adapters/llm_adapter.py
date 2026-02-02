"""
LLM NER 适配器

使用大语言模型（LLM）进行实体抽取。
支持本地部署的模型或 API 调用。
"""

from typing import List, Dict, Any, Optional, Callable
import json
import re
import importlib

from contract_deid.config import NERConfig
from contract_deid.core.ner_adapters.base import BaseNERAdapter


class LLMNERAdapter(BaseNERAdapter):
    """
    LLM NER 适配器
    
    使用 LLM 进行实体识别，通过 prompt 工程引导模型输出结构化结果。
    支持多种 LLM 后端（需要实现 _call_llm 方法）。
    """

    ENTITY_TYPE_MAPPING = {
        "组织机构": "ORGANIZATION",
        "人名": "PERSON",
        "地点": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
        "LOC": "LOCATION",
        "MISC": "MISC",
    }

    # 默认实体类型列表
    DEFAULT_SCHEMA = ["组织机构", "人名", "地点"]

    def __init__(
        self,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        schema: Optional[List[str]] = None,
        llm_call_func: Optional[Callable[[str, str], str]] = None,
        **kwargs
    ):
        """
        初始化 LLM 适配器
        
        Args:
            model_name: 模型名称（用于标识）
            model_path: 模型路径（如果使用本地模型）
            schema: 实体类型列表，如 ["组织机构", "人名", "地点"]
            llm_call_func: LLM 调用函数，签名：callable(text: str, prompt: str) -> str
            **kwargs: 其他参数
        """
        super().__init__(
            model_name=model_name or "llm-ner",
            model_path=model_path,
            **kwargs
        )
        self.schema = schema or self.DEFAULT_SCHEMA
        self.llm_call_func = llm_call_func
        
        if self.llm_call_func is None:
            # 尝试从环境变量加载 LLM 调用函数
            func_module = NERConfig.get_llm_call_func_module()
            if func_module:
                self.llm_call_func = self._load_llm_func_from_module(func_module)
            else:
                # 尝试自动检测 LLM 后端
                self.llm_call_func = self._detect_llm_backend()

    def _load_llm_func_from_module(self, module_path: str) -> Callable[[str, str], str]:
        """
        从模块路径加载 LLM 调用函数
        
        Args:
            module_path: 模块路径，格式如 "module.path:function_name"
            
        Returns:
            LLM 调用函数
        """
        try:
            if ":" not in module_path:
                raise ValueError(f"Invalid module path format: {module_path}. Expected format: 'module.path:function_name'")
            
            module_name, func_name = module_path.rsplit(":", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            
            if not callable(func):
                raise ValueError(f"{func_name} is not callable")
            
            return func
        except (ImportError, AttributeError, ValueError) as e:
            raise ValueError(f"Failed to load LLM function from {module_path}: {e}")

    def _detect_llm_backend(self) -> Callable[[str, str], str]:
        """
        自动检测可用的 LLM 后端
        
        Returns:
            LLM 调用函数
        """
        # 尝试导入 transformers（本地模型）
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
            import torch  # type: ignore
            
            if self.model_path:
                tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                model = AutoModelForCausalLM.from_pretrained(self.model_path)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model.to(device)
                
                def _call_local_llm(text: str, prompt: str) -> str:
                    full_prompt = prompt + "\n\n文本：" + text + "\n\n结果："
                    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
                    outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    return response.split("结果：")[-1].strip()
                
                return _call_local_llm
        except ImportError:
            pass
        
        # 如果没有找到可用的后端，抛出错误
        raise ValueError(
            "No LLM backend found. Please provide llm_call_func or install transformers."
        )

    def _load_model(self):
        """LLM 适配器不需要显式加载模型"""
        return self.llm_call_func

    def _build_prompt(self, text: str) -> str:
        """
        构建 LLM prompt
        
        Args:
            text: 待识别的文本
            
        Returns:
            prompt 字符串
        """
        schema_str = "、".join(self.schema)
        prompt = f"""请从以下文本中提取实体，实体类型包括：{schema_str}。

要求：
1. 返回 JSON 格式，格式如下：
{{
  "组织机构": [{{"text": "实体文本", "start": 起始位置, "end": 结束位置, "probability": 0.9}}],
  "人名": [{{"text": "实体文本", "start": 起始位置, "end": 结束位置, "probability": 0.9}}],
  "地点": [{{"text": "实体文本", "start": 起始位置, "end": 结束位置, "probability": 0.9}}]
}}

2. start 和 end 是实体在原文中的字符位置（从 0 开始）
3. 如果某个类型没有实体，返回空数组 []
4. 只返回 JSON，不要有其他文字说明

文本：{text}

结果："""
        return prompt

    def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用 LLM 提取实体
        
        Args:
            text: 待识别的文本
            
        Returns:
            Dict[str, List[Dict]]: 实体字典
        """
        prompt = self._build_prompt(text)
        
        # 调用 LLM
        response = self.llm_call_func(text, prompt)
        
        # 解析 JSON 响应
        try:
            # 尝试提取 JSON 部分（可能包含其他文本）
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            entities = json.loads(response)
            
            # 验证并标准化格式
            standardized = {}
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    standardized[entity_type] = []
                    for entity in entity_list:
                        if isinstance(entity, dict) and "text" in entity:
                            standardized[entity_type].append({
                                "text": entity["text"],
                                "start": entity.get("start", 0),
                                "end": entity.get("end", len(entity["text"])),
                                "probability": entity.get("probability", 0.9),
                            })
                else:
                    standardized[entity_type] = []
            
            return standardized
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Failed to parse LLM response: {e}")
            print(f"Response: {response}")
            return {}

    def _map_entity_type(self, raw_type: str) -> Optional[str]:
        """
        将 LLM 返回的实体类型映射到 Presidio 类型
        
        Args:
            raw_type: 原始实体类型
            
        Returns:
            Presidio 实体类型
        """
        return self.ENTITY_TYPE_MAPPING.get(raw_type)

"""
第四层：大模型"润色"与逻辑修复（LLM Refinement）

利用本地部署的 Teacher 模型做最后的兜底，处理前三层可能遗漏的实体。
"""

from typing import Dict, Optional


class LLMRefiner:
    """
    LLM 润色器：使用本地部署的模型进行最终检查和修复
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        初始化 LLM 润色器

        Args:
            model_path: 本地模型路径，如果为 None 则使用默认模型
        """
        self.model_path = model_path
        self._model = None

    @property
    def model(self):
        """懒加载模型"""
        if self._model is None:
            # TODO: 实现本地模型的加载逻辑
            # 这里需要根据实际使用的模型框架（如 transformers, llama.cpp 等）进行实现
            raise NotImplementedError(
                "LLM model loading is not implemented yet. "
                "Please implement according to your local model framework."
            )
        return self._model

    def refine(self, text: str, mapping: Dict[str, Dict[str, str]]) -> str:
        """
        使用 LLM 对文本进行润色和修复

        Args:
            text: 已经过前三层处理的文本
            mapping: 已有的映射表

        Returns:
            润色后的文本

        Note:
            这一步必须在本地部署的模型上运行，严禁调用公有云 API
        """
        prompt = self._build_prompt(text, mapping)

        # TODO: 实现模型推理逻辑
        # refined_text = self.model.generate(prompt)
        # return refined_text

        # 临时返回原文本，等待实现
        return text

    def _build_prompt(self, text: str, mapping: Dict[str, Dict[str, str]]) -> str:
        """
        构建 LLM 提示词

        Args:
            text: 待润色的文本
            mapping: 已有的映射表

        Returns:
            完整的提示词
        """
        prompt = f"""请检查以下文本，如果发现遗漏的真实公司名、人名或具体项目地址，请将其修改为虚拟名称，保持上下文一致，不要改变合同原意。

已有映射关系：
{mapping}

待检查文本：
{text}

请输出润色后的文本："""
        return prompt

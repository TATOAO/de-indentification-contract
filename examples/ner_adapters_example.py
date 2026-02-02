#!/usr/bin/env python3
"""
NER 适配器使用示例

演示如何使用不同的 NER 适配器：
1. ModelScope 适配器（推荐）
2. PaddleNLP 适配器（向后兼容）
3. LLM 适配器（使用大语言模型）
"""

from contract_deid.core.ner_engine import NEREngine

# 示例文本
sample_text = """
甲方：腾讯科技（深圳）有限公司
统一社会信用代码：91440300MA5D123456
法定代表人：马化腾
联系电话：13800138000
合同金额：人民币 1,000,000 元
项目地址：深圳市南山区科技园
"""


def example_modelscope():
    """使用 ModelScope 适配器（推荐）"""
    print("=" * 60)
    print("示例 1: 使用 ModelScope 适配器")
    print("=" * 60)
    
    # 使用默认 ModelScope 模型
    ner_engine = NEREngine(adapter_type="modelscope")
    
    # 或者指定特定的 ModelScope 模型
    # ner_engine = NEREngine(
    #     adapter_type="modelscope",
    #     model_name="damo/nlp_structbert_named-entity-recognition_chinese-base-ecommerce"
    # )
    
    results = ner_engine.analyze(sample_text)
    
    print(f"识别到 {len(results)} 个实体：")
    for result in results:
        entity_text = sample_text[result.start:result.end]
        print(f"  - {result.entity_type}: {entity_text} (位置: {result.start}-{result.end}, 置信度: {result.score:.2f})")
    print()


def example_paddlenlp():
    """使用 PaddleNLP 适配器（向后兼容）"""
    print("=" * 60)
    print("示例 2: 使用 PaddleNLP 适配器")
    print("=" * 60)
    
    ner_engine = NEREngine(adapter_type="paddlenlp")
    
    results = ner_engine.analyze(sample_text)
    
    print(f"识别到 {len(results)} 个实体：")
    for result in results:
        entity_text = sample_text[result.start:result.end]
        print(f"  - {result.entity_type}: {entity_text} (位置: {result.start}-{result.end}, 置信度: {result.score:.2f})")
    print()


def example_llm():
    """使用 LLM 适配器"""
    print("=" * 60)
    print("示例 3: 使用 LLM 适配器")
    print("=" * 60)
    
    # 需要提供 LLM 调用函数
    def llm_call_func(text: str, prompt: str) -> str:
        """
        自定义 LLM 调用函数
        
        这里是一个示例，实际使用时需要替换为真实的 LLM API 调用
        例如：OpenAI API、本地部署的模型等
        """
        # 示例：使用 OpenAI API（需要安装 openai 包）
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content
        
        # 或者使用本地模型（需要 transformers）
        # from transformers import AutoTokenizer, AutoModelForCausalLM
        # tokenizer = AutoTokenizer.from_pretrained("your-model-path")
        # model = AutoModelForCausalLM.from_pretrained("your-model-path")
        # inputs = tokenizer(prompt, return_tensors="pt")
        # outputs = model.generate(**inputs)
        # return tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        raise NotImplementedError("请实现 LLM 调用函数")
    
    try:
        ner_engine = NEREngine(
            adapter_type="llm",
            llm_call_func=llm_call_func
        )
        
        results = ner_engine.analyze(sample_text)
        
        print(f"识别到 {len(results)} 个实体：")
        for result in results:
            entity_text = sample_text[result.start:result.end]
            print(f"  - {result.entity_type}: {entity_text} (位置: {result.start}-{result.end}, 置信度: {result.score:.2f})")
    except NotImplementedError as e:
        print(f"⚠️  {e}")
        print("提示: 需要提供 LLM 调用函数才能使用 LLM 适配器")
    print()


def example_custom_schema():
    """使用自定义实体类型列表"""
    print("=" * 60)
    print("示例 4: 使用自定义实体类型列表")
    print("=" * 60)
    
    # 自定义实体类型
    custom_schema = ["组织机构", "人名", "地点", "金额"]
    
    ner_engine = NEREngine(
        adapter_type="modelscope",
        schema=custom_schema
    )
    
    results = ner_engine.analyze(sample_text)
    
    print(f"识别到 {len(results)} 个实体：")
    for result in results:
        entity_text = sample_text[result.start:result.end]
        print(f"  - {result.entity_type}: {entity_text} (位置: {result.start}-{result.end}, 置信度: {result.score:.2f})")
    print()


if __name__ == "__main__":
    print("\nNER 适配器使用示例\n")
    
    # 示例 1: ModelScope（推荐）
    try:
        example_modelscope()
    except Exception as e:
        print(f"⚠️  ModelScope 示例失败: {e}\n")
    
    # 示例 2: PaddleNLP（向后兼容）
    try:
        example_paddlenlp()
    except Exception as e:
        print(f"⚠️  PaddleNLP 示例失败: {e}\n")
    
    # 示例 3: LLM
    example_llm()
    
    # 示例 4: 自定义实体类型
    try:
        example_custom_schema()
    except Exception as e:
        print(f"⚠️  自定义实体类型示例失败: {e}\n")

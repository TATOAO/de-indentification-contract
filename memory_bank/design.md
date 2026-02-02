
# 合同脱敏

## 第一层：规则引擎（Regex & Pattern）— 解决“硬格式”
这一层处理所有格式固定的实体，准确率 100%，成本最低。

统一社会信用代码：正则匹配 18 位代码，替换为符合校验规则的随机 18 位代码。

身份证号：匹配 15/18 位数字，替换为生成的虚拟身份证号（需符合校验位算法，否则模型可能学会“身份证号最后一位不合法”这种错误逻辑）。

电话/手机/邮箱：正则匹配，使用 Python Faker 库生成虚拟数据替换。

银行账号：匹配常见的银行卡号格式进行替换。

金额/价格：这是一个特例。

策略：建议引入“高斯噪声”或“随机倍数”。例如，检测到合同内所有金额，统一乘以一个 0.8 到 1.2 之间的随机系数。

目的：保留了价格之间的比例逻辑（单价 x 数量 ≈ 总价），但掩盖了真实的商业底价。

## 第二层：NLP 实体识别（NER）— 解决“软实体”
合同里的公司名、人名、项目名、地址，没有固定格式，需要模型识别。

工具选择：建议使用轻量级的 BERT-NER 或专门的中文 NLP 工具包（如 HanLP、SpaCy 中文版）。

目标实体：

ORG（组织机构）：甲方、乙方、关联公司。

PER（人名）：法人代表、授权签字人。

LOC（地点）：项目地址、管辖法院地（重要！要把“北京市朝阳区法院”替换为“上海市浦东新区法院”，因为地域会影响法律管辖判断）。

替换策略：建立一个行业实体库。

准备 1000 个假的“科技公司”、“置业公司”、“贸易公司”名字。

识别到 ORG 后，从库里随机抽一个替换。

## 第三层：上下文一致性映射（Context Consistency Map）— 关键！
这是很多脱敏方案失败的地方。

问题：合同第一页叫“阿里巴巴”，你换成了“大山科技”；合同第十页又出现了“阿里巴巴”，如果 NER 把它换成了“绿水贸易”，合同逻辑就崩了（变成了三方合同）。

解决方案：

对每一份合同，在内存中维护一个 Session Mapping Dictionary。

Map = { "阿里巴巴": "大山科技", "马云": "张三" }

每识别到一个实体，先查 Map。如果有，用 Map 里的值；如果没有，生成新值并存入 Map。

处理完该合同后，销毁 Map。

## 第四层：大模型“润色”与逻辑修复（LLM Refinement）
前三层可能由漏网之鱼（比如“那个姓马的老板”这种指代）。利用你们强大的 Teacher 模型做最后的兜底。

Prompt：

“请检查以下文本，如果发现遗漏的真实公司名、人名或具体项目地址，请将其修改为虚拟名称，保持上下文一致，不要改变合同原意。”

注意：这一步要在本地部署的 Teacher 模型上跑，严禁将原始未脱敏数据发给 OpenAI 等公有云 API。


# 技术方案

利用**“Microsoft Presidio”作为骨架，集成“PaddleNLP/HanLP”作为大脑，再挂载“Faker”作为伪造器**，快速构建出这个流水线。这是目前工业界最成熟的落地路径。
以下是具体的选型建议和架构映射：

---
1. 核心框架选型：Microsoft Presidio
定位： 你的流水线“总线” (Pipeline Backbone)
微软开源的工业级 PII 保护框架，它的架构与你的设计高度吻合，完全解耦了“识别（Analyze）”和“处理（Anonymize）”。
- 为什么选它？
  - 架构解耦： 它将 Analyzer (找敏感词) 和 Anonymizer (替换敏感词) 分开，允许你自定义每一层的逻辑。
  - 支持自定义 Operator： 你可以轻松写一个 Python 函数（比如调用 Faker），替换掉默认的 *** 掩盖逻辑。
  - 多语言支持： 虽然原生对中文支持一般，但它允许插件式接入 SpaCy, Transformers 或 HanLP。
- 如何适配你的方案？
  - 利用它的 Deanonymize 或自定义 Operator 接口来实现你的 Layer 3（一致性映射）。
2. 第二层（NER）选型：PaddleNLP 或 ModelScope
定位： 解决中文法律实体识别 (The Brain)
Presidio 自带的 NLP 模型对中文人名、公司名识别较弱，你需要替换引擎。
- 推荐：PaddleNLP (百度)
  - 理由： 百度在中文 NLP 领域（特别是实体识别）表现极强。PaddleNLP 提供了针对法律领域（Legal NER）的预训练模型，能更好地区分“甲方”、“乙方”、“法院”等实体。
  - ModelScope (阿里达摩院) 也是极佳的选择，拥有大量针对中文垂直领域的 NER 模型。
- 如何集成？ 编写一个 Python 类继承 Presidio 的 NlpEngine，在内部调用 PaddleNLP 的 API 即可。
3. 第一层 & 第三层工具：Faker & Redis/Dict
定位： 假数据生成与状态管理
- Faker (faker.providers.company.zh_CN)： 这是生成“看起来像真的”数据的标准库。
- 一致性管理： Presidio 默认是无状态的（Stateless）。你需要写一个 Wrapper（包装器），在处理单份合同期间，维护一个 Dict 或 Redis 缓存，作为你的 Session Mapping Dictionary。

---
🚀 落地架构参考：基于 Presidio 的魔改方案
为了实现你的目标，不要从零写脚本，建议基于 Presidio 进行二次开发。以下是逻辑映射图：
核心代码逻辑（Python 伪代码）
这比你手写脚本更健壮，因为它利用了 Presidio 的并发处理和置信度评分机制。
Python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker

# 1. 准备假数据生成器
fake = Faker('zh_CN')

# 2. 状态保持 (Layer 3: Consistency Map)# 在处理一份合同时，这个 mapping 必须保持class ConsistencyProvider:def __init__(self):
        self.mapping = {}

    def replace_consistent(self, entity_text):if entity_text not in self.mapping:
            # 这里可以根据 entity 类型调用 fake.name() 或 fake.company()
            self.mapping[entity_text] = f"虚拟_{fake.company()}" 
        return self.mapping[entity_text]

# 3. 定义自定义替换逻辑 (Layer 1 & 2)def fake_replacement(x):# 这里接入你的 ConsistencyProviderreturn provider.replace_consistent(x.entity_text)

# 4. 执行流水线# 初始化 Presidio (假设已经配置好中文 NER 模型)
analyzer = AnalyzerEngine() 
anonymizer = AnonymizerEngine()

text = "腾讯科技（深圳）有限公司与阿里巴巴网络技术有限公司..."# Step 1: 识别 (Analyze)
results = analyzer.analyze(text=text, language='zh')

# Step 2: 替换 (Anonymize with Custom Operator)
anonymized_result = anonymizer.anonymize(
    text=text,
    analyzer_results=results,
    operators={
        "ORGANIZATION": OperatorConfig("custom", {"lambda": fake_replacement}),
        "PERSON": OperatorConfig("custom", {"lambda": fake_replacement}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": fake.phone_number()})
    }
)

print(anonymized_result.text)
# 输出: "海蓝科技（北京）有限公司与大山网络技术有限公司..."

---
⚠️ 现有方案的“巨坑”与补充
虽然有 Presidio，但你要特别注意以下两点，这通常是开源项目不覆盖的：
1. 地址的“法律效力”一致性（你的 Layer 2 细节）：
  - 现有的 Faker 生成的地址是随机的。但在法律合同中，如果原文是“北京市海淀区法院管辖”，你替换成“上海市黄浦区...”，可能会导致管辖权逻辑冲突。
  - 建议： 建立一个**“城市级别”**的映射表。如果原文是 北京，假数据必须也是 北京 或 一线城市A，且全篇保持该映射。不要完全随机化行政区划。
2. 金额逻辑（你的 Layer 1 特例）：
  - Presidio 不处理数字逻辑。你提到的 x 0.8~1.2 系数非常棒。
  - 实现： 这需要写一个专门的 PatternRecognizer 识别金额，并在 Operator 中传入一个函数，解析数字 -> 乘系数 -> 还原格式（保留千分位、小数点）。这是一个纯代码工作，没有现成库能直接做到“保持比例”。


# 最后呈现形式

## Package 设计目标

用户安装后，只需一行代码即可完成合同脱敏，同时获得：
1. **脱敏后的文本**：可直接用于模型训练或数据共享
2. **敏感数据映射表**：记录所有原始值与脱敏值的对应关系，便于后续追溯或审计

## 项目结构

```
contract-deidentification/
├── pyproject.toml          # 使用 uv init 创建，管理依赖和元数据
├── README.md               # 使用说明
├── LICENSE
├── src/
│   └── contract_deid/
│       ├── __init__.py     # 暴露主要 API
│       ├── core/
│       │   ├── analyzer.py      # 第一层：规则引擎
│       │   ├── ner_engine.py    # 第二层：NER 识别
│       │   ├── consistency.py   # 第三层：一致性映射
│       │   └── llm_refine.py    # 第四层：LLM 润色（可选）
│       ├── recognizers/
│       │   ├── credit_code.py   # 统一社会信用代码识别器
│       │   ├── id_card.py       # 身份证号识别器
│       │   ├── phone.py         # 电话/手机识别器
│       │   ├── bank_account.py  # 银行账号识别器
│       │   └── amount.py        # 金额识别器（带比例保持）
│       ├── anonymizers/
│       │   ├── faker_provider.py # Faker 数据生成器
│       │   └── entity_library.py # 行业实体库（1000+ 假公司名）
│       └── utils/
│           ├── location_mapper.py # 城市级别映射表
│           └── mapping_export.py  # 映射表导出工具
└── tests/
    └── test_deidentification.py
```

## 核心 API 设计

### 主要接口：`deidentify()`

```python
from contract_deid import deidentify

# 最简单的使用方式
result = deidentify(
    text="甲方：腾讯科技（深圳）有限公司，统一社会信用代码：91440300MA5D123456，..."
)

# result 包含：
# - result.anonymized_text: 脱敏后的文本
# - result.mapping: 敏感数据映射表（字典格式）
# - result.mapping_json: 映射表的 JSON 字符串
# - result.mapping_csv: 映射表的 CSV 格式（可选）
```

### 映射表结构

映射表是一个嵌套字典，按实体类型分类：

```python
{
    "ORGANIZATION": {
        "腾讯科技（深圳）有限公司": "海蓝科技（北京）有限公司",
        "阿里巴巴网络技术有限公司": "大山网络技术有限公司"
    },
    "PERSON": {
        "马云": "张三",
        "马化腾": "李四"
    },
    "CREDIT_CODE": {
        "91440300MA5D123456": "91110108MA01234567"
    },
    "ID_CARD": {
        "110101199001011234": "320101198512151234"
    },
    "PHONE_NUMBER": {
        "13800138000": "15912345678"
    },
    "AMOUNT": {
        "1000000": "950000",  # 乘以了 0.95 系数
        "500000": "475000"    # 保持比例关系
    },
    "LOCATION": {
        "北京市朝阳区": "上海市浦东新区",
        "深圳市南山区": "广州市天河区"
    }
}
```

### 高级配置选项

```python
from contract_deid import deidentify, DeidentificationConfig

config = DeidentificationConfig(
    # 金额处理策略
    amount_noise_range=(0.8, 1.2),  # 金额随机系数范围
    
    # 地址映射策略
    location_preserve_level=True,   # 保持城市级别一致性（北京 -> 北京或上海）
    
    # LLM 润色（可选）
    enable_llm_refinement=False,    # 默认关闭，需要本地部署 Teacher 模型
    llm_model_path=None,            # 本地模型路径
    
    # 输出格式
    export_mapping_csv=True,        # 是否导出 CSV 格式映射表
    mapping_file_path=None          # 映射表保存路径（可选）
)

result = deidentify(
    text=long_contract_text,
    config=config
)
```

## 使用示例

### 示例 1：基础使用

```python
from contract_deid import deidentify

contract_text = """
甲方：腾讯科技（深圳）有限公司
统一社会信用代码：91440300MA5D123456
法定代表人：马化腾
联系电话：13800138000
合同金额：人民币 1,000,000 元
项目地址：深圳市南山区科技园
"""

result = deidentify(contract_text)

print("脱敏后文本：")
print(result.anonymized_text)
print("\n敏感数据映射表：")
print(result.mapping_json)
```

### 示例 2：批量处理 + 导出映射表

```python
from contract_deid import deidentify, DeidentificationConfig
import json

config = DeidentificationConfig(
    export_mapping_csv=True,
    mapping_file_path="./mappings/contract_001.json"
)

contracts = [
    "合同1的文本...",
    "合同2的文本...",
    "合同3的文本..."
]

results = []
for i, contract in enumerate(contracts):
    result = deidentify(contract, config=config)
    results.append({
        "contract_id": f"contract_{i+1}",
        "anonymized_text": result.anonymized_text,
        "mapping": result.mapping
    })

# 保存所有映射表
with open("all_mappings.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 示例 3：命令行工具（CLI）

安装后自动提供命令行接口：

```bash
# 处理单个文件
contract-deid input.txt -o output.txt --mapping mapping.json

# 批量处理目录
contract-deid --batch ./contracts/ --output ./anonymized/ --mappings ./mappings/

# 查看帮助
contract-deid --help
```

## 安装与依赖

### 使用 uv 初始化项目

```bash
uv init contract-deidentification
cd contract-deidentification
```

### pyproject.toml 核心依赖

```toml
[project]
name = "contract-deidentification"
version = "0.1.0"
description = "合同文本脱敏工具，支持四层脱敏策略"
requires-python = ">=3.9"
dependencies = [
    "presidio-analyzer>=2.2.0",
    "presidio-anonymizer>=2.2.0",
    "faker>=20.0.0",
    "paddlenlp>=2.6.0",  # 或 modelscope
    "pandas>=2.0.0",     # 用于 CSV 导出
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
contract-deid = "contract_deid.cli:main"
```

### 安装方式

```bash
# 开发模式安装
uv pip install -e .

# 生产环境安装
uv pip install contract-deidentification

# 或从源码安装
git clone <repo>
cd contract-deidentification
uv pip install .
```

## 输出格式说明

### 1. 脱敏文本（字符串）

直接返回脱敏后的完整文本，保持原格式和结构。

### 2. 映射表（多种格式）

- **Python 字典**：`result.mapping` - 程序内使用
- **JSON 字符串**：`result.mapping_json` - 便于存储和传输
- **CSV 文件**：`result.mapping_csv` - 便于 Excel 查看和审计
- **JSON 文件**：通过 `config.mapping_file_path` 指定路径保存

### CSV 映射表示例

```csv
entity_type,original_value,anonymized_value,position_start,position_end
ORGANIZATION,腾讯科技（深圳）有限公司,海蓝科技（北京）有限公司,5,20
CREDIT_CODE,91440300MA5D123456,91110108MA01234567,45,63
PERSON,马化腾,张三,75,78
PHONE_NUMBER,13800138000,15912345678,90,101
AMOUNT,1000000,950000,110,117
LOCATION,深圳市南山区,广州市天河区,125,132
```

## 性能与扩展性

- **单文档处理**：支持任意长度的合同文本（通过流式处理大文件）
- **批量处理**：提供 `batch_deidentify()` 函数，支持多进程并行
- **内存管理**：每份合同处理完成后自动清理 Session Mapping，避免内存泄漏
- **模型缓存**：NER 模型首次加载后缓存，后续调用无需重复加载

## 安全注意事项

1. **本地处理**：所有敏感数据在本地处理，不会上传到云端
2. **映射表加密**（可选）：支持对映射表进行加密存储
3. **日志脱敏**：内部日志自动脱敏，避免敏感信息泄露
4. **LLM 调用**：第四层 LLM 润色必须在本地部署的模型上运行，严禁调用公有云 API

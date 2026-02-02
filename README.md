# 合同脱敏工具 (Contract Deidentification)

一个专业的合同文本脱敏工具，支持四层脱敏策略，确保敏感信息的安全处理。

## 功能特性

### 四层脱敏策略

1. **第一层：规则引擎（Regex & Pattern）**
   - 统一社会信用代码识别与替换
   - 身份证号识别与替换（符合校验规则）
   - 电话/手机/邮箱识别与替换
   - 银行账号识别与替换
   - 金额识别与比例保持（乘以随机系数，保持价格逻辑）

2. **第二层：NLP 实体识别（NER）**
   - 使用 PaddleNLP 识别中文法律实体
   - 组织机构（ORG）：甲方、乙方、关联公司
   - 人名（PER）：法人代表、授权签字人
   - 地点（LOC）：项目地址、管辖法院地

3. **第三层：上下文一致性映射**
   - 确保同一实体在整个文档中映射一致
   - 维护 Session Mapping Dictionary
   - 避免合同逻辑冲突

4. **第四层：LLM 润色与逻辑修复（可选）**
   - 使用本地部署的模型进行最终检查
   - 处理前三层可能遗漏的实体
   - 保持上下文一致性

## 安装

### 使用 uv（推荐）

```bash
# 克隆仓库
git clone <repo>
cd contract-deidentification

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -e .
```

### 使用 pip

```bash
pip install contract-deidentification
```

## 快速开始

### 基础使用

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

### 高级配置

```python
from contract_deid import deidentify, DeidentificationConfig

config = DeidentificationConfig(
    # 金额处理策略
    amount_noise_range=(0.8, 1.2),  # 金额随机系数范围
    
    # 地址映射策略
    location_preserve_level=True,   # 保持城市级别一致性
    
    # LLM 润色（可选）
    enable_llm_refinement=False,    # 默认关闭
    llm_model_path=None,            # 本地模型路径
    
    # 输出格式
    export_mapping_csv=True,        # 是否导出 CSV 格式映射表
    mapping_file_path="./mapping.json"  # 映射表保存路径
)

result = deidentify(contract_text, config=config)
```

### 命令行工具

```bash
# 处理单个文件
contract-deid input.txt -o output.txt --mapping mapping.json

# 批量处理目录
contract-deid --batch ./contracts/ --output-dir ./anonymized/ --mappings-dir ./mappings/

# 查看帮助
contract-deid --help
```

## 输出格式

### 脱敏文本

直接返回脱敏后的完整文本，保持原格式和结构。

### 映射表

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

支持多种格式：
- **Python 字典**：`result.mapping`
- **JSON 字符串**：`result.mapping_json`
- **CSV 文件**：`result.mapping_csv`
- **JSON 文件**：通过 `config.mapping_file_path` 指定路径保存

## 项目结构

```
contract-deidentification/
├── pyproject.toml          # 项目配置
├── README.md               # 使用说明
├── src/
│   └── contract_deid/
│       ├── __init__.py     # 主 API
│       ├── cli.py          # 命令行工具
│       ├── core/           # 核心模块
│       │   ├── analyzer.py      # 脱敏引擎
│       │   ├── ner_engine.py    # NER 识别
│       │   ├── consistency.py   # 一致性映射
│       │   └── llm_refine.py   # LLM 润色
│       ├── recognizers/    # 识别器
│       │   ├── credit_code.py
│       │   ├── id_card.py
│       │   ├── phone.py
│       │   ├── bank_account.py
│       │   └── amount.py
│       ├── anonymizers/    # 匿名化器
│       │   ├── faker_provider.py
│       │   └── entity_library.py
│       └── utils/          # 工具
│           ├── location_mapper.py
│           └── mapping_export.py
└── tests/                  # 测试
    └── test_deidentification.py
```

## 依赖

- `presidio-analyzer>=2.2.0` - 核心分析框架
- `presidio-anonymizer>=2.2.0` - 匿名化框架
- `faker>=20.0.0` - 虚拟数据生成
- `paddlenlp>=2.6.0` - 中文 NER
- `pandas>=2.0.0` - CSV 导出

## 安全注意事项

1. **本地处理**：所有敏感数据在本地处理，不会上传到云端
2. **映射表加密**（可选）：支持对映射表进行加密存储
3. **日志脱敏**：内部日志自动脱敏，避免敏感信息泄露
4. **LLM 调用**：第四层 LLM 润色必须在本地部署的模型上运行，严禁调用公有云 API

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

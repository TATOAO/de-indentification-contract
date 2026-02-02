# 合同脱敏工具 (Contract Deidentification)

一个专业的合同文本脱敏工具，支持四层脱敏策略，确保敏感信息的安全处理。

## Progress

### 开发计划与里程碑

#### 四层脱敏策略开发进度

| 层级 | 功能模块 | 状态 | 完成度 | 备注 |
|------|---------|------|--------|------|
| **第一层** | 规则引擎框架 | ✅ 已完成 | 100% | Presidio Analyzer 集成完成 |
| | 统一社会信用代码识别 | ✅ 已完成 | 90% | 基础识别完成，校验位算法待完善 |
| | 身份证号识别 | ✅ 已完成 | 95% | 15/18位识别，校验位算法已实现 |
| | 电话/手机/邮箱识别 | ✅ 已完成 | 100% | 正则匹配 + Faker 替换 |
| | 银行账号识别 | ✅ 已完成 | 85% | 基础识别完成，Luhn算法验证待添加 |
| | 金额识别与比例保持 | ✅ 已完成 | 80% | 基础功能完成，中文数字转换待实现 |
| **第二层** | NER 引擎框架 | ✅ 已完成 | 100% | PaddleNLP 集成完成 |
| | 组织机构识别（ORG） | ✅ 已完成 | 100% | 使用 PaddleNLP UIE 模型 |
| | 人名识别（PER） | ✅ 已完成 | 100% | 使用 PaddleNLP UIE 模型 |
| | 地点识别（LOC） | ✅ 已完成 | 100% | 使用 PaddleNLP UIE 模型 |
| **第三层** | 一致性映射框架 | ✅ 已完成 | 100% | Session Mapping Dictionary 实现完成 |
| | 实体映射一致性 | ✅ 已完成 | 100% | 同一文档内实体映射保持一致 |
| | 映射表导出（JSON/CSV） | ✅ 已完成 | 100% | 支持多种格式导出 |
| **第四层** | LLM 润色框架 | 🚧 进行中 | 30% | 框架已搭建，模型加载待实现 |
| | 本地模型集成 | ⏳ 待开发 | 0% | 需要根据实际模型框架实现 |
| | 逻辑修复与兜底 | ⏳ 待开发 | 0% | 等待模型集成后实现 |

#### 核心功能模块进度

| 模块 | 状态 | 完成度 | 说明 |
|------|------|--------|------|
| **核心引擎** | ✅ 已完成 | 95% | DeidentificationEngine 核心流程已实现 |
| **CLI 工具** | ✅ 已完成 | 100% | 命令行接口已实现 |
| **配置系统** | ✅ 已完成 | 100% | DeidentificationConfig 配置类完成 |
| **实体库** | ✅ 已完成 | 80% | 基础实体库完成，支持扩展加载 |
| **地址映射** | ✅ 已完成 | 100% | 城市级别映射表已实现 |
| **测试框架** | ✅ 已完成 | 90% | 基础测试用例已覆盖主要功能 |

### 当前版本状态

**版本**: `0.1.0` (Alpha)

**总体完成度**: ~85%

### 下一步计划

#### 短期目标（v0.2.0）
- [ ] 完善统一社会信用代码校验位算法
- [ ] 添加银行卡号 Luhn 算法验证
- [ ] 实现中文数字转阿拉伯数字功能
- [ ] 扩展实体库，支持从文件/数据库加载
- [ ] 完善测试覆盖率

#### 中期目标（v0.3.0）
- [ ] 实现 LLM 润色层的本地模型集成
- [ ] 添加批量处理性能优化
- [ ] 实现映射表加密功能
- [ ] 添加日志脱敏功能

#### 长期目标（v1.0.0）
- [ ] 完整的文档和示例
- [ ] 性能基准测试
- [ ] 生产环境稳定性优化
- [ ] 多语言支持扩展

### 已知问题与待办事项

- ⚠️ 统一社会信用代码校验位算法需要完善（`credit_code.py`, `faker_provider.py`）
- ⚠️ 银行卡号 Luhn 算法验证待添加（`bank_account.py`）
- ⚠️ 中文数字转阿拉伯数字功能待实现（`amount.py`）
- ⚠️ LLM 润色层需要根据实际模型框架实现（`llm_refine.py`）
- 📝 实体库支持从文件/数据库加载更多数据（`entity_library.py`）

## 功能特性

### 四层脱敏策略

1. **第一层：规则引擎（Regex & Pattern）**
   - 统一社会信用代码识别与替换
   - 身份证号识别与替换（符合校验规则）
   - 电话/手机/邮箱识别与替换
   - 银行账号识别与替换
   - 金额识别与比例保持（乘以随机系数，保持价格逻辑）

2. **第二层：NLP 实体识别（NER）**
   - 使用适配器模式支持多种 NER 后端：
     - **ModelScope**（推荐）：模型下载更稳定
     - **PaddleNLP**：向后兼容
     - **LLM**：支持使用大语言模型进行实体抽取
   - 识别中文法律实体：
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

### 模型配置

项目支持通过 `.env` 文件配置模型相关选项。首先复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，配置你需要的选项：

```bash
# 选择适配器类型（推荐使用 modelscope）
NER_ADAPTER_TYPE=modelscope

# 指定模型名称（可选）
# NER_MODEL_NAME=damo/nlp_structbert_named-entity-recognition_chinese-base-ecommerce

# 指定本地模型路径（如果已下载）
# NER_MODEL_PATH=/path/to/your/model

# 自定义实体类型列表（可选）
# NER_SCHEMA=["组织机构", "人名", "地点"]
```

### 模型下载

项目使用 ModelScope 下载 NER 模型（推荐），也支持 PaddleNLP（向后兼容）。模型会下载到项目的 `./models/` 目录：

```bash
# 方法 1: 使用下载脚本下载 ModelScope 模型（推荐）
python scripts/download_models.py --backend modelscope

# 方法 2: 下载 PaddleNLP 模型（向后兼容）
python scripts/download_models.py --backend paddlenlp

# 方法 3: 模型会在首次使用时自动下载到 ./models/ 目录
# 只需运行一次代码即可触发下载
```

**模型位置**:
- ModelScope: `./models/modelscope/`
- PaddleNLP: `./models/taskflow/information_extraction/uie-base/`

详细说明请参考 [models/README.md](models/README.md)

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

#### 使用环境变量配置（推荐）

创建 `.env` 文件来配置模型选项：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
# NER_ADAPTER_TYPE=modelscope
# NER_MODEL_NAME=your-model-name
# NER_MODEL_PATH=/path/to/model
```

#### 使用代码配置

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

#### 使用不同的 NER 适配器

```python
from contract_deid.core.ner_engine import NEREngine

# 使用 ModelScope 适配器（推荐，默认）
ner_engine = NEREngine(adapter_type="modelscope")

# 使用 PaddleNLP 适配器（向后兼容）
ner_engine = NEREngine(adapter_type="paddlenlp")

# 使用 LLM 适配器
def my_llm_call(text: str, prompt: str) -> str:
    # 实现你的 LLM 调用逻辑
    pass

ner_engine = NEREngine(
    adapter_type="llm",
    llm_call_func=my_llm_call
)

# 识别实体
results = ner_engine.analyze("测试文本：北京是中国的首都。")
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

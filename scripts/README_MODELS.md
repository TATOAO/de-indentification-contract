# 模型下载说明

本项目使用 PaddleNLP 的 UIE 模型进行实体识别。

## 自动下载（推荐）

运行下载脚本：

```bash
source .venv/bin/activate
python scripts/download_models.py
```

模型将自动下载到 `models/` 目录。

## 手动下载方法

如果自动下载失败，可以使用以下方法手动下载：

### 方法 1: 使用 PaddleNLP Taskflow（自动下载）

PaddleNLP 的 Taskflow 在首次使用时会自动下载模型。只需运行一次代码即可：

```python
from paddlenlp import Taskflow

# 设置模型保存目录
import os
os.environ["PADDLE_HOME"] = "./models"

# 初始化 Taskflow，会自动下载模型
taskflow = Taskflow(
    "information_extraction",
    schema=["组织机构", "人名", "地点"],
    model="uie-base",
)

# 测试
result = taskflow("测试文本：北京是中国的首都。")
print(result)
```

### 方法 2: 使用 Hugging Face

PaddleNLP 的 UIE 模型也可以从 Hugging Face 下载：

```bash
# 安装 huggingface_hub
uv pip install huggingface_hub

# 下载模型
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='PaddlePaddle/uie-base',
    local_dir='./models/uie-base',
    local_dir_use_symlinks=False
)
"
```

### 方法 3: 直接使用（让 PaddleNLP 自动管理）

如果不指定模型路径，PaddleNLP 会自动下载模型到默认缓存目录（通常是 `~/.paddlenlp/models/`）。

## 模型目录结构

下载后的模型目录结构：

```
models/
└── uie-base/
    ├── model_state.pdparams
    ├── tokenizer_config.json
    └── ...
```

## 注意事项

1. 模型文件较大（约几百MB），首次下载需要一些时间
2. `models/` 目录已在 `.gitignore` 中配置，不会被提交到 Git
3. 如果下载失败，请检查网络连接或使用代理

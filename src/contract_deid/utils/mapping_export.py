"""
映射表导出工具

提供多种格式的映射表导出功能：
- Python 字典
- JSON 字符串
- CSV 文件
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None


@dataclass
class DeidentificationConfig:
    """
    脱敏配置类
    """

    # 金额处理策略
    amount_noise_range: Tuple[float, float] = (0.8, 1.2)

    # 地址映射策略
    location_preserve_level: bool = True

    # NER 启用
    enable_ner: bool = True

    # LLM 润色（可选）
    enable_llm_refinement: bool = False
    llm_model_path: Optional[str] = None

    # 输出格式
    export_mapping_csv: bool = True
    mapping_file_path: Optional[str] = None


@dataclass
class DeidentificationResult:
    """
    脱敏结果类
    """

    anonymized_text: str
    mapping: Dict[str, Dict[str, str]]
    config: DeidentificationConfig

    def __post_init__(self):
        """初始化后处理"""
        # 如果配置了保存路径，自动保存映射表
        if self.config.mapping_file_path:
            self.save_mapping(self.config.mapping_file_path)

    @property
    def mapping_json(self) -> str:
        """
        获取映射表的 JSON 字符串

        Returns:
            JSON 格式的映射表
        """
        return json.dumps(self.mapping, ensure_ascii=False, indent=2)

    @property
    def mapping_csv(self) -> str:
        """
        获取映射表的 CSV 格式字符串

        Returns:
            CSV 格式的映射表
        """
        if pd is None:
            raise ImportError("pandas is required for CSV export. Install it with: pip install pandas")

        # 将嵌套字典转换为扁平列表
        rows = []
        for entity_type, mappings in self.mapping.items():
            for original_value, anonymized_value in mappings.items():
                rows.append(
                    {
                        "entity_type": entity_type,
                        "original_value": original_value,
                        "anonymized_value": anonymized_value,
                    }
                )

        df = pd.DataFrame(rows)
        return df.to_csv(index=False, encoding="utf-8-sig")

    def save_mapping(self, file_path: str):
        """
        保存映射表到文件

        Args:
            file_path: 文件路径，支持 .json 和 .csv 格式
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix.lower() == ".json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.mapping, f, ensure_ascii=False, indent=2)
        elif path.suffix.lower() == ".csv":
            if pd is None:
                raise ImportError("pandas is required for CSV export")
            csv_content = self.mapping_csv
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write(csv_content)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .csv")

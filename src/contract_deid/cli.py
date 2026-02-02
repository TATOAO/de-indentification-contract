"""
命令行工具（CLI）

提供命令行接口，支持单文件和批量处理
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from contract_deid import deidentify, DeidentificationConfig


def main():
    """CLI 主函数"""
    parser = argparse.ArgumentParser(
        description="合同文本脱敏工具，支持四层脱敏策略",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 输入输出选项
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        help="输入文件路径或文本（如果不指定则从标准输入读取）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="输出文件路径（如果不指定则输出到标准输出）",
    )
    parser.add_argument(
        "--mapping",
        type=str,
        help="映射表保存路径（JSON 或 CSV 格式）",
    )

    # 批量处理选项
    parser.add_argument(
        "--batch",
        type=str,
        help="批量处理目录路径",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="批量处理输出目录",
    )
    parser.add_argument(
        "--mappings-dir",
        type=str,
        help="批量处理映射表保存目录",
    )

    # 配置选项
    parser.add_argument(
        "--amount-noise-range",
        type=float,
        nargs=2,
        metavar=("MIN", "MAX"),
        default=[0.8, 1.2],
        help="金额随机系数范围（默认：0.8 1.2）",
    )
    parser.add_argument(
        "--no-location-preserve",
        action="store_false",
        dest="location_preserve_level",
        help="不保持城市级别一致性",
    )
    parser.add_argument(
        "--disable-ner",
        action="store_false",
        dest="enable_ner",
        help="禁用 NER 识别（仅使用规则引擎）",
    )
    parser.add_argument(
        "--enable-llm",
        action="store_true",
        help="启用 LLM 润色（需要指定模型路径）",
    )
    parser.add_argument(
        "--llm-model-path",
        type=str,
        help="LLM 模型路径（启用 LLM 润色时必需）",
    )

    args = parser.parse_args()

    # 创建配置
    config = DeidentificationConfig(
        amount_noise_range=tuple(args.amount_noise_range),
        location_preserve_level=args.location_preserve_level,
        enable_ner=args.enable_ner,
        enable_llm_refinement=args.enable_llm,
        llm_model_path=args.llm_model_path,
        export_mapping_csv=True,
        mapping_file_path=args.mapping,
    )

    # 批量处理模式
    if args.batch:
        batch_process(args.batch, args.output_dir, args.mappings_dir, config)
        return

    # 单文件处理模式
    # 读取输入
    if args.input:
        if Path(args.input).is_file():
            with open(args.input, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            # 直接作为文本处理
            text = args.input
    else:
        # 从标准输入读取
        text = sys.stdin.read()

    # 执行脱敏
    try:
        result = deidentify(text, config=config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.anonymized_text)
    else:
        print(result.anonymized_text)

    # 输出映射表（如果指定了路径但不在配置中）
    if args.mapping and not config.mapping_file_path:
        result.save_mapping(args.mapping)


def batch_process(
    input_dir: str,
    output_dir: str | None,
    mappings_dir: str | None,
    config: DeidentificationConfig,
):
    """
    批量处理目录中的文件

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        mappings_dir: 映射表保存目录
        config: 脱敏配置
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # 创建输出目录
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = None

    if mappings_dir:
        mappings_path = Path(mappings_dir)
        mappings_path.mkdir(parents=True, exist_ok=True)
    else:
        mappings_path = None

    # 查找所有文本文件
    text_files = list(input_path.glob("*.txt")) + list(input_path.glob("*.md"))

    if not text_files:
        print(f"Warning: No text files found in {input_dir}", file=sys.stderr)
        return

    # 处理每个文件
    results = []
    for file_path in text_files:
        print(f"Processing: {file_path.name}", file=sys.stderr)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # 更新配置中的映射表路径
            if mappings_path:
                config.mapping_file_path = str(mappings_path / f"{file_path.stem}_mapping.json")
            else:
                config.mapping_file_path = None

            # 执行脱敏
            result = deidentify(text, config=config)

            # 保存输出文件
            if output_path:
                output_file = output_path / f"{file_path.stem}_anonymized{file_path.suffix}"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result.anonymized_text)

            results.append(
                {
                    "file": file_path.name,
                    "anonymized_text": result.anonymized_text,
                    "mapping": result.mapping,
                }
            )

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}", file=sys.stderr)
            continue

    # 保存汇总结果
    if mappings_path:
        summary_file = mappings_path / "batch_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nProcessed {len(results)} files", file=sys.stderr)


if __name__ == "__main__":
    main()

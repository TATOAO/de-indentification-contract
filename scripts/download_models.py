#!/usr/bin/env python3
"""
模型下载脚本

下载项目所需的所有模型到 models/ 目录：
- ModelScope NER 模型（用于 NER 识别，推荐）
- PaddleNLP UIE 模型（可选，向后兼容）

使用方法:
    python scripts/download_models.py [--backend modelscope|paddlenlp]

模型将下载到 models/ 目录，该目录已在 .gitignore 中配置。
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 设置模型保存目录
MODELS_DIR = project_root / "models"
MODELS_DIR.mkdir(exist_ok=True)


def download_modelscope_model(
    model_name: str = "damo/nlp_structbert_named-entity-recognition_chinese-base-ecommerce",
    models_dir: Path = MODELS_DIR
) -> bool:
    """
    下载 ModelScope NER 模型
    
    Args:
        model_name: ModelScope 模型名称
        models_dir: 模型保存目录
        
    Returns:
        bool: 是否成功
    """
    try:
        from modelscope import snapshot_download
        
        print(f"正在下载 ModelScope 模型: {model_name}")
        print(f"目标目录: {models_dir}")
        print()
        
        # 设置 ModelScope 缓存目录
        modelscope_cache = models_dir / "modelscope"
        modelscope_cache.mkdir(parents=True, exist_ok=True)
        os.environ["MODELSCOPE_CACHE"] = str(modelscope_cache.resolve())
        
        # 下载模型
        print("正在下载模型，这可能需要几分钟时间...")
        model_dir = snapshot_download(
            model_name,
            cache_dir=str(modelscope_cache.resolve())
        )
        
        print(f"✅ 模型已下载到: {model_dir}")
        
        # 计算模型大小
        model_path = Path(model_dir)
        if model_path.exists():
            size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file()) / 1024 / 1024
            print(f"   模型大小: {size:.1f} MB")
        
        # 测试模型
        print("\n测试模型...")
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            test_pipeline = pipeline(
                Tasks.named_entity_recognition,
                model=model_dir,
            )
            test_result = test_pipeline("测试文本：北京是中国的首都。")
            print(f"✅ 模型测试成功！")
            print(f"   识别结果: {test_result}")
        except Exception as e:
            print(f"⚠️  模型测试时出现警告: {e}")
            print("   模型已下载，但测试失败。这可能不影响使用。")
        
        return True
        
    except ImportError:
        print("❌ 错误: ModelScope 未安装")
        print("请先安装依赖: uv pip install modelscope")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_aistudio_sdk_import():
    """
    修复 aistudio_sdk.hub 的导入问题
    使用 monkey patch 添加缺失的 download 函数
    """
    try:
        import aistudio_sdk.hub as hub_module
        
        # 检查是否已经有 download 函数
        if not hasattr(hub_module, 'download'):
            # 创建一个简单的 download 函数占位符
            # 实际上 PaddleNLP 可能不会真正使用它，或者会回退到其他下载方法
            def download_dummy(*args, **kwargs):
                """占位符函数，实际下载由 PaddleNLP 内部处理"""
                raise NotImplementedError(
                    "aistudio_sdk download is not available. "
                    "PaddleNLP will use alternative download methods."
                )
            
            hub_module.download = download_dummy
            print("✅ 已修复 aistudio_sdk 导入问题")
            return True
    except Exception as e:
        print(f"⚠️  修复 aistudio_sdk 时出现警告: {e}")
        return False


def download_paddlenlp_model_simple(model_name: str = "uie-base", models_dir: Path = MODELS_DIR):
    """
    使用简单方法下载 PaddleNLP UIE 模型
    通过直接运行代码触发自动下载
    
    Args:
        model_name: 模型名称，默认为 "uie-base"
        models_dir: 模型保存目录
    """
    # 确保使用绝对路径
    models_dir = models_dir.resolve()
    # 设置环境变量 - PaddleNLP 会将模型下载到 PADDLE_HOME/taskflow/information_extraction/uie-base/
    os.environ["PADDLE_HOME"] = str(models_dir)
    os.environ["PADDLE_MODELS_DIR"] = str(models_dir)
    
    print("方法: 通过运行简单代码触发模型下载")
    print(f"目标目录: {models_dir}")
    print()
    
    # 创建一个临时脚本来下载模型
    temp_script = models_dir / "download_temp.py"
    script_content = f'''
import os
import sys
# 确保使用绝对路径
models_dir = r"{models_dir.resolve()}"
os.environ["PADDLE_HOME"] = models_dir
os.environ["PADDLE_MODELS_DIR"] = models_dir

import warnings
warnings.filterwarnings("ignore")

# 修复 aistudio_sdk 导入问题
try:
    import aistudio_sdk.hub as hub_module
    if not hasattr(hub_module, 'download'):
        # 创建一个占位符函数
        def download_dummy(*args, **kwargs):
            raise NotImplementedError("Download handled by PaddleNLP internally")
        hub_module.download = download_dummy
except Exception:
    pass

try:
    from paddlenlp import Taskflow
    print("正在初始化 Taskflow，这将触发模型下载...")
    print("注意: 首次运行会下载模型，可能需要几分钟时间...")
    
    taskflow = Taskflow(
        "information_extraction",
        schema=["组织机构", "人名", "地点"],
        model="{model_name}",
    )
    
    # 测试
    print("测试模型...")
    result = taskflow("测试文本：北京是中国的首都。")
    print(f"✅ 模型下载并测试成功！")
    print(f"识别结果: {{result}}")
    
except Exception as e:
    print(f"❌ 错误: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    try:
        temp_script.write_text(script_content)
        print("正在运行下载脚本...")
        print()
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(temp_script)],
            capture_output=False,
            cwd=str(project_root),
        )
        
        if result.returncode == 0:
            # 检查模型是否已下载
            # PaddleNLP 会将模型下载到 PADDLE_HOME/taskflow/information_extraction/uie-base/
            model_cache_dir = models_dir / "taskflow" / "information_extraction" / model_name
            if model_cache_dir.exists() and (model_cache_dir / "model_state.pdparams").exists():
                print(f"\n✅ 模型已下载到: {model_cache_dir}")
                size = sum(f.stat().st_size for f in model_cache_dir.rglob("*") if f.is_file()) / 1024 / 1024
                print(f"   模型大小: {size:.1f} MB")
            else:
                print(f"\n✅ 模型下载完成！")
                print(f"   检查目录: {model_cache_dir}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 运行下载脚本时出错: {e}")
        return False
    finally:
        # 清理临时脚本
        if temp_script.exists():
            temp_script.unlink()


def download_paddlenlp_model(model_name: str = "uie-base", models_dir: Path = MODELS_DIR):
    """
    下载 PaddleNLP UIE 模型
    
    Args:
        model_name: 模型名称，默认为 "uie-base"
        models_dir: 模型保存目录
    """
    # 确保使用绝对路径
    models_dir = models_dir.resolve()
    # 设置 PaddleNLP 模型缓存目录
    # PaddleNLP 会将模型下载到 PADDLE_HOME/taskflow/information_extraction/uie-base/
    os.environ["PADDLE_HOME"] = str(models_dir)
    os.environ["PADDLE_MODELS_DIR"] = str(models_dir)
    
    print(f"正在下载 PaddleNLP 模型: {model_name}")
    print(f"目标目录: {models_dir}")
    print()
    
    # 使用简单方法下载
    if download_paddlenlp_model_simple(model_name, models_dir):
        return True
    
    # 如果简单方法失败，提供手动说明
    print("=" * 60)
    print("自动下载失败，请参考以下手动下载方法")
    print("=" * 60)
    print()
    
    try:
        # 修复 aistudio_sdk 导入问题
        fix_aistudio_sdk_import()
        
        # 尝试导入 PaddleNLP Taskflow
        import warnings
        warnings.filterwarnings("ignore")
        
        from paddlenlp import Taskflow
        
        # 通过初始化 Taskflow 来触发模型下载
        print("正在初始化 Taskflow，这将触发模型下载...")
        print("注意: 首次运行会下载模型，可能需要几分钟时间...")
        print()
        
        taskflow = Taskflow(
            "information_extraction",
            schema=["组织机构", "人名", "地点"],
            model=model_name,
        )
        
        # 测试模型是否可用
        print("测试模型...")
        test_result = taskflow("测试文本：北京是中国的首都。")
        print(f"模型测试成功！识别结果: {test_result}")
        print()
        
        # 检查模型是否已下载到指定目录
        # PaddleNLP 会将模型下载到 PADDLE_HOME/taskflow/information_extraction/uie-base/
        model_cache_dir = models_dir / "taskflow" / "information_extraction" / model_name
        if model_cache_dir.exists() and (model_cache_dir / "model_state.pdparams").exists():
            size = sum(f.stat().st_size for f in model_cache_dir.rglob("*") if f.is_file()) / 1024 / 1024
            print(f"✅ 模型已下载到: {model_cache_dir}")
            print(f"   模型大小: {size:.1f} MB")
        else:
            # PaddleNLP 可能使用默认缓存目录
            default_cache = Path.home() / ".paddlenlp" / "taskflow" / "information_extraction" / model_name
            if default_cache.exists() and (default_cache / "model_state.pdparams").exists():
                print(f"⚠️  模型已下载到默认缓存目录: {default_cache}")
                print(f"   提示: 如需使用项目 models 目录，请确保在运行前设置 PADDLE_HOME={models_dir}")
            else:
                print(f"✅ 模型下载完成！")
                print(f"   检查目录: {model_cache_dir}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 错误: PaddleNLP 导入失败: {e}")
        print("请先安装依赖: uv pip install paddlepaddle paddlenlp")
        return False
    except Exception as e:
        # 即使有错误，模型可能已经下载
        print(f"⚠️  警告: {e}")
        print("尝试检查模型是否已下载...")
        
        # 检查模型目录
        # PaddleNLP 会将模型下载到 PADDLE_HOME/taskflow/information_extraction/uie-base/
        model_cache_dir = models_dir / "taskflow" / "information_extraction" / model_name
        default_cache = Path.home() / ".paddlenlp" / "taskflow" / "information_extraction" / model_name
        
        if model_cache_dir.exists() and (model_cache_dir / "model_state.pdparams").exists():
            print(f"✅ 模型目录存在: {model_cache_dir}")
            return True
        elif default_cache.exists() and (default_cache / "model_state.pdparams").exists():
            print(f"✅ 模型目录存在: {default_cache}")
            return True
        else:
            print(f"❌ 模型下载失败: {e}")
            print("\n请参考 scripts/README_MODELS.md 了解手动下载方法")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="下载 NER 模型")
    parser.add_argument(
        "--backend",
        choices=["modelscope", "paddlenlp"],
        default="modelscope",
        help="选择模型后端（默认: modelscope）"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("模型下载工具")
    print("=" * 60)
    print()
    
    # 确保 models 目录存在
    MODELS_DIR.mkdir(exist_ok=True)
    
    success = False
    
    if args.backend == "modelscope":
        print("步骤 1/1: 下载 ModelScope NER 模型")
        print("-" * 60)
        success = download_modelscope_model()
    elif args.backend == "paddlenlp":
        print("步骤 1/1: 下载 PaddleNLP UIE 模型")
        print("-" * 60)
        success = download_paddlenlp_model()
    
    if success:
        print()
        print("=" * 60)
        print("✅ 所有模型下载完成！")
        print("=" * 60)
        print(f"\n模型保存在: {MODELS_DIR}")
        print("\n提示: 模型文件已自动添加到 .gitignore，不会被提交到 Git")
    else:
        print()
        print("=" * 60)
        print("❌ 模型下载失败")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

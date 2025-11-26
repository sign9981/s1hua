# core/io.py
import shutil
from pathlib import Path
from datetime import datetime
from .utils import logger


def get_task_dirs(input_identifier: str, config: dict) -> tuple[Path, Path]:
    """
    根据配置返回 logs 和 results 的任务子目录路径。
    若 archive_by_task 为 false，则直接返回 logs_dir / results_dir。
    """
    safe_input = "".join(c if c.isalnum() or c in "._-" else "_" for c in input_identifier)
    now_str = datetime.now().strftime("%y%m%d_%H%M")
    
    base_logs = Path(config["output"].get("logs_dir", "./logs")).resolve()
    base_results = Path(config["output"].get("results_dir", "./results")).resolve()

    archive = config["output"].get("archive_by_task", True)

    if archive:
        task_name = f"{safe_input}_{now_str}"
        log_dir = base_logs / task_name
        result_dir = base_results / task_name
    else:
        log_dir = base_logs
        result_dir = base_results

    log_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    return log_dir, result_dir


def build_output_file(
    tool_name: str,
    input_identifier: str,
    output_dir: Path,
    suffix: str
) -> Path:
    """构建输出文件路径（用于工具原始输出）"""
    now = datetime.now()
    date_str = now.strftime("%y%m%d")   # 两位年
    time_str = now.strftime("%H%M")
    safe_input = "".join(c if c.isalnum() or c in "._-" else "_" for c in input_identifier)
    base_name = f"{safe_input}_{tool_name}_{date_str}_{time_str}"
    filename = base_name + suffix
    full_path = (output_dir / filename).resolve()
    return full_path


def copy_to_results(src: Path, result_dir: Path):
    """将高价值文件复制到 results 目录"""
    try:
        dst = result_dir / src.name
        shutil.copy2(src, dst)
        logger.info(f"✅ 已复制至结果目录: {dst.name}")
    except Exception as e:
        logger.warning(f"⚠️  复制到 results 失败: {e}")

def validate_target(file_path: str) -> Path:
    """验证目标文件是否存在且非空"""
    path = Path(file_path).resolve()
    if not path.is_file():
        logger.error(f"❌ 目标文件不存在: {path}")
        raise FileNotFoundError(f"File not found: {path}")
    if path.stat().st_size == 0:
        logger.warning(f"⚠️  目标文件为空: {path}")
    return path


def create_temp_file_from_domain(domain: str) -> Path:
    """将单个域名写入临时文件并返回路径"""
    from .utils import TEMP_DIR
    safe_domain = "".join(c if c.isalnum() or c in "._-" else "_" for c in domain.strip().lower())
    temp_file = TEMP_DIR / f"{safe_domain}.tmp.txt"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(domain.strip().lower() + '\n')
        logger.debug(f"📝 临时目标文件已创建: {temp_file}")
        return temp_file
    except Exception as e:
        logger.error(f"❌ 创建临时目标文件失败: {e}")
        raise
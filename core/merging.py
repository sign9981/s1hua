# core/merging.py
import re
from datetime import datetime
from pathlib import Path
from .utils import logger
from .parsing import extract_subdomains
from .io import copy_to_results

def generate_unique_prefixes(tool_names):
    tool_names = [name.lower() for name in tool_names]
    result = {}

    for name in tool_names:
        n = len(name)
        start_len = min(3, n)
        found = False
        for l in range(start_len, n + 1):
            candidate = name[:l]
            conflict = False
            for other in tool_names:
                if other == name:
                    continue
                if other.startswith(candidate):
                    conflict = True
                    break
            if not conflict:
                result[name] = candidate
                found = True
                break
        if not found:
            result[name] = name

    return result

def merge_and_dedup(selected_tools, tool_output_map, input_identifier, log_dir: Path, result_dir: Path):
    if not tool_output_map:
        logger.warning("⚠️  无有效结果可合并")
        return None

    logger.info("🔄 正在合并并去重子域名结果...")

    all_subs = set()
    for tool_name, file_path in tool_output_map.items():
        if not file_path.exists():
            continue
        subs = extract_subdomains(file_path)
        logger.debug(f"  [{tool_name}] 提取 {len(subs)} 个有效子域名")
        all_subs.update(subs)

    if not all_subs:
        logger.warning("⚠️  合并后无有效子域名")
        return None

    active_tool_names = [name for name in selected_tools if name in tool_output_map]
    prefix_map = generate_unique_prefixes(active_tool_names)
    prefixes_str = '_'.join(prefix_map[name] for name in active_tool_names)

    safe_input = re.sub(r'[^\w.-]', '_', str(input_identifier))
    now = datetime.now().strftime("%y%m%d_%H%M")
    merged_filename = f"{safe_input}_{prefixes_str}_{now}.merged.txt"
    
    # 先写入 logs 目录
    merged_path_in_logs = log_dir / merged_filename
    try:
        with open(merged_path_in_logs, 'w', encoding='utf-8') as f:
            for sub in sorted(all_subs):
                f.write(sub + '\n')
        logger.info(f"✅ 合并完成: {merged_path_in_logs.name} ({len(all_subs)} unique)")
        
        # 再复制到 results 目录
        copy_to_results(merged_path_in_logs, result_dir)
        return merged_path_in_logs

    except Exception as e:
        logger.error(f"❌ 写入合并文件失败: {e}")
        return None
# core/tools.py
import os
import sys
import subprocess
import shlex
import re
import shutil
from datetime import datetime
from pathlib import Path
from .utils import logger
from .io import build_output_file


def run_tool(tool_name: str, tool_cfg: dict, target_file: Path, input_identifier: str, output_dir: Path, is_single_domain: bool = False):
    # === Step 1: 解析工具路径（支持 ~, 相对路径, 绝对路径）===
    raw_path = tool_cfg["path"]
    expanded_path = os.path.expanduser(raw_path)
    
    if os.path.isabs(expanded_path):
        tool_path = Path(expanded_path).resolve()
    else:
        tool_path = (Path.cwd() / expanded_path).resolve()

    if not tool_path.exists():
        logger.warning(f"⚠️  [{tool_name}] 路径不存在: {tool_path}，跳过...")
        return None

    # === 非 OneForAll 工具：通用逻辑 ===
    if tool_name.lower() != "oneforall":
        suffix = tool_cfg.get("output_suffix", ".txt")
        if not suffix.startswith("."):
            suffix = "." + suffix
        output_file = build_output_file(tool_name, input_identifier, output_dir, suffix)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            cmd_str = tool_cfg["command"].format(
                tool_path=shlex.quote(str(tool_path)),
                target_file=shlex.quote(str(target_file)),
                output_file=shlex.quote(str(output_file))
            )
        except KeyError as e:
            logger.error(f"❌ [{tool_name}] 命令模板缺少变量: {{{e}}}")
            return None

        logger.info(f"🚀 正在运行 [{tool_name}] ...")
        logger.debug(f"执行命令: {cmd_str}")

        try:
            result = subprocess.run(
                cmd_str,
                shell=True,
                check=False,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                logger.info(f"✅ [{tool_name}] 成功 → {output_file.name}")
                return output_file
            else:
                logger.warning(f"⚠️  [{tool_name}] 失败 (退出码: {result.returncode})")
                return None

        except Exception as e:
            logger.error(f"❌ 执行 [{tool_name}] 异常: {e}")
            return None

    # ========== OneForAll 特殊处理（v0.4.x 兼容 + 边读边匹配 + 内存安全）==========
    logger.info(f"🚀 正在运行 [OneForAll]（智能模式: {'单域名' if is_single_domain else '多域名'}）...")

    cmd_list = [
        "python3",
        str(tool_path),
        "run",
        "--targets", str(target_file),
        "--dns", "false",
        "--fmt", "csv"
    ]
    cmd_str = " ".join(shlex.quote(arg) for arg in cmd_list)
    logger.debug(f"OneForAll 实际命令: {cmd_str}")

    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    try:
        oneforall_dir = tool_path.parent
        proc = subprocess.Popen(
            cmd_str,
            shell=True,
            cwd=str(oneforall_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )

        # === 关键：边读边匹配，不缓存全部 stdout ===
        extracted_filename = None

        for line in proc.stdout:
            print(line, end='', flush=True)  # 实时透传给用户
            
            clean_line = ansi_escape.sub('', line)

            if is_single_domain:
                match = re.search(r"The subdomain result for [^:]+:\s*(\S+\.csv)", clean_line)
                if match:
                    extracted_filename = match.group(1)
            else:
                # 优先匹配标准输出行
                match = re.search(r"The txt subdomain result for all main domains:\s*(\S+\.txt)", clean_line)
                if match:
                    extracted_filename = match.group(1)
                else:
                    # 兜底：匹配时间戳格式的文件名（兼容旧版或异常情况）
                    fallback_match = re.search(r"(all_subdomain_result_\d{8}_\d{6}\.(?:txt|csv))", clean_line)
                    if fallback_match:
                        candidate_name = fallback_match.group(1)
                        candidate_path = oneforall_dir / "results" / candidate_name
                        if candidate_path.exists():
                            extracted_filename = candidate_name

        proc.wait()

        if proc.returncode != 0:
            logger.warning(f"⚠️  [OneForAll] 失败 (退出码: {proc.returncode})")
            return None

        # === 构建最终结果路径 ===
        if extracted_filename:
            real_output_path = (oneforall_dir / "results" / extracted_filename).resolve()
            if real_output_path.exists():
                safe_input = "".join(c if c.isalnum() or c in "._-" else "_" for c in input_identifier)
                stem = real_output_path.stem
                if stem.startswith("all_subdomain_result_") and len(stem) >= 25:
                    time_part = '_'.join(stem.split('_')[-2:])
                else:
                    time_part = datetime.now().strftime("%y%m%d_%H%M")
                new_name = f"{safe_input}_oneforall_{time_part}{real_output_path.suffix}"
                copied_path = output_dir / new_name
                shutil.copy2(real_output_path, copied_path)
                logger.info(f"\n✅ [OneForAll] 成功 → {copied_path.name}")
                return copied_path

        logger.error("❌ 未能从 OneForAll 输出中提取有效结果文件路径")
        return None

    except Exception as e:
        logger.error(f"❌ 执行 [OneForAll] 异常: {e}")
        return None


def select_tools_interactive(tools_order, tools_config):
    if not tools_order:
        return []

    print("\n🔍 可用子域名收集工具:")
    for i, name in enumerate(tools_order, 1):
        desc = tools_config.get(name, {}).get("description", "").strip()
        if desc:
            print(f"  [{i}] {name:<16} → {desc}")
        else:
            print(f"  [{i}] {name}")

    print(f"  [0] 全部运行（默认）")

    while True:
        try:
            user_input = input("\n👉 请选择要运行的工具（如: 1,3 或 2-4 或 1 3 5，直接回车=全部）: ").strip()

            if user_input == "" or user_input == "0":
                print("✅ 已选择: 全部工具")
                return tools_order

            normalized_input = re.sub(r'\s+', ',', user_input)
            parts = [p.strip() for p in normalized_input.split(',') if p.strip()]

            selected_indices = set()
            total = len(tools_order)

            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start < 1 or end > total or start > end:
                        raise ValueError("范围无效")
                    selected_indices.update(range(start, end + 1))
                else:
                    idx = int(part)
                    if idx < 1 or idx > total:
                        raise ValueError("编号超出范围")
                    selected_indices.add(idx)

            selected_tools = [tools_order[i - 1] for i in sorted(selected_indices)]
            print(f"✅ 已选择: {', '.join(selected_tools)}")
            return selected_tools

        except (ValueError, IndexError):
            print("❌ 输入格式错误，请输入有效编号（如: 1,3 或 2-4 或 1 3 5）")
        except KeyboardInterrupt:
            print("\n👋 用户取消")
            sys.exit(0)
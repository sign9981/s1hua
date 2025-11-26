#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化子域名收集调度器 v1.7+ —— 合并去重 + DNS清洗 + Excel报告
✨ 描述格式：「特点；适用场景｜地域」
   - 地域值：国内 / 国外 / 通用
"""

import sys
import argparse
import os
from pathlib import Path
from core.utils import print_banner, setup_logging, setup_temp_dir, logger
from core.config import generate_default_config, load_config
from core.io import validate_target, create_temp_file_from_domain
from core.tools import select_tools_interactive, run_tool
from core.merging import merge_and_dedup


# ============ 新增：辅助函数 ============
def count_domains_in_file(file_path: Path) -> int:
    """统计目标文件中非空、非注释的有效域名行数"""
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    count += 1
    except Exception as e:
        logger.warning(f"⚠️  读取目标文件时出错，按多域名处理: {e}")
        return 2  # 默认视为多域名
    return count


def main():
    parser = argparse.ArgumentParser(
        prog='s1hua.py',
        description='智能子域名收集调度器 v1.7+ —— DNS清洗 + Excel报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python3 %(prog)s --init\n"
               "  python3 %(prog)s -t baidu.com\n"
               "  python3 %(prog)s -T targets.txt"
    )

    parser.add_argument('--init', action='store_true', help='初始化或重置 config.yaml 并退出')
    
    target_group = parser.add_mutually_exclusive_group(required=False)
    target_group.add_argument('-t', '--target', metavar='<domain>', type=str, help='单个域名')
    target_group.add_argument('-T', '--target-list', metavar='<file>', type=str, help='域名列表文件')

    args = parser.parse_args()

    if args.init:
        if generate_default_config():
            sys.exit(0)
        else:
            sys.exit(1)

    print_banner()

    if not args.target and not args.target_list:
        parser.error("必须指定 -t/--target 或 -T/--target-list（除非使用 --init）")

    config = load_config()
    setup_logging(config.get("log_level", "INFO"))
    setup_temp_dir()

    if args.target:
        logger.info(f"📥 单域名模式: {args.target}")
        target_file = create_temp_file_from_domain(args.target)
        input_identifier = args.target
        is_single_domain = True
    else:
        logger.info(f"📂 文件模式: {args.target_list}")
        try:
            target_file = validate_target(args.target_list)
            input_identifier = Path(args.target_list).stem
            domain_count = count_domains_in_file(target_file)
            is_single_domain = (domain_count == 1)
            if is_single_domain:
                logger.info("🔍 检测到目标文件仅包含一个域名，启用 OneForAll 单域名模式")
            else:
                logger.info(f"🔍 检测到目标文件包含 {domain_count} 个域名，启用 OneForAll 多域名模式")
        except Exception:
            sys.exit(1)

    from core.io import get_task_dirs
    log_task_dir, result_task_dir = get_task_dirs(input_identifier, config)
    logger.info(f"📁 日志目录: {log_task_dir}")
    logger.info(f"📁 结果目录: {result_task_dir}")

    tools_config = config.get("subdomain_enumerators", {})
    if not isinstance(tools_config, dict) or not tools_config:
        logger.error("❌ 配置文件中 'subdomain_enumerators' 字段为空或格式错误，请检查 config.yaml")
        sys.exit(1)

    tools_order = list(tools_config.keys())
    logger.info(f"⚙️  配置中定义了 {len(tools_order)} 个工具")

    selected_tools = select_tools_interactive(tools_order, tools_config)
    if not selected_tools:
        logger.info("⚠️  未选择任何工具，退出。")
        sys.exit(0)
    logger.info(f"🎯 将运行 {len(selected_tools)} 个工具: {', '.join(selected_tools)}")

    tool_output_map = {}

    # ======== 获取当前 Python 可执行文件路径（用于替换 python3） ========
    current_python = sys.executable  # 完整路径，如 C:\Python\python.exe 或 /usr/bin/python3

    for tool_name in selected_tools:
        tool_cfg = tools_config[tool_name]

        if not isinstance(tool_cfg, dict):
            logger.warning(f"⚠️  工具 '{tool_name}' 配置格式错误（应为字典），跳过...")
            continue
        if "path" not in tool_cfg:
            logger.error(f"❌ 工具 '{tool_name}' 缺少 'path' 字段，跳过...")
            continue
        if "command" not in tool_cfg:
            logger.error(f"❌ 工具 '{tool_name}' 缺少 'command' 字段，跳过...")
            continue

        # ========== 关键修复：跨平台替换 python3 ==========
        original_command = tool_cfg["command"]
        # 如果 command 中包含 "python3"，替换为当前 Python 解释器
        if "python3" in original_command:
            fixed_command = original_command.replace("python3", current_python)
            logger.debug(f"🔧 [{tool_name}] 将 'python3' 替换为: {current_python}")
        else:
            fixed_command = original_command

        # 创建临时修正后的配置副本
        tool_cfg_fixed = tool_cfg.copy()
        tool_cfg_fixed["command"] = fixed_command

        output_path = run_tool(
            tool_name=tool_name,
            tool_cfg=tool_cfg_fixed,  # ← 使用修正后的配置
            target_file=target_file,
            input_identifier=input_identifier,
            output_dir=log_task_dir,
            is_single_domain=is_single_domain
        )
        if output_path is not None:
            tool_output_map[tool_name] = output_path

    success_count = len(tool_output_map)
    total_requested = len(selected_tools)
    logger.info(f"🎉 任务 '{input_identifier}' 执行完成（{success_count}/{total_requested} 个工具成功）")

    failed_tools = [tool for tool in selected_tools if tool not in tool_output_map]
    if failed_tools:
        logger.info(f"⚠️  以下 {len(failed_tools)} 个工具运行失败:")
        for ft in failed_tools:
            logger.info(f"  • [{ft}]")

    if success_count > 0:
        logger.info("📊 各工具结果行数统计（原始输出，未去重）:")
        for tool_name in selected_tools:
            if tool_name in tool_output_map:
                output_file = tool_output_map[tool_name]
                if not output_file.exists():
                    count = "文件不存在（但曾报告成功）"
                else:
                    try:
                        with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                            count = sum(1 for line in f if line.strip())
                    except Exception as e:
                        count = f"读取异常: {type(e).__name__}"
                logger.info(f"  • [{tool_name}] → {count}")

        merged_path = merge_and_dedup(
            selected_tools, 
            tool_output_map, 
            input_identifier, 
            log_task_dir, 
            result_task_dir
        )

        if merged_path and merged_path.exists():
            try:
                from core.dns_resolver import run_dns_resolution_and_export
                dns_config = config.get("dns_resolution", {})
                if not dns_config or "command" not in dns_config:
                    logger.error("❌ config.yaml 中缺少 'dns_resolution.command'，请检查配置！")
                    sys.exit(1)

                excel_path, reachable_path = run_dns_resolution_and_export(
                    merged_path, result_task_dir, input_identifier, dns_config
                )
                logger.info(f"📊 DNS 报告已生成: {excel_path.name}")
                logger.info(f"🎯 可探测目标清单: {reachable_path.name}")
            except Exception as e:
                logger.error(f"❌ DNS 清洗阶段发生错误: {e}")
                sys.exit(1)
        else:
            logger.warning("⚠️ 合并文件不存在，跳过 DNS 清洗。")
    else:
        logger.warning("⚠️ 无成功工具，跳过合并与 DNS 清洗步骤。")

    logger.info(f"✅ 任务完成！高价值结果位于: {result_task_dir}")


if __name__ == '__main__':
    main()
# core/config.py
import sys
import os
from pathlib import Path
import platform
import yaml
from .utils import CONFIG_FILE, logger


def _get_default_config_for_os():
    """根据操作系统返回适配的默认配置内容"""
    system = platform.system().lower()

    # 判断是否为 Windows
    is_windows = system == "windows"

    # 工具路径分隔符和扩展名处理
    def fix_path(p):
        if is_windows:
            return p.replace("/", "\\")
        return p

    def tool_path(tool_name, default_posix_path):
        """根据系统返回合适的工具路径字符串"""
        if is_windows:
            # Windows 偏好 .exe（如果存在），否则保留原路径
            exe_path = default_posix_path.replace(".py", ".exe").replace("./toolList", "toolList")
            # 简化：统一使用相对路径，不强制 .exe（因部分工具无 exe）
            return default_posix_path.replace("/", "\\")
        else:
            return default_posix_path

    # 注意：command 中的路径占位符 {tool_path} 会在运行时替换，所以这里只需保证 path 字段合理
    oneforall_path = tool_path("oneforall", "./toolList/OneForAll/oneforall.py")
    subfinder_path = tool_path("subfinder", "./toolList/subfinder/subfinder")
    ksubdomain_path = tool_path("ksubdomain", "./toolList/ksubdomain/ksubdomain")
    findomain_path = tool_path("findomain", "./toolList/findomain/findomain")
    assetfinder_path = tool_path("assetfinder", "./toolList/assetfinder/assetfinder")

    # amass 特殊处理：若在 PATH 中，直接写 "amass"；否则需指定路径
    amass_path = "amass"  # 默认假设已加入 PATH（跨平台通用）

    # DNS 解析命令：Windows 不支持 ">" 重定向（但 dnsx 支持 -o），所以统一用 dnsx 自带输出
    if is_windows:
        dns_cmd = ".\\toolList\\dnsx\\dnsx.exe -a -cname -resp -retry 4 -t 80 -nc"
    else:
        dns_cmd = "./toolList/dnsx/dnsx -a -cname -resp -retry 4 -t 80 -nc"

    config_template = f'''# config.yaml - 子域名收集配置 v1.7+（自动适配 {platform.system()} 系统）
# subdomain_enumerators: 用户可选的子域名枚举工具（支持多选）

subdomain_enumerators:
  oneforall:
    path: "{oneforall_path}"
    command: "python3 {{tool_path}} --targets {{target_file}} --dns False --fmt csv run"
    output_suffix: ".csv"
    description: "多源综合，支持 CDN 识别；适合国内目标｜国内"

  subfinder:
    path: "{subfinder_path}"
    command: "{{{{tool_path}}}} -dL {{target_file}} -o {{output_file}}"
    output_suffix: ".txt"
    description: "速度快，依赖 API；适合常规扫描｜国外"

  ksubdomain:
    path: "{ksubdomain_path}"
    command: "{{{{tool_path}}}} enum --dl {{target_file}} -o {{output_file}}"
    output_suffix: ".txt"
    description: "DNS 爆破，支持泛解析绕过；适合无 API 环境｜通用"

  findomain:
    path: "{findomain_path}"
    command: "{{{{tool_path}}}} -f {{target_file}} --quiet -u {{output_file}}"
    output_suffix: ".txt"
    description: "极速多源聚合，依赖证书日志；国内目标可能遗漏｜通用（国外更优）"

  amass:
    path: "{amass_path}"
    command: "{{{{tool_path}}}} enum -df {{target_file}} -o {{output_file}}"
    output_suffix: ".txt"
    description: "多源集成，结果全但慢；适合深度挖掘｜国外"

  assetfinder:
    path: "{assetfinder_path}"
    command: "{{{{tool_path}}}} --subs-only {{target_file}} > {{output_file}}"
    output_suffix: ".txt"
    description: "极快轻量，结果少；依赖API，适合初步侦察｜通用"

dns_resolution:
  command: "{dns_cmd}"

# ========== 新版输出配置（推荐使用） ==========
output:
  archive_by_task: true        # 按任务建子目录（强烈建议开启）
  logs_dir: "./logs"           # 全流程中间产物（原始输出）
  results_dir: "./results"     # 高价值交付物（合并后结果）

# log_level: "INFO"          # 可选：DEBUG/INFO/WARNING/ERROR
'''
    return config_template.strip() + '\n'


def generate_default_config():
    if not CONFIG_FILE.exists():
        print(f"📝 正在生成配置文件: {CONFIG_FILE}")
        try:
            default_config = _get_default_config_for_os()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(default_config)
            print("✅ 默认配置已生成！")
            print("💡 请编辑该文件，确认工具的实际路径和权限（尤其 Windows 需 .exe 或 python 调用）。")
            return True
        except Exception as e:
            print(f"❌ 无法写入配置文件: {e}")
            return False

    print(f"⚠️  配置文件已存在: {CONFIG_FILE}")
    print("💡 建议先备份现有配置（如: cp config.yaml config.yaml.bak）")
    while True:
        choice = input("❓ 是否覆盖现有配置？(y/N): ").strip().lower()
        if choice == '':
            choice = 'n'
        if choice in ('y', 'yes'):
            break
        elif choice in ('n', 'no'):
            print("🛑 操作已取消。")
            return False
        else:
            print("请输入 y 或 n")

    print(f"🔄 正在覆盖配置文件: {CONFIG_FILE}")
    try:
        default_config = _get_default_config_for_os()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(default_config)
        print("✅ 配置文件已更新为当前系统适配模板！")
        print("💡 请根据实际情况重新检查工具路径和执行方式。")
        return True
    except Exception as e:
        print(f"❌ 覆盖配置文件失败: {e}")
        return False


def load_config():
    if not CONFIG_FILE.exists():
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        script_name = Path(sys.argv[0]).name if sys.argv else "your_script.py"
        print(f"👉 请先运行: python {script_name} --init")
        sys.exit(1)
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError("配置文件为空")
            return config
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        sys.exit(1)
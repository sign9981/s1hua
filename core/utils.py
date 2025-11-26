# core/utils.py
import sys
import logging
import shutil
import signal
import atexit
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = SCRIPT_DIR / "config.yaml"
TEMP_DIR = SCRIPT_DIR / "temp"

logger = logging.getLogger("SubCollector")

BANNER = r"""
          ____  .__                             
  ______ /_   | |  |__    __ __  _____          
 /  ___/  |   | |  |  \  |  |  \ \__  \         
 \___ \   |   | |   Y  \ |  |  /  / __ \_       
/____  >  |___| |___|  / |____/  (____  / ______
     \/              \/               \/ /_____/
"""

def print_banner():
    # 仅在终端输出 Banner，避免管道/重定向时污染输出
    if sys.stdout.isatty():
        print(BANNER)
        print("  s1hua v1.6.7  \t\tby s1gN_今晚早睡\n")

def setup_logging(level_str="INFO"):
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    log_level = level_map.get(level_str.upper(), logging.INFO)
    
    # 增加时间戳，便于调试（尤其长时间任务）
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def cleanup_temp_dir():
    if TEMP_DIR.exists():
        try:
            shutil.rmtree(TEMP_DIR)
        except Exception as e:
            # 使用 logger 而非 print，保持日志一致性
            logger.warning(f"清理临时目录失败: {e}")

def signal_handler(signum, frame):
    sig_name = {2: "SIGINT (Ctrl+C)", 15: "SIGTERM"}.get(signum, f"信号 {signum}")
    logger.info(f"检测到中断信号: {sig_name}，正在清理临时文件...")
    cleanup_temp_dir()
    logger.info("程序已退出。")
    sys.exit(0)  # 正常退出码 0，表示用户主动终止

def setup_temp_dir():
    try:
        TEMP_DIR.mkdir(exist_ok=True)
        atexit.register(cleanup_temp_dir)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception as e:
        logger.error(f"无法创建临时目录: {e}")
        sys.exit(1)
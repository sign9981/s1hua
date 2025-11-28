# s1hua - 丝滑

> 轻量级、高兼容、易扩展的自动化子域名收集与整合工具  
> ✨ 集成 GitHub Star 数千+ 的成熟开源工具，低配 VPS 也能流畅运行！

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20|%20macOS-lightgrey)

## 🌟 为什么选择 s1hua？

相比 [ARL (Asset Reconnaissance Lighthouse)] 等重型平台，**s1hua 具有以下显著优势**：

- ✅ **资源占用极低**：无需高配 VPS（512MB 内存即可运行），适合个人安全研究或低成本部署；
- ✅ **工具链透明可控**：所有子域名引擎均为独立二进制/脚本，**命令行参数可直接修改**，灵活适配各种场景；
- ✅ **集成高星成熟工具**：一键安装 `subfinder`、`amass`、`OneForAll`、`ksubdomain` 等 GitHub 上广受认可的开源项目；
- ✅ **跨平台支持**：提供 Linux/macOS (`install_tools.sh`) 和 Windows (`install_tools.bat`) 双脚本，开箱即用；
- ✅ **无 Web 依赖**：纯命令行工具，避免复杂环境配置和安全风险。

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/sign9981/s1hua.git
cd s1hua
```

### 2. 安装依赖工具

#### ▶ Linux / macOS
```bash
chmod +x install_tools.sh
./install_tools.sh  # 支持国内加速（自动提示）
python3 s1hua.py --init
```

#### ▶ Windows
- 双击运行 `install_tools.bat`（需已安装 [Git for Windows](https://git-scm.com/)）
- 首次运行会提示是否启用国内加速（推荐选 `Y`）
- 初始化配置：
  ```cmd
  python s1hua.py --init
  ```

> 💡 安装脚本会自动下载并解压所有工具到 `toolList/` 目录，无需手动处理！

### 3. 扫描目标

```bash
# 基础扫描
python3 s1hua.py -t example.com

# 多目标（从文件读取）
python3 s1hua.py -f targets.txt

# 查看所有选项
python3 s1hua.py -h
```

---

## 🔧 自定义工具命令

所有工具调用逻辑集中在 `core/parsing.py` 和 `core/config.py` 中。  
例如，若想为 `subfinder` 添加 `-silent` 参数：

```python
# 在 core/parsing.py 中找到类似代码
cmd = [tool_path, "-d", domain]
# 修改为
cmd = [tool_path, "-d", domain, "-silent"]
```

> 💡 因为每个工具都是独立进程调用，**修改命令行参数极其简单**，无需理解复杂框架。

---

## 📦 集成工具列表

| 工具 | GitHub Stars | 功能 |
|------|--------------|------|
| [subfinder](https://github.com/projectdiscovery/subfinder) | ⭐ 12k+ | 快速被动子域发现 |
| [amass](https://github.com/OWASP/Amass) | ⭐ 11k+ | OWASP 官方资产测绘 |
| [OneForAll](https://github.com/shmilylty/OneForAll) | ⭐ 9k+ | 全面子域爆破与验证 |
| [ksubdomain](https://github.com/boyhack/ksubdomain) | ⭐ 4k+ | 高速无状态 DNS 爆破 |
| [findomain](https://github.com/Edu4rdSHL/findomain) | ⭐ 3k+ | 基于证书透明日志 |
| [assetfinder](https://github.com/tomnomnom/assetfinder) | ⭐ 5k+ | TomNomNom 经典工具 |
| [dnsx](https://github.com/projectdiscovery/dnsx) | ⭐ 3k+ | 快速 DNS 解析与存活探测 |

> 所有工具均由官方 Release 下载，确保安全可靠。

---

## 📁 项目结构

```
s1hua/
├── s1hua.py                # 主程序入口
├── install_tools.sh        # Linux/macOS 一键安装脚本
├── install_tools.bat       # Windows 一键安装脚本
├── core/                   # 核心模块
│   ├── config.py           # 工具路径与参数配置
│   ├── parsing.py          # 工具命令构造与执行
│   ├── merging.py          # 结果去重与合并
│   └── ...                 # 其他辅助模块
└── .gitignore              # 忽略敏感/临时文件
```

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

> 注：各子工具（如 amass、subfinder 等）遵循其各自许可证，请遵守相关条款。

---

## 🙌 致谢

感谢以下优秀开源项目为网络安全社区做出的贡献：
- [ProjectDiscovery](https://github.com/projectdiscovery)
- [OWASP Amass](https://github.com/OWASP/Amass)
- [TomNomTom](https://github.com/tomnomnom)
- [shmilylty / OneForAll](https://github.com/shmilylty/OneForAll)
- [boyhack / ksubdomain](https://github.com/boyhack/ksubdomain)

---

> 🐚 **轻量、自由、高效 —— s1hua，为实战而生。**
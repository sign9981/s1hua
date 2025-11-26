#!/bin/bash
# install_tools.sh - 一键安装 s1hua 所需工具 (Linux/macOS)
# 支持国内加速代理（ghproxy.com）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_LIST_DIR="$SCRIPT_DIR/toolList"
mkdir -p "$TOOL_LIST_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# === 询问是否使用国内加速 ===
read -p "🌍 是否启用国内 GitHub 加速？(Y/n): " USE_PROXY_INPUT
case ${USE_PROXY_INPUT:-Y} in
    [Nn]* ) USE_PROXY=false; BASE_URL="https://github.com";;
    * )     USE_PROXY=true;  BASE_URL="https://ghproxy.com/https://github.com";;
esac

if [ "$USE_PROXY" = true ]; then
    log "已启用国内加速代理: https://ghproxy.com"
else
    log "使用官方 GitHub 源"
fi

# 下载函数（自动拼接 proxy）
get_release_url() {
    local repo=$1
    local pattern=$2  # 如 "*linux_amd64.tar.gz"
    local api_url="https://api.github.com/repos/$repo/releases/latest"
    
    if [ "$USE_PROXY" = true ]; then
        # 通过代理获取 release 信息（注意：API 不能走 ghproxy，但可临时用 jsDelivr 或 raw.githubusercontent）
        # 改为直接构造 URL（更可靠）—— 多数工具命名规则固定
        echo "暂无法通过代理获取 API，将尝试直接构造下载链接..." >&2
        return 1
    else
        curl -s "$api_url" | grep "browser_download_url.*$pattern" | head -n1 | cut -d '"' -f 4
    fi
}

# 更可靠方式：直接构造下载链接（因多数工具命名规范）
construct_url() {
    local repo=$1
    local tag=$2      # 如 "latest"
    local filename=$3 # 如 "subfinder_linux_amd64.tar.gz"
    if [ "$USE_PROXY" = true ]; then
        echo "$BASE_URL/$repo/releases/$tag/download/$filename"
    else
        echo "https://github.com/$repo/releases/$tag/download/$filename"
    fi
}

download_and_extract() {
    local tool_name=$1
    local url=$2
    local dest_dir=$3
    local bin_name=$4

    log "正在安装 $tool_name..."
    mkdir -p "$dest_dir"
    local tmp_file="/tmp/${tool_name}_latest$(echo $url | grep -o '\.[^.]*$')"
    
    curl -fL "$url" -o "$tmp_file" || error "下载失败: $url"

    if [[ "$tmp_file" == *.zip ]]; then
        unzip -o "$tmp_file" -d "/tmp/${tool_name}_extract"
    else
        tar -xzf "$tmp_file" -C "/tmp" --strip-components=1 --wildcards "*/$bin_name*" 2>/dev/null || \
        tar -xzf "$tmp_file" -C "/tmp"
    fi

    local bin_path=$(find "/tmp" -name "$bin_name*" -type f ! -name "*.txt" ! -name "*.md" | head -n1)
    if [[ -n "$bin_path" ]]; then
        mv "$bin_path" "$dest_dir/$bin_name"
        chmod +x "$dest_dir/$bin_name"
        log "✅ $tool_name 已安装"
    else
        error "未在压缩包中找到 $bin_name"
    fi
    rm -rf "/tmp/${tool_name}_*" "$tmp_file"
}

# ========================
# 工具安装（使用构造 URL）
# ========================

# subfinder - projectdiscovery/subfinder
SUBFINDER_URL=$(construct_url "projectdiscovery/subfinder" "latest" "subfinder_$(uname -s)_amd64.tar.gz")
download_and_extract "subfinder" "$SUBFINDER_URL" "$TOOL_LIST_DIR/subfinder" "subfinder"

# ksubdomain - boyhack/ksubdomain ✅ 修正链接
KS_URL=$(construct_url "boyhack/ksubdomain" "latest" "ksubdomain_$(uname -s)_amd64.tar.gz")
download_and_extract "ksubdomain" "$KS_URL" "$TOOL_LIST_DIR/ksubdomain" "ksubdomain"

# findomain - Edu4rdSHL/findomain
FD_URL=$(construct_url "Edu4rdSHL/findomain" "latest" "findomain-$(uname -s)-x86_64.zip")
download_and_extract "findomain" "$FD_URL" "$TOOL_LIST_DIR/findomain" "findomain"

# amass - OWASP/Amass
AMASS_URL=$(construct_url "OWASP/Amass" "latest" "amass_$(uname -s)_amd64.zip")
download_and_extract "amass" "$AMASS_URL" "$TOOL_LIST_DIR/amass" "amass"

# assetfinder - tomnomnom/assetfinder
AF_URL=$(construct_url "tomnomnom/assetfinder" "latest" "assetfinder_$(uname -s)_amd64.tar.gz")
download_and_extract "assetfinder" "$AF_URL" "$TOOL_LIST_DIR/assetfinder" "assetfinder"

# dnsx - projectdiscovery/dnsx
DNSX_URL=$(construct_url "projectdiscovery/dnsx" "latest" "dnsx_$(uname -s)_amd64.tar.gz")
download_and_extract "dnsx" "$DNSX_URL" "$TOOL_LIST_DIR/dnsx" "dnsx"

# OneForAll (Git clone，建议不用代理，或用户自行配置 git proxy)
if [ ! -d "$TOOL_LIST_DIR/OneForAll" ]; then
    if [ "$USE_PROXY" = true ]; then
        log "克隆 OneForAll（可能较慢，请耐心等待）..."
        git clone --depth=1 https://ghproxy.com/https://github.com/shmilylty/OneForAll.git "$TOOL_LIST_DIR/OneForAll"
    else
        git clone --depth=1 https://github.com/shmilylty/OneForAll.git "$TOOL_LIST_DIR/OneForAll"
    fi
else
    log "OneForAll 已存在，跳过克隆"
fi

log "🎉 所有工具安装完成！"
log "💡 运行: python3 s1hua.py --init 初始化配置"
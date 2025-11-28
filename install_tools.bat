@chcp 65001 >nul
@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set TOOL_LIST_DIR=%SCRIPT_DIR%toolList

REM ========== 询问是否使用国内加速 ==========
set /p USE_PROXY_INPUT=🌍 是否启用国内 GitHub 加速？(Y/n): 
if /i "%USE_PROXY_INPUT%"=="n" (
    set USE_PROXY=false
    set BASE_URL=https://github.com
    echo [INFO] 使用官方 GitHub 源
) else (
    set USE_PROXY=true
    set BASE_URL=https://ghproxy.com/https://github.com
    echo [INFO] 已启用国内加速代理: https://ghproxy.com
)

REM 创建目录
powershell -Command "if (!(Test-Path '%TOOL_LIST_DIR%')) { New-Item -ItemType Directory -Path '%TOOL_LIST_DIR%' }"

REM ========== 函数：下载并解压 ==========
:download_tool
set tool_name=%1
set url=%2
set dest_dir=%3
set bin_name=%4

echo [INFO] 正在安装 %tool_name%...
powershell -Command "if (!(Test-Path '%dest_dir%')) { New-Item -ItemType Directory -Path '%dest_dir%' }"

set tmp_zip=%TEMP%\%tool_name%_latest.zip
powershell -Command "Invoke-WebRequest -Uri '%url%' -OutFile '%tmp_zip%'"

REM 解压
powershell -Command "Expand-Archive -Path '%tmp_zip%' -DestinationPath '%TEMP%\%tool_name%_extract' -Force"

REM 查找 .exe 并复制
for /f "delims=" %%i in ('dir /b /s "%TEMP%\%tool_name%_extract\%bin_name%*.exe" 2^>nul') do (
    copy "%%i" "%dest_dir%\%bin_name%.exe" >nul
)

if not exist "%dest_dir%\%bin_name%.exe" (
    echo [ERROR] 未找到 %bin_name%.exe
    exit /b 1
)

del "%tmp_zip%" >nul 2>&1
rmdir /s /q "%TEMP%\%tool_name%_extract" >nul 2>&1
echo [INFO] ✅ %tool_name% 已安装
goto :eof

REM ========== 构造下载链接 ==========
set SUBFINDER_URL=%BASE_URL%/projectdiscovery/subfinder/releases/latest/download/subfinder_windows_amd64.zip
set KS_URL=%BASE_URL%/boyhack/ksubdomain/releases/latest/download/ksubdomain_windows_amd64.zip
set FINDOMAIN_URL=%BASE_URL%/Edu4rdSHL/findomain/releases/latest/download/findomain-windows-x86_64.zip
set AMASS_URL=%BASE_URL%/OWASP/Amass/releases/latest/download/amass_windows_amd64.zip
set ASSET_URL=%BASE_URL%/tomnomnom/assetfinder/releases/latest/download/assetfinder_windows_amd64.tar.gz
set DNSX_URL=%BASE_URL%/projectdiscovery/dnsx/releases/latest/download/dnsx_windows_amd64.zip

REM ========== 开始安装 ==========
call :download_tool subfinder "%SUBFINDER_URL%" "%TOOL_LIST_DIR%\subfinder" "subfinder"
call :download_tool ksubdomain "%KS_URL%" "%TOOL_LIST_DIR%\ksubdomain" "ksubdomain"
call :download_tool findomain "%FINDOMAIN_URL%" "%TOOL_LIST_DIR%\findomain" "findomain"
call :download_tool amass "%AMASS_URL%" "%TOOL_LIST_DIR%\amass" "amass"
call :download_tool assetfinder "%ASSET_URL%" "%TOOL_LIST_DIR%\assetfinder" "assetfinder"
call :download_tool dnsx "%DNSX_URL%" "%TOOL_LIST_DIR%\dnsx" "dnsx"

REM OneForAll
if not exist "%TOOL_LIST_DIR%\OneForAll" (
    echo [INFO] 正在克隆 OneForAll...
    if "%USE_PROXY%"=="true" (
        git clone --depth=1 https://ghproxy.com/https://github.com/shmilylty/OneForAll.git "%TOOL_LIST_DIR%\OneForAll"
    ) else (
        git clone --depth=1 https://github.com/shmilylty/OneForAll.git "%TOOL_LIST_DIR%\OneForAll"
    )
) else (
    echo [INFO] OneForAll 已存在，跳过克隆
)

echo.
echo 🎉 所有工具已安装完成！
echo 💡 请运行: python s1hua.py --init 生成配置文件
pause
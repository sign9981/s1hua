@echo off
REM s1hua Tool Installer (Windows)
REM Pure English version, no Chinese characters

REM Clear screen
cls

REM Show banner
echo ==============================================
echo         s1hua Tool Installer         
echo ==============================================
echo.

REM Create tool directory
echo Creating tool directory...
mkdir toolList 2>nul
if exist toolList (
    echo Tool directory: %~dp0toolList
) else (
    echo ERROR: Failed to create tool directory!
    pause
    exit /b 1
)
echo.

REM GitHub proxy option
echo Use GitHub proxy? (y/n): 
set /p USE_PROXY=
if /i "%USE_PROXY%"=="y" (
    set PROXY=https://gh-proxy.org/
    echo Using proxy acceleration...
) else (
    set PROXY=
    echo Using official links...
)
echo.

REM Install Findomain
echo Installing Findomain...
mkdir toolList\findomain 2>nul
curl -L -o %TEMP%\findomain.zip %PROXY%https://github.com/Findomain/Findomain/releases/download/10.0.1/findomain-windows.exe.zip 2>nul
if exist %TEMP%\findomain.zip (
    powershell -Command Expand-Archive -Path %TEMP%\findomain.zip -DestinationPath %TEMP%\findomain_extract -Force 2>nul
    copy %TEMP%\findomain_extract\*.exe toolList\findomain\ 2>nul
    del %TEMP%\findomain.zip 2>nul
    rmdir /s /q %TEMP%\findomain_extract 2>nul
    echo Findomain installed!
) else (
    echo Findomain download failed!
)
echo.

REM Install Assetfinder
echo Installing Assetfinder...
mkdir toolList\assetfinder 2>nul
curl -L -o %TEMP%\assetfinder.zip %PROXY%https://github.com/tomnomnom/assetfinder/releases/download/v0.1.1/assetfinder-windows-amd64-0.1.1.zip 2>nul
if exist %TEMP%\assetfinder.zip (
    powershell -Command Expand-Archive -Path %TEMP%\assetfinder.zip -DestinationPath %TEMP%\assetfinder_extract -Force 2>nul
    copy %TEMP%\assetfinder_extract\*.exe toolList\assetfinder\ 2>nul
    del %TEMP%\assetfinder.zip 2>nul
    rmdir /s /q %TEMP%\assetfinder_extract 2>nul
    echo Assetfinder installed!
) else (
    echo Assetfinder download failed!
)
echo.

REM Install Subfinder
echo Installing Subfinder...
mkdir toolList\subfinder 2>nul
curl -L -o %TEMP%\subfinder.zip %PROXY%https://github.com/projectdiscovery/subfinder/releases/download/v2.10.1/subfinder_2.10.1_windows_amd64.zip 2>nul
if exist %TEMP%\subfinder.zip (
    powershell -Command Expand-Archive -Path %TEMP%\subfinder.zip -DestinationPath %TEMP%\subfinder_extract -Force 2>nul
    copy %TEMP%\subfinder_extract\*.exe toolList\subfinder\ 2>nul
    del %TEMP%\subfinder.zip 2>nul
    rmdir /s /q %TEMP%\subfinder_extract 2>nul
    echo Subfinder installed!
) else (
    echo Subfinder download failed!
)
echo.

REM Install DNSx
echo Installing DNSx...
mkdir toolList\dnsx 2>nul
curl -L -o %TEMP%\dnsx.zip %PROXY%https://github.com/projectdiscovery/dnsx/releases/download/v1.2.2/dnsx_1.2.2_windows_amd64.zip 2>nul
if exist %TEMP%\dnsx.zip (
    powershell -Command Expand-Archive -Path %TEMP%\dnsx.zip -DestinationPath %TEMP%\dnsx_extract -Force 2>nul
    copy %TEMP%\dnsx_extract\*.exe toolList\dnsx\ 2>nul
    del %TEMP%\dnsx.zip 2>nul
    rmdir /s /q %TEMP%\dnsx_extract 2>nul
    echo DNSx installed!
) else (
    echo DNSx download failed!
)
echo.

REM Install KSubdomain
echo Installing KSubdomain...
mkdir toolList\ksubdomain 2>nul
curl -L -o %TEMP%\ksubdomain.zip %PROXY%https://github.com/boy-hack/ksubdomain/releases/download/v2.4.0/KSubdomain-v2.4.0-windows-amd64.zip 2>nul
if exist %TEMP%\ksubdomain.zip (
    powershell -Command Expand-Archive -Path %TEMP%\ksubdomain.zip -DestinationPath %TEMP%\ksubdomain_extract -Force 2>nul
    copy %TEMP%\ksubdomain_extract\*.exe toolList\ksubdomain\ 2>nul
    del %TEMP%\ksubdomain.zip 2>nul
    rmdir /s /q %TEMP%\ksubdomain_extract 2>nul
    echo KSubdomain installed!
) else (
    echo KSubdomain download failed!
)
echo.

REM Install Amass
echo Installing Amass...
mkdir toolList\amass 2>nul
curl -L -o %TEMP%\amass.zip %PROXY%https://github.com/owasp-amass/amass/releases/download/v5.0.1/amass_windows_amd64.zip 2>nul
if exist %TEMP%\amass.zip (
    powershell -Command Expand-Archive -Path %TEMP%\amass.zip -DestinationPath %TEMP%\amass_extract -Force 2>nul
    copy %TEMP%\amass_extract\*.exe toolList\amass\ 2>nul
    del %TEMP%\amass.zip 2>nul
    rmdir /s /q %TEMP%\amass_extract 2>nul
    echo Amass installed!
) else (
    echo Amass download failed!
)
echo.

REM Install OneForAll
echo Installing OneForAll...
mkdir toolList\OneForAll 2>nul
if not exist toolList\OneForAll\oneforall.py (
    if /i "%USE_PROXY%"=="y" (
        git clone --depth=1 https://gh-proxy.org/https://github.com/shmilylty/OneForAll.git toolList\OneForAll 2>nul
    ) else (
        git clone --depth=1 https://github.com/shmilylty/OneForAll.git toolList\OneForAll 2>nul
    )
    if exist toolList\OneForAll\oneforall.py (
        echo OneForAll installed!
    ) else (
        echo OneForAll download failed!
    )
) else (
    echo OneForAll already exists!
)
echo.

REM Installation completed
echo ==============================================
echo Installation completed!
echo ==============================================
echo Run: python s1hua.py --init
echo.
echo Tool directory: %~dp0toolList
echo.
echo Press any key to exit...
pause >nul

exit /b 0
@echo off
chcp 65001 >nul
:: ============================================================
:: 小红书自动评论脚本 - 依赖检查工具
:: ============================================================

echo.
echo ============================================================
echo   小红书自动评论脚本 - 依赖检查工具
echo ============================================================
echo.

:: 检查Python
echo [检查] Python环境...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ✗ Python 未安装
    echo.
    set /a errors+=1
) else (
    echo ✓ Python 已安装
    echo.
)

:: 检查pip
echo [检查] pip工具...
pip --version 2>nul
if %errorlevel% neq 0 (
    echo ✗ pip 不可用
    echo.
    set /a errors+=1
) else (
    echo ✓ pip 可用
    echo.
)

:: 检查undetected-chromedriver
echo [检查] undetected-chromedriver...
python -c "import undetected_chromedriver as uc; print('版本:', uc.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ✗ undetected-chromedriver 未安装
    echo.
    set /a errors+=1
) else (
    echo ✓ undetected-chromedriver 已安装
    echo.
)

:: 检查selenium
echo [检查] selenium...
python -c "import selenium; print('版本:', selenium.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ✗ selenium 未安装
    echo.
    set /a errors+=1
) else (
    echo ✓ selenium 已安装
    echo.
)

:: 检查chromedriver.exe
echo [检查] chromedriver.exe...
if exist "chromedriver.exe" (
    echo ✓ chromedriver.exe 存在
    echo.
) else (
    echo ✗ chromedriver.exe 不存在
    echo   请下载并放置在脚本目录下
    echo.
    set /a errors+=1
)

:: 检查config.py
echo [检查] config.py...
if exist "config.py" (
    echo ✓ config.py 存在
    echo.
) else (
    echo ✗ config.py 不存在
    echo   请确保配置文件在脚本目录下
    echo.
    set /a errors+=1
)

:: 检查主程序
echo [检查] xiaohongshu_auto_comment_v5.py...
if exist "xiaohongshu_auto_comment_v5.py" (
    echo ✓ 主程序存在
    echo.
) else (
    echo ✗ 主程序不存在
    echo.
    set /a errors+=1
)

:: 总结
echo ============================================================
echo   检查完成
echo ============================================================
echo.

if defined errors (
    echo ⚠ 发现 %errors% 个问题,请先解决后再运行脚本
    echo.
    echo 如需安装Python依赖,请运行: install_dependencies.bat
) else (
    echo ✓ 所有检查通过,可以正常运行脚本!
)

echo.
echo ============================================================
echo.

pause


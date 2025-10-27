@echo off
chcp 65001 >nul
title 小红书自动评论工具 - 配置面板

echo ========================================
echo   小红书自动评论工具 - 配置面板
echo ========================================
echo.
echo 正在启动图形化配置界面...
echo.

python config_gui.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   启动失败!
    echo ========================================
    echo.
    echo 可能原因:
    echo 1. Python 未安装或未添加到环境变量
    echo 2. config.py 文件不存在
    echo.
    pause
)


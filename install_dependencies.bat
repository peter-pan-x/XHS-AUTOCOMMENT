@echo off
echo ========================================
echo 小红书自动评论脚本 - 依赖安装
echo ========================================
echo.
echo 正在安装必要的Python模块...
echo.

pip install psutil
pip install undetected-chromedriver
pip install selenium

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 现在可以运行脚本了:
echo python xiaohongshu_auto_comment_v5.py
echo.
pause


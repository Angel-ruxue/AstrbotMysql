@echo off
title 程序启动工具
setlocal enabledelayedexpansion

:: 设置颜色为亮绿色
color 0A

:: 配置（请根据实际情况修改）
set "MAIN_EXE=%~dp0main.exe"                     :: 主程序EXE路径（默认与脚本同目录）
set "REQUIREMENTS=%~dp0requirements.txt"         :: 依赖文件路径

:: 显示欢迎信息
echo ======================================
echo        程序启动工具
echo ======================================
echo.

:: 检查网络连接
echo 正在检查网络连接...
ping www.baidu.com -n 1 -w 2000 >nul
if %errorlevel% neq 0 (
    echo 错误：无法连接到网络，请检查网络设置！
    goto :end
)
echo 网络连接正常！
echo.

:: 检查EXE文件是否存在
if not exist "%MAIN_EXE%" (
    echo 错误：主程序EXE文件不存在！
    echo 请确保 "%MAIN_EXE%" 正确指向你的程序。
    goto :end
)

:: 检查依赖文件并安装（如果存在）
echo 正在检查依赖文件...
if exist "!REQUIREMENTS!" (
    echo 找到依赖文件：!REQUIREMENTS!
    
    :: 检查是否安装了pip
    where pip >nul 2>nul
    if %errorlevel% equ 0 (
        echo 正在安装依赖...
        pip install -r "!REQUIREMENTS!"
        
        if %errorlevel% neq 0 (
            echo 警告：依赖安装失败，但继续启动程序...
        ) else (
            echo 依赖安装完成！
        )
    ) else (
        echo 警告：未找到pip，无法安装依赖！
        echo 请确保已安装Python并将pip添加到系统PATH中。
        echo 继续启动程序...
    )
) else (
    echo 未找到依赖文件，跳过安装步骤...
)
echo.

:: 启动程序
echo 正在启动程序...
start "" "%MAIN_EXE%"

echo 程序已启动！
echo.
echo ======================================
echo      程序启动完成！
echo ======================================

:end
timeout /t 5 >nul
exit /b
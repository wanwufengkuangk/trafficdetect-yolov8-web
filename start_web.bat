@echo off
setlocal
set "ACTIVATE_BAT="
for %%P in ("%USERPROFILE%\miniconda3\Scripts\activate.bat" "%USERPROFILE%\anaconda3\Scripts\activate.bat" "D:\Anaconda\Scripts\activate.bat") do (
    if not defined ACTIVATE_BAT if exist %%~P set "ACTIVATE_BAT=%%~P"
)
if not defined ACTIVATE_BAT (
    echo [ERROR] 未找到 Conda 的 activate.bat，请先安装 Anaconda 或 Miniconda，并将环境命名为 yolov8。
    exit /b 1
)
call "%ACTIVATE_BAT%" yolov8
python "%~dp0start_web.py" --port 8010

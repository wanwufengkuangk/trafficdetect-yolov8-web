@echo off
setlocal

cd /d "%~dp0"

if "%CONDA_ENV_NAME%"=="" (
    set "CONDA_ENV_NAME=yolov8"
)

if "%TRAFFICDETECT_CONFIG%"=="" (
    set "TRAFFICDETECT_CONFIG=%~dp0configs\default.yaml"
)

if "%TRAFFICDETECT_HOST%"=="" (
    set "TRAFFICDETECT_HOST=0.0.0.0"
)

if "%TRAFFICDETECT_PORT%"=="" (
    set "TRAFFICDETECT_PORT=8010"
)

echo [TrafficDetect] 项目目录: %cd%
echo [TrafficDetect] Conda 环境: %CONDA_ENV_NAME%
echo [TrafficDetect] 配置文件: %TRAFFICDETECT_CONFIG%
echo [TrafficDetect] 访问端口: %TRAFFICDETECT_PORT%

call conda activate %CONDA_ENV_NAME%
if errorlevel 1 (
    echo [TrafficDetect] Conda 环境激活失败，请确认 Conda 已安装且环境 %CONDA_ENV_NAME% 存在。
    pause
    exit /b 1
)

python start_web.py --config "%TRAFFICDETECT_CONFIG%" --host %TRAFFICDETECT_HOST% --port %TRAFFICDETECT_PORT%

pause

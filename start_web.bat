@echo off
setlocal
call D:\Anaconda\Scripts\activate.bat yolov8
python "%~dp0start_web.py" --port 8010

@echo off
cd /d %~dp0
cd ..
call .venv\Scripts\Activate.bat
python -u src\main.py
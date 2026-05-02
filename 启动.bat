@echo off
chcp 65001 >nul
set PYTHONPATH=%~dp0
set PYTHONIOENCODING=utf-8
python "%~dp0launcher.py"

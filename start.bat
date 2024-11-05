@echo off

cd /d %~dp0

echo
start python main.py

echo
timeout /t 2 > nul

echo
start python config.py


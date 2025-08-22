@echo off
echo Generating Upstox Portfolio Report...
cd /d "%~dp0"
"C:/Users/SURESH KUMAR/AppData/Local/Microsoft/WindowsApps/python3.13.exe" generate_report.py
echo Opening report in browser...
start "" "%~dp0report\index.html"
echo Done!
@echo off
set "PATH=C:\Program Files\KiCad\10.0\bin;%PATH%"
cd /d "%~dp0"
"C:\Program Files\KiCad\10.0\bin\python.exe" "%~dp0fabricate.py"
pause

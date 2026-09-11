@echo off
rem Double-click me to start the whole AI Agent Control Panel stack.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-all.ps1"
echo.
echo Press any key to close this window (the 4 app windows stay open)...
pause >nul
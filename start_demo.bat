@echo off
title Med Help USA - Voice Agent Demo
color 0A

echo.
echo ============================================================
echo    Med Help USA - Voice Agent Demo
echo ============================================================
echo.
echo Starting demo server and voice agent...
echo.

:: Start demo server in a new window
start "Demo Server" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe demo_server.py"

:: Wait a moment for server to start
timeout /t 2 /nobreak > nul

:: Start voice agent in dev mode
start "Voice Agent" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe main.py dev"

:: Wait a moment
timeout /t 3 /nobreak > nul

:: Open browser
echo.
echo Opening browser...
start http://localhost:8080

echo.
echo ============================================================
echo    Demo is running!
echo ============================================================
echo.
echo    Web Interface: http://localhost:8080
echo    Demo Server:   Running in separate window
echo    Voice Agent:   Running in separate window
echo.
echo    To stop: Close the two terminal windows
echo ============================================================
echo.
pause

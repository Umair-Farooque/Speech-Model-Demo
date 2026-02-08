@echo off
title Med Help USA - CLEAN RESTART
color 0C

echo ============================================================
echo   STOPPING ALL PREVIOUS PROCESSES...
echo ============================================================
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM cmd.exe /FI "windowtitle eq Demo Server*" 2>nul
taskkill /F /IM cmd.exe /FI "windowtitle eq Voice Agent*" 2>nul
timeout /t 2 > nul

echo.
echo ============================================================
echo   STARTING DEMO SERVER...
echo ============================================================
start "Demo Server" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe demo_server.py"
timeout /t 3 > nul

echo.
echo ============================================================
echo   STARTING AGENT (FORCED CONNECT TO demo-room)...
echo ============================================================
start "Voice Agent" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe main.py connect --room demo-room"
timeout /t 5 > nul

echo.
echo ============================================================
echo   OPENING BROWSER...
echo ============================================================
start http://localhost:8080

echo.
echo ============================================================
echo   DIAGNOSTIC CHECKLIST:
echo   1. Is "Demo Server" window open?
echo   2. Does "Voice Agent" window say "worker started"?
echo   3. Click "Test Browser Sound" in the browser. 
echo   4. Click "Call".
echo ============================================================
pause

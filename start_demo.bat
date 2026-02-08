@echo off
echo ================================
echo Speech-to-Speech Demo Launcher
echo ================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then activate it and install requirements: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    pause
    exit /b 1
)

echo Starting Token Server...
start "Token Server" cmd /k ".venv\Scripts\activate && python services/token_server.py"

timeout /t 3 /nobreak >nul

echo Starting Voice Agent...
start "Voice Agent" cmd /k ".venv\Scripts\activate && python agent/main.py start"

timeout /t 3 /nobreak >nul

echo.
echo ================================
echo Demo is starting!
echo ================================
echo.
echo Token Server: http://localhost:8000
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start http://localhost:8000

echo.
echo [SUCCESS] Demo launched successfully!
echo.
echo To stop the demo, close the terminal windows.
echo.
pause

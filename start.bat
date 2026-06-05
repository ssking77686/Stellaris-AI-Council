@echo off
chcp 65001 >nul
title 群星AI智囊团

cd /d "%~dp0"

:: 自动添加 Node.js 到 PATH
set "NODE_PATH=C:\Program Files\nodejs"
if exist "%NODE_PATH%\node.exe" set "PATH=%NODE_PATH%;%PATH%"

echo.
echo   === Stellaris AI Brain Trust ===
echo   ================================
echo.

echo [*] Starting backend...
start "Stellaris-Backend" cmd /c "cd /d backend && python -m uvicorn app.main:app --port 8001 --host 0.0.0.0"

echo [*] Starting frontend...
start "Stellaris-Frontend" cmd /c "cd /d stellaris-command-center && pnpm dev --port 5173"

echo [*] Waiting for services to be ready...
timeout /t 8 /nobreak >nul

echo [*] Opening browser...
start http://localhost:5173

echo.
echo   All services started!
echo   ----------------------
echo   Dashboard:    http://localhost:5173
echo   Save Manager: http://localhost:5173/saves
echo   API Docs:     http://localhost:8001/docs
echo.
echo   Close the two "Stellaris-*" windows to stop services.
echo.
pause

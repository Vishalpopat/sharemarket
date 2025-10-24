@echo off
echo Starting F&O Breakout WebApp...
call "%~dp0venv\Scripts\activate.bat"

REM Stay in ShareMarket directory where webapp is located
cd /d "%~dp0"

if not "%WEBAPP_HOST%"=="" (
  echo Using existing ENV host: %WEBAPP_HOST%
) else (
  set WEBAPP_HOST=0.0.0.0
)
if not "%WEBAPP_PORT%"=="" (
  echo Using existing ENV port: %WEBAPP_PORT%
) else (
  set WEBAPP_PORT=8000
)
echo Host: %WEBAPP_HOST%  Port: %WEBAPP_PORT%
echo Launching uvicorn from %CD% ...
python -m uvicorn webapp.app:app --reload --host %WEBAPP_HOST% --port %WEBAPP_PORT%

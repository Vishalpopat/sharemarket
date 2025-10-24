@echo off
REM Quick activation script for the virtual environment

echo Activating Stock Market Analysis Tool environment...
call venv\Scripts\activate.bat

echo Checking for uvicorn...
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
  echo uvicorn not found. Installing web dependencies...
  if exist webapp\requirements.txt (
    pip install -r webapp\requirements.txt
  ) else (
    pip install uvicorn fastapi python-dotenv pydantic
  )
)

echo.
echo ========================================
echo Virtual Environment Activated!
echo ========================================
echo.
echo Available commands:
echo   python main.py          - Run the main application
echo   python test_setup.py    - Test the installation
echo   deactivate              - Exit virtual environment
echo.
echo Current Python: %cd%\venv\Scripts\python.exe
echo.
echo To start web app: run_webapp.bat

REM Keep the command prompt open
cmd /k

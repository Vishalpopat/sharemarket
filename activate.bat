@echo off
REM Quick activation script for the virtual environment

echo Activating Stock Market Analysis Tool environment...
call venv\Scripts\activate.bat

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

REM Keep the command prompt open
cmd /k

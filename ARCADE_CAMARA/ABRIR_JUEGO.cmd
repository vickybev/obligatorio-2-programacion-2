@echo off
setlocal
set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo No encontre el entorno del juego. Segui las instrucciones de README.md.
    pause
    exit /b 1
)
"%PYTHON%" -u "%~dp0main.py" %*
if errorlevel 1 pause


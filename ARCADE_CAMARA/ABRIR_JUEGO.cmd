@echo off
setlocal
set "PYTHON=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON%" goto ejecutar
set "PYTHON=%~dp0..\..\ejercicios-clase\.venv\Scripts\python.exe"
if exist "%PYTHON%" goto ejecutar
set "PYTHON=%~dp0..\..\..\ejercicios-clase\.venv\Scripts\python.exe"
if exist "%PYTHON%" goto ejecutar
set "PYTHON=%~dp0..\..\..\..\ejercicios-clase\.venv\Scripts\python.exe"
if exist "%PYTHON%" goto ejecutar

echo Preparando el entorno local de La casita de los hechizos...
py -3.12 -m venv "%~dp0.venv"
if errorlevel 1 goto error_instalacion
set "PYTHON=%~dp0.venv\Scripts\python.exe"

:ejecutar
"%PYTHON%" -c "import cv2, mediapipe, pygame" >nul 2>&1
if not errorlevel 1 goto juego
echo Instalando las dependencias del juego...
"%PYTHON%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto error_instalacion

:juego
"%PYTHON%" -u "%~dp0main.py" %*
if not errorlevel 1 exit /b 0
echo.
echo El juego se cerro con un error. Revisa el mensaje de arriba.
pause
exit /b 1

:error_instalacion
echo.
echo No se pudo preparar el entorno. Revisa Python 3.12 y las instrucciones de README.md.
pause
exit /b 1

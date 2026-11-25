@echo off
rem Complete l'installation des plugins faite dans Meshroom (moteur RNb-NeuS2).
chcp 65001 >nul
setlocal
set "UV=%~dp0Meshroom\bin\uv.exe"
if not exist "%UV%" (
    echo Meshroom n'est pas encore installe : lancez d'abord installer.bat
    if /i not "%~1"=="--no-pause" pause
    exit /b 1
)
"%UV%" run --no-project --python 3.11 "%~dp0scripts\finaliser.py"
set "RESULT=%ERRORLEVEL%"
echo.
if /i not "%~1"=="--no-pause" pause
exit /b %RESULT%

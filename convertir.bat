@echo off
rem Convertit une archive Nenuscanner en dossier pour Meshroom.
rem Double-cliquez, ou glissez l'archive (.zip ou dossier) sur ce fichier.
chcp 65001 >nul
setlocal
set "UV=%~dp0Meshroom\bin\uv.exe"
if not exist "%UV%" (
    echo Meshroom n'est pas encore installe : lancez d'abord installer.bat
    pause
    exit /b 1
)
"%UV%" run --no-project --python 3.11 "%~dp0scripts\nenuscan2mr.py" %*
echo.
pause

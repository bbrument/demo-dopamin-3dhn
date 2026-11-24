@echo off
rem Lance Meshroom (installe par installer.bat).
setlocal
if not exist "%~dp0Meshroom\Meshroom.exe" (
    echo Meshroom n'est pas encore installe : lancez d'abord installer.bat
    pause
    exit /b 1
)
start "" "%~dp0Meshroom\Meshroom.exe"

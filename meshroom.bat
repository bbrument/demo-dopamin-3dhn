@echo off
rem Lance Meshroom (installe par installer.bat).
setlocal
if not exist "%~dp0Meshroom\Meshroom.exe" (
    echo Meshroom n'est pas encore installe : lancez d'abord installer.bat
    pause
    exit /b 1
)
if exist "%~dp0models\sam3.pt" set "RDS_SAM3_MODEL_PATH=%~dp0models\sam3.pt"
start "" "%~dp0Meshroom\Meshroom.exe"

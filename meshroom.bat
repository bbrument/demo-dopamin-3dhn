@echo off
rem Lance Meshroom (installe par installer.bat).
setlocal
if not exist "%~dp0Meshroom\Meshroom.exe" (
    echo Meshroom n'est pas encore installe : lancez d'abord installer.bat
    pause
    exit /b 1
)
rem Chemins longs pour git (le depot RNb-NeuS2 depasse la limite Windows de 260 caracteres).
set "GIT_CONFIG_COUNT=1"
set "GIT_CONFIG_KEY_0=core.longpaths"
set "GIT_CONFIG_VALUE_0=true"
start "" "%~dp0Meshroom\Meshroom.exe"

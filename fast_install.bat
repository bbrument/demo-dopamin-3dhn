@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
rem Chemins longs pour git (precaution : certains depots depassent la limite Windows de 260 caracteres).
set "GIT_CONFIG_COUNT=1"
set "GIT_CONFIG_KEY_0=core.longpaths"
set "GIT_CONFIG_VALUE_0=true"

set "INSTALL_ENGRAVING=0"
if /i "%~1"=="--engraving" set "INSTALL_ENGRAVING=1"
if /i "%~1"=="--help" goto aide
if /i "%~1"=="-h" goto aide
if not "%~1"=="" if /i not "%~1"=="--engraving" goto usage
if not "%~2"=="" goto usage

echo Cette installation telecharge plusieurs dizaines de Go et peut durer 1 a 2 heures.
if not exist "Meshroom\Meshroom.exe" (
    call installer.bat --no-pause
    if errorlevel 1 goto erreur
)

set "PLUGIN_CLI=%~dp0Meshroom\meshroom_plugins.exe"
if not exist "%PLUGIN_CLI%" (
    echo ERREUR : meshroom_plugins.exe est introuvable dans Meshroom.
    echo Cette version doit etre remplacee par la nightly actuelle ; renommez l'ancien dossier Meshroom puis relancez.
    goto erreur
)

call :installerPlugin mrSegmentation || goto erreur
rem mrLedGetter : pas sous Windows (JAX n'y a pas de version GPU).
call :installerPlugin mrLINOUniPS || goto erreur
call :installerPlugin mrRNbNeuS2 || goto erreur
if "%INSTALL_ENGRAVING%"=="1" (
    call :installerPlugin mrEngravingSeg
    if errorlevel 1 goto erreur
)

call finaliser.bat --no-pause
if errorlevel 1 goto erreur

echo.
echo Installation terminee. Lancez Meshroom avec meshroom.bat.
pause
exit /b 0

:installerPlugin
set "PLUGIN=%~1"
if exist "Meshroom\plugins\%PLUGIN%\meshroom" (
    echo %PLUGIN% : deja installe.
    exit /b 0
)
echo Installation de %PLUGIN%...
"%PLUGIN_CLI%" install --force "%PLUGIN%"
if errorlevel 1 exit /b 1
if not exist "Meshroom\plugins\%PLUGIN%\meshroom" (
    echo ERREUR : l'installation de %PLUGIN% n'a pas cree le dossier attendu.
    exit /b 1
)
exit /b 0

:aide
echo Usage: fast_install.bat [--engraving]
echo Installe Meshroom, les plugins requis (sauf mrLedGetter, Linux seulement) et le moteur RNb-NeuS2.
echo --engraving installe aussi le plugin facultatif mrEngravingSeg (environ 4,5 Go).
exit /b 0

:usage
echo Usage: fast_install.bat [--engraving]
exit /b 2

:erreur
echo.
echo ERREUR : installation incomplete. Corrigez le probleme puis relancez fast_install.bat.
pause
exit /b 1

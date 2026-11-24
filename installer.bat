@echo off
rem Installe Meshroom dans le dossier Meshroom\ a cote de ce fichier. Les plugins s'installent ensuite dans Meshroom.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if exist "Meshroom\Meshroom.exe" goto fin

echo Telechargement de Meshroom (600 Mo)...
for /f "usebackq delims=" %%u in (`powershell -NoProfile -Command "((Invoke-RestMethod 'https://api.github.com/repos/alicevision/Meshroom/releases/tags/nightly').assets | Where-Object name -like '*windows-full.zip' | Select-Object -First 1).browser_download_url"`) do set "URL=%%u"
if not defined URL (
    echo ERREUR : impossible de trouver Meshroom en ligne. Verifiez la connexion internet.
    pause
    exit /b 1
)
curl.exe -L -C - --retry 5 -o meshroom.zip "%URL%" || goto erreur
echo Extraction...
tar.exe -xf meshroom.zip || goto erreur
for /d %%d in (Meshroom-*-windows) do ren "%%d" Meshroom
if not exist "Meshroom\Meshroom.exe" goto erreur
del meshroom.zip

:fin
echo.
echo Meshroom est installe. Lancez-le avec meshroom.bat, puis installez les plugins (etape 3 du README).
pause
exit /b 0

:erreur
echo.
echo ERREUR pendant l'installation. Relancez installer.bat.
pause
exit /b 1

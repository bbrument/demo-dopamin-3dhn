@echo off
rem Installe Meshroom et les plugins de l'atelier dans le dossier Meshroom\ a cote de ce fichier.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if exist "Meshroom\bin\uv.exe" goto plugins

echo [1/2] Telechargement de Meshroom (600 Mo)...
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
if not exist "Meshroom\bin\uv.exe" goto erreur
del meshroom.zip

:plugins
echo [2/2] Installation des plugins (1 a 2 heures, 30 Go)...
"Meshroom\bin\uv.exe" run --no-project --python 3.11 scripts\install.py || goto erreur
echo.
echo Installation terminee. Lancez Meshroom avec meshroom.bat
pause
exit /b 0

:erreur
echo.
echo ERREUR pendant l'installation. Relancez installer.bat : il reprend ou il s'est arrete.
pause
exit /b 1

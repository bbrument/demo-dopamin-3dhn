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
rem Raccourci sur le Bureau (sans consequence s'il ne peut pas etre cree)
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Meshroom 3DHN.lnk'); $s.TargetPath='%~dp0meshroom.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0Meshroom\Meshroom.exe,0'; $s.Save()" >nul 2>&1
echo.
if /i "%~1"=="--no-pause" (
    echo Meshroom est installe.
) else (
    echo Meshroom est installe. Lancez-le avec meshroom.bat, puis installez les plugins (etape 3 du README^).
)
if /i not "%~1"=="--no-pause" pause
exit /b 0

:erreur
echo.
echo ERREUR pendant l'installation. Relancez installer.bat.
if /i not "%~1"=="--no-pause" pause
exit /b 1

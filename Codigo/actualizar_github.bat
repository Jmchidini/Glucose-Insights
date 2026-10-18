@echo off
setlocal
if not exist "%~dp0..\ACTUALIZAR_GITHUB.bat" (
    echo Usa ACTUALIZAR_GITHUB.bat en la carpeta principal Glucose Insights APK.
    pause
    exit /b 1
)
call "%~dp0..\ACTUALIZAR_GITHUB.bat"
exit /b %ERRORLEVEL%

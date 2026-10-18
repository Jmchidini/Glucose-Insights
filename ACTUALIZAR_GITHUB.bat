@echo off
setlocal
title Glucose Insights - Actualizar GitHub
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Publicar-GitHub.ps1"
set "RESULTADO=%ERRORLEVEL%"
echo.
if not "%RESULTADO%"=="0" echo No se completo la publicacion. Revisa el mensaje anterior.
pause
exit /b %RESULTADO%

@echo off
setlocal
title Glucose Insights - Revisar archivos
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Publicar-GitHub.ps1" -SoloRevisar
set "RESULTADO=%ERRORLEVEL%"
echo.
pause
exit /b %RESULTADO%

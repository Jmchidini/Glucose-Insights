@echo off
setlocal enabledelayedexpansion
title Glucose Insights - Servidor local
cd /d "%~dp0"

echo ============================================================
echo  Glucose Insights - iniciando servidor local
echo ============================================================
echo.

set "PYCMD="
where py >nul 2>nul
if not errorlevel 1 set "PYCMD=py"

if not defined PYCMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYCMD=python"
)

if not defined PYCMD (
    echo No se encontro Python instalado en este equipo.
    echo Descargalo desde https://www.python.org/downloads/
    echo IMPORTANTE: durante la instalacion, tildar la opcion "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo Usando interprete: %PYCMD%
echo.
echo Verificando dependencias (la primera vez puede tardar un par de minutos)...
%PYCMD% -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo Hubo un problema instalando las dependencias. Revisa el mensaje de arriba.
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencias listas.
echo Iniciando el servidor en una ventana aparte...
echo.

start "Glucose Insights - Servidor (no cerrar)" /min cmd /c "%PYCMD% app.py"

echo Esperando a que el servidor arranque...
timeout /t 3 /nobreak >nul

start "" http://localhost:5000

echo ============================================================
echo  Listo. Se abrio http://localhost:5000 en el navegador.
echo.
echo  El servidor sigue corriendo en una ventana minimizada
echo  llamada "Glucose Insights - Servidor (no cerrar)".
echo  Para APAGARLO: buscala en la barra de tareas y cerrala
echo  (o cerrala desde el Administrador de tareas).
echo.
echo  Esta ventana se puede cerrar sin problema.
echo ============================================================
echo.
pause

@echo off
setlocal enabledelayedexpansion
title Glucose Insights - Generar PDF
cd /d "%~dp0"

if "%~1"=="" (
    echo ============================================================
    echo  Glucose Insights - generador por linea de comandos
    echo ============================================================
    echo.
    echo Arrastra un archivo CSV de LibreView sobre este .bat
    echo para generar el informe en PDF.
    echo.
    echo Tambien se puede ejecutar manualmente:
    echo    generar_informe.bat "ruta\al\archivo.csv" [dias]
    echo.
    echo Ejemplo:
    echo    generar_informe.bat "C:\Users\pc\Downloads\datos.csv" 15
    echo.
    pause
    exit /b 0
)

set "CSV_PATH=%~1"
set "DIAS=%~2"
if "%DIAS%"=="" set "DIAS=15"

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

echo ============================================================
echo  Generando informe CGM
echo  Archivo:  %CSV_PATH%
echo  Periodo:  ultimos %DIAS% dias  (0 = todo el archivo)
echo ============================================================
echo.

echo Verificando dependencias...
%PYCMD% -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo Hubo un problema instalando las dependencias. Revisa el mensaje de arriba.
    echo.
    pause
    exit /b 1
)

set "OUT_PATH=%~dpn1_informe.pdf"

echo.
echo Analizando datos y generando el PDF...
%PYCMD% glucose_insights.py "%CSV_PATH%" --days %DIAS% --output "%OUT_PATH%"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo  Hubo un error al generar el informe. Revisa el mensaje de arriba.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Listo. Informe generado en:
echo    %OUT_PATH%
echo ============================================================
echo.

start "" "%OUT_PATH%"
pause

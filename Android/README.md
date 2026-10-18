# Glucose Insights Android

Primera versión para Android 9 (API 28) o posterior, arquitectura ARM de 32 bits.
Pantalla nativa: seleccionar TSV/CSV, elegir período, generar, abrir, compartir y guardar PDF.
Los datos provienen de archivos exportados de Juggluco. El lector admite
Stream TSV/CSV y CSV con formato LibreView; no hay conexión directa al sensor ni a Juggluco.
No solicita permiso de Internet ni acceso general al almacenamiento. Usa el selector de archivos de Android.

## Compilación

Requiere JDK 17, Gradle 8.9, Android SDK 35 con build-tools 34.0.0 y Python 3.10 completo.
Configurar JAVA_HOME y ANDROID_HOME; GLUCOSE_BUILD_PYTHON puede indicar la ruta a python.exe.
Desde esta carpeta, ejecutar `gradle assembleDebug` (o el wrapper incluido cuando esté disponible).
Las dependencias de compilación se descargan; el uso de la app no necesita conexión.

El motor en app/src/main/python/glucose_insights.py parte de ../Codigo/glucose_insights.py.
La diferencia móvil es GLUCOSE_CHART_DPI (120 al generar) para limitar memoria y tamaño de PDF.
Se fijan versiones compatibles con las bibliotecas ARM de Chaquopy; no sustituirlas por
las versiones del requirements.txt de escritorio sin comprobar disponibilidad para Android.

## Prueba en el dispositivo

1. Instalar la APK de prueba y abrir Glucose Insights.
2. Elegir el TSV Stream, últimos 15 días, y generar; repetir con el CSV LibreView.
3. Comprobar apertura, guardado y compartición del PDF.
4. Probar cancelación del selector, archivo inválido y rotación de pantalla.
5. Comprobar funcionamiento sin conexión y comparar métricas con el informe de escritorio.

No se incluyen datos del usuario en la APK. El último PDF generado queda dentro de la app;
las copias guardadas o compartidas quedan bajo control del usuario. La selección admite hasta 20 MB.
Mantener la app abierta durante la generación. Si Android la cierra por falta de memoria,
volver a abrir y repetir; esta primera versión no continúa trabajos tras un cierre del proceso.
La compilación por sí sola no confirma el funcionamiento ni el rendimiento en el Galaxy J7 Neo.

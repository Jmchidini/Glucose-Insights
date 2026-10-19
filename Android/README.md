# Glucose Insights Android

Versión 0.2 para Android 9 (API 28) o posterior, arquitectura ARM de 32 bits.
Pantalla nativa: seleccionar TSV/CSV, elegir período, generar, abrir, compartir y guardar PDF.
Los datos provienen de archivos exportados de Juggluco. El lector admite
Stream TSV/CSV y CSV con formato LibreView; no hay conexión directa al sensor ni a Juggluco.
No solicita permiso de Internet ni acceso general al almacenamiento. Usa el selector de archivos de Android.

## Idiomas / Languages

Seleccioná **Español** o **English** en la pantalla principal. La elección se
recuerda al cerrar la app. En el primer inicio se usa español si el teléfono está
en español; en los demás casos, inglés. La interfaz y los nuevos PDF se generan
en el idioma seleccionado, incluidos gráficos, tablas y explicaciones.
Cambiar el idioma conserva el archivo y el período seleccionados. Para traducir
un informe ya generado, generarlo nuevamente; las copias guardadas no se modifican.
El selector de archivos y otras ventanas del sistema usan el idioma de Android.

Choose **Español** or **English** on the main screen. The app remembers your
choice and uses it for the interface and newly generated PDF reports, including
charts, tables and explanations. Generate the report again after changing
language. Previously saved copies are unchanged. Android file pickers use the
system language. Glucose values and units (mg/dL) are identical in both languages.

## Compilación

Requiere JDK 17, Gradle 8.9, Android SDK 35 con build-tools 34.0.0 y Python 3.10 completo.
Configurar JAVA_HOME y ANDROID_HOME; GLUCOSE_BUILD_PYTHON puede indicar la ruta a python.exe.
Desde esta carpeta, ejecutar `gradle assembleDebug` (o el wrapper incluido cuando esté disponible).
Las dependencias de compilación se descargan; el uso de la app no necesita conexión.

El motor en app/src/main/python/glucose_insights.py parte de ../Codigo/glucose_insights.py.
La versión móvil usa GLUCOSE_CHART_DPI (120 al generar) para limitar memoria y
tamaño de PDF, y report_i18n.py para traducir la presentación sin modificar los cálculos.
Los textos de la interfaz están en res/values/strings.xml (inglés) y
res/values-es/strings.xml (español). Las pruebas de idioma se ejecutan con
`python -m unittest discover -s tests` desde Android/, con las dependencias del informe instaladas.
Se fijan versiones compatibles con las bibliotecas ARM de Chaquopy; no sustituirlas por
las versiones del requirements.txt de escritorio sin comprobar disponibilidad para Android.

## Prueba en el dispositivo

1. Instalar la APK de prueba y abrir Glucose Insights.
2. Elegir el TSV Stream, últimos 15 días, y generar; repetir con el CSV LibreView.
3. Comprobar apertura, guardado y compartición del PDF.
4. Probar cancelación del selector, archivo inválido y rotación de pantalla.
5. Comprobar funcionamiento sin conexión y comparar métricas con el informe de escritorio.
6. Cambiar entre Español y English; comprobar que conserva archivo y período.
7. Generar un PDF en cada idioma, cerrar y abrir la app y comprobar el idioma guardado.

No se incluyen datos del usuario en la APK. El último PDF generado queda dentro de la app;
las copias guardadas o compartidas quedan bajo control del usuario. La selección admite hasta 20 MB.
Mantener la app abierta durante la generación. Si Android la cierra por falta de memoria,
volver a abrir y repetir; esta primera versión no continúa trabajos tras un cierre del proceso.
La compilación por sí sola no confirma el funcionamiento ni el rendimiento en el Galaxy J7 Neo.

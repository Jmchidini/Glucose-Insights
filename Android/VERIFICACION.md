# Verificación de la versión 0.1 de prueba

- Compilación assembleDebug: correcta.
- Android lint: sin errores. Avisos sobre traducción de textos, versiones de bibliotecas, ChromeOS y reglas de copia de seguridad en Android 12+.
- Firma APK v2: verificada con apksigner.
- minSdk 28 (Android 9), targetSdk 35, ABI armeabi-v7a.
- Sin permisos de Internet ni de almacenamiento general en el manifiesto resultante.
- Cinco pruebas de lectura y cálculos temporales: correctas.
- Motor móvil probado en Windows con Python 3.10, NumPy 1.26.2, pandas 2.1.3, Matplotlib 3.6.0, Pillow 9.2.0 y ReportLab 4.0.9.
- TSV Stream: PDF generado, últimos 15 días, 21.560 lecturas, intervalo detectado 1 minuto.
- CSV LibreView: PDF generado, últimos 15 días, 4.320 lecturas, intervalo detectado 5 minutos.

Pendiente: ejecutar la APK en el Galaxy J7 Neo. No se ha validado todavía la interfaz,
la importación mediante el selector del teléfono, la generación con las bibliotecas
nativas de Android, el guardado, la compartición ni el consumo de memoria en ese equipo.
La prueba del motor en Windows no reemplaza esas comprobaciones.

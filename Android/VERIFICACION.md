# Verificación de la versión 0.2 bilingüe

Verificada el 18/10/2026.

- assembleDebug y lintDebug: correctos; lint informa 0 errores y 4 avisos
  (bibliotecas, ChromeOS y configuración de copias de seguridad en Android 12+).
- APK firmada con esquema v2; mismo certificado que la APK 0.1.
- versionCode 2, versionName 0.2-bilingual, minSdk 28 (Android 9),
  targetSdk 35, ABI armeabi-v7a.
- Sin permiso de Internet ni de almacenamiento general en el manifiesto resultante.
- Cinco pruebas automatizadas de idioma: traducciones y parámetros, restauración
  del contexto tras errores, formatos numéricos, mensajes de validación y lectura
  de encabezados españoles al generar informes en inglés.
- Motor móvil probado en Windows con Python 3.10, NumPy 1.26.2, pandas 2.1.3,
  Matplotlib 3.6.0, Pillow 9.2.0 y ReportLab 4.0.9.
- TSV Stream y CSV LibreView: generados los últimos 15 días en ambos idiomas
  (cuatro PDF, 13 páginas cada uno). 21.560 y 4.320 lecturas respectivamente.
- Lecturas, métricas y eventos comparados con el motor anterior: coinciden.
- Texto e índice de los PDF comprobados; revisión visual de los informes.
  Corregida la tabla de rango estricto que excedía el ancho de página y
  las etiquetas recortadas en segmentos pequeños del gráfico.

La versión 0.1 fue probada por el usuario en el Galaxy J7 Neo. La versión 0.2
todavía requiere comprobar en ese teléfono: cambio de idioma, persistencia de la
elección al cerrar y abrir, conservación del archivo y período al cambiar idioma,
generación, apertura, guardado y compartición del PDF en ambos idiomas.
Las pruebas del motor en Windows y la compilación no sustituyen esa prueba física.

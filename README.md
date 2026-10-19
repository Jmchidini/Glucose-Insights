# Glucose Insights

Generador local de informes de glucosa con métricas, gráficos y exportación a PDF,
disponible como aplicación de escritorio y como APK Android de prueba.

La APK 0.2 incluye **Español / English** para la interfaz y los informes PDF.
El idioma se elige en la pantalla principal y queda guardado para el próximo uso.
Los cálculos y las unidades (mg/dL) son iguales en ambos idiomas.

**English:** Android version 0.2 supports Spanish and English for both the app
and PDF reports. Choose a language on the main screen; your choice is saved.
Reports use locally processed files exported from Juggluco (Stream TSV/CSV or
LibreView-format CSV). Glucose values and units remain the same in either language.

## Fuente de los datos

Los datos utilizados para generar los informes provienen de **Juggluco**.
Glucose Insights analiza los archivos que el usuario exporta y selecciona;
no se conecta directamente con Juggluco ni con el sensor.

Actualmente admite las variantes comprobadas en este proyecto:

- **Stream TSV/CSV:** fecha y hora en `YYYY-mm-ddTHH:MM:SS` y glucosa en `mg/dL`.
- **CSV con formato LibreView:** fecha y hora en `Device Timestamp` y glucosa
  histórica en `Historic Glucose mg/dL`.

Stream y LibreView identifican los formatos de archivo que reconoce el lector.
El intervalo entre lecturas se detecta a partir de las fechas del archivo.

## Uso

- `Codigo/`: aplicación de escritorio en Python y pruebas de formatos.
- `Android/`: aplicación Android de prueba para Android 9 y ARM de 32 bits.

En Windows, con Python instalado, ejecutar `Codigo/iniciar_app.bat`.
Para compilar Android, consultar `Android/README.md`.

## Privacidad y estado

El procesamiento del informe se realiza localmente. El repositorio no incluye
archivos personales de glucosa, informes de usuarios ni claves.
La APK está en fase de prueba; su funcionamiento y rendimiento deben comprobarse
en cada dispositivo.

El informe es material de apoyo para consulta médica, no un diagnóstico ni una indicación terapéutica.

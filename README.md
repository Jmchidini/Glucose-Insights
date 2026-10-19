# Glucose Insights

[English](#english) · [Español](#espanol)

<a id="english"></a>

## English

Glucose Insights generates glucose reports locally, with metrics, charts and PDF
export. It is available as a Python desktop application and an Android test APK.

### Languages

Android version 0.2 supports **English and Spanish** for the interface and PDF
reports, including charts, tables and explanations. Choose a language on the main
screen; the app remembers your choice. Generate the report again after changing
language to obtain a PDF in that language. Calculations and units (mg/dL) remain
the same in both languages. The desktop interface is currently in Spanish.

### Data source

The data used for reports comes from **Juggluco**. Glucose Insights analyzes files
that the user exports and selects; it does not connect directly to Juggluco or
the sensor.

The following formats have been tested in this project:

- **Stream TSV/CSV:** timestamps in `YYYY-mm-ddTHH:MM:SS` and glucose in `mg/dL`.
- **LibreView-format CSV:** timestamps in `Device Timestamp` and historical
  glucose in `Historic Glucose mg/dL`.

Stream and LibreView identify the file formats recognized by the reader. The
interval between readings is detected from the timestamps in the file.

### Getting started

- **Windows:** with Python installed, run `Codigo/iniciar_app.bat`, select a CSV
  or TSV file, choose the report period and generate the PDF. Dependencies are
  installed on the first run, which requires an Internet connection.
- **Android:** the test app targets Android 9 (API 28) or later and 32-bit ARM.
  Select a file and report period, then generate, open, save or share the PDF.
  Report generation works offline with files stored on the phone.

The [desktop guide](Codigo/README.md), [Android build guide](Android/README.md)
and [installation instructions](Android/INSTALAR-Y-PROBAR.md) provide more detail
(primarily in Spanish).

### Privacy and project status

Reports are processed locally. This repository does not include personal glucose
data, user reports or signing keys. The Android app is a test version; its
operation and performance must be checked on each device. See the
[verification notes](Android/VERIFICACION.md) for completed checks and pending
device tests.

Reports are supporting material for medical consultation, not a diagnosis or
treatment recommendation.

---

<a id="espanol"></a>

## Español

Glucose Insights genera informes de glucosa de forma local, con métricas,
gráficos y exportación a PDF. Está disponible como aplicación de escritorio en
Python y como APK Android de prueba.

### Idiomas

La versión Android 0.2 incluye **inglés y español** para la interfaz y los
informes PDF, incluidos gráficos, tablas y explicaciones. Elegí el idioma en la
pantalla principal; la app recuerda tu elección. Después de cambiarlo, generá
nuevamente el informe para obtener el PDF en ese idioma. Los cálculos y las
unidades (mg/dL) son iguales en ambos idiomas. La interfaz de escritorio está
actualmente en español.

### Fuente de los datos

Los datos utilizados para generar los informes provienen de **Juggluco**.
Glucose Insights analiza los archivos que el usuario exporta y selecciona;
no se conecta directamente con Juggluco ni con el sensor.

Actualmente admite las variantes comprobadas en este proyecto:

- **Stream TSV/CSV:** fecha y hora en `YYYY-mm-ddTHH:MM:SS` y glucosa en `mg/dL`.
- **CSV con formato LibreView:** fecha y hora en `Device Timestamp` y glucosa
  histórica en `Historic Glucose mg/dL`.

Stream y LibreView identifican los formatos de archivo que reconoce el lector.
El intervalo entre lecturas se detecta a partir de las fechas del archivo.

### Primeros pasos

- **Windows:** con Python instalado, ejecutá `Codigo/iniciar_app.bat`, seleccioná
  un CSV o TSV, elegí el período y generá el PDF. Las dependencias se instalan en
  el primer inicio, que requiere conexión a Internet.
- **Android:** la app de prueba está preparada para Android 9 (API 28) o posterior
  y ARM de 32 bits. Seleccioná un archivo y el período, y generá, abrí, guardá o
  compartí el PDF. La generación funciona sin conexión con archivos descargados
  en el teléfono.

Consultá la [guía de escritorio](Codigo/README.md), la
[guía de compilación Android](Android/README.md) y las
[instrucciones de instalación](Android/INSTALAR-Y-PROBAR.md) para más detalles.

### Privacidad y estado del proyecto

El procesamiento del informe se realiza localmente. El repositorio no incluye
archivos personales de glucosa, informes de usuarios ni claves de firma.
La app Android está en fase de prueba; su funcionamiento y rendimiento deben
comprobarse en cada dispositivo. Las [notas de verificación](Android/VERIFICACION.md)
detallan las comprobaciones realizadas y las pruebas pendientes en el teléfono.

El informe es material de apoyo para consulta médica, no un diagnóstico ni una
indicación terapéutica.

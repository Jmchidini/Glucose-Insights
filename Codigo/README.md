# Glucose Insights — App local (drag & drop)

Interfaz web sencilla para generar el informe de monitoreo continuo de
glucosa en PDF a partir de un CSV exportado de LibreView, sin usar la
línea de comandos.

Corre 100% en tu computadora: no sube el CSV a ningún servidor externo.

## Windows: uso con doble clic (recomendado)

No hace falta usar la terminal. Hay dos accesos directos listos para usar:

### Opción A — Interfaz web (arrastrar y soltar en el navegador)
1. Doble clic en **`iniciar_app.bat`**.
2. La primera vez va a instalar las dependencias (tarda un par de minutos); las siguientes veces arranca al instante.
3. Se abre automáticamente el navegador en `http://localhost:5000`. Ahí arrastrás el CSV, elegís el período y descargás el PDF.
4. El servidor queda corriendo en una ventana minimizada llamada **"Glucose Insights - Servidor (no cerrar)"**. Para apagarlo, cerrá esa ventana (o buscala en el Administrador de tareas).

### Opción B — Arrastrar el CSV directo sobre el ícono (sin navegador)
1. Arrastrá tu archivo CSV de LibreView y soltalo **encima del ícono de `generar_informe.bat`**.
2. Se abre una ventana, procesa el archivo, y al terminar abre el PDF automáticamente.
3. El PDF queda guardado al lado del CSV original, con el mismo nombre + `_informe.pdf`.
4. Por defecto analiza los últimos 15 días. Para otro período, ejecutalo desde una terminal:
   ```
   generar_informe.bat "C:\ruta\datos.csv" 30
   ```
   (30 = días; usar 0 para todo el archivo).

Ambos `.bat` requieren tener Python instalado (ver más abajo) y, la primera vez, conexión a internet para instalar las dependencias.

## Instalación de Python (si no lo tenés)

Descargalo desde https://www.python.org/downloads/ — durante la instalación, **tildá la opción "Add python.exe to PATH"**. Después de instalarlo, los `.bat` funcionan solos.

## Uso manual por línea de comandos (alternativa)

Levantar la interfaz web:
```bash
cd Glucose-Insights
pip install -r requirements.txt
python app.py
```
Vas a ver un mensaje con el link `http://localhost:5000`. Abrilo en el navegador y ahí podés arrastrar el CSV, elegir el período (7 / 15 / 30 / 90 días, o todo el archivo) y hacer clic en "Generar informe PDF"; el PDF se descarga automáticamente. Para detener el servidor, volvé a la terminal y presioná `Ctrl+C`.

O generar el PDF directo, sin servidor:
```bash
python glucose_insights.py archivo.csv --days 15 --output informe.pdf
```

## Archivos

- `iniciar_app.bat` — (Windows) doble clic para levantar la interfaz web e instalar dependencias automáticamente.
- `generar_informe.bat` — (Windows) arrastrá un CSV sobre este ícono para generar el PDF sin usar el navegador.
- `actualizar_github.bat` — (Windows) sube los cambios del proyecto a GitHub con un doble clic (ver sección de abajo).
- `app.py` — servidor web local (Flask) + interfaz de arrastrar y soltar.
- `glucose_insights.py` — motor de análisis y generación del PDF (mismo código que la versión de línea de comandos).
- `requirements.txt` — dependencias necesarias.
- `.gitignore` — evita que los CSV/PDF con datos personales se suban al repositorio.

## Publicar y actualizar en GitHub

Usar **ACTUALIZAR_GITHUB.bat** en la carpeta principal **Glucose Insights APK**.
El acceso de esta carpeta redirige a ese publicador; no ejecuta el script antiguo.
Consultar **GITHUB.md** en la carpeta principal para requisitos y protecciones.
El publicador muestra los cambios, pide confirmación y bloquea datos, informes y claves.

## Notas

- El informe es un documento descriptivo de apoyo para consulta médica; no constituye diagnóstico ni indicación terapéutica.
- Si el CSV no tiene el formato esperado de LibreView (columna de "Historic Glucose" y timestamp), la app va a mostrar un mensaje de error explicando el problema en lugar de descargar un PDF vacío o incorrecto.

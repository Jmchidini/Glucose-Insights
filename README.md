# Glucose Insights

Generador local de informes de glucosa a partir de Stream TSV/CSV y LibreView CSV.

- `Codigo/`: aplicación de escritorio en Python y pruebas de formatos.
- `Android/`: aplicación Android de prueba para Android 9 y ARM de 32 bits.
- `ACTUALIZAR_GITHUB.bat`: publicación del código con revisión previa.
- `REVISAR_SIN_SUBIR.bat`: comprueba localmente los archivos permitidos, sin conectarse a GitHub.
- `GITHUB.md`: instrucciones de publicación y recuperación ante errores.

En Windows, con Python instalado, ejecutar `Codigo/iniciar_app.bat`.
Para compilar Android, consultar `Android/README.md`.

Los datos de ejemplo, informes, APK, archivos originales y claves se conservan
solo en la carpeta local del proyecto y no se incluyen con el publicador.
La APK de prueba debe validarse en el teléfono; compilar no garantiza su rendimiento.

El informe es material de apoyo para consulta médica, no un diagnóstico ni una indicación terapéutica.

# Actualizar GitHub

Repositorio configurado: https://github.com/Jmchidini/Glucose-Insights
Rama: `main`. Estos archivos no crean el repositorio en GitHub ni cambian su visibilidad.

## Primera vez

1. Verificá que el repositorio exista en tu cuenta. Si todavía no existe, crealo
   con el nombre **Glucose-Insights**. Puede estar vacío. Podés elegir privado.
2. Necesitás Git para Windows o GitHub Desktop. Si falta, el programa lo indica.
3. En **Glucose Insights APK**, abrí **ACTUALIZAR_GITHUB.bat**.
4. Si Git solicita iniciar sesión, usá el flujo de autenticación de Git/GitHub.
   El script no guarda contraseñas ni tokens. Si falta tu identidad de Git,
   pedirá nombre y correo para el commit, y los guardará solo en esta copia local.
5. Revisá el resumen; escribí **S** y presioná Enter para subir. Enter sin S cancela.

El correo del commit forma parte del historial. Podés usar tu dirección `noreply`
de GitHub si preferís no publicar el correo personal.

## Después

Editá el código en **Codigo/** o **Android/** y repetí el doble clic.
Si no hay cambios, el programa lo indica. Si no estás seguro de qué archivos
incluye, usá **REVISAR_SIN_SUBIR.bat**: no modifica GitHub ni crea commits.

## Protecciones

- Solo toma código y documentación de las ubicaciones previstas; excluye CSV,
  TSV, PDF, planillas, JSON, ZIP, APK, claves, entornos y archivos temporales.
- Comprueba también el índice y cada commit pendiente de subir, no solo `.gitignore`.
- Detecta algunos formatos frecuentes de tokens y claves privadas. No es un
  detector universal de secretos: revisá el código y no pegues datos personales en él.
- Bloquea enlaces, archivos grandes inesperados y cambios no revisados del wrapper.
- Comprueba cada comando. Solo anuncia éxito cuando Git confirma el push.
- No hace push forzado, no borra ramas ni reemplaza el historial remoto.
- Usa una copia técnica local **.github-sync/**. No edites ni borres esa carpeta:
  puede contener commits pendientes. Tus archivos de trabajo quedan intactos.
- No publica APK automáticamente. La distribución de instaladores se puede
  preparar más adelante mediante Releases.

Si el repositorio ya contiene los scripts antiguos en su raíz, se conservan.
La versión actual estará en **Codigo/** y **Android/**; el README principal lo explica.
Los archivos eliminados dentro de las carpetas administradas se reflejan en
el resumen antes de confirmar. Las carpetas ajenas a estas no se limpian automáticamente.

## Si se detiene

- **Permisos o conexión:** solucioná el acceso y volvé a ejecutar. Un commit
  cuyo push falló queda pendiente; se vuelve a revisar antes de reintentarlo.
- **Cambios nuevos en GitHub:** no los mezcla automáticamente. Hay que revisar
  e incorporar esos cambios en el proyecto antes de continuar; pedí ayuda.
- **Archivo o credencial bloqueados:** no hay opción de ignorar la alerta.
  Revisá el contenido y, si está en commits pendientes, también su historial.
- **main ausente o historial inesperado:** requiere revisar el repositorio.
- **Dos ventanas abiertas:** cerrá una y volvé a intentar; solo una publicación
  puede usar la copia local a la vez.

El script no cambia permisos del repositorio ni publica desde un repositorio
padre de esta carpeta. La autenticación y una publicación real en GitHub se
comprueban al ejecutarlo; las pruebas automatizadas se realizan contra un
repositorio local de prueba, sin subir datos a GitHub.

# Versión adaptada a Stream TSV/CSV

Descomprimí el ZIP en una carpeta nueva y ejecutá iniciar_app.bat.
Elegí tu archivo .tsv o .csv, seleccioná el período y generá el PDF.
También podés arrastrar el TSV sobre generar_informe.bat.
Requiere Python instalado; el inicio instala las bibliotecas necesarias.

Formatos: Stream con columnas YYYY-mm-ddTHH:MM:SS y mg/dL (tabulación,
coma o punto y coma); LibreView con fecha/hora y glucosa histórica en mg/dL.
Las fechas Stream se interpretan en la hora local escrita en el archivo.
No se utiliza Raw como glucosa ni se convierte a otra zona horaria.

Cambios: intervalo mediano detectado; cobertura y días completos ajustados
a ese intervalo; diferencias a 15 minutos por fecha con tolerancia máxima
de un minuto; episodios separados por lecturas normales o huecos mayores
a dos intervalos típicos (máximo 15 minutos). Duplicados idénticos se
eliminan; valores contradictorios en la misma fecha/hora se rechazan.

Los porcentajes de rango siguen siendo porcentajes de lecturas, como en
el programa original; sus duraciones son estimaciones sobre el período.
Esta versión está pensada para archivos de frecuencia aproximadamente
regular. No corrige automáticamente cambios de zona horaria ni mezclas
de sensores con frecuencias distintas. Filas sin fecha válida o glucosa
positiva y finita se excluyen. Las fechas CSV ambiguas priorizan día/mes.

Verificación: cinco pruebas automáticas de formatos y cálculos temporales;
generación de PDF con los últimos 15 días del TSV aportado (21.560 lecturas).
El ZIP no incluye datos personales ni informes del usuario. Aún es una
versión para computadora; no es la APK Android.

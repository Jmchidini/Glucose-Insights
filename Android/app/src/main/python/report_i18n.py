"""Local report translations. Computation and source-file parsing are language independent."""
from contextlib import contextmanager
from contextvars import ContextVar

_language = ContextVar("report_language", default="es")

def language():
    return _language.get()

@contextmanager
def use_language(code):
    token = _language.set(code if code in ("es", "en") else "es")
    try:
        yield
    finally:
        _language.reset(token)

def tr(message, *values):
    template = EN.get(message, message) if language() == "en" else message
    values = tuple(EN.get(v, v) if language() == "en" and isinstance(v, str) else v for v in values)
    return template.format(*values) if values else template

EN = {'Madrugada (00-06h)': 'Overnight (00-06h)',
 'Mañana (06-11h)': 'Morning (06-11h)',
 'Mediodía (11-14h)': 'Midday (11-14h)',
 'Tarde (14-19h)': 'Afternoon (14-19h)',
 'Noche (19-24h)': 'Evening (19-24h)',
 'El período debe ser positivo, o usar 0 para todo el archivo.': 'The period must be positive, or use 0 for '
                                                                 'the whole file.',
 'Formato no reconocido: se admite Stream TSV/CSV o LibreView CSV en mg/dL.': 'Unrecognized format: Stream '
                                                                              'TSV/CSV or LibreView CSV in '
                                                                              'mg/dL is required.',
 'Faltan fecha/hora o glucosa histórica en mg/dL.': 'Date/time or historical glucose in mg/dL is missing.',
 'No hay lecturas válidas en el archivo.': 'There are no valid readings in the file.',
 'Hay lecturas distintas con la misma fecha/hora; revisá los sensores superpuestos.': 'Different readings '
                                                                                      'share the same '
                                                                                      'date/time; check for '
                                                                                      'overlapping sensors.',
 'Se necesitan al menos dos lecturas con fechas diferentes.': 'At least two readings with different '
                                                              'timestamps are required.',
 'El período seleccionado contiene menos de dos lecturas.': 'The selected period contains fewer than two '
                                                            'readings.',
 'Muy alto  (>{0} mg/dL)': 'Very high  (>{0} mg/dL)',
 'Alto  ({0}-{1} mg/dL)': 'High  ({0}-{1} mg/dL)',
 'Rango objetivo  ({0}-{1} mg/dL)': 'Target range  ({0}-{1} mg/dL)',
 'Bajo  ({0}-{1} mg/dL)': 'Low  ({0}-{1} mg/dL)',
 'Muy bajo  (<{0} mg/dL)': 'Very low  (<{0} mg/dL)',
 '{0}-{1} mg/dL (objetivo estricto)': '{0}-{1} mg/dL (strict target)',
 'Glucosa (mg/dL)': 'Glucose (mg/dL)',
 'Curva completa de glucosa — {0}': 'Full glucose trace - {0}',
 'P25–P75 (RIC)': 'P25-P75 (IQR)',
 'Media': 'Mean',
 'Hora del día': 'Hour of day',
 'Perfil de Glucosa Ambulatorio (AGP) — promedio por hora': 'Ambulatory Glucose Profile (AGP) - hourly mean',
 'Media: {0} mg/dL': 'Mean: {0} mg/dL',
 'Mediana: {0} mg/dL': 'Median: {0} mg/dL',
 'N.º de lecturas': 'Number of readings',
 'Distribución de valores de glucosa (histograma)': 'Distribution of glucose values (histogram)',
 'Alto\n(181-250)': 'High\n(181-250)',
 'Bajo\n(54-69)': 'Low\n(54-69)',
 'Muy alto\n(>250)': 'Very high\n(>250)',
 'Muy bajo\n(<54)': 'Very low\n(<54)',
 'Rango objetivo\n(70-180)': 'Target range\n(70-180)',
 '% del tiempo': '% of time',
 'Distribución del tiempo por rango de glucosa (Tiempo en Rango)': 'Time distribution by glucose range (Time '
                                                                   'in Range)',
 'Distribución horaria de glucosa (boxplot por hora)': 'Hourly glucose distribution (boxplot)',
 'Fecha': 'Date',
 'Mapa de calor glucosa promedio por día y hora': 'Mean glucose heatmap by day and hour',
 'Glucosa media (mg/dL)': 'Mean glucose (mg/dL)',
 'Glucosa media ± DE (mg/dL)': 'Mean glucose ± SD (mg/dL)',
 'Glucosa media por hora del día': 'Mean glucose by hour of day',
 'Umbral CV={0}% (ATTD)': 'CV threshold={0}% (ATTD)',
 'Coeficiente de variación (%)': 'Coefficient of variation (%)',
 'Variabilidad glucémica por hora (CV%)': 'Hourly glucose variability (CV%)',
 'moderada, dentro del umbral de estabilidad': 'moderate, within the stability threshold',
 'moderada a elevada, levemente por encima del umbral de estabilidad': 'moderate to high, slightly above the '
                                                                       'stability threshold',
 'Se analizaron {0} lecturas de glucosa intersticial histórica (intervalo típico de {1} minutos) correspondientes a {2}, con un tiempo activo de sensor del {3} % dentro de esa ventana.': '{0} '
                                                                                                                                                                                           'historical '
                                                                                                                                                                                           'interstitial '
                                                                                                                                                                                           'glucose '
                                                                                                                                                                                           'readings '
                                                                                                                                                                                           '(typical '
                                                                                                                                                                                           'interval: '
                                                                                                                                                                                           '{1} '
                                                                                                                                                                                           'minutes) '
                                                                                                                                                                                           'were '
                                                                                                                                                                                           'analyzed '
                                                                                                                                                                                           'for '
                                                                                                                                                                                           '{2}, '
                                                                                                                                                                                           'with '
                                                                                                                                                                                           'sensor '
                                                                                                                                                                                           'activity '
                                                                                                                                                                                           'of '
                                                                                                                                                                                           '{3} '
                                                                                                                                                                                           '% '
                                                                                                                                                                                           'within '
                                                                                                                                                                                           'that '
                                                                                                                                                                                           'window.',
 'El GMI de {0} % se calcula sobre una ventana de {1} días. Cuanto más corta la ventana respecto de los 14-90 días habitualmente recomendados para estimar HbA1c, más aproximada (y no equivalente directa) debe considerarse esta estimación. El CV de {2} % indica una variabilidad glucémica {3} (umbral de referencia ATTD: {4} %).': 'The '
                                                                                                                                                                                                                                                                                                                                          'GMI '
                                                                                                                                                                                                                                                                                                                                          'of '
                                                                                                                                                                                                                                                                                                                                          '{0} '
                                                                                                                                                                                                                                                                                                                                          '% '
                                                                                                                                                                                                                                                                                                                                          'is '
                                                                                                                                                                                                                                                                                                                                          'calculated '
                                                                                                                                                                                                                                                                                                                                          'over '
                                                                                                                                                                                                                                                                                                                                          'a '
                                                                                                                                                                                                                                                                                                                                          'window '
                                                                                                                                                                                                                                                                                                                                          'of '
                                                                                                                                                                                                                                                                                                                                          '{1} '
                                                                                                                                                                                                                                                                                                                                          'days. '
                                                                                                                                                                                                                                                                                                                                          'The '
                                                                                                                                                                                                                                                                                                                                          'shorter '
                                                                                                                                                                                                                                                                                                                                          'the '
                                                                                                                                                                                                                                                                                                                                          'window '
                                                                                                                                                                                                                                                                                                                                          'compared '
                                                                                                                                                                                                                                                                                                                                          'with '
                                                                                                                                                                                                                                                                                                                                          'the '
                                                                                                                                                                                                                                                                                                                                          '14-90 '
                                                                                                                                                                                                                                                                                                                                          'days '
                                                                                                                                                                                                                                                                                                                                          'usually '
                                                                                                                                                                                                                                                                                                                                          'recommended '
                                                                                                                                                                                                                                                                                                                                          'for '
                                                                                                                                                                                                                                                                                                                                          'estimating '
                                                                                                                                                                                                                                                                                                                                          'HbA1c, '
                                                                                                                                                                                                                                                                                                                                          'the '
                                                                                                                                                                                                                                                                                                                                          'more '
                                                                                                                                                                                                                                                                                                                                          'approximate '
                                                                                                                                                                                                                                                                                                                                          'this '
                                                                                                                                                                                                                                                                                                                                          'estimate '
                                                                                                                                                                                                                                                                                                                                          'should '
                                                                                                                                                                                                                                                                                                                                          'be '
                                                                                                                                                                                                                                                                                                                                          'considered '
                                                                                                                                                                                                                                                                                                                                          '(it '
                                                                                                                                                                                                                                                                                                                                          'is '
                                                                                                                                                                                                                                                                                                                                          'not '
                                                                                                                                                                                                                                                                                                                                          'a '
                                                                                                                                                                                                                                                                                                                                          'direct '
                                                                                                                                                                                                                                                                                                                                          'equivalent). '
                                                                                                                                                                                                                                                                                                                                          'The '
                                                                                                                                                                                                                                                                                                                                          'CV '
                                                                                                                                                                                                                                                                                                                                          'of '
                                                                                                                                                                                                                                                                                                                                          '{2} '
                                                                                                                                                                                                                                                                                                                                          '% '
                                                                                                                                                                                                                                                                                                                                          'indicates '
                                                                                                                                                                                                                                                                                                                                          '{3} '
                                                                                                                                                                                                                                                                                                                                          'glucose '
                                                                                                                                                                                                                                                                                                                                          'variability '
                                                                                                                                                                                                                                                                                                                                          '(ATTD '
                                                                                                                                                                                                                                                                                                                                          'reference '
                                                                                                                                                                                                                                                                                                                                          'threshold: '
                                                                                                                                                                                                                                                                                                                                          '{4} '
                                                                                                                                                                                                                                                                                                                                          '%).',
 'El tiempo en rango objetivo (70-180 mg/dL) fue de {0} %': 'Time in the target range (70-180 mg/dL) was {0} '
                                                            '%',
 ', superando el umbral de referencia habitual de 70 %': ', above the usual reference threshold of 70 %',
 ', por debajo del umbral de referencia habitual de 70 %': ', below the usual reference threshold of 70 %',
 '. El tiempo bajo rango combinado (<70 mg/dL) fue de {0} %': '. Combined time below range (<70 mg/dL) was '
                                                              '{0} %',
 ', cifra que excede el objetivo de seguridad recomendado (<4 % del tiempo)': ', exceeding the recommended '
                                                                              'safety target (<4 % of time)',
 ', dentro del objetivo de seguridad recomendado (<4 % del tiempo)': ', within the recommended safety target '
                                                                     '(<4 % of time)',
 '. El tiempo por encima de 180 mg/dL fue de {0} %.': '. Time above 180 mg/dL was {0} %.',
 'Bajo un criterio más estricto (70-140 mg/dL), el tiempo en rango {0} a {1} %.': 'Under a stricter '
                                                                                  'criterion (70-140 mg/dL), '
                                                                                  'time in range {0} to {1} '
                                                                                  '%.',
 ' Esta diferencia entre el {0} % (rango estándar) y el {1} % (rango estricto) señala que buena parte del tiempo "en rango objetivo" se concentra en la franja alta de 140-180 mg/dL.': ' '
                                                                                                                                                                                        'This '
                                                                                                                                                                                        'difference '
                                                                                                                                                                                        'between '
                                                                                                                                                                                        '{0} '
                                                                                                                                                                                        '% '
                                                                                                                                                                                        '(standard '
                                                                                                                                                                                        'range) '
                                                                                                                                                                                        'and '
                                                                                                                                                                                        '{1} '
                                                                                                                                                                                        '% '
                                                                                                                                                                                        '(strict '
                                                                                                                                                                                        'range) '
                                                                                                                                                                                        'indicates '
                                                                                                                                                                                        'that '
                                                                                                                                                                                        'much '
                                                                                                                                                                                        'of '
                                                                                                                                                                                        'the '
                                                                                                                                                                                        'time '
                                                                                                                                                                                        '"in '
                                                                                                                                                                                        'target '
                                                                                                                                                                                        'range" '
                                                                                                                                                                                        'falls '
                                                                                                                                                                                        'in '
                                                                                                                                                                                        'the '
                                                                                                                                                                                        'upper '
                                                                                                                                                                                        'band '
                                                                                                                                                                                        'of '
                                                                                                                                                                                        '140-180 '
                                                                                                                                                                                        'mg/dL.',
 'Con un CV de {0} %, la variabilidad glucémica del período se clasifica como {1}. La SD de {2} mg/dL sobre una media de {3} mg/dL {4}.': 'With '
                                                                                                                                          'a '
                                                                                                                                          'CV '
                                                                                                                                          'of '
                                                                                                                                          '{0} '
                                                                                                                                          '%, '
                                                                                                                                          'glucose '
                                                                                                                                          'variability '
                                                                                                                                          'during '
                                                                                                                                          'the '
                                                                                                                                          'period '
                                                                                                                                          'is '
                                                                                                                                          'classified '
                                                                                                                                          'as '
                                                                                                                                          '{1}. '
                                                                                                                                          'The '
                                                                                                                                          'SD '
                                                                                                                                          'of '
                                                                                                                                          '{2} '
                                                                                                                                          'mg/dL '
                                                                                                                                          'around '
                                                                                                                                          'a '
                                                                                                                                          'mean '
                                                                                                                                          'of '
                                                                                                                                          '{3} '
                                                                                                                                          'mg/dL '
                                                                                                                                          '{4}.',
 'La variabilidad no es homogénea a lo largo del día: los valores de CV horario oscilan entre {0} % ({1}:00 h) y {2} % ({3}:00 h).': 'Variability '
                                                                                                                                     'is '
                                                                                                                                     'not '
                                                                                                                                     'uniform '
                                                                                                                                     'throughout '
                                                                                                                                     'the '
                                                                                                                                     'day: '
                                                                                                                                     'hourly '
                                                                                                                                     'CV '
                                                                                                                                     'values '
                                                                                                                                     'range '
                                                                                                                                     'from '
                                                                                                                                     '{0} '
                                                                                                                                     '% '
                                                                                                                                     '({1}:00 '
                                                                                                                                     'h) '
                                                                                                                                     'to '
                                                                                                                                     '{2} '
                                                                                                                                     '% '
                                                                                                                                     '({3}:00 '
                                                                                                                                     'h).',
 'La duración mediana de los episodios de hipoglucemia (<70 mg/dL) fue de {0} minutos (media {1} min), con un máximo de {2} minutos.': 'The '
                                                                                                                                       'median '
                                                                                                                                       'duration '
                                                                                                                                       'of '
                                                                                                                                       'hypoglycemia '
                                                                                                                                       'episodes '
                                                                                                                                       '(<70 '
                                                                                                                                       'mg/dL) '
                                                                                                                                       'was '
                                                                                                                                       '{0} '
                                                                                                                                       'minutes '
                                                                                                                                       '(mean '
                                                                                                                                       '{1} '
                                                                                                                                       'min), '
                                                                                                                                       'with '
                                                                                                                                       'a '
                                                                                                                                       'maximum '
                                                                                                                                       'of '
                                                                                                                                       '{2} '
                                                                                                                                       'minutes.',
 'Los episodios de hipoglucemia se concentran principalmente ': 'Hypoglycemia episodes are mainly '
                                                                'concentrated ',
 'en torno a las {0}:00 h ({1} episodio{2})': 'around {0}:00 h ({1} episode{2})',
 'No se registraron episodios de hipoglucemia (<70 mg/dL) en el período analizado.': 'No hypoglycemia '
                                                                                     'episodes (<70 mg/dL) '
                                                                                     'were recorded during '
                                                                                     'the analyzed period.',
 'La duración mediana de los episodios de hiperglucemia (>180 mg/dL) fue de {0} minutos (media {1} min), con un máximo de {2} minutos.': 'The '
                                                                                                                                         'median '
                                                                                                                                         'duration '
                                                                                                                                         'of '
                                                                                                                                         'hyperglycemia '
                                                                                                                                         'episodes '
                                                                                                                                         '(>180 '
                                                                                                                                         'mg/dL) '
                                                                                                                                         'was '
                                                                                                                                         '{0} '
                                                                                                                                         'minutes '
                                                                                                                                         '(mean '
                                                                                                                                         '{1} '
                                                                                                                                         'min), '
                                                                                                                                         'with '
                                                                                                                                         'a '
                                                                                                                                         'maximum '
                                                                                                                                         'of '
                                                                                                                                         '{2} '
                                                                                                                                         'minutes.',
 'Los episodios de hiperglucemia se concentran principalmente ': 'Hyperglycemia episodes are mainly '
                                                                 'concentrated ',
 'No se registraron episodios de hiperglucemia (>180 mg/dL) en el período analizado.': 'No hyperglycemia '
                                                                                       'episodes (>180 '
                                                                                       'mg/dL) were recorded '
                                                                                       'during the analyzed '
                                                                                       'period.',
 'La franja "{0}" concentra el mayor porcentaje de tiempo en hipoglucemia del día ({1} %), mientras que la franja "{2}" concentra el mayor porcentaje de tiempo en hiperglucemia ({3} %).': 'The '
                                                                                                                                                                                            '"{0}" '
                                                                                                                                                                                            'time '
                                                                                                                                                                                            'band '
                                                                                                                                                                                            'has '
                                                                                                                                                                                            'the '
                                                                                                                                                                                            'highest '
                                                                                                                                                                                            'percentage '
                                                                                                                                                                                            'of '
                                                                                                                                                                                            'time '
                                                                                                                                                                                            'in '
                                                                                                                                                                                            'hypoglycemia '
                                                                                                                                                                                            '({1} '
                                                                                                                                                                                            '%), '
                                                                                                                                                                                            'while '
                                                                                                                                                                                            '"{2}" '
                                                                                                                                                                                            'has '
                                                                                                                                                                                            'the '
                                                                                                                                                                                            'highest '
                                                                                                                                                                                            'percentage '
                                                                                                                                                                                            'of '
                                                                                                                                                                                            'time '
                                                                                                                                                                                            'in '
                                                                                                                                                                                            'hyperglycemia '
                                                                                                                                                                                            '({3} '
                                                                                                                                                                                            '%).',
 '{0} fue el día con mejor control del período: {1} % de tiempo en rango, con CV de {2} %.': '{0} had the '
                                                                                             'best control '
                                                                                             'during the '
                                                                                             'period: {1} % '
                                                                                             'time in range, '
                                                                                             'with a CV of '
                                                                                             '{2} %.',
 '{0} fue el día con menor tiempo en rango del período ({1} %), con {2} % de tiempo en hiperglucemia y {3} % en hipoglucemia.': '{0} '
                                                                                                                                'had '
                                                                                                                                'the '
                                                                                                                                'lowest '
                                                                                                                                'time '
                                                                                                                                'in '
                                                                                                                                'range '
                                                                                                                                'during '
                                                                                                                                'the '
                                                                                                                                'period '
                                                                                                                                '({1} '
                                                                                                                                '%), '
                                                                                                                                'with '
                                                                                                                                '{2} '
                                                                                                                                '% '
                                                                                                                                'time '
                                                                                                                                'in '
                                                                                                                                'hyperglycemia '
                                                                                                                                'and '
                                                                                                                                '{3} '
                                                                                                                                '% '
                                                                                                                                'in '
                                                                                                                                'hypoglycemia.',
 'Informe de Monitoreo Continuo de Glucosa · Juggluco': 'Continuous Glucose Monitoring Report · Juggluco',
 'Documento generado automáticamente — material de apoyo para consulta médica, no constituye diagnóstico. Página {0}': 'Automatically '
                                                                                                                       'generated '
                                                                                                                       '- '
                                                                                                                       'supports '
                                                                                                                       'medical '
                                                                                                                       'consultation; '
                                                                                                                       'not '
                                                                                                                       'a '
                                                                                                                       'diagnosis. '
                                                                                                                       'Page '
                                                                                                                       '{0}',
 'INFORME DE MONITOREO CONTINUO DE GLUCOSA': 'CONTINUOUS GLUCOSE MONITORING REPORT',
 'Análisis de glucosa · Exportaciones de Juggluco': 'Glucose analysis · Juggluco exports',
 'Período analizado': 'Analyzed period',
 'Cantidad de días de registro': 'Days of recorded data',
 '{0} días · {1} fechas calendario': '{0} days · {1} calendar dates',
 'Fecha de generación del informe': 'Report generation date',
 'Registros analizados: {0} lecturas (intervalo típico: {1} min)': 'Records analyzed: {0} readings (typical '
                                                                   'interval: {1} min)',
 'Documento generado automáticamente a partir del archivo de glucosa proporcionado.': 'Automatically '
                                                                                      'generated from the '
                                                                                      'supplied glucose data '
                                                                                      'file.',
 'No constituye diagnóstico ni indicación terapéutica. Para uso exclusivo como material de apoyo en consulta con profesional médico.': 'This '
                                                                                                                                       'is '
                                                                                                                                       'not '
                                                                                                                                       'a '
                                                                                                                                       'diagnosis '
                                                                                                                                       'or '
                                                                                                                                       'treatment '
                                                                                                                                       'recommendation. '
                                                                                                                                       'For '
                                                                                                                                       'use '
                                                                                                                                       'only '
                                                                                                                                       'as '
                                                                                                                                       'supporting '
                                                                                                                                       'material '
                                                                                                                                       'during '
                                                                                                                                       'consultation '
                                                                                                                                       'with '
                                                                                                                                       'a '
                                                                                                                                       'medical '
                                                                                                                                       'professional.',
 'Índice': 'Contents',
 '1. Resumen ejecutivo': '1. Executive summary',
 'Glucosa media': 'Mean glucose',
 'GMI (HbA1c estimada)': 'GMI (estimated HbA1c)',
 'Desviación estándar': 'Standard deviation',
 'Coeficiente de variación': 'Coefficient of variation',
 'Tiempo activo del sensor': 'Sensor active time',
 'Mediciones analizadas': 'Readings analyzed',
 'Tiempo en rango (70-180)': 'Time in range (70-180)',
 'Tiempo bajo rango (<70)': 'Time below range (<70)',
 '1.1 Significado de las métricas principales': '1.1 Meaning of the main metrics',
 '<b>Glucosa media:</b> promedio aritmético de todas las lecturas del período.': '<b>Mean glucose:</b> '
                                                                                 'arithmetic mean of all '
                                                                                 'readings in the period.',
 '<b>GMI (Glucose Management Indicator):</b> estimación de HbA1c derivada de la glucosa media de sensor (GMI % = 3,31 + 0,02392 × glucosa media en mg/dL). No reemplaza a la HbA1c de laboratorio.': '<b>GMI '
                                                                                                                                                                                                     '(Glucose '
                                                                                                                                                                                                     'Management '
                                                                                                                                                                                                     'Indicator):</b> '
                                                                                                                                                                                                     'HbA1c '
                                                                                                                                                                                                     'estimate '
                                                                                                                                                                                                     'derived '
                                                                                                                                                                                                     'from '
                                                                                                                                                                                                     'mean '
                                                                                                                                                                                                     'sensor '
                                                                                                                                                                                                     'glucose '
                                                                                                                                                                                                     '(GMI '
                                                                                                                                                                                                     '% '
                                                                                                                                                                                                     '= '
                                                                                                                                                                                                     '3.31 '
                                                                                                                                                                                                     '+ '
                                                                                                                                                                                                     '0.02392 '
                                                                                                                                                                                                     '× '
                                                                                                                                                                                                     'mean '
                                                                                                                                                                                                     'glucose '
                                                                                                                                                                                                     'in '
                                                                                                                                                                                                     'mg/dL). '
                                                                                                                                                                                                     'It '
                                                                                                                                                                                                     'does '
                                                                                                                                                                                                     'not '
                                                                                                                                                                                                     'replace '
                                                                                                                                                                                                     'laboratory '
                                                                                                                                                                                                     'HbA1c.',
 '<b>Desviación estándar (SD):</b> dispersión absoluta de los valores de glucosa alrededor de la media, en mg/dL.': '<b>Standard '
                                                                                                                    'deviation '
                                                                                                                    '(SD):</b> '
                                                                                                                    'absolute '
                                                                                                                    'dispersion '
                                                                                                                    'of '
                                                                                                                    'glucose '
                                                                                                                    'values '
                                                                                                                    'around '
                                                                                                                    'the '
                                                                                                                    'mean, '
                                                                                                                    'in '
                                                                                                                    'mg/dL.',
 '<b>Coeficiente de variación (CV):</b> SD relativizada a la media (%). Métrica de variabilidad recomendada por el consenso ATTD, con umbral de variabilidad estable en CV &lt; {0} %.': '<b>Coefficient '
                                                                                                                                                                                         'of '
                                                                                                                                                                                         'variation '
                                                                                                                                                                                         '(CV):</b> '
                                                                                                                                                                                         'SD '
                                                                                                                                                                                         'relative '
                                                                                                                                                                                         'to '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'mean '
                                                                                                                                                                                         '(%). '
                                                                                                                                                                                         'Variability '
                                                                                                                                                                                         'metric '
                                                                                                                                                                                         'recommended '
                                                                                                                                                                                         'by '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'ATTD '
                                                                                                                                                                                         'consensus, '
                                                                                                                                                                                         'with '
                                                                                                                                                                                         'a '
                                                                                                                                                                                         'stable '
                                                                                                                                                                                         'variability '
                                                                                                                                                                                         'threshold '
                                                                                                                                                                                         'of '
                                                                                                                                                                                         'CV '
                                                                                                                                                                                         '&lt; '
                                                                                                                                                                                         '{0} '
                                                                                                                                                                                         '%.',
 '<b>Tiempo activo del sensor:</b> porcentaje del período con datos válidos; el consenso ATTD recomienda un mínimo de 70 % de tiempo activo.': '<b>Sensor '
                                                                                                                                               'active '
                                                                                                                                               'time:</b> '
                                                                                                                                               'percentage '
                                                                                                                                               'of '
                                                                                                                                               'the '
                                                                                                                                               'period '
                                                                                                                                               'with '
                                                                                                                                               'valid '
                                                                                                                                               'data; '
                                                                                                                                               'the '
                                                                                                                                               'ATTD '
                                                                                                                                               'consensus '
                                                                                                                                               'recommends '
                                                                                                                                               'at '
                                                                                                                                               'least '
                                                                                                                                               '70 '
                                                                                                                                               '% '
                                                                                                                                               'active '
                                                                                                                                               'time.',
 '2. Tiempo en rango (TIR)': '2. Time in range (TIR)',
 'El "tiempo en rango" cuantifica la proporción de tiempo que la glucosa permaneció dentro de distintas bandas objetivo, según el consenso ATTD/ADA para monitoreo continuo.': '"Time '
                                                                                                                                                                               'in '
                                                                                                                                                                               'range" '
                                                                                                                                                                               'quantifies '
                                                                                                                                                                               'the '
                                                                                                                                                                               'proportion '
                                                                                                                                                                               'of '
                                                                                                                                                                               'time '
                                                                                                                                                                               'glucose '
                                                                                                                                                                               'remained '
                                                                                                                                                                               'within '
                                                                                                                                                                               'different '
                                                                                                                                                                               'target '
                                                                                                                                                                               'bands, '
                                                                                                                                                                               'according '
                                                                                                                                                                               'to '
                                                                                                                                                                               'the '
                                                                                                                                                                               'ATTD/ADA '
                                                                                                                                                                               'consensus '
                                                                                                                                                                               'for '
                                                                                                                                                                               'continuous '
                                                                                                                                                                               'monitoring.',
 '2.1 Objetivo estándar': '2.1 Standard target',
 'N.º lecturas': 'Readings',
 'Rango de glucosa': 'Glucose range',
 'Tiempo equiv.': 'Equivalent time',
 'Figura 1. Distribución del tiempo en rango.': 'Figure 1. Time in range distribution.',
 '2.2 Objetivo estricto (70-140 mg/dL)': '2.2 Strict target (70-140 mg/dL)',
 'Rango': 'Range',
 'Tiempo equivalente': 'Equivalent time',
 '3. Variabilidad glucémica': '3. Glucose variability',
 'La variabilidad glucémica describe la magnitud y frecuencia de las oscilaciones de glucosa, independientemente del nivel medio.': 'Glucose '
                                                                                                                                    'variability '
                                                                                                                                    'describes '
                                                                                                                                    'the '
                                                                                                                                    'magnitude '
                                                                                                                                    'and '
                                                                                                                                    'frequency '
                                                                                                                                    'of '
                                                                                                                                    'glucose '
                                                                                                                                    'fluctuations, '
                                                                                                                                    'independently '
                                                                                                                                    'of '
                                                                                                                                    'the '
                                                                                                                                    'mean '
                                                                                                                                    'level.',
 'Métrica': 'Metric',
 'Referencia (ATTD)': 'Reference (ATTD)',
 'Valor': 'Value',
 'Desviación estándar (SD)': 'Standard deviation (SD)',
 'Se interpreta junto al CV': 'Interpret together with CV',
 '< {0}% estable · ≥ {1}% inestable': '< {0}% stable · ≥ {1}% unstable',
 'Coeficiente de variación (CV)': 'Coefficient of variation (CV)',
 'Rango intercuartílico (IQR)': 'Interquartile range (IQR)',
 'Mín {0} – Máx {1}': 'Min {0} - Max {1}',
 'Rango total': 'Total range',
 'Figura 2. Distribución horaria de glucosa (boxplot por hora).': 'Figure 2. Hourly glucose distribution '
                                                                  '(boxplot).',
 '4. Hipoglucemias': '4. Hypoglycemia',
 'Se definieron episodios de hipoglucemia como intervalos continuos con glucosa &lt;70 mg/dL, agrupando lecturas consecutivas, sin unir huecos mayores a dos intervalos típicos (máximo 15 minutos).': 'Hypoglycemia '
                                                                                                                                                                                                       'episodes '
                                                                                                                                                                                                       'were '
                                                                                                                                                                                                       'defined '
                                                                                                                                                                                                       'as '
                                                                                                                                                                                                       'continuous '
                                                                                                                                                                                                       'intervals '
                                                                                                                                                                                                       'with '
                                                                                                                                                                                                       'glucose '
                                                                                                                                                                                                       '&lt;70 '
                                                                                                                                                                                                       'mg/dL, '
                                                                                                                                                                                                       'grouping '
                                                                                                                                                                                                       'consecutive '
                                                                                                                                                                                                       'readings '
                                                                                                                                                                                                       'without '
                                                                                                                                                                                                       'bridging '
                                                                                                                                                                                                       'gaps '
                                                                                                                                                                                                       'longer '
                                                                                                                                                                                                       'than '
                                                                                                                                                                                                       'two '
                                                                                                                                                                                                       'typical '
                                                                                                                                                                                                       'intervals '
                                                                                                                                                                                                       '(maximum '
                                                                                                                                                                                                       '15 '
                                                                                                                                                                                                       'minutes).',
 'Episodios <70 mg/dL': 'Episodes <70 mg/dL',
 'Episodios <54 mg/dL': 'Episodes <54 mg/dL',
 'Duración mediana': 'Median duration',
 'Más prolongado': 'Longest episode',
 'Hipoglucemias prolongadas (≥ 60 min)': 'Prolonged hypoglycemia (≥ 60 min)',
 '%d/%m/%Y %H:%M': '%Y-%m-%d %H:%M',
 'Duración': 'Duration',
 'Fecha y hora de inicio': 'Start date and time',
 '5. Hiperglucemias': '5. Hyperglycemia',
 'Se definieron episodios de hiperglucemia como intervalos continuos con glucosa &gt;180 mg/dL, con el mismo criterio de agrupación.': 'Hyperglycemia '
                                                                                                                                       'episodes '
                                                                                                                                       'were '
                                                                                                                                       'defined '
                                                                                                                                       'as '
                                                                                                                                       'continuous '
                                                                                                                                       'intervals '
                                                                                                                                       'with '
                                                                                                                                       'glucose '
                                                                                                                                       '&gt;180 '
                                                                                                                                       'mg/dL, '
                                                                                                                                       'using '
                                                                                                                                       'the '
                                                                                                                                       'same '
                                                                                                                                       'grouping '
                                                                                                                                       'criterion.',
 'Episodios >180 mg/dL': 'Episodes >180 mg/dL',
 'Episodios >250 mg/dL': 'Episodes >250 mg/dL',
 'Hiperglucemias prolongadas (≥ 120 min)': 'Prolonged hyperglycemia (≥ 120 min)',
 'Pico': 'Peak',
 '6. Análisis por horario': '6. Analysis by time of day',
 'Figura 3. Perfil de Glucosa Ambulatorio (AGP).': 'Figure 3. Ambulatory Glucose Profile (AGP).',
 '% en rango': '% in range',
 '% hiper': '% high',
 '% hipo': '% low',
 'Franja horaria': 'Time band',
 'Figura 4. Glucosa media ± desviación estándar por hora del día.': 'Figure 4. Mean glucose ± standard '
                                                                    'deviation by hour of day.',
 'Figura 5. Coeficiente de variación (%) por hora del día.': 'Figure 5. Coefficient of variation (%) by hour '
                                                             'of day.',
 '7. Perfil diario': '7. Daily profile',
 'Figura 6. Curva completa de glucosa vs. tiempo.': 'Figure 6. Full glucose trace over time.',
 '8. Días destacados': '8. Notable days',
 '8.1 Mejores días (mayor tiempo en rango)': '8.1 Best days (highest time in range)',
 '8.2 Peores días (menor tiempo en rango)': '8.2 Worst days (lowest time in range)',
 '9. Eventos llamativos': '9. Notable events',
 'Hiperglucemia prolongada: {0} h → {1} min por encima de 180 mg/dL, pico de {2} mg/dL.': 'Prolonged '
                                                                                          'hyperglycemia: '
                                                                                          '{0} h - {1} min '
                                                                                          'above 180 mg/dL, '
                                                                                          'peak {2} mg/dL.',
 'Hipoglucemia prolongada: {0} h → {1} min por debajo de 70 mg/dL, nadir de {2} mg/dL.': 'Prolonged '
                                                                                         'hypoglycemia: {0} '
                                                                                         'h - {1} min below '
                                                                                         '70 mg/dL, nadir '
                                                                                         '{2} mg/dL.',
 'Descenso rápido: {0} h → caída de {1} a {2} mg/dL en ~15 minutos.': 'Rapid fall: {0} h - from {1} to {2} '
                                                                      'mg/dL in approximately 15 minutes.',
 'Ascenso rápido: {0} h → subida de {1} a {2} mg/dL en ~15 minutos.': 'Rapid rise: {0} h - from {1} to {2} '
                                                                      'mg/dL in approximately 15 minutes.',
 'No se identificaron ascensos de glucosa ≥70 mg/dL en una ventana de 15 minutos durante el período.': 'No '
                                                                                                       'glucose '
                                                                                                       'rises '
                                                                                                       '≥70 '
                                                                                                       'mg/dL '
                                                                                                       'within '
                                                                                                       'a '
                                                                                                       '15-minute '
                                                                                                       'window '
                                                                                                       'were '
                                                                                                       'identified '
                                                                                                       'during '
                                                                                                       'the '
                                                                                                       'period.',
 'No se detectaron eventos de magnitud destacable en el período analizado.': 'No events of notable magnitude '
                                                                             'were detected during the '
                                                                             'analyzed period.',
 '10. Estadísticas adicionales': '10. Additional statistics',
 'Mínimo': 'Minimum',
 'Percentil 10': '10th percentile',
 'Mediana (P50)': 'Median (P50)',
 'Percentil 25': '25th percentile',
 'Percentil 75': '75th percentile',
 'Percentil 90': '90th percentile',
 'Máximo': 'Maximum',
 'Estadístico': 'Statistic',
 'Figura 7. Histograma de valores de glucosa.': 'Figure 7. Histogram of glucose values.',
 'Figura 8. Mapa de calor glucosa media por día y hora.': 'Figure 8. Mean glucose heatmap by day and hour.',
 '11. Tabla de datos': '11. Data table',
 'El registro completo contiene {0} lecturas individuales. A continuación, el resumen diario. Conservá el CSV/TSV original para consultar las lecturas individuales.': 'The '
                                                                                                                                                                       'complete '
                                                                                                                                                                       'record '
                                                                                                                                                                       'contains '
                                                                                                                                                                       '{0} '
                                                                                                                                                                       'individual '
                                                                                                                                                                       'readings. '
                                                                                                                                                                       'The '
                                                                                                                                                                       'daily '
                                                                                                                                                                       'summary '
                                                                                                                                                                       'is '
                                                                                                                                                                       'shown '
                                                                                                                                                                       'below. '
                                                                                                                                                                       'Keep '
                                                                                                                                                                       'the '
                                                                                                                                                                       'original '
                                                                                                                                                                       'CSV/TSV '
                                                                                                                                                                       'file '
                                                                                                                                                                       'for '
                                                                                                                                                                       'individual '
                                                                                                                                                                       'readings.',
 'N. lect.': 'Readings',
 '12. Conclusiones': '12. Conclusions',
 'Resumen descriptivo, sin indicaciones terapéuticas, de los puntos a discutir en consulta.': 'Descriptive '
                                                                                              'summary of '
                                                                                              'points to '
                                                                                              'discuss '
                                                                                              'during '
                                                                                              'consultation, '
                                                                                              'without '
                                                                                              'treatment '
                                                                                              'recommendations.',
 '12.1 Aspectos positivos': '12.1 Positive findings',
 'El tiempo en rango estándar fue de {0} %, por encima del umbral de referencia habitual de 70 %.': 'Time in '
                                                                                                    'the '
                                                                                                    'standard '
                                                                                                    'range '
                                                                                                    'was {0} '
                                                                                                    '%, '
                                                                                                    'above '
                                                                                                    'the '
                                                                                                    'usual '
                                                                                                    'reference '
                                                                                                    'threshold '
                                                                                                    'of 70 '
                                                                                                    '%.',
 'El tiempo activo del sensor fue del {0} %, lo que otorga alta confiabilidad a las métricas.': 'Sensor '
                                                                                                'active time '
                                                                                                'was {0} %, '
                                                                                                'supporting '
                                                                                                'high '
                                                                                                'reliability '
                                                                                                'of the '
                                                                                                'metrics.',
 'Ver detalle de métricas en las secciones anteriores.': 'See the detailed metrics in the preceding '
                                                         'sections.',
 '12.2 Aspectos a revisar': '12.2 Points to review',
 'El tiempo bajo rango (&lt;70 mg/dL) fue de {0} %, por encima del objetivo de seguridad de &lt;4 %.': 'Time '
                                                                                                       'below '
                                                                                                       'range '
                                                                                                       '(&lt;70 '
                                                                                                       'mg/dL) '
                                                                                                       'was '
                                                                                                       '{0} '
                                                                                                       '%, '
                                                                                                       'above '
                                                                                                       'the '
                                                                                                       'safety '
                                                                                                       'target '
                                                                                                       'of '
                                                                                                       '&lt;4 '
                                                                                                       '%.',
 'El coeficiente de variación ({0} %) se ubica en o por encima del umbral de {1} % del consenso ATTD.': 'The '
                                                                                                        'coefficient '
                                                                                                        'of '
                                                                                                        'variation '
                                                                                                        '({0} '
                                                                                                        '%) '
                                                                                                        'is '
                                                                                                        'at '
                                                                                                        'or '
                                                                                                        'above '
                                                                                                        'the '
                                                                                                        'ATTD '
                                                                                                        'consensus '
                                                                                                        'threshold '
                                                                                                        'of '
                                                                                                        '{1} '
                                                                                                        '%.',
 'Se identificaron {0} episodios de hipoglucemia ≥60 min y {1} de hiperglucemia ≥120 min.': '{0} '
                                                                                            'hypoglycemia '
                                                                                            'episodes ≥60 '
                                                                                            'min and {1} '
                                                                                            'hyperglycemia '
                                                                                            'episodes ≥120 '
                                                                                            'min were '
                                                                                            'identified.',
 'No se identificaron aspectos de alarma relevantes más allá de lo descripto en las secciones anteriores.': 'No '
                                                                                                            'further '
                                                                                                            'relevant '
                                                                                                            'warning '
                                                                                                            'findings '
                                                                                                            'were '
                                                                                                            'identified '
                                                                                                            'beyond '
                                                                                                            'those '
                                                                                                            'described '
                                                                                                            'in '
                                                                                                            'the '
                                                                                                            'preceding '
                                                                                                            'sections.',
 '12.3 Patrones que podrían discutirse con la diabetóloga': '12.3 Patterns to discuss with the diabetes '
                                                            'clinician',
 'Contraste entre el tiempo en rango estándar ({0} %) y estricto ({1} %): buena parte del tiempo "en rango" se concentra en 140-180 mg/dL.': 'Contrast '
                                                                                                                                             'between '
                                                                                                                                             'time '
                                                                                                                                             'in '
                                                                                                                                             'the '
                                                                                                                                             'standard '
                                                                                                                                             'range '
                                                                                                                                             '({0} '
                                                                                                                                             '%) '
                                                                                                                                             'and '
                                                                                                                                             'strict '
                                                                                                                                             'range '
                                                                                                                                             '({1} '
                                                                                                                                             '%): '
                                                                                                                                             'much '
                                                                                                                                             'of '
                                                                                                                                             'the '
                                                                                                                                             'time '
                                                                                                                                             '"in '
                                                                                                                                             'range" '
                                                                                                                                             'falls '
                                                                                                                                             'within '
                                                                                                                                             '140-180 '
                                                                                                                                             'mg/dL.',
 '12.4 Preguntas sugeridas para la consulta': '12.4 Suggested questions for the consultation',
 '¿A qué podría deberse la concentración de hipoglucemias en la franja "{0}"?': 'What could explain the '
                                                                                'concentration of '
                                                                                'hypoglycemia in the "{0}" '
                                                                                'time band?',
 '¿El patrón de hiperglucemia en la franja "{0}" corresponde a algo esperable según el esquema actual?': 'Is '
                                                                                                         'the '
                                                                                                         'hyperglycemia '
                                                                                                         'pattern '
                                                                                                         'in '
                                                                                                         'the '
                                                                                                         '"{0}" '
                                                                                                         'time '
                                                                                                         'band '
                                                                                                         'expected '
                                                                                                         'under '
                                                                                                         'the '
                                                                                                         'current '
                                                                                                         'regimen?',
 '¿El tiempo bajo rango ({0} %) y muy bajo ({1} %) requieren algún ajuste de seguimiento?': 'Do time below '
                                                                                            'range ({0} %) '
                                                                                            'and very low '
                                                                                            'glucose ({1} %) '
                                                                                            'call for any '
                                                                                            'adjustment to '
                                                                                            'follow-up?',
 '¿Cómo interpretar la diferencia de variabilidad entre los mejores y los peores días del período?': 'How '
                                                                                                     'should '
                                                                                                     'the '
                                                                                                     'difference '
                                                                                                     'in '
                                                                                                     'variability '
                                                                                                     'between '
                                                                                                     'the '
                                                                                                     'best '
                                                                                                     'and '
                                                                                                     'worst '
                                                                                                     'days '
                                                                                                     'of the '
                                                                                                     'period '
                                                                                                     'be '
                                                                                                     'interpreted?',
 'ANEXO TÉCNICO': 'TECHNICAL APPENDIX',
 'Metodología, definiciones y limitaciones del análisis': 'Methodology, definitions and limitations of the '
                                                          'analysis',
 'A.1 Metodología de cálculo': 'A.1 Calculation methodology',
 'Se procesaron lecturas en mg/dL; intervalo típico detectado: {0} minutos.': 'Readings were processed in '
                                                                              'mg/dL; typical detected '
                                                                              'interval: {0} minutes.',
 'Media, SD y percentiles se calcularon sobre el total de lecturas válidas del período (n = {0}).': 'Mean, '
                                                                                                    'SD and '
                                                                                                    'percentiles '
                                                                                                    'were '
                                                                                                    'calculated '
                                                                                                    'across '
                                                                                                    'all '
                                                                                                    'valid '
                                                                                                    'readings '
                                                                                                    'in the '
                                                                                                    'period '
                                                                                                    '(n = '
                                                                                                    '{0}).',
 'El coeficiente de variación se calculó como CV (%) = (SD / media) × 100.': 'The coefficient of variation '
                                                                             'was calculated as CV (%) = (SD '
                                                                             '/ mean) × 100.',
 'El GMI se calculó con la fórmula de Bergenstal et al. (2018): GMI (%) = 3,31 + 0,02392 × [glucosa media en mg/dL].': 'GMI '
                                                                                                                       'was '
                                                                                                                       'calculated '
                                                                                                                       'using '
                                                                                                                       'the '
                                                                                                                       'formula '
                                                                                                                       'from '
                                                                                                                       'Bergenstal '
                                                                                                                       'et '
                                                                                                                       'al. '
                                                                                                                       '(2018): '
                                                                                                                       'GMI '
                                                                                                                       '(%) '
                                                                                                                       '= '
                                                                                                                       '3.31 '
                                                                                                                       '+ '
                                                                                                                       '0.02392 '
                                                                                                                       '× '
                                                                                                                       '[mean '
                                                                                                                       'glucose '
                                                                                                                       'in '
                                                                                                                       'mg/dL].',
 'El tiempo activo del sensor se calculó como (lecturas válidas / lecturas esperadas según el intervalo mediano detectado) × 100.': 'Sensor '
                                                                                                                                    'active '
                                                                                                                                    'time '
                                                                                                                                    'was '
                                                                                                                                    'calculated '
                                                                                                                                    'as '
                                                                                                                                    '(valid '
                                                                                                                                    'readings '
                                                                                                                                    '/ '
                                                                                                                                    'expected '
                                                                                                                                    'readings '
                                                                                                                                    'based '
                                                                                                                                    'on '
                                                                                                                                    'the '
                                                                                                                                    'detected '
                                                                                                                                    'median '
                                                                                                                                    'interval) '
                                                                                                                                    '× '
                                                                                                                                    '100.',
 'Los episodios de hipo/hiperglucemia se definieron agrupando lecturas consecutivas que cruzan el umbral, sin unir lecturas normales intermedias ni huecos mayores a dos intervalos típicos (máximo 15 minutos).': 'Hypo/hyperglycemia '
                                                                                                                                                                                                                   'episodes '
                                                                                                                                                                                                                   'were '
                                                                                                                                                                                                                   'defined '
                                                                                                                                                                                                                   'by '
                                                                                                                                                                                                                   'grouping '
                                                                                                                                                                                                                   'consecutive '
                                                                                                                                                                                                                   'readings '
                                                                                                                                                                                                                   'crossing '
                                                                                                                                                                                                                   'the '
                                                                                                                                                                                                                   'threshold, '
                                                                                                                                                                                                                   'without '
                                                                                                                                                                                                                   'bridging '
                                                                                                                                                                                                                   'normal '
                                                                                                                                                                                                                   'readings '
                                                                                                                                                                                                                   'or '
                                                                                                                                                                                                                   'gaps '
                                                                                                                                                                                                                   'longer '
                                                                                                                                                                                                                   'than '
                                                                                                                                                                                                                   'two '
                                                                                                                                                                                                                   'typical '
                                                                                                                                                                                                                   'intervals '
                                                                                                                                                                                                                   '(maximum '
                                                                                                                                                                                                                   '15 '
                                                                                                                                                                                                                   'minutes).',
 'Los ascensos/descensos rápidos se calcularon como diferencia de glucosa entre una lectura y la registrada aproximadamente 15 minutos antes (tolerancia máxima de un minuto), marcando eventos con diferencia ≥70 mg/dL en valor absoluto.': 'Rapid '
                                                                                                                                                                                                                                              'rises/falls '
                                                                                                                                                                                                                                              'were '
                                                                                                                                                                                                                                              'calculated '
                                                                                                                                                                                                                                              'as '
                                                                                                                                                                                                                                              'the '
                                                                                                                                                                                                                                              'glucose '
                                                                                                                                                                                                                                              'difference '
                                                                                                                                                                                                                                              'between '
                                                                                                                                                                                                                                              'a '
                                                                                                                                                                                                                                              'reading '
                                                                                                                                                                                                                                              'and '
                                                                                                                                                                                                                                              'the '
                                                                                                                                                                                                                                              'one '
                                                                                                                                                                                                                                              'recorded '
                                                                                                                                                                                                                                              'approximately '
                                                                                                                                                                                                                                              '15 '
                                                                                                                                                                                                                                              'minutes '
                                                                                                                                                                                                                                              'earlier '
                                                                                                                                                                                                                                              '(maximum '
                                                                                                                                                                                                                                              'tolerance '
                                                                                                                                                                                                                                              'of '
                                                                                                                                                                                                                                              'one '
                                                                                                                                                                                                                                              'minute), '
                                                                                                                                                                                                                                              'marking '
                                                                                                                                                                                                                                              'events '
                                                                                                                                                                                                                                              'with '
                                                                                                                                                                                                                                              'an '
                                                                                                                                                                                                                                              'absolute '
                                                                                                                                                                                                                                              'difference '
                                                                                                                                                                                                                                              '≥70 '
                                                                                                                                                                                                                                              'mg/dL.',
 'Las franjas horarias se definieron por hora del reloj del dispositivo, agregando todas las lecturas del período correspondientes a cada franja, sin distinguir fecha calendario.': 'Time '
                                                                                                                                                                                     'bands '
                                                                                                                                                                                     'were '
                                                                                                                                                                                     'defined '
                                                                                                                                                                                     'using '
                                                                                                                                                                                     'the '
                                                                                                                                                                                     'device '
                                                                                                                                                                                     'clock '
                                                                                                                                                                                     'hour, '
                                                                                                                                                                                     'combining '
                                                                                                                                                                                     'all '
                                                                                                                                                                                     'readings '
                                                                                                                                                                                     'in '
                                                                                                                                                                                     'each '
                                                                                                                                                                                     'band '
                                                                                                                                                                                     'across '
                                                                                                                                                                                     'the '
                                                                                                                                                                                     'period, '
                                                                                                                                                                                     'regardless '
                                                                                                                                                                                     'of '
                                                                                                                                                                                     'calendar '
                                                                                                                                                                                     'date.',
 'Los "días destacados" se calcularon solo sobre días con registro completo (al menos 97,22% de las lecturas diarias esperadas según la frecuencia detectada).': '"Notable '
                                                                                                                                                                 'days" '
                                                                                                                                                                 'were '
                                                                                                                                                                 'calculated '
                                                                                                                                                                 'only '
                                                                                                                                                                 'for '
                                                                                                                                                                 'days '
                                                                                                                                                                 'with '
                                                                                                                                                                 'a '
                                                                                                                                                                 'complete '
                                                                                                                                                                 'record '
                                                                                                                                                                 '(at '
                                                                                                                                                                 'least '
                                                                                                                                                                 '97.22% '
                                                                                                                                                                 'of '
                                                                                                                                                                 'expected '
                                                                                                                                                                 'daily '
                                                                                                                                                                 'readings '
                                                                                                                                                                 'based '
                                                                                                                                                                 'on '
                                                                                                                                                                 'the '
                                                                                                                                                                 'detected '
                                                                                                                                                                 'frequency).',
 'A.2 Definición de métricas utilizadas': 'A.2 Definitions of the metrics used',
 'Porcentaje de lecturas dentro del rango objetivo (habitualmente 70-180 mg/dL).': 'Percentage of readings '
                                                                                   'within the target range '
                                                                                   '(usually 70-180 mg/dL).',
 'Porcentaje de tiempo por encima del límite superior del rango objetivo (subdividido en nivel 1: 181-250 y nivel 2: >250 mg/dL).': 'Percentage '
                                                                                                                                    'of '
                                                                                                                                    'time '
                                                                                                                                    'above '
                                                                                                                                    'the '
                                                                                                                                    'upper '
                                                                                                                                    'target '
                                                                                                                                    'limit '
                                                                                                                                    '(subdivided '
                                                                                                                                    'into '
                                                                                                                                    'level '
                                                                                                                                    '1: '
                                                                                                                                    '181-250 '
                                                                                                                                    'and '
                                                                                                                                    'level '
                                                                                                                                    '2: '
                                                                                                                                    '>250 '
                                                                                                                                    'mg/dL).',
 'Porcentaje de tiempo por debajo del límite inferior del rango objetivo (nivel 1: 54-69, nivel 2: <54 mg/dL).': 'Percentage '
                                                                                                                 'of '
                                                                                                                 'time '
                                                                                                                 'below '
                                                                                                                 'the '
                                                                                                                 'lower '
                                                                                                                 'target '
                                                                                                                 'limit '
                                                                                                                 '(level '
                                                                                                                 '1: '
                                                                                                                 '54-69, '
                                                                                                                 'level '
                                                                                                                 '2: '
                                                                                                                 '<54 '
                                                                                                                 'mg/dL).',
 'Estimación basada en la glucosa media de sensor, calculada con la fórmula de Bergenstal et al. (2018).': 'Estimate '
                                                                                                           'based '
                                                                                                           'on '
                                                                                                           'mean '
                                                                                                           'sensor '
                                                                                                           'glucose, '
                                                                                                           'calculated '
                                                                                                           'with '
                                                                                                           'the '
                                                                                                           'formula '
                                                                                                           'from '
                                                                                                           'Bergenstal '
                                                                                                           'et '
                                                                                                           'al. '
                                                                                                           '(2018).',
 'Medida de dispersión absoluta de los valores de glucosa respecto de su media, en mg/dL.': 'Measure of '
                                                                                            'absolute '
                                                                                            'dispersion of '
                                                                                            'glucose values '
                                                                                            'around their '
                                                                                            'mean, in mg/dL.',
 'SD — Desviación Estándar': 'SD - Standard Deviation',
 'CV — Coeficiente de Variación': 'CV - Coefficient of Variation',
 'Medida de dispersión relativa (SD/media, en %), métrica de variabilidad priorizada por el consenso ATTD.': 'Measure '
                                                                                                             'of '
                                                                                                             'relative '
                                                                                                             'dispersion '
                                                                                                             '(SD/mean, '
                                                                                                             'in '
                                                                                                             '%), '
                                                                                                             'a '
                                                                                                             'variability '
                                                                                                             'metric '
                                                                                                             'prioritized '
                                                                                                             'by '
                                                                                                             'the '
                                                                                                             'ATTD '
                                                                                                             'consensus.',
 'A.3 Limitaciones de la interpretación': 'A.3 Limitations of interpretation',
 'El período analizado ({0} días) puede ser más corto que los 14-90 días recomendados para algunas métricas (en particular el GMI como aproximación de HbA1c).': 'The '
                                                                                                                                                                 'analyzed '
                                                                                                                                                                 'period '
                                                                                                                                                                 '({0} '
                                                                                                                                                                 'days) '
                                                                                                                                                                 'may '
                                                                                                                                                                 'be '
                                                                                                                                                                 'shorter '
                                                                                                                                                                 'than '
                                                                                                                                                                 'the '
                                                                                                                                                                 '14-90 '
                                                                                                                                                                 'days '
                                                                                                                                                                 'recommended '
                                                                                                                                                                 'for '
                                                                                                                                                                 'some '
                                                                                                                                                                 'metrics '
                                                                                                                                                                 '(particularly '
                                                                                                                                                                 'GMI '
                                                                                                                                                                 'as '
                                                                                                                                                                 'an '
                                                                                                                                                                 'approximation '
                                                                                                                                                                 'of '
                                                                                                                                                                 'HbA1c).',
 'Este informe no analiza insulina, alimentación ni actividad física, por lo que no es posible establecer relaciones causales.': 'This '
                                                                                                                                 'report '
                                                                                                                                 'does '
                                                                                                                                 'not '
                                                                                                                                 'analyze '
                                                                                                                                 'insulin, '
                                                                                                                                 'food '
                                                                                                                                 'intake '
                                                                                                                                 'or '
                                                                                                                                 'physical '
                                                                                                                                 'activity, '
                                                                                                                                 'so '
                                                                                                                                 'causal '
                                                                                                                                 'relationships '
                                                                                                                                 'cannot '
                                                                                                                                 'be '
                                                                                                                                 'established.',
 'El criterio de agrupación para definir un "episodio" es una convención metodológica; otros criterios podrían generar recuentos distintos.': 'The '
                                                                                                                                              'grouping '
                                                                                                                                              'rule '
                                                                                                                                              'used '
                                                                                                                                              'to '
                                                                                                                                              'define '
                                                                                                                                              'an '
                                                                                                                                              '"episode" '
                                                                                                                                              'is '
                                                                                                                                              'a '
                                                                                                                                              'methodological '
                                                                                                                                              'convention; '
                                                                                                                                              'other '
                                                                                                                                              'criteria '
                                                                                                                                              'could '
                                                                                                                                              'produce '
                                                                                                                                              'different '
                                                                                                                                              'episode '
                                                                                                                                              'counts.',
 'Los datos provienen de glucosa intersticial (sensor), que puede diferir de la glucosa capilar/plasmática, especialmente durante cambios rápidos.': 'The '
                                                                                                                                                     'data '
                                                                                                                                                     'reflect '
                                                                                                                                                     'interstitial '
                                                                                                                                                     'glucose '
                                                                                                                                                     '(sensor), '
                                                                                                                                                     'which '
                                                                                                                                                     'may '
                                                                                                                                                     'differ '
                                                                                                                                                     'from '
                                                                                                                                                     'capillary/plasma '
                                                                                                                                                     'glucose, '
                                                                                                                                                     'especially '
                                                                                                                                                     'during '
                                                                                                                                                     'rapid '
                                                                                                                                                     'changes.',
 'Este documento fue generado mediante procesamiento automatizado y no constituye un diagnóstico médico ni una indicación de tratamiento.': 'This '
                                                                                                                                            'document '
                                                                                                                                            'was '
                                                                                                                                            'generated '
                                                                                                                                            'by '
                                                                                                                                            'automated '
                                                                                                                                            'processing '
                                                                                                                                            'and '
                                                                                                                                            'is '
                                                                                                                                            'not '
                                                                                                                                            'a '
                                                                                                                                            'medical '
                                                                                                                                            'diagnosis '
                                                                                                                                            'or '
                                                                                                                                            'treatment '
                                                                                                                                            'recommendation.',
 'A.4 Referencias a recomendaciones internacionales': 'A.4 References to international recommendations',
 'American Diabetes Association. "Standards of Care in Diabetes" (sección de monitoreo continuo de glucosa), edición vigente.': 'American '
                                                                                                                                'Diabetes '
                                                                                                                                'Association. '
                                                                                                                                '"Standards '
                                                                                                                                'of '
                                                                                                                                'Care '
                                                                                                                                'in '
                                                                                                                                'Diabetes" '
                                                                                                                                '(continuous '
                                                                                                                                'glucose '
                                                                                                                                'monitoring '
                                                                                                                                'section), '
                                                                                                                                'current '
                                                                                                                                'edition.',
 'Genera un informe clínico en PDF a partir de un CSV exportado de LibreView.': 'Generate a PDF glucose '
                                                                                'report from an exported '
                                                                                'CSV/TSV file.',
 'Ruta al CSV exportado de LibreView': 'Path to the exported CSV/TSV file',
 'Cantidad de días (contados hacia atrás desde el último registro) a incluir en el análisis. Usar 0 para incluir todo el archivo. Default: 15': 'Number '
                                                                                                                                                'of '
                                                                                                                                                'days '
                                                                                                                                                'back '
                                                                                                                                                'from '
                                                                                                                                                'the '
                                                                                                                                                'last '
                                                                                                                                                'reading '
                                                                                                                                                'to '
                                                                                                                                                'include. '
                                                                                                                                                'Use '
                                                                                                                                                '0 '
                                                                                                                                                'for '
                                                                                                                                                'the '
                                                                                                                                                'whole '
                                                                                                                                                'file. '
                                                                                                                                                'Default: '
                                                                                                                                                '15',
 'Ruta del PDF de salida (default: informe_cgm.pdf)': 'Output PDF path (default: informe_cgm.pdf)',
 'Cargando datos de: {0}': 'Loading data from: {0}',
 'Período: {0}  ·  {1} lecturas': 'Period: {0} · {1} readings',
 'Generando gráficos y armando PDF...': 'Generating charts and PDF...',
 'Listo. Informe generado en: {0}': 'Done. Report generated at: {0}',
 'baja': 'low',
 'elevada': 'high',
 'desciende': 'decreases',
 'asciende': 'increases',
 'es compatible con excursiones frecuentes que atraviesan los límites del rango objetivo en ambos sentidos': 'is '
                                                                                                             'consistent '
                                                                                                             'with '
                                                                                                             'frequent '
                                                                                                             'excursions '
                                                                                                             'across '
                                                                                                             'both '
                                                                                                             'limits '
                                                                                                             'of '
                                                                                                             'the '
                                                                                                             'target '
                                                                                                             'range',
 'refleja oscilaciones acotadas en torno a la media': 'reflects limited fluctuations around the mean',
 '%d/%m/%Y': '%Y-%m-%d',
 '%d/%m': '%m/%d'}

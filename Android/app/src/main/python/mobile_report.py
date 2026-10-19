import os
import tempfile
from datetime import datetime


def generate(input_path, output_path, days, cache_dir, language='es'):
    os.environ['MPLCONFIGDIR'] = os.path.join(cache_dir, 'matplotlib')
    os.environ['GLUCOSE_CHART_DPI'] = '120'
    tempfile.tempdir = cache_dir
    import glucose_insights as cgm
    from report_i18n import use_language, tr
    with use_language(language):
        data = cgm.load_data(input_path, days=None if days == 0 else days)
        first, last = data.ts.min(), data.ts.max()
        date_format = tr('%d/%m/%Y')
        period = first.strftime(date_format) + ' - ' + last.strftime(date_format)
        cgm.build_pdf(data, output_path, period, datetime.now().strftime(date_format), days)
        label = 'readings' if language == 'en' else 'lecturas'
        return f'{cgm.fint(len(data))} {label} · {period}'

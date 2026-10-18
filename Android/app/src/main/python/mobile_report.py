import os
import tempfile
from datetime import datetime


def generate(input_path, output_path, days, cache_dir):
    os.environ['MPLCONFIGDIR'] = os.path.join(cache_dir, 'matplotlib')
    os.environ['GLUCOSE_CHART_DPI'] = '120'
    tempfile.tempdir = cache_dir
    import glucose_insights as cgm
    data = cgm.load_data(input_path, days=None if days == 0 else days)
    first, last = data.ts.min(), data.ts.max()
    period = first.strftime('%d/%m/%Y') + ' - ' + last.strftime('%d/%m/%Y')
    cgm.build_pdf(data, output_path, period, datetime.now().strftime('%d/%m/%Y'), days)
    return f'{len(data):,} lecturas · {period}'.replace(',', '.')

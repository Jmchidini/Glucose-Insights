"""Run with Python and the report dependencies: python -m unittest discover -s tests."""
import sys
import math
import tempfile
import unittest
from pathlib import Path
from string import Formatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app/src/main/python'))
from report_i18n import EN, tr, use_language, language
import glucose_insights as cgm


def comparable(value):
    if isinstance(value, float) and math.isnan(value):
        return 'NaN'
    if isinstance(value, cgm.pd.Series):
        return comparable(value.to_dict())
    if isinstance(value, dict):
        return {k: comparable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [comparable(v) for v in value]
    return value


class ReportLanguageTests(unittest.TestCase):
    def test_placeholders_match(self):
        fields = lambda text: sorted(field for _, field, _, _ in Formatter().parse(text) if field is not None)
        for original, translated in EN.items():
            self.assertEqual(fields(original), fields(translated), original)

    def test_language_restored_after_failure(self):
        with self.assertRaises(ValueError):
            with use_language('en'):
                self.assertEqual(language(), 'en')
                raise ValueError('test')
        self.assertEqual(language(), 'es')
        with use_language('unsupported'):
            self.assertEqual(language(), 'es')

    def test_metrics_and_input_parsing_are_language_independent(self):
        # Spanish input headers must remain recognizable even with an English report.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'data.csv'
            path.write_text('Sello de fecha y hora,Glucosa histórica mg/dL\n'
                            '17/10/2026 00:00,50\n17/10/2026 00:05,90\n'
                            '17/10/2026 00:10,190\n17/10/2026 00:15,260\n', encoding='utf-8')
            results = []
            for code in ('es', 'en', 'es'):
                with use_language(code):
                    data = cgm.load_data(path)
                    core = cgm.compute_core_stats(data)
                    results.append(comparable((core, cgm.compute_ranges(data, core)[2], cgm.compute_events(data))))
            self.assertEqual(results[0], results[1])
            self.assertEqual(results[0], results[2])

    def test_localized_numbers_and_segments(self):
        with use_language('en'):
            self.assertEqual(cgm.fnum(123.45, 2), '123.45')
            self.assertEqual(cgm.fint(12345), '12,345')
            self.assertEqual(tr('Madrugada (00-06h)'), 'Overnight (00-06h)')
            self.assertEqual(cgm.describe_variability(20), 'low')
        self.assertEqual(cgm.fnum(123.45, 2), '123,45')
        self.assertEqual(cgm.fint(12345), '12.345')

    def test_validation_error_is_localized(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            path.write_text('invalid\n', encoding='utf-8')
            for code, message in [('en', 'Unrecognized format'), ('es', 'Formato no reconocido')]:
                with use_language(code), self.assertRaisesRegex(ValueError, message):
                    cgm.load_data(path)


if __name__ == '__main__':
    unittest.main()

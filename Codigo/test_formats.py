import tempfile
import unittest
from pathlib import Path
import pandas as pd
import glucose_insights as g


class FormatsTest(unittest.TestCase):
    def load(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_text(text, encoding='utf-8-sig')
            return g.load_data(path)

    def test_stream_delimiters(self):
        for sep in ('\t', ',', ';'):
            df = self.load(sep.join(['YYYY-mm-ddTHH:MM:SS', 'mg/dL']) + '\n' +
                           sep.join(['2026-10-01T00:00:00', '100']) + '\n' +
                           sep.join(['2026-10-01T00:01:00', '110']))
            self.assertEqual(g.sample_interval(df), 1)
            self.assertEqual(g.compute_core_stats(df)['active_pct'], 100)

    def test_libreview(self):
        df = self.load('Generated on today\nDevice Timestamp,Historic Glucose mg/dL\n01-10-2026 00:00,100\n01-10-2026 00:05,110\n')
        self.assertEqual(g.sample_interval(df), 5)

    def test_real_fifteen_minutes(self):
        df = pd.DataFrame({'ts': pd.date_range('2026-10-01', periods=20, freq='min'),
                           'glucose': [100]*15 + [180]*5})
        self.assertEqual(len(g.compute_events(df)['rise_groups']), 1)
        short = df.iloc[12:].reset_index(drop=True)
        self.assertEqual(len(g.compute_events(short)['rise_groups']), 0)

    def test_events_do_not_bridge_normal_readings(self):
        df = pd.DataFrame({'ts': pd.date_range('2026-10-01', periods=3, freq='min'),
                           'glucose': [60, 100, 60]})
        events = g.find_events(df, df.glucose < 70)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['duration_min'], 1)

    def test_partial_day_not_complete(self):
        daily = pd.DataFrame({'count': [300], 'tir': [80]})
        daily.attrs['interval_minutes'] = 1
        self.assertTrue(g.best_worst_days(daily)[0].empty)


if __name__ == '__main__':
    unittest.main()

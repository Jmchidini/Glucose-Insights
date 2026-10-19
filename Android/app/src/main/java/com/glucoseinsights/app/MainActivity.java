package com.glucoseinsights.app;

import android.app.Activity;
import android.content.*;
import android.content.res.Configuration;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.*;
import android.widget.*;
import androidx.core.content.FileProvider;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.io.*;
import java.util.Locale;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

public class MainActivity extends Activity {
    private static final int PICK = 10, SAVE = 11;
    private static final ExecutorService WORKER = Executors.newSingleThreadExecutor();
    private Uri selected;
    private TextView filename, status;
    private Button pick, generate, open, save, share;
    private Spinner period, languagePicker;
    private Context localized;
    private String languageCode;
    private String selectedName;
    private ProgressBar progress;
    private boolean busy;
    private File report;

    private int dp(int value) { return (int)(value * getResources().getDisplayMetrics().density); }
    private TextView text(String value, int size) {
        TextView view = new TextView(this); view.setText(value); view.setTextSize(size);
        view.setTextColor(0xff1b3a5c); view.setPadding(0, dp(10), 0, dp(10)); return view;
    }
    private Button button(LinearLayout parent, String title, View.OnClickListener click) {
        Button button = new Button(this); button.setText(title); button.setTextSize(18);
        button.setAllCaps(false); button.setMinHeight(dp(56)); button.setOnClickListener(click);
        parent.addView(button, new LinearLayout.LayoutParams(-1, -2)); return button;
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        report = new File(getFilesDir(), "reports/informe-glucosa.pdf");
        String systemLanguage = getResources().getConfiguration().getLocales().get(0).getLanguage();
        languageCode = getPreferences(MODE_PRIVATE).getString("language", "es".equals(systemLanguage) ? "es" : "en");
        if (!"en".equals(languageCode)) languageCode = "es";
        int savedPeriod = 1;
        if (state != null) {
            String uri = state.getString("selected"); if (uri != null) selected = Uri.parse(uri);
            selectedName = state.getString("filename");
            savedPeriod = state.getInt("period", 1);
        }
        buildScreen(savedPeriod);
    }
    private String s(int resource) { return localized.getString(resource); }
    private void buildScreen(int periodIndex) {
        Configuration config = new Configuration(getResources().getConfiguration());
        config.setLocale(new Locale(languageCode));
        localized = createConfigurationContext(config);
        ScrollView scroll = new ScrollView(this);
        LinearLayout panel = new LinearLayout(this); panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(22), dp(24), dp(22), dp(24)); scroll.addView(panel); setContentView(scroll);
        panel.addView(text("Glucose Insights", 28));
        panel.addView(text(s(R.string.subtitle), 18));
        TextView languageLabel = text(s(R.string.language_label), 16);
        panel.addView(languageLabel);
        languagePicker = new Spinner(this);
        languagePicker.setId(View.generateViewId());
        languageLabel.setLabelFor(languagePicker.getId());
        languagePicker.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item,
            new String[]{"Español", "English"}));
        languagePicker.setSelection("es".equals(languageCode) ? 0 : 1);
        panel.addView(languagePicker, new LinearLayout.LayoutParams(-1, dp(56)));
        languagePicker.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onNothingSelected(AdapterView<?> parent) { }
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                String next = position == 0 ? "es" : "en";
                if (next.equals(languageCode) || busy) return;
                int previousPeriod = period.getSelectedItemPosition();
                languageCode = next;
                getPreferences(MODE_PRIVATE).edit().putString("language", languageCode).apply();
                buildScreen(previousPeriod);
                status.setText(s(R.string.language_changed));
            }
        });
        pick = button(panel, s(R.string.pick_file), v -> {
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.setType("*/*"); intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            startActivityForResult(intent, PICK);
        });
        filename = text(selectedName == null ? s(R.string.choose_file) : selectedName, 16); panel.addView(filename);
        panel.addView(text(s(R.string.period), 18));
        period = new Spinner(this);
        period.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item,
            new String[]{s(R.string.days7), s(R.string.days15), s(R.string.days30), s(R.string.all_days)}));
        period.setSelection(periodIndex); panel.addView(period, new LinearLayout.LayoutParams(-1, dp(56)));
        generate = button(panel, s(R.string.generate), v -> generateReport());
        progress = new ProgressBar(this); progress.setVisibility(View.GONE); panel.addView(progress);
        status = text(s(R.string.local_processing), 16); status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE); panel.addView(status);
        open = button(panel, s(R.string.open_pdf), v -> openReport(false));
        share = button(panel, s(R.string.share_pdf), v -> openReport(true));
        save = button(panel, s(R.string.save_copy), v -> {
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.setType("application/pdf"); intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.putExtra(Intent.EXTRA_TITLE, s(R.string.save_filename)); startActivityForResult(intent, SAVE);
        });
        panel.addView(text(s(R.string.disclaimer), 14));
        refresh();
    }
    private void refresh() {
        languagePicker.setEnabled(!busy); pick.setEnabled(!busy); period.setEnabled(!busy); generate.setEnabled(!busy && selected != null);
        open.setEnabled(!busy && report.isFile()); share.setEnabled(!busy && report.isFile()); save.setEnabled(!busy && report.isFile());
        progress.setVisibility(busy ? View.VISIBLE : View.GONE);
        if (busy) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
    private void finishWork(String message) {
        runOnUiThread(() -> { if (!isDestroyed()) { busy = false; status.setText(message); refresh(); } });
    }
    private void copy(InputStream input, OutputStream output, long limit) throws IOException {
        if (input == null || output == null) throw new IOException(s(R.string.cannot_open));
        byte[] buffer = new byte[32768]; long total = 0; int size;
        while ((size = input.read(buffer)) != -1) {
            total += size; if (total > limit) throw new IOException(s(R.string.too_large));
            output.write(buffer, 0, size);
        }
    }
    private void generateReport() {
        final Uri inputUri = selected;
        final String reportLanguage = languageCode;
        final int days = new int[]{7, 15, 30, 0}[period.getSelectedItemPosition()];
        busy = true; status.setText(s(R.string.generating)); refresh();
        WORKER.execute(() -> {
            File input = new File(getCacheDir(), "input-data.txt");
            File pending = new File(getCacheDir(), "pending.pdf");
            try {
                try (InputStream source = getContentResolver().openInputStream(inputUri); OutputStream dest = new FileOutputStream(input)) {
                    copy(source, dest, 20L * 1024 * 1024);
                }
                if (!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
                String summary = Python.getInstance().getModule("mobile_report").callAttr("generate",
                    input.getAbsolutePath(), pending.getAbsolutePath(), days, getCacheDir().getAbsolutePath(), reportLanguage).toString();
                if (!report.getParentFile().isDirectory() && !report.getParentFile().mkdirs()) throw new IOException(s(R.string.cannot_create_folder));
                if (!pending.renameTo(report)) throw new IOException(s(R.string.cannot_save_pdf));
                finishWork(s(R.string.ready) + summary);
            } catch (Exception error) {
                finishWork(s(R.string.generation_failed) + error.getMessage());
            } finally { input.delete(); pending.delete(); }
        });
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (result != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        if (request == PICK) {
            String name = "";
            try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int column = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                    if (column >= 0) name = cursor.getString(column);
                }
            } catch (Exception error) { status.setText(s(R.string.cannot_read)); return; }
            if (name == null || !(name.toLowerCase(Locale.ROOT).endsWith(".csv") || name.toLowerCase(Locale.ROOT).endsWith(".tsv"))) {
                status.setText(s(R.string.wrong_extension)); return;
            }
            if (selected != null && !selected.equals(uri)) {
                try { getContentResolver().releasePersistableUriPermission(selected, Intent.FLAG_GRANT_READ_URI_PERMISSION); }
                catch (SecurityException ignored) { }
            }
            try { getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION); }
            catch (SecurityException ignored) { }
            selected = uri; selectedName = name; filename.setText(name); status.setText(s(R.string.selected)); refresh();
        } else if (request == SAVE) {
            busy = true; refresh(); status.setText(s(R.string.saving));
            WORKER.execute(() -> {
                try (InputStream input = new FileInputStream(report); OutputStream output = getContentResolver().openOutputStream(uri, "wt")) {
                    copy(input, output, Long.MAX_VALUE); finishWork(s(R.string.saved));
                } catch (Exception error) { finishWork(s(R.string.save_failed) + error.getMessage()); }
            });
        }
    }
    private void openReport(boolean sharing) {
        Uri uri = FileProvider.getUriForFile(this, getPackageName() + ".files", report);
        Intent intent = new Intent(sharing ? Intent.ACTION_SEND : Intent.ACTION_VIEW);
        if (sharing) { intent.setType("application/pdf"); intent.putExtra(Intent.EXTRA_STREAM, uri); }
        else intent.setDataAndType(uri, "application/pdf");
        intent.setClipData(ClipData.newRawUri(s(R.string.report_title), uri));
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { startActivity(Intent.createChooser(intent, sharing ? s(R.string.share_report) : s(R.string.open_report))); }
        catch (ActivityNotFoundException error) { status.setText(s(R.string.no_pdf_app)); }
    }
    @Override protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        if (selected != null) state.putString("selected", selected.toString());
        state.putString("filename", selectedName); state.putInt("period", period.getSelectedItemPosition());
    }
    @Override public void onBackPressed() {
        if (busy) Toast.makeText(this, s(R.string.please_wait), Toast.LENGTH_SHORT).show();
        else super.onBackPressed();
    }
}

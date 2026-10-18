package com.glucoseinsights.app;

import android.app.Activity;
import android.content.*;
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
    private Spinner period;
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
        ScrollView scroll = new ScrollView(this);
        LinearLayout panel = new LinearLayout(this); panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(22), dp(24), dp(22), dp(24)); scroll.addView(panel); setContentView(scroll);
        panel.addView(text("Glucose Insights", 28));
        panel.addView(text("Tu informe de glucosa, sin Internet", 18));
        pick = button(panel, "1. Elegir archivo", v -> {
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.setType("*/*"); intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            startActivityForResult(intent, PICK);
        });
        filename = text("Elegí un archivo CSV o TSV", 16); panel.addView(filename);
        panel.addView(text("2. Período del informe", 18));
        period = new Spinner(this);
        period.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item,
            new String[]{"Últimos 7 días", "Últimos 15 días", "Últimos 30 días", "Todo el archivo"}));
        period.setSelection(1); panel.addView(period, new LinearLayout.LayoutParams(-1, dp(56)));
        generate = button(panel, "3. Generar informe", v -> generateReport());
        progress = new ProgressBar(this); progress.setVisibility(View.GONE); panel.addView(progress);
        status = text("Los datos se procesan en este celular.", 16); status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE); panel.addView(status);
        open = button(panel, "Abrir PDF", v -> openReport(false));
        share = button(panel, "Compartir PDF", v -> openReport(true));
        save = button(panel, "Guardar una copia", v -> {
            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            intent.setType("application/pdf"); intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.putExtra(Intent.EXTRA_TITLE, "informe-glucosa.pdf"); startActivityForResult(intent, SAVE);
        });
        panel.addView(text("Versión de prueba. El informe sirve de apoyo para la consulta médica.", 14));
        if (state != null) {
            String uri = state.getString("selected"); if (uri != null) selected = Uri.parse(uri);
            filename.setText(state.getString("filename", "Elegí un archivo CSV o TSV"));
            period.setSelection(state.getInt("period", 1));
        }
        refresh();
    }
    private void refresh() {
        pick.setEnabled(!busy); period.setEnabled(!busy); generate.setEnabled(!busy && selected != null);
        open.setEnabled(!busy && report.isFile()); share.setEnabled(!busy && report.isFile()); save.setEnabled(!busy && report.isFile());
        progress.setVisibility(busy ? View.VISIBLE : View.GONE);
        if (busy) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
    private void finishWork(String message) {
        runOnUiThread(() -> { if (!isDestroyed()) { busy = false; status.setText(message); refresh(); } });
    }
    private static void copy(InputStream input, OutputStream output, long limit) throws IOException {
        if (input == null || output == null) throw new IOException("No se pudo abrir el archivo.");
        byte[] buffer = new byte[32768]; long total = 0; int size;
        while ((size = input.read(buffer)) != -1) {
            total += size; if (total > limit) throw new IOException("El archivo supera el tamaño admitido (20 MB).");
            output.write(buffer, 0, size);
        }
    }
    private void generateReport() {
        final Uri inputUri = selected;
        final int days = new int[]{7, 15, 30, 0}[period.getSelectedItemPosition()];
        busy = true; status.setText("Generando el informe… Mantené la app abierta; la primera vez puede tardar."); refresh();
        WORKER.execute(() -> {
            File input = new File(getCacheDir(), "input-data.txt");
            File pending = new File(getCacheDir(), "pending.pdf");
            try {
                try (InputStream source = getContentResolver().openInputStream(inputUri); OutputStream dest = new FileOutputStream(input)) {
                    copy(source, dest, 20L * 1024 * 1024);
                }
                if (!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
                String summary = Python.getInstance().getModule("mobile_report").callAttr("generate",
                    input.getAbsolutePath(), pending.getAbsolutePath(), days, getCacheDir().getAbsolutePath()).toString();
                if (!report.getParentFile().isDirectory() && !report.getParentFile().mkdirs()) throw new IOException("No se pudo crear la carpeta de informes.");
                if (!pending.renameTo(report)) throw new IOException("No se pudo guardar el PDF generado.");
                finishWork("Informe listo.\n" + summary);
            } catch (Exception error) {
                finishWork("No se pudo generar el informe.\n" + error.getMessage());
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
            } catch (Exception error) { status.setText("No se pudo leer el archivo seleccionado."); return; }
            if (name == null || !(name.toLowerCase(Locale.ROOT).endsWith(".csv") || name.toLowerCase(Locale.ROOT).endsWith(".tsv"))) {
                status.setText("Seleccioná un archivo con extensión .csv o .tsv."); return;
            }
            if (selected != null && !selected.equals(uri)) {
                try { getContentResolver().releasePersistableUriPermission(selected, Intent.FLAG_GRANT_READ_URI_PERMISSION); }
                catch (SecurityException ignored) { }
            }
            try { getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION); }
            catch (SecurityException ignored) { }
            selected = uri; filename.setText(name); status.setText("Archivo seleccionado. Elegí el período y generá el informe."); refresh();
        } else if (request == SAVE) {
            busy = true; refresh(); status.setText("Guardando copia…");
            WORKER.execute(() -> {
                try (InputStream input = new FileInputStream(report); OutputStream output = getContentResolver().openOutputStream(uri, "wt")) {
                    copy(input, output, Long.MAX_VALUE); finishWork("Copia guardada.");
                } catch (Exception error) { finishWork("No se pudo guardar la copia: " + error.getMessage()); }
            });
        }
    }
    private void openReport(boolean sharing) {
        Uri uri = FileProvider.getUriForFile(this, getPackageName() + ".files", report);
        Intent intent = new Intent(sharing ? Intent.ACTION_SEND : Intent.ACTION_VIEW);
        if (sharing) { intent.setType("application/pdf"); intent.putExtra(Intent.EXTRA_STREAM, uri); }
        else intent.setDataAndType(uri, "application/pdf");
        intent.setClipData(ClipData.newRawUri("Informe de glucosa", uri));
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { startActivity(Intent.createChooser(intent, sharing ? "Compartir informe" : "Abrir informe")); }
        catch (ActivityNotFoundException error) { status.setText("No hay una aplicación para abrir PDF. Podés guardar una copia."); }
    }
    @Override protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        if (selected != null) state.putString("selected", selected.toString());
        state.putString("filename", filename.getText().toString()); state.putInt("period", period.getSelectedItemPosition());
    }
    @Override public void onBackPressed() {
        if (busy) Toast.makeText(this, "Esperá a que termine la generación del informe.", Toast.LENGTH_SHORT).show();
        else super.onBackPressed();
    }
}

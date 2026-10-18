#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — Interfaz web local (drag & drop) para generar el informe CGM en PDF.

Uso:
    pip install -r requirements.txt
    python app.py
    Abrir http://localhost:5000 en el navegador

El procesamiento se hace enteramente en tu computadora: el CSV no se envía
a ningún servidor externo, todo corre localmente con Flask.
"""
import os
import shutil
import tempfile
import traceback
import uuid
from datetime import datetime

from flask import Flask, request, send_file, jsonify, Response

import glucose_insights as cgm

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB máx por archivo

# Carpeta base para archivos temporales de esta sesión del servidor
BASE_TMP = tempfile.mkdtemp(prefix="cgm_app_")


# ============================================================
# FRONTEND (una sola página, sin dependencias externas)
# ============================================================
INDEX_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Glucose Insights · LibreView</title>
<style>
  :root {
    --navy: #1B3A5C; --blue: #1565C0; --teal: #0F6E63; --green: #2E7D32;
    --red: #C62828; --grey: #5A5A5A; --lightgrey: #F2F4F6; --lightblue: #E8F0FA;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: linear-gradient(180deg, #f7f9fb 0%, #eef2f6 100%);
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    padding: 24px;
  }
  .card {
    background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(27,58,92,0.12);
    max-width: 560px; width: 100%; padding: 40px 36px 32px;
  }
  .brand { color: var(--blue); font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 6px; }
  h1 { color: var(--navy); font-size: 22px; margin: 0 0 4px; }
  .subtitle { color: var(--grey); font-size: 14px; margin: 0 0 28px; line-height: 1.5; }
  .dropzone {
    border: 2px dashed #b9c6d6; border-radius: 12px; padding: 36px 20px;
    text-align: center; cursor: pointer; transition: all 0.15s ease; background: var(--lightblue);
  }
  .dropzone.dragover { border-color: var(--blue); background: #dceafc; transform: scale(1.01); }
  .dropzone.has-file { border-color: var(--green); background: #eaf5ea; }
  .dz-icon { font-size: 40px; margin-bottom: 8px; }
  .dz-text { color: var(--navy); font-weight: 600; font-size: 15px; margin-bottom: 4px; }
  .dz-sub { color: var(--grey); font-size: 12.5px; }
  input[type=file] { display: none; }

  .options { margin-top: 22px; }
  .options label { display: block; font-size: 13px; font-weight: 600; color: var(--navy); margin-bottom: 6px; }
  select {
    width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid #cdd6e0;
    font-size: 14px; color: #222; background: white;
  }

  button#genBtn {
    margin-top: 24px; width: 100%; padding: 13px; border: none; border-radius: 10px;
    background: var(--blue); color: white; font-size: 15px; font-weight: 600; cursor: pointer;
    transition: background 0.15s ease;
  }
  button#genBtn:disabled { background: #a9b8c8; cursor: not-allowed; }
  button#genBtn:not(:disabled):hover { background: var(--navy); }

  .status { margin-top: 16px; font-size: 13.5px; text-align: center; min-height: 20px; }
  .status.error { color: var(--red); }
  .status.ok { color: var(--green); }
  .status.working { color: var(--blue); }

  .spinner {
    display: inline-block; width: 14px; height: 14px; border: 2px solid #cfe0f5;
    border-top-color: var(--blue); border-radius: 50%; animation: spin 0.7s linear infinite;
    margin-right: 6px; vertical-align: -2px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .footer-note { margin-top: 22px; font-size: 11.5px; color: #9aa5b1; text-align: center; line-height: 1.5; }
</style>
</head>
<body>
  <div class="card">
    <div class="brand">GLUCOSE INSIGHTS</div>
    <h1>Informe de Monitoreo Continuo de Glucosa</h1>
    <p class="subtitle">Arrastrá tu archivo Stream TSV/CSV o LibreView CSV y generá el informe en PDF. Todo el procesamiento ocurre en esta computadora.</p>

    <div class="dropzone" id="dropzone">
      <div class="dz-icon">📄</div>
      <div class="dz-text" id="dzText">Arrastrá el CSV o TSV acá, o hacé clic para elegirlo</div>
      <div class="dz-sub" id="dzSub">Formato esperado: Stream (.tsv/.csv) o LibreView (.csv)</div>
      <input type="file" id="fileInput" accept=".csv,.tsv">
    </div>

    <div class="options">
      <label for="daysSelect">Período a analizar</label>
      <select id="daysSelect">
        <option value="7">Últimos 7 días</option>
        <option value="15" selected>Últimos 15 días</option>
        <option value="30">Últimos 30 días</option>
        <option value="90">Últimos 90 días</option>
        <option value="0">Todo el archivo</option>
      </select>
    </div>

    <button id="genBtn" disabled>Generar informe PDF</button>
    <div class="status" id="status"></div>

    <div class="footer-note">El archivo no se envía a internet: se procesa localmente y el PDF se descarga directo a tu computadora.</div>
  </div>

<script>
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const genBtn = document.getElementById('genBtn');
  const statusEl = document.getElementById('status');
  const dzText = document.getElementById('dzText');
  const dzSub = document.getElementById('dzSub');
  let selectedFile = null;

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(evt =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add('dragover'); })
  );
  ['dragleave', 'drop'].forEach(evt =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove('dragover'); })
  );
  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  function handleFile(file) {
    if (!(/[.](csv|tsv)$/i.test(file.name))) {
      setStatus('El archivo debe ser un .tsv o .csv compatible.', 'error');
      return;
    }
    selectedFile = file;
    dropzone.classList.add('has-file');
    dzText.textContent = '✓ ' + file.name;
    dzSub.textContent = (file.size / 1024).toFixed(0) + ' KB — clic para cambiar el archivo';
    genBtn.disabled = false;
    setStatus('', '');
  }

  function setStatus(msg, cls) {
    statusEl.textContent = msg;
    statusEl.className = 'status' + (cls ? ' ' + cls : '');
  }

  genBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    genBtn.disabled = true;
    setStatus('⏳ Analizando datos y generando el PDF… puede tardar unos segundos.', 'working');

    const formData = new FormData();
    formData.append('csv_file', selectedFile);
    formData.append('days', document.getElementById('daysSelect').value);

    try {
      const resp = await fetch('/generate', { method: 'POST', body: formData });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({error: 'Error desconocido'}));
        throw new Error(err.error || ('Error del servidor (' + resp.status + ')'));
      }
      const blob = await resp.blob();
      const cd = resp.headers.get('Content-Disposition') || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : 'informe_cgm.pdf';

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename;
      document.body.appendChild(a); a.click(); a.remove();
      window.URL.revokeObjectURL(url);

      setStatus('✓ Informe generado y descargado correctamente.', 'ok');
    } catch (e) {
      setStatus('✗ ' + e.message, 'error');
    } finally {
      genBtn.disabled = false;
    }
  });
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


@app.route("/generate", methods=["POST"])
def generate():
    if "csv_file" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo."}), 400

    f = request.files["csv_file"]
    if f.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400
    if not f.filename.lower().endswith((".csv", ".tsv")):
        return jsonify({"error": "El archivo debe tener extensión .csv o .tsv"}), 400

    days_raw = request.form.get("days", "15")
    try:
        days = int(days_raw)
    except ValueError:
        days = 15
    days_arg = None if days == 0 else days

    job_id = uuid.uuid4().hex[:10]
    job_dir = os.path.join(BASE_TMP, job_id)
    os.makedirs(job_dir, exist_ok=True)
    csv_path = os.path.join(job_dir, "input.csv")
    f.save(csv_path)

    try:
        df = cgm.load_data(csv_path, days=days_arg)
        first_ts, last_ts = df["ts"].min(), df["ts"].max()
        period_label = f"{first_ts.strftime('%d/%m/%Y')} – {last_ts.strftime('%d/%m/%Y')}"
        generated_on = datetime.now().strftime("%d/%m/%Y")

        pdf_path = os.path.join(job_dir, "informe_cgm.pdf")
        cgm.build_pdf(df, pdf_path, period_label, generated_on, days)

        out_name = f"Informe CGM {first_ts.strftime('%d-%m-%Y')} a {last_ts.strftime('%d-%m-%Y')}.pdf"

        response = send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=out_name,
        )

        @response.call_on_close
        def _cleanup():
            shutil.rmtree(job_dir, ignore_errors=True)

        return response

    except Exception as e:
        traceback.print_exc()
        shutil.rmtree(job_dir, ignore_errors=True)
        msg = str(e) or "Error al procesar el archivo."
        return jsonify({"error": msg}), 500


if __name__ == "__main__":
    print("=" * 60)
    print(" Glucose Insights — servidor local")
    print(" Abrí este link en tu navegador: http://localhost:5000")
    print(" Para detener el servidor: Ctrl+C")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)

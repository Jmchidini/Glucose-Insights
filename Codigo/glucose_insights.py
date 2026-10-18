#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cgm_report.py
=============
Genera un informe clínico en PDF a partir de un CSV exportado de LibreView
(FreeStyle Libre), con el mismo formato/contenido que el informe de
referencia: portada, índice, resumen ejecutivo, tiempo en rango,
variabilidad, hipo/hiperglucemias, análisis por horario, perfil diario,
días destacados, eventos llamativos, estadísticas adicionales, tabla
resumen y anexo técnico.

Uso:
    python cgm_report.py entrada.csv --days 15 --output informe.pdf

Dependencias:
    pandas, numpy, matplotlib, reportlab
    pip install pandas numpy matplotlib reportlab

Autor: generado con Claude (Anthropic) a pedido del usuario.
"""

import argparse
import os
import sys
import tempfile
import shutil
import collections
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, NextPageTemplate, FrameBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas as pdfcanvas

# ============================================================
# CONFIGURACIÓN / PALETA
# ============================================================
NAVY = colors.HexColor("#1B3A5C")
BLUE = colors.HexColor("#1565C0")
TEAL = colors.HexColor("#0F6E63")
GREEN = colors.HexColor("#2E7D32")
RED = colors.HexColor("#C62828")
ORANGE = colors.HexColor("#E65100")
GREY = colors.HexColor("#5A5A5A")
LIGHTGREY = colors.HexColor("#F2F4F6")
LIGHTBLUE = colors.HexColor("#E8F0FA")

# umbrales clínicos estándar (mg/dL) — consenso ATTD / ADA
VERY_LOW, LOW, HIGH, VERY_HIGH = 54, 70, 180, 250
STRICT_LOW, STRICT_HIGH = 70, 140
CV_THRESHOLD = 36.0  # % — variabilidad estable vs. inestable (ATTD)

# colores para gráficos (hex string, no reportlab Color)
C_TIR = "#2e7d32"
C_LOW = "#e53935"
C_VLOW = "#8b0000"
C_HIGH = "#fb8c00"
C_VHIGH = "#c62828"
C_LINE = "#1565c0"

SEGMENTS_DEF = [
    ("Madrugada (00-06h)", 0, 6),
    ("Mañana (06-11h)", 6, 11),
    ("Mediodía (11-14h)", 11, 14),
    ("Tarde (14-19h)", 14, 19),
    ("Noche (19-24h)", 19, 24),
]


# ============================================================
# 1. CARGA Y LIMPIEZA DE DATOS
# ============================================================
def load_data(csv_path, days=None):
    """Read Stream TSV/CSV or LibreView CSV, preserving device-local time."""
    if days is not None and days <= 0:
        raise ValueError("El período debe ser positivo, o usar 0 para todo el archivo.")
    with open(csv_path, encoding="utf-8-sig") as f:
        lines = [f.readline() for _ in range(12)]
    header = next((i for i, line in enumerate(lines)
                   if "Historic Glucose" in line or "Glucosa histórica" in line
                   or ("mg/dL" in line and "YYYY-mm-ddTHH:MM:SS" in line)), None)
    if header is None:
        raise ValueError("Formato no reconocido: se admite Stream TSV/CSV o LibreView CSV en mg/dL.")
    import csv
    separator = csv.Sniffer().sniff(lines[header], delimiters="\t,;").delimiter
    df = pd.read_csv(csv_path, skiprows=header, sep=separator, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    stream = {"YYYY-mm-ddTHH:MM:SS", "mg/dL"}.issubset(df.columns)
    if stream:
        ts_col, glu_col = "YYYY-mm-ddTHH:MM:SS", "mg/dL"
        df["ts"] = pd.to_datetime(df[ts_col], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    else:
        ts_col = next((c for c in df if "Timestamp" in c or ("fecha" in c.lower() and "hora" in c.lower())), None)
        glu_col = next((c for c in df if "mg/dL" in c and ("Historic Glucose" in c or "Glucosa histórica" in c)), None)
        if ts_col is None or glu_col is None:
            raise ValueError("Faltan fecha/hora o glucosa histórica en mg/dL.")
        df["ts"] = pd.to_datetime(df[ts_col], format="mixed", dayfirst=True, errors="coerce")
    df["glucose"] = pd.to_numeric(df[glu_col], errors="coerce")
    original_count = len(df)
    df = df.dropna(subset=["ts", "glucose"])
    df = df[np.isfinite(df["glucose"]) & (df["glucose"] > 0)].copy()
    invalid_count = original_count - len(df)
    if df.empty:
        raise ValueError("No hay lecturas válidas en el archivo.")
    if df.groupby("ts")["glucose"].nunique().gt(1).any():
        raise ValueError("Hay lecturas distintas con la misma fecha/hora; revisá los sensores superpuestos.")
    df = df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    cadence = df["ts"].diff().dt.total_seconds().dropna().median() / 60
    if not np.isfinite(cadence) or cadence <= 0:
        raise ValueError("Se necesitan al menos dos lecturas con fechas diferentes.")
    if days is not None:
        df = df[df["ts"] > df["ts"].max() - timedelta(days=days)].copy().reset_index(drop=True)
    if len(df) < 2:
        raise ValueError("El período seleccionado contiene menos de dos lecturas.")
    df["date"] = df["ts"].dt.date
    df["hour"] = df["ts"].dt.hour
    df["segment"] = df["hour"].apply(assign_segment)
    df.attrs.update(interval_minutes=float(cadence), source="Stream" if stream else "LibreView",
                    invalid_rows=invalid_count)
    return df


def sample_interval(df):
    return float(df.attrs.get("interval_minutes", df["ts"].diff().dt.total_seconds().median() / 60))


def assign_segment(h):
    for name, start, end in SEGMENTS_DEF:
        if start <= h < end:
            return name
    return SEGMENTS_DEF[-1][0]


# ============================================================
# 2. ESTADÍSTICAS PRINCIPALES
# ============================================================
def compute_core_stats(df):
    g = df["glucose"]
    n = len(g)
    first_ts, last_ts = df["ts"].min(), df["ts"].max()
    span_days = (last_ts - first_ts).total_seconds() / 86400.0

    mean_g = g.mean()
    sd_g = g.std()
    cv = 100 * sd_g / mean_g if mean_g else np.nan
    gmi = 3.31 + 0.02392 * mean_g  # Bergenstal et al. 2018

    expected_readings = span_days * 24 * 60 / sample_interval(df) + 1 if span_days > 0 else n
    active_pct = min(100.0, 100 * n / expected_readings) if expected_readings else 100.0

    pct = g.quantile([0.10, 0.25, 0.5, 0.75, 0.9])

    return {
        "interval_minutes": sample_interval(df), "n": n, "first_ts": first_ts, "last_ts": last_ts, "span_days": span_days,
        "mean": mean_g, "sd": sd_g, "cv": cv, "gmi": gmi, "active_pct": active_pct,
        "p10": pct[0.10], "p25": pct[0.25], "p50": pct[0.5], "p75": pct[0.75], "p90": pct[0.9],
        "iqr": pct[0.75] - pct[0.25], "min": g.min(), "max": g.max(), "range": g.max() - g.min(),
        "median": g.median(),
    }


def time_str(fraction, span_days):
    """Convierte una fracción de tiempo (0-1) del período total a texto d/h/min."""
    minutes = fraction * span_days * 24 * 60
    d = int(minutes // 1440)
    h = int((minutes % 1440) // 60)
    m = int(minutes % 60)
    parts = []
    if d:
        parts.append(f"{d} d")
    if h:
        parts.append(f"{h} h")
    parts.append(f"{m} min")
    return " ".join(parts)


def compute_ranges(df, core):
    g = df["glucose"]
    n = core["n"]
    span_days = core["span_days"]

    def row(mask, label):
        c = int(mask.sum())
        frac = c / n
        return [label, f"{fnum(100*frac, 2)} %", time_str(frac, span_days), fint(c)]

    standard = [
        row(g > VERY_HIGH, f"Muy alto  (>{VERY_HIGH} mg/dL)"),
        row((g > HIGH) & (g <= VERY_HIGH), f"Alto  ({HIGH+1}-{VERY_HIGH} mg/dL)"),
        row((g >= LOW) & (g <= HIGH), f"Rango objetivo  ({LOW}-{HIGH} mg/dL)"),
        row((g >= VERY_LOW) & (g < LOW), f"Bajo  ({VERY_LOW}-{LOW-1} mg/dL)"),
        row(g < VERY_LOW, f"Muy bajo  (<{VERY_LOW} mg/dL)"),
    ]
    strict = [
        row(g < STRICT_LOW, f"< {STRICT_LOW} mg/dL"),
        row((g >= STRICT_LOW) & (g <= STRICT_HIGH), f"{STRICT_LOW}-{STRICT_HIGH} mg/dL (objetivo estricto)"),
        row(g > STRICT_HIGH, f"> {STRICT_HIGH} mg/dL"),
    ]
    summary = {
        "tir": 100 * ((g >= LOW) & (g <= HIGH)).mean(),
        "tar": 100 * (g > HIGH).mean(),
        "tbr": 100 * (g < LOW).mean(),
        "tar2": 100 * (g > VERY_HIGH).mean(),
        "tbr2": 100 * (g < VERY_LOW).mean(),
        "strict_tir": 100 * ((g >= STRICT_LOW) & (g <= STRICT_HIGH)).mean(),
    }
    return standard, strict, summary


# ============================================================
# 3. EVENTOS DE HIPO / HIPERGLUCEMIA
# ============================================================
def find_events(df, mask, min_gap_minutes=15):
    """Agrupa lecturas consecutivas que cumplen `mask` en episodios,
    tolerando huecos menores a `min_gap_minutes` entre lecturas."""
    idxs = np.where(mask.values)[0]
    if len(idxs) == 0:
        return []
    ts = df["ts"].values
    events = []
    start_i = idxs[0]
    prev_i = idxs[0]
    for i in idxs[1:]:
        gap = (ts[i] - ts[prev_i]).astype("timedelta64[m]").astype(int)
        if i != prev_i + 1 or gap > min(min_gap_minutes, 2 * sample_interval(df)):
            events.append((start_i, prev_i))
            start_i = i
        prev_i = i
    events.append((start_i, prev_i))

    out = []
    for s, e in events:
        seg = df.iloc[s:e+1]
        dur = (df["ts"].iloc[e] - df["ts"].iloc[s]).total_seconds() / 60 + sample_interval(df)
        out.append({
            "start": df["ts"].iloc[s], "end": df["ts"].iloc[e], "duration_min": dur,
            "nadir": seg["glucose"].min(), "peak": seg["glucose"].max(),
            "hour_start": df["ts"].iloc[s].hour,
        })
    return out


def compute_events(df):
    hypo = find_events(df, df["glucose"] < LOW)
    hypo_l2 = find_events(df, df["glucose"] < VERY_LOW)
    hyper = find_events(df, df["glucose"] > HIGH)
    hyper_l2 = find_events(df, df["glucose"] > VERY_HIGH)

    d = df.copy()
    target = d[["ts"]].copy()
    target["lookup"] = target["ts"] - pd.Timedelta(minutes=15)
    prior = d[["ts", "glucose"]].rename(columns={"ts": "lookup", "glucose": "previous"})
    matched = pd.merge_asof(target, prior, on="lookup", direction="nearest",
                            tolerance=pd.Timedelta(seconds=min(60, sample_interval(df) * 30)))
    d["delta15"] = d["glucose"].to_numpy() - matched["previous"].to_numpy()
    rapid_rise = d[d["delta15"] >= 70]
    rapid_fall = d[d["delta15"] <= -70]

    def group_rapid(sub, gap=30):
        if len(sub) == 0:
            return []
        sub = sub.sort_values("ts")
        groups, start, prev = [], sub.iloc[0], sub.iloc[0]
        for _, row in sub.iloc[1:].iterrows():
            if (row["ts"] - prev["ts"]).total_seconds() / 60 > gap:
                groups.append((start, prev))
                start = row
            prev = row
        groups.append((start, prev))
        return groups

    rise_groups = group_rapid(rapid_rise)
    fall_groups = group_rapid(rapid_fall)

    return {
        "hypo": hypo, "hypo_l2": hypo_l2, "hyper": hyper, "hyper_l2": hyper_l2,
        "rise_groups": rise_groups, "fall_groups": fall_groups,
    }


# ============================================================
# 4. ANÁLISIS POR HORARIO Y POR DÍA
# ============================================================
def compute_segment_stats(df):
    order = [s[0] for s in SEGMENTS_DEF]
    g = df.groupby("segment")["glucose"]
    stats = g.agg(["mean", "std", "min", "max", "count"])
    stats["cv"] = 100 * stats["std"] / stats["mean"]
    stats["pct_hypo"] = df.groupby("segment")["glucose"].apply(lambda x: 100 * (x < LOW).mean())
    stats["pct_hyper"] = df.groupby("segment")["glucose"].apply(lambda x: 100 * (x > HIGH).mean())
    stats["pct_tir"] = df.groupby("segment")["glucose"].apply(lambda x: 100 * ((x >= LOW) & (x <= HIGH)).mean())
    return stats.reindex(order)


def compute_hourly_stats(df):
    g = df.groupby("hour")["glucose"]
    hourly = g.agg(["mean", "std", "count"])
    hourly["p10"] = g.quantile(0.10)
    hourly["p25"] = g.quantile(0.25)
    hourly["p75"] = g.quantile(0.75)
    hourly["p90"] = g.quantile(0.90)
    hourly["cv"] = 100 * hourly["std"] / hourly["mean"]
    hourly = hourly.reindex(range(24))
    return hourly


def compute_daily_stats(df):
    g = df.groupby("date")["glucose"]
    daily = g.agg(["mean", "std", "min", "max", "count"])
    daily["cv"] = 100 * daily["std"] / daily["mean"]
    daily["tir"] = df.groupby("date")["glucose"].apply(lambda x: 100 * ((x >= LOW) & (x <= HIGH)).mean())
    daily["tbr"] = df.groupby("date")["glucose"].apply(lambda x: 100 * (x < LOW).mean())
    daily["tar"] = df.groupby("date")["glucose"].apply(lambda x: 100 * (x > HIGH).mean())
    daily.attrs["interval_minutes"] = sample_interval(df)
    return daily


def best_worst_days(daily, min_readings=None):
    if min_readings is None:
        min_readings = np.ceil(1440 / daily.attrs.get("interval_minutes", 5) * (280 / 288))
    complete = daily[daily["count"] >= min_readings].copy()
    best = complete.sort_values("tir", ascending=False).head(4)
    worst = complete.sort_values("tir", ascending=True).head(4)
    return complete, best, worst


# ============================================================
# 5. GRÁFICOS
# ============================================================
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": "#444444",
    "axes.labelcolor": "#222222", "text.color": "#222222", "xtick.color": "#333333",
    "ytick.color": "#333333", "axes.titleweight": "bold", "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def generate_charts(df, hourly, daily, outdir, period_label):
    paths = {}
    ndays = df["date"].nunique()

    # 1. Curva completa
    fig, ax = plt.subplots(figsize=(14, 5), dpi=200)
    ax.axhspan(LOW, HIGH, color=C_TIR, alpha=0.10, zorder=0)
    ax.axhspan(0, VERY_LOW, color=C_VLOW, alpha=0.08, zorder=0)
    ax.axhspan(VERY_LOW, LOW, color=C_LOW, alpha=0.08, zorder=0)
    ax.axhspan(HIGH, VERY_HIGH, color=C_HIGH, alpha=0.08, zorder=0)
    ax.axhspan(VERY_HIGH, max(350, df["glucose"].max() + 20), color=C_VHIGH, alpha=0.08, zorder=0)
    ax.plot(df["ts"], df["glucose"], color=C_LINE, linewidth=0.6)
    ax.axhline(LOW, color=C_LOW, linestyle="--", linewidth=0.8)
    ax.axhline(HIGH, color=C_HIGH, linestyle="--", linewidth=0.8)
    ax.set_ylim(max(0, df["glucose"].min() - 20), df["glucose"].max() + 20)
    ax.set_ylabel("Glucosa (mg/dL)")
    ax.set_title(f"Curva completa de glucosa — {period_label}")
    interval = max(1, ndays // 15)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(alpha=0.25, linewidth=0.5)
    fig.tight_layout()
    p = os.path.join(outdir, "01_curva_completa.png"); fig.savefig(p); plt.close(fig)
    paths["curva"] = p

    # 2. AGP
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
    x = hourly.index.values
    ax.axhspan(LOW, HIGH, color=C_TIR, alpha=0.10, zorder=0)
    ax.fill_between(x, hourly["p10"], hourly["p90"], color=C_LINE, alpha=0.15, label="P10–P90")
    ax.fill_between(x, hourly["p25"], hourly["p75"], color=C_LINE, alpha=0.30, label="P25–P75 (RIC)")
    ax.plot(x, hourly["mean"], color=C_LINE, linewidth=2.2, label="Media")
    ax.axhline(LOW, color=C_LOW, linestyle="--", linewidth=0.8)
    ax.axhline(HIGH, color=C_HIGH, linestyle="--", linewidth=0.8)
    ax.set_xlim(0, 23); ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Hora del día"); ax.set_ylabel("Glucosa (mg/dL)")
    ax.set_title("Perfil de Glucosa Ambulatorio (AGP) — promedio por hora")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.grid(alpha=0.25, linewidth=0.5)
    fig.tight_layout()
    p = os.path.join(outdir, "02_agp.png"); fig.savefig(p); plt.close(fig)
    paths["agp"] = p

    # 3. Histograma
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    lo = max(20, int(df["glucose"].min() // 10) * 10 - 10)
    hi = int(df["glucose"].max() // 10) * 10 + 20
    bins = np.arange(lo, hi, 10)
    n_, bins_, patches = ax.hist(df["glucose"], bins=bins, edgecolor="white", linewidth=0.5)
    for patch, b in zip(patches, bins[:-1]):
        if b < VERY_LOW: c = C_VLOW
        elif b < LOW: c = C_LOW
        elif b < HIGH: c = C_TIR
        elif b < VERY_HIGH: c = C_HIGH
        else: c = C_VHIGH
        patch.set_facecolor(c)
    ax.axvline(df["glucose"].mean(), color="black", linewidth=1.3, label=f"Media: {df['glucose'].mean():.0f} mg/dL")
    ax.axvline(df["glucose"].median(), color="black", linewidth=1.3, linestyle=":", label=f"Mediana: {df['glucose'].median():.0f} mg/dL")
    ax.set_xlabel("Glucosa (mg/dL)"); ax.set_ylabel("N.º de lecturas")
    ax.set_title("Distribución de valores de glucosa (histograma)")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25, linewidth=0.5, axis="y")
    fig.tight_layout()
    p = os.path.join(outdir, "03_histograma.png"); fig.savefig(p); plt.close(fig)
    paths["histograma"] = p

    # 4. Distribución por rangos
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=200)
    g = df["glucose"]
    labels = ["Muy alto\n(>250)", "Alto\n(181-250)", "Rango objetivo\n(70-180)", "Bajo\n(54-69)", "Muy bajo\n(<54)"]
    vals = [100*(g > VERY_HIGH).mean(), 100*((g > HIGH) & (g <= VERY_HIGH)).mean(),
            100*((g >= LOW) & (g <= HIGH)).mean(), 100*((g >= VERY_LOW) & (g < LOW)).mean(),
            100*(g < VERY_LOW).mean()]
    colors4 = [C_VHIGH, C_HIGH, C_TIR, C_LOW, C_VLOW]
    left = 0
    for lab, v, c in zip(labels, vals, colors4):
        ax.barh(0, v, left=left, color=c, edgecolor="white", height=0.5)
        if v > 2:
            ax.text(left + v/2, 0, f"{v:.1f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        left += v
    ax.set_xlim(0, 100); ax.set_yticks([]); ax.set_xlabel("% del tiempo")
    ax.set_title("Distribución del tiempo por rango de glucosa (Tiempo en Rango)")
    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=l.replace(chr(10), " ")) for l, c in zip(labels, colors4)]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=5, frameon=False, fontsize=8)
    fig.tight_layout()
    p = os.path.join(outdir, "04_distribucion_rangos.png"); fig.savefig(p); plt.close(fig)
    paths["rangos"] = p

    # 5. Boxplot horario
    fig, ax = plt.subplots(figsize=(12, 5), dpi=200)
    data_by_hour = [df.loc[df["hour"] == h, "glucose"].values for h in range(24)]
    bp = ax.boxplot(data_by_hour, positions=range(24), widths=0.6, patch_artist=True, showfliers=False,
                     medianprops=dict(color="black", linewidth=1.3))
    for patch in bp["boxes"]:
        patch.set_facecolor(C_LINE); patch.set_alpha(0.35); patch.set_edgecolor(C_LINE)
    ax.axhspan(LOW, HIGH, color=C_TIR, alpha=0.08, zorder=0)
    ax.axhline(LOW, color=C_LOW, linestyle="--", linewidth=0.8)
    ax.axhline(HIGH, color=C_HIGH, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Hora del día"); ax.set_ylabel("Glucosa (mg/dL)")
    ax.set_title("Distribución horaria de glucosa (boxplot por hora)")
    ax.set_xticks(range(24)); ax.grid(alpha=0.25, linewidth=0.5, axis="y")
    fig.tight_layout()
    p = os.path.join(outdir, "05_boxplot_horario.png"); fig.savefig(p); plt.close(fig)
    paths["boxplot"] = p

    # 6. Heatmap día-hora
    pivot = df.pivot_table(index="date", columns="hour", values="glucose", aggfunc="mean").sort_index()
    fig_h = max(4, min(20, 0.4 * len(pivot.index) + 2))
    fig, ax = plt.subplots(figsize=(12, fig_h), dpi=200)
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn_r", vmin=VERY_LOW, vmax=VERY_HIGH)
    ax.set_xticks(range(24)); ax.set_xticklabels(range(24))
    step = max(1, len(pivot.index) // 40)
    ax.set_yticks(range(0, len(pivot.index), step))
    ax.set_yticklabels([d.strftime("%d-%b") for d in pivot.index[::step]])
    ax.set_xlabel("Hora del día"); ax.set_ylabel("Fecha")
    ax.set_title("Mapa de calor glucosa promedio por día y hora")
    fig.colorbar(im, ax=ax, label="Glucosa media (mg/dL)")
    fig.tight_layout()
    p = os.path.join(outdir, "06_heatmap.png"); fig.savefig(p); plt.close(fig)
    paths["heatmap"] = p

    # 7. Promedio por hora
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=200)
    ax.axhspan(LOW, HIGH, color=C_TIR, alpha=0.10, zorder=0)
    ax.plot(hourly.index, hourly["mean"], marker="o", markersize=4, color=C_LINE, linewidth=2)
    ax.fill_between(hourly.index, hourly["mean"] - hourly["std"], hourly["mean"] + hourly["std"], color=C_LINE, alpha=0.15)
    ax.axhline(LOW, color=C_LOW, linestyle="--", linewidth=0.8)
    ax.axhline(HIGH, color=C_HIGH, linestyle="--", linewidth=0.8)
    ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hora del día"); ax.set_ylabel("Glucosa media ± DE (mg/dL)")
    ax.set_title("Glucosa media por hora del día")
    ax.grid(alpha=0.25, linewidth=0.5)
    fig.tight_layout()
    p = os.path.join(outdir, "07_promedio_hora.png"); fig.savefig(p); plt.close(fig)
    paths["promedio_hora"] = p

    # 8. Variabilidad por hora
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=200)
    colorsv = ["#c62828" if v >= CV_THRESHOLD else ("#fb8c00" if v >= CV_THRESHOLD - 3 else "#2e7d32") for v in hourly["cv"]]
    ax.bar(hourly.index, hourly["cv"], color=colorsv, edgecolor="white")
    ax.axhline(CV_THRESHOLD, color="#c62828", linestyle="--", linewidth=1, label=f"Umbral CV={CV_THRESHOLD:.0f}% (ATTD)")
    ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hora del día"); ax.set_ylabel("Coeficiente de variación (%)")
    ax.set_title("Variabilidad glucémica por hora (CV%)")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.25, linewidth=0.5, axis="y")
    fig.tight_layout()
    p = os.path.join(outdir, "08_variabilidad_hora.png"); fig.savefig(p); plt.close(fig)
    paths["variabilidad_hora"] = p

    return paths


# ============================================================
# 6. TEXTO NARRATIVO DINÁMICO
# ============================================================
def fnum(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def fint(n):
    """Formatea un entero con separador de miles al estilo es-AR (punto)."""
    return f"{n:,}".replace(",", ".")


def describe_variability(cv):
    if cv < 25:
        return "baja"
    elif cv < CV_THRESHOLD:
        return "moderada, dentro del umbral de estabilidad"
    elif cv < CV_THRESHOLD + 10:
        return "moderada a elevada, levemente por encima del umbral de estabilidad"
    else:
        return "elevada"


def build_narrative(core, ranges_summary, seg_stats, hourly, events, complete_days, best, worst, period_label, ndays):
    N = {}
    N["periodo_label"] = period_label
    N["ndays"] = ndays

    N["resumen_intro"] = (
        f"Se analizaron {fint(core['n'])} lecturas de glucosa intersticial histórica (intervalo típico de {fnum(core['interval_minutes'], 2)} minutos) "
        f"correspondientes a {period_label}, con un tiempo activo de sensor del {fnum(core['active_pct'])} % "
        f"dentro de esa ventana."
    )

    cv = core["cv"]
    N["gmi_nota"] = (
        f"El GMI de {fnum(core['gmi'], 2)} % se calcula sobre una ventana de {fnum(core['span_days'],1)} días. "
        f"Cuanto más corta la ventana respecto de los 14-90 días habitualmente recomendados para estimar HbA1c, "
        f"más aproximada (y no equivalente directa) debe considerarse esta estimación. "
        f"El CV de {fnum(cv)} % indica una variabilidad glucémica {describe_variability(cv)} "
        f"(umbral de referencia ATTD: {CV_THRESHOLD:.0f} %)."
    )

    tir, tar, tbr = ranges_summary["tir"], ranges_summary["tar"], ranges_summary["tbr"]
    N["tir_parrafo"] = (
        f"El tiempo en rango objetivo (70-180 mg/dL) fue de {fnum(tir)} %"
        + (", superando el umbral de referencia habitual de 70 %" if tir >= 70 else
           ", por debajo del umbral de referencia habitual de 70 %")
        + f". El tiempo bajo rango combinado (<70 mg/dL) fue de {fnum(tbr)} %"
        + (", cifra que excede el objetivo de seguridad recomendado (<4 % del tiempo)" if tbr > 4 else
           ", dentro del objetivo de seguridad recomendado (<4 % del tiempo)")
        + f". El tiempo por encima de 180 mg/dL fue de {fnum(tar)} %."
    )

    strict_tir = ranges_summary["strict_tir"]
    N["tir_estricto_parrafo"] = (
        f"Bajo un criterio más estricto (70-140 mg/dL), el tiempo en rango {'desciende' if strict_tir < tir else 'asciende'} "
        f"a {fnum(strict_tir)} %."
        + (f" Esta diferencia entre el {fnum(tir)} % (rango estándar) y el {fnum(strict_tir)} % (rango estricto) "
           f"señala que buena parte del tiempo \"en rango objetivo\" se concentra en la franja alta de 140-180 mg/dL."
           if (tir - strict_tir) > 8 else "")
    )

    N["variabilidad_parrafo"] = (
        f"Con un CV de {fnum(cv)} %, la variabilidad glucémica del período se clasifica como {describe_variability(cv)}. "
        f"La SD de {fnum(core['sd'])} mg/dL sobre una media de {fnum(core['mean'],0)} mg/dL "
        f"{'es compatible con excursiones frecuentes que atraviesan los límites del rango objetivo en ambos sentidos' if cv >= 30 else 'refleja oscilaciones acotadas en torno a la media'}."
    )

    cv_hourly = hourly["cv"].dropna()
    if len(cv_hourly):
        h_min_cv, h_max_cv = cv_hourly.idxmin(), cv_hourly.idxmax()
        N["variabilidad_horaria"] = (
            f"La variabilidad no es homogénea a lo largo del día: los valores de CV horario oscilan entre "
            f"{fnum(cv_hourly.min())} % ({h_min_cv:02d}:00 h) y {fnum(cv_hourly.max())} % ({h_max_cv:02d}:00 h)."
        )
    else:
        N["variabilidad_horaria"] = ""

    # hipo
    hypo = events["hypo"]; hypo_l2 = events["hypo_l2"]
    hyper = events["hyper"]; hyper_l2 = events["hyper_l2"]
    N["n_hipo"], N["n_hipo_l2"] = len(hypo), len(hypo_l2)
    N["n_hiper"], N["n_hiper_l2"] = len(hyper), len(hyper_l2)

    if hypo:
        durs = [e["duration_min"] for e in hypo]
        N["hipo_duracion"] = (
            f"La duración mediana de los episodios de hipoglucemia (<70 mg/dL) fue de {fnum(np.median(durs),0)} minutos "
            f"(media {fnum(np.mean(durs),1)} min), con un máximo de {fnum(max(durs),0)} minutos."
        )
        hrs = collections.Counter(e["hour_start"] for e in hypo)
        top_hrs = sorted(hrs.items(), key=lambda x: -x[1])[:3]
        N["hipo_horario"] = "Los episodios de hipoglucemia se concentran principalmente " + ", ".join(
            f"en torno a las {h:02d}:00 h ({c} episodio{'s' if c>1 else ''})" for h, c in top_hrs
        ) + "."
    else:
        N["hipo_duracion"] = "No se registraron episodios de hipoglucemia (<70 mg/dL) en el período analizado."
        N["hipo_horario"] = ""

    if hyper:
        durs = [e["duration_min"] for e in hyper]
        N["hiper_duracion"] = (
            f"La duración mediana de los episodios de hiperglucemia (>180 mg/dL) fue de {fnum(np.median(durs),0)} minutos "
            f"(media {fnum(np.mean(durs),1)} min), con un máximo de {fnum(max(durs),0)} minutos."
        )
        hrs = collections.Counter(e["hour_start"] for e in hyper)
        top_hrs = sorted(hrs.items(), key=lambda x: -x[1])[:3]
        N["hiper_horario"] = "Los episodios de hiperglucemia se concentran principalmente " + ", ".join(
            f"en torno a las {h:02d}:00 h ({c} episodio{'s' if c>1 else ''})" for h, c in top_hrs
        ) + "."
    else:
        N["hiper_duracion"] = "No se registraron episodios de hiperglucemia (>180 mg/dL) en el período analizado."
        N["hiper_horario"] = ""

    # segmentos: identificar mayor hipo / mayor hiper
    seg_hypo_max = seg_stats["pct_hypo"].idxmax() if seg_stats["pct_hypo"].notna().any() else None
    seg_hyper_max = seg_stats["pct_hyper"].idxmax() if seg_stats["pct_hyper"].notna().any() else None
    N["seg_hypo_max"] = seg_hypo_max
    N["seg_hyper_max"] = seg_hyper_max
    if seg_hypo_max is not None and seg_hyper_max is not None:
        N["segmentos_conclusion"] = (
            f"La franja \"{seg_hypo_max}\" concentra el mayor porcentaje de tiempo en hipoglucemia del día "
            f"({fnum(seg_stats.loc[seg_hypo_max,'pct_hypo'])} %), mientras que la franja \"{seg_hyper_max}\" "
            f"concentra el mayor porcentaje de tiempo en hiperglucemia ({fnum(seg_stats.loc[seg_hyper_max,'pct_hyper'])} %)."
        )
    else:
        N["segmentos_conclusion"] = ""

    # rapid rise/fall
    N["n_rise"] = len(events["rise_groups"])
    N["n_fall"] = len(events["fall_groups"])

    # dias destacados
    if len(best):
        b0 = best.iloc[0]
        N["mejor_dia"] = (
            f"{pd.Timestamp(best.index[0]).strftime('%d/%m/%Y')} fue el día con mejor control del período: "
            f"{fnum(b0['tir'])} % de tiempo en rango, con CV de {fnum(b0['cv'])} %."
        )
    else:
        N["mejor_dia"] = ""
    if len(worst):
        w0 = worst.iloc[0]
        N["peor_dia"] = (
            f"{pd.Timestamp(worst.index[0]).strftime('%d/%m/%Y')} fue el día con menor tiempo en rango del período "
            f"({fnum(w0['tir'])} %), con {fnum(w0['tar'])} % de tiempo en hiperglucemia y {fnum(w0['tbr'])} % en hipoglucemia."
        )
    else:
        N["peor_dia"] = ""

    return N


# ============================================================
# 7. ESTILOS Y HELPERS DE REPORTLAB
# ============================================================
def get_styles():
    ss = getSampleStyleSheet()
    styles = {}
    styles["h1"] = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15, textColor=NAVY,
                                   spaceBefore=18, spaceAfter=8, borderWidth=0)
    styles["h2"] = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12.5, textColor=BLUE,
                                   spaceBefore=12, spaceAfter=6)
    styles["h3"] = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=11, textColor=TEAL,
                                   spaceBefore=8, spaceAfter=4)
    styles["body"] = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9.6, leading=14,
                                     alignment=TA_JUSTIFY, spaceAfter=8)
    styles["bullet"] = ParagraphStyle("bullet", parent=styles["body"], leftIndent=14, spaceAfter=4)
    styles["caption"] = ParagraphStyle("caption", parent=ss["BodyText"], fontSize=8.3, leading=11,
                                        alignment=TA_CENTER, textColor=GREY, italic=True, spaceAfter=12, spaceBefore=3)
    styles["note"] = ParagraphStyle("note", parent=styles["body"], fontSize=8.8, backColor=LIGHTGREY,
                                     borderPadding=6, spaceAfter=10)
    styles["kpi_val"] = ParagraphStyle("kpi_val", parent=ss["BodyText"], fontSize=15, alignment=TA_CENTER,
                                        textColor=NAVY, leading=18)
    styles["kpi_lab"] = ParagraphStyle("kpi_lab", parent=ss["BodyText"], fontSize=7.6, alignment=TA_CENTER,
                                        textColor=GREY, leading=9)
    styles["cover_title"] = ParagraphStyle("cover_title", parent=ss["Title"], fontSize=23, textColor=NAVY,
                                            alignment=TA_CENTER, leading=27)
    styles["cover_sub"] = ParagraphStyle("cover_sub", parent=ss["BodyText"], fontSize=12.5, textColor=BLUE,
                                          alignment=TA_CENTER, spaceAfter=6)
    styles["cover_label"] = ParagraphStyle("cover_label", parent=ss["BodyText"], fontSize=10.5, textColor=GREY,
                                            alignment=TA_CENTER, spaceBefore=10, fontName="Helvetica-Bold")
    styles["cover_value"] = ParagraphStyle("cover_value", parent=ss["BodyText"], fontSize=13, textColor=NAVY,
                                            alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
    styles["cover_small"] = ParagraphStyle("cover_small", parent=ss["BodyText"], fontSize=8.6, textColor=GREY,
                                            alignment=TA_CENTER, italic=True)
    styles["disclaimer"] = ParagraphStyle("disclaimer", parent=styles["cover_small"], textColor=RED)
    styles["toc1"] = ParagraphStyle("toc1", fontSize=10.5, leading=16, textColor=NAVY, fontName="Helvetica-Bold")
    styles["toc2"] = ParagraphStyle("toc2", fontSize=9.5, leading=14, textColor=colors.HexColor("#333333"),
                                     leftIndent=14)
    return styles


def p(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return ListFlowable([ListItem(Paragraph(t, style), leftIndent=10, value="•") for t in items],
                         bulletType="bullet", start="•")


def kpi_row(items, styles):
    """items: list of (value, label)"""
    cell_w = (A4[0] - 3*cm) / len(items)
    row = []
    for val, lab in items:
        row.append([Paragraph(val, styles["kpi_val"]), Paragraph(lab, styles["kpi_lab"])])
    t = Table([[Table([[c[0]], [c[1]]], colWidths=[cell_w-6]) for c in row]], colWidths=[cell_w]*len(items))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHTBLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def data_table(headers, rows, col_widths, styles, small=False):
    fs = 7.6 if small else 8.3
    hdr = [Paragraph(f"<b>{h}</b>", ParagraphStyle("th", fontSize=fs, textColor=colors.white, alignment=TA_CENTER, leading=fs+2)) for h in headers]
    body_rows = []
    for r in rows:
        body_rows.append([Paragraph(str(v), ParagraphStyle("td", fontSize=fs, alignment=TA_CENTER if i > 0 else TA_LEFT, leading=fs+2))
                           for i, v in enumerate(r)])
    t = Table([hdr] + body_rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i in range(1, len(body_rows) + 1):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHTGREY))
    t.setStyle(TableStyle(style_cmds))
    return t


def chart_image(path, max_width, max_height_ratio=0.42):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        iw, ih = im.size
    max_h = A4[1] * max_height_ratio
    w = max_width
    h = w * ih / iw
    if h > max_h:
        h = max_h
        w = h * iw / ih
    return Image(path, width=w, height=h)


# ============================================================
# 8. DOCTEMPLATE CON PORTADA, ENCABEZADO/PIE E ÍNDICE AUTOMÁTICO
# ============================================================
PAGE_W, PAGE_H = A4
MARGIN = 1.6 * cm
CONTENT_W = PAGE_W - 2 * MARGIN


class ReportDocTemplate(BaseDocTemplate):
    """DocTemplate que arma un índice (TOC) real con números de página
    correctos, usando multiBuild, y dibuja encabezado/pie en cada página
    (salvo la portada)."""

    def __init__(self, filename, period_label, **kw):
        super().__init__(filename, pagesize=A4, **kw)
        self.period_label = period_label
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                             topPadding=0, bottomPadding=0)
        content_frame = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2*MARGIN, id="content")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=self._draw_cover_decor),
            PageTemplate(id="Content", frames=[content_frame], onPage=self._draw_header_footer),
        ])

    def _draw_cover_decor(self, canv, doc):
        pass  # la portada ya trae todo su contenido como flowables

    def _draw_header_footer(self, canv, doc):
        canv.saveState()
        # encabezado
        canv.setStrokeColor(colors.HexColor("#CCCCCC"))
        canv.setLineWidth(0.6)
        canv.line(MARGIN, PAGE_H - MARGIN + 10, PAGE_W - MARGIN, PAGE_H - MARGIN + 10)
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, PAGE_H - MARGIN + 14, "Informe de Monitoreo Continuo de Glucosa · FreeStyle Libre")
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 14, self.period_label)
        # pie
        canv.line(MARGIN, MARGIN - 12, PAGE_W - MARGIN, MARGIN - 12)
        canv.setFont("Helvetica", 7)
        canv.setFillColor(colors.HexColor("#8A8A8A"))
        canv.drawCentredString(
            PAGE_W / 2, MARGIN - 24,
            f"Documento generado automáticamente — material de apoyo para consulta médica, no constituye diagnóstico. Página {canv.getPageNumber()}"
        )
        canv.restoreState()

    def afterFlowable(self, flowable):
        """Registra encabezados H1/H2 en el índice (TOC) con su número de página."""
        if hasattr(flowable, "style") and flowable.style is not None:
            style_name = getattr(flowable.style, "name", "")
            text = flowable.getPlainText() if hasattr(flowable, "getPlainText") else ""
            if style_name == "h1":
                self.notify("TOCEntry", (0, text, self.page))
                key = f"h1-{self.page}-{text}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=0, closed=False)
            elif style_name == "h2":
                self.notify("TOCEntry", (1, text, self.page))
                key = f"h2-{self.page}-{text}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=1, closed=True)


def h1_flow(text, styles):
    return Paragraph(text, styles["h1"])


def h2_flow(text, styles):
    return Paragraph(text, styles["h2"])


# ============================================================
# 9. ARMADO COMPLETO DEL INFORME (PDF)
# ============================================================
def build_pdf(df, output_path, period_label, generated_on, days_arg):
    core = compute_core_stats(df)
    standard, strict, ranges_summary = compute_ranges(df, core)
    seg_stats = compute_segment_stats(df)
    hourly = compute_hourly_stats(df)
    daily = compute_daily_stats(df)
    complete_days, best, worst = best_worst_days(daily)
    events = compute_events(df)

    tmpdir = tempfile.mkdtemp(prefix="cgm_charts_")
    charts = generate_charts(df, hourly, daily, tmpdir, period_label)

    ndays_calendar = df["date"].nunique()
    N = build_narrative(core, ranges_summary, seg_stats, hourly, events, complete_days, best, worst,
                         period_label, ndays_calendar)

    styles = get_styles()
    story = []

    # ---------- PORTADA ----------
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("INFORME DE MONITOREO CONTINUO DE GLUCOSA", styles["cover_title"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Análisis de glucosa · Archivos Stream / LibreView", styles["cover_sub"]))
    story.append(Spacer(1, 0.6*cm))
    line_tbl = Table([[""]], colWidths=[10*cm])
    line_tbl.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.2, BLUE)]))
    story.append(KeepTogether([line_tbl]))
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("Período analizado", styles["cover_label"]))
    story.append(Paragraph(period_label, styles["cover_value"]))
    story.append(Paragraph("Cantidad de días de registro", styles["cover_label"]))
    story.append(Paragraph(f"{fnum(core['span_days'],1)} días · {ndays_calendar} fechas calendario", styles["cover_value"]))
    story.append(Paragraph("Fecha de generación del informe", styles["cover_label"]))
    story.append(Paragraph(generated_on, styles["cover_value"]))
    story.append(Spacer(1, 1.2*cm))
    story.append(Paragraph(f"Registros analizados: {fint(core['n'])} lecturas (intervalo típico: {fnum(core['interval_minutes'], 2)} min)", styles["cover_small"]))
    story.append(Paragraph("Documento generado automáticamente a partir del archivo de glucosa proporcionado.", styles["cover_small"]))
    story.append(Paragraph("No constituye diagnóstico ni indicación terapéutica. Para uso exclusivo como material "
                            "de apoyo en consulta con profesional médico.", styles["disclaimer"]))

    story.append(NextPageTemplate("Content"))
    story.append(PageBreak())

    # ---------- INDICE ----------
    story.append(h1_flow("Índice", styles))
    toc = TableOfContents()
    toc.levelStyles = [styles["toc1"], styles["toc2"]]
    story.append(toc)
    story.append(PageBreak())

    # ---------- 1. RESUMEN EJECUTIVO ----------
    story.append(h1_flow("1. Resumen ejecutivo", styles))
    story.append(p(N["resumen_intro"], styles["body"]))
    story.append(kpi_row([
        (f"{fnum(core['mean'],0)} mg/dL", "Glucosa media"),
        (f"{fnum(core['gmi'],2)} %", "GMI (HbA1c estimada)"),
        (f"{fnum(core['sd'],1)} mg/dL", "Desviación estándar"),
        (f"{fnum(core['cv'],1)} %", "Coeficiente de variación"),
    ], styles))
    story.append(Spacer(1, 6))
    story.append(kpi_row([
        (f"{fnum(core['active_pct'],0)} %", "Tiempo activo del sensor"),
        (fint(core["n"]), "Mediciones analizadas"),
        (f"{fnum(ranges_summary['tir'],1)} %", "Tiempo en rango (70-180)"),
        (f"{fnum(ranges_summary['tbr'],1)} %", "Tiempo bajo rango (<70)"),
    ], styles))
    story.append(Spacer(1, 10))

    story.append(h2_flow("1.1 Significado de las métricas principales", styles))
    story.append(bullets([
        "<b>Glucosa media:</b> promedio aritmético de todas las lecturas del período.",
        "<b>GMI (Glucose Management Indicator):</b> estimación de HbA1c derivada de la glucosa media de sensor "
        "(GMI % = 3,31 + 0,02392 × glucosa media en mg/dL). No reemplaza a la HbA1c de laboratorio.",
        "<b>Desviación estándar (SD):</b> dispersión absoluta de los valores de glucosa alrededor de la media, en mg/dL.",
        "<b>Coeficiente de variación (CV):</b> SD relativizada a la media (%). Métrica de variabilidad recomendada "
        f"por el consenso ATTD, con umbral de variabilidad estable en CV &lt; {CV_THRESHOLD:.0f} %.",
        "<b>Tiempo activo del sensor:</b> porcentaje del período con datos válidos; el consenso ATTD recomienda "
        "un mínimo de 70 % de tiempo activo.",
    ], styles["bullet"]))
    story.append(p(N["gmi_nota"], styles["note"]))

    # ---------- 2. TIEMPO EN RANGO ----------
    story.append(h1_flow("2. Tiempo en rango (TIR)", styles))
    story.append(p("El \"tiempo en rango\" cuantifica la proporción de tiempo que la glucosa permaneció dentro de "
                    "distintas bandas objetivo, según el consenso ATTD/ADA para monitoreo continuo.", styles["body"]))
    story.append(h2_flow("2.1 Objetivo estándar", styles))
    story.append(data_table(["Rango de glucosa", "% del tiempo", "Tiempo equiv.", "N.º lecturas"], standard,
                             [7.2*cm, 3.2*cm, 3.6*cm, 3.2*cm], styles))
    story.append(chart_image(charts["rangos"], CONTENT_W))
    story.append(p("Figura 1. Distribución del tiempo en rango.", styles["caption"]))
    story.append(p(N["tir_parrafo"], styles["body"]))

    story.append(h2_flow("2.2 Objetivo estricto (70-140 mg/dL)", styles))
    story.append(data_table(["Rango", "% del tiempo", "Tiempo equivalente"], strict,
                             [6*cm, 4*cm, 7.2*cm], styles))
    story.append(p(N["tir_estricto_parrafo"], styles["body"]))

    # ---------- 3. VARIABILIDAD ----------
    story.append(h1_flow("3. Variabilidad glucémica", styles))
    story.append(p("La variabilidad glucémica describe la magnitud y frecuencia de las oscilaciones de glucosa, "
                    "independientemente del nivel medio.", styles["body"]))
    story.append(data_table(
        ["Métrica", "Valor", "Referencia (ATTD)"],
        [
            ["Desviación estándar (SD)", f"{fnum(core['sd'])} mg/dL", "Se interpreta junto al CV"],
            ["Coeficiente de variación (CV)", f"{fnum(core['cv'])} %", f"< {CV_THRESHOLD:.0f}% estable · ≥ {CV_THRESHOLD:.0f}% inestable"],
            ["Rango intercuartílico (IQR)", f"{fnum(core['iqr'],0)} mg/dL", "P25-P75"],
            ["Rango total", f"{fnum(core['range'],0)} mg/dL", f"Mín {fnum(core['min'],0)} – Máx {fnum(core['max'],0)}"],
        ], [5.5*cm, 5.5*cm, 6.2*cm], styles))
    story.append(p(N["variabilidad_parrafo"], styles["body"]))
    story.append(chart_image(charts["boxplot"], CONTENT_W))
    story.append(p("Figura 2. Distribución horaria de glucosa (boxplot por hora).", styles["caption"]))
    story.append(p(N["variabilidad_horaria"], styles["body"]))

    # ---------- 4. HIPOGLUCEMIAS ----------
    story.append(h1_flow("4. Hipoglucemias", styles))
    story.append(p("Se definieron episodios de hipoglucemia como intervalos continuos con glucosa &lt;70 mg/dL, "
                    "agrupando lecturas consecutivas, sin unir huecos mayores a dos intervalos típicos (máximo 15 minutos).", styles["body"]))
    if events["hypo"]:
        story.append(kpi_row([
            (str(N["n_hipo"]), "Episodios <70 mg/dL"),
            (str(N["n_hipo_l2"]), "Episodios <54 mg/dL"),
            (f"{fnum(np.median([e['duration_min'] for e in events['hypo']]),0)} min", "Duración mediana"),
            (f"{fnum(max(e['duration_min'] for e in events['hypo']),0)} min", "Más prolongado"),
        ], styles))
    story.append(p(N["hipo_duracion"], styles["body"]))
    story.append(p(N["hipo_horario"], styles["body"]))
    long_hypo = sorted([e for e in events["hypo"] if e["duration_min"] >= 60], key=lambda x: -x["duration_min"])
    if long_hypo:
        story.append(h3_flow("Hipoglucemias prolongadas (≥ 60 min)", styles))
        rows = [[e["start"].strftime("%d/%m/%Y %H:%M"), f"{fnum(e['duration_min'],0)} min", f"{fnum(e['nadir'],0)} mg/dL"]
                for e in long_hypo[:12]]
        story.append(data_table(["Fecha y hora de inicio", "Duración", "Nadir"], rows, [6*cm, 4*cm, 7.2*cm], styles))

    # ---------- 5. HIPERGLUCEMIAS ----------
    story.append(h1_flow("5. Hiperglucemias", styles))
    story.append(p("Se definieron episodios de hiperglucemia como intervalos continuos con glucosa &gt;180 mg/dL, "
                    "con el mismo criterio de agrupación.", styles["body"]))
    if events["hyper"]:
        story.append(kpi_row([
            (str(N["n_hiper"]), "Episodios >180 mg/dL"),
            (str(N["n_hiper_l2"]), "Episodios >250 mg/dL"),
            (f"{fnum(np.median([e['duration_min'] for e in events['hyper']]),0)} min", "Duración mediana"),
            (f"{fnum(max(e['duration_min'] for e in events['hyper']),0)} min", "Más prolongado"),
        ], styles))
    story.append(p(N["hiper_duracion"], styles["body"]))
    story.append(p(N["hiper_horario"], styles["body"]))
    long_hyper = sorted([e for e in events["hyper"] if e["duration_min"] >= 120], key=lambda x: -x["duration_min"])
    if long_hyper:
        story.append(h3_flow("Hiperglucemias prolongadas (≥ 120 min)", styles))
        rows = [[e["start"].strftime("%d/%m/%Y %H:%M"), f"{fnum(e['duration_min'],0)} min", f"{fnum(e['peak'],0)} mg/dL"]
                for e in long_hyper[:12]]
        story.append(data_table(["Fecha y hora de inicio", "Duración", "Pico"], rows, [6*cm, 4*cm, 7.2*cm], styles))

    # ---------- 6. ANALISIS POR HORARIO ----------
    story.append(h1_flow("6. Análisis por horario", styles))
    story.append(chart_image(charts["agp"], CONTENT_W))
    story.append(p("Figura 3. Perfil de Glucosa Ambulatorio (AGP).", styles["caption"]))
    seg_rows = []
    for name, *_ in SEGMENTS_DEF:
        if name in seg_stats.index:
            r = seg_stats.loc[name]
            seg_rows.append([name, f"{fnum(r['mean'],0)} mg/dL", f"{fnum(r['cv'],1)} %",
                              f"{fnum(r['pct_tir'],1)} %", f"{fnum(r['pct_hypo'],1)} %", f"{fnum(r['pct_hyper'],1)} %"])
    story.append(data_table(["Franja horaria", "Media", "CV", "% en rango", "% hipo", "% hiper"], seg_rows,
                             [4.6*cm, 2.4*cm, 2.0*cm, 2.6*cm, 2.2*cm, 2.2*cm], styles, small=True))
    story.append(p(N["segmentos_conclusion"], styles["body"]))
    story.append(chart_image(charts["promedio_hora"], CONTENT_W))
    story.append(p("Figura 4. Glucosa media ± desviación estándar por hora del día.", styles["caption"]))
    story.append(chart_image(charts["variabilidad_hora"], CONTENT_W))
    story.append(p("Figura 5. Coeficiente de variación (%) por hora del día.", styles["caption"]))

    # ---------- 7. PERFIL DIARIO ----------
    story.append(h1_flow("7. Perfil diario", styles))
    story.append(chart_image(charts["curva"], CONTENT_W))
    story.append(p("Figura 6. Curva completa de glucosa vs. tiempo.", styles["caption"]))

    # ---------- 8. DIAS DESTACADOS ----------
    story.append(h1_flow("8. Días destacados", styles))
    if len(best):
        story.append(h2_flow("8.1 Mejores días (mayor tiempo en rango)", styles))
        rows = [[pd.Timestamp(idx).strftime("%d/%m/%Y"), f"{fnum(r['tir'])} %", f"{fnum(r['tbr'])} %",
                 f"{fnum(r['tar'])} %", f"{fnum(r['mean'],0)} mg/dL", f"{fnum(r['cv'],1)} %"]
                for idx, r in best.iterrows()]
        story.append(data_table(["Fecha", "TIR", "TBR", "TAR", "Media", "CV"], rows,
                                 [3*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.6*cm, 2*cm], styles))
        story.append(p(N["mejor_dia"], styles["body"]))
    if len(worst):
        story.append(h2_flow("8.2 Peores días (menor tiempo en rango)", styles))
        rows = [[pd.Timestamp(idx).strftime("%d/%m/%Y"), f"{fnum(r['tir'])} %", f"{fnum(r['tbr'])} %",
                 f"{fnum(r['tar'])} %", f"{fnum(r['mean'],0)} mg/dL", f"{fnum(r['cv'],1)} %"]
                for idx, r in worst.iterrows()]
        story.append(data_table(["Fecha", "TIR", "TBR", "TAR", "Media", "CV"], rows,
                                 [3*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.6*cm, 2*cm], styles))
        story.append(p(N["peor_dia"], styles["body"]))

    # ---------- 9. EVENTOS LLAMATIVOS ----------
    story.append(h1_flow("9. Eventos llamativos", styles))
    ev_items = []
    for e in long_hyper[:5]:
        ev_items.append(f"Hiperglucemia prolongada: {e['start'].strftime('%d/%m/%Y %H:%M')} h → "
                         f"{fnum(e['duration_min'],0)} min por encima de 180 mg/dL, pico de {fnum(e['peak'],0)} mg/dL.")
    for e in long_hypo[:5]:
        ev_items.append(f"Hipoglucemia prolongada: {e['start'].strftime('%d/%m/%Y %H:%M')} h → "
                         f"{fnum(e['duration_min'],0)} min por debajo de 70 mg/dL, nadir de {fnum(e['nadir'],0)} mg/dL.")
    if events["fall_groups"]:
        s, en = events["fall_groups"][0]
        ev_items.append(f"Descenso rápido: {s['ts'].strftime('%d/%m/%Y %H:%M')} h → caída de {fnum(s['glucose'],0)} "
                         f"a {fnum(en['glucose'],0)} mg/dL en ~15 minutos.")
    if events["rise_groups"]:
        s, en = events["rise_groups"][0]
        ev_items.append(f"Ascenso rápido: {s['ts'].strftime('%d/%m/%Y %H:%M')} h → subida de {fnum(s['glucose'],0)} "
                         f"a {fnum(en['glucose'],0)} mg/dL en ~15 minutos.")
    else:
        ev_items.append("No se identificaron ascensos de glucosa ≥70 mg/dL en una ventana de 15 minutos durante el período.")
    if ev_items:
        story.append(bullets(ev_items, styles["bullet"]))
    else:
        story.append(p("No se detectaron eventos de magnitud destacable en el período analizado.", styles["body"]))

    # ---------- 10. ESTADISTICAS ADICIONALES ----------
    story.append(h1_flow("10. Estadísticas adicionales", styles))
    stat_rows = [
        ["Mínimo", f"{fnum(core['min'],0)} mg/dL"], ["Percentil 10", f"{fnum(core['p10'],0)} mg/dL"],
        ["Percentil 25", f"{fnum(core['p25'],0)} mg/dL"], ["Mediana (P50)", f"{fnum(core['p50'],0)} mg/dL"],
        ["Percentil 75", f"{fnum(core['p75'],0)} mg/dL"], ["Percentil 90", f"{fnum(core['p90'],0)} mg/dL"],
        ["Máximo", f"{fnum(core['max'],0)} mg/dL"], ["Rango", f"{fnum(core['range'],0)} mg/dL"],
        ["IQR", f"{fnum(core['iqr'],0)} mg/dL"],
    ]
    story.append(data_table(["Estadístico", "Valor"], stat_rows, [8*cm, 8.2*cm], styles))
    story.append(chart_image(charts["histograma"], CONTENT_W))
    story.append(p("Figura 7. Histograma de valores de glucosa.", styles["caption"]))
    story.append(chart_image(charts["heatmap"], CONTENT_W, max_height_ratio=0.55))
    story.append(p("Figura 8. Mapa de calor glucosa media por día y hora.", styles["caption"]))

    # ---------- 11. TABLA DE DATOS ----------
    story.append(h1_flow("11. Tabla de datos", styles))
    story.append(p(f"El registro completo contiene {fint(core['n'])} lecturas individuales; se entrega el detalle "
                    f"completo (Fecha, Hora, Glucosa, Tipo de registro) como archivo anexo en Excel/CSV. "
                    f"A continuación, el resumen diario.", styles["body"]))
    daily_rows = []
    for idx, r in daily.iterrows():
        daily_rows.append([pd.Timestamp(idx).strftime("%d/%m/%Y"), int(r["count"]), f"{fnum(r['mean'],0)}",
                            f"{fnum(r['std'],1)}", f"{fnum(r['cv'],1)}%", f"{fnum(r['tir'],1)}%",
                            f"{fnum(r['tbr'],1)}%", f"{fnum(r['tar'],1)}%"])
    story.append(data_table(["Fecha", "N. lect.", "Media", "SD", "CV", "TIR", "TBR", "TAR"], daily_rows,
                             [2.4*cm, 1.7*cm, 1.8*cm, 1.6*cm, 1.8*cm, 1.9*cm, 1.9*cm, 1.9*cm], styles, small=True))

    # ---------- 12. CONCLUSIONES ----------
    story.append(h1_flow("12. Conclusiones", styles))
    story.append(p("Resumen descriptivo, sin indicaciones terapéuticas, de los puntos a discutir en consulta.", styles["body"]))
    story.append(h2_flow("12.1 Aspectos positivos", styles))
    pos = []
    if ranges_summary["tir"] >= 70:
        pos.append(f"El tiempo en rango estándar fue de {fnum(ranges_summary['tir'])} %, por encima del umbral de referencia habitual de 70 %.")
    if core["active_pct"] >= 90:
        pos.append(f"El tiempo activo del sensor fue del {fnum(core['active_pct'],0)} %, lo que otorga alta confiabilidad a las métricas.")
    if len(best):
        pos.append(N["mejor_dia"])
    if not pos:
        pos.append("Ver detalle de métricas en las secciones anteriores.")
    story.append(bullets(pos, styles["bullet"]))

    story.append(h2_flow("12.2 Aspectos a revisar", styles))
    rev = []
    if ranges_summary["tbr"] > 4:
        rev.append(f"El tiempo bajo rango (&lt;70 mg/dL) fue de {fnum(ranges_summary['tbr'])} %, por encima del objetivo de seguridad de &lt;4 %.")
    if core["cv"] >= CV_THRESHOLD:
        rev.append(f"El coeficiente de variación ({fnum(core['cv'])} %) se ubica en o por encima del umbral de {CV_THRESHOLD:.0f} % del consenso ATTD.")
    if long_hypo or long_hyper:
        rev.append(f"Se identificaron {len(long_hypo)} episodios de hipoglucemia ≥60 min y {len(long_hyper)} de hiperglucemia ≥120 min.")
    if len(worst):
        rev.append(N["peor_dia"])
    if not rev:
        rev.append("No se identificaron aspectos de alarma relevantes más allá de lo descripto en las secciones anteriores.")
    story.append(bullets(rev, styles["bullet"]))

    story.append(h2_flow("12.3 Patrones que podrían discutirse con la diabetóloga", styles))
    pat = [N["segmentos_conclusion"]] if N["segmentos_conclusion"] else []
    pat.append(N["variabilidad_horaria"])
    if (ranges_summary["tir"] - ranges_summary["strict_tir"]) > 8:
        pat.append(f"Contraste entre el tiempo en rango estándar ({fnum(ranges_summary['tir'])} %) y estricto "
                    f"({fnum(ranges_summary['strict_tir'])} %): buena parte del tiempo \"en rango\" se concentra en 140-180 mg/dL.")
    pat = [x for x in pat if x]
    if pat:
        story.append(bullets(pat, styles["bullet"]))

    story.append(h2_flow("12.4 Preguntas sugeridas para la consulta", styles))
    q = []
    if N["seg_hypo_max"]:
        q.append(f"¿A qué podría deberse la concentración de hipoglucemias en la franja \"{N['seg_hypo_max']}\"?")
    if N["seg_hyper_max"]:
        q.append(f"¿El patrón de hiperglucemia en la franja \"{N['seg_hyper_max']}\" corresponde a algo esperable según el esquema actual?")
    q.append(f"¿El tiempo bajo rango ({fnum(ranges_summary['tbr'])} %) y muy bajo ({fnum(ranges_summary['tbr2'])} %) requieren algún ajuste de seguimiento?")
    q.append("¿Cómo interpretar la diferencia de variabilidad entre los mejores y los peores días del período?")
    story.append(bullets(q, styles["bullet"]))

    # ---------- ANEXO TECNICO ----------
    story.append(PageBreak())
    story.append(Paragraph("ANEXO TÉCNICO", ParagraphStyle("annex_title", parent=styles["cover_title"], fontSize=18)))
    story.append(Paragraph("Metodología, definiciones y limitaciones del análisis", styles["cover_sub"]))
    story.append(Spacer(1, 10))

    story.append(h1_flow("A.1 Metodología de cálculo", styles))
    story.append(bullets([
        f"Se procesaron lecturas en mg/dL; intervalo típico detectado: {fnum(core['interval_minutes'],2)} minutos.",
        f"Media, SD y percentiles se calcularon sobre el total de lecturas válidas del período (n = {fint(core['n'])}).",
        "El coeficiente de variación se calculó como CV (%) = (SD / media) × 100.",
        "El GMI se calculó con la fórmula de Bergenstal et al. (2018): GMI (%) = 3,31 + 0,02392 × [glucosa media en mg/dL].",
        "El tiempo activo del sensor se calculó como (lecturas válidas / lecturas esperadas según el intervalo mediano detectado) × 100.",
        "Los episodios de hipo/hiperglucemia se definieron agrupando lecturas consecutivas que cruzan el umbral, "
        "sin unir lecturas normales intermedias ni huecos mayores a dos intervalos típicos (máximo 15 minutos).",
        "Los ascensos/descensos rápidos se calcularon como diferencia de glucosa entre una lectura y la registrada "
        "aproximadamente 15 minutos antes (tolerancia máxima de un minuto), marcando eventos con diferencia ≥70 mg/dL en valor absoluto.",
        "Las franjas horarias se definieron por hora del reloj del dispositivo, agregando todas las lecturas del "
        "período correspondientes a cada franja, sin distinguir fecha calendario.",
        "Los \"días destacados\" se calcularon solo sobre días con registro completo (al menos 97,22% de las lecturas diarias esperadas según la frecuencia detectada).",
    ], styles["bullet"]))

    story.append(h1_flow("A.2 Definición de métricas utilizadas", styles))
    defs = [
        ("TIR — Time in Range", "Porcentaje de lecturas dentro del rango objetivo (habitualmente 70-180 mg/dL)."),
        ("TAR — Time Above Range", "Porcentaje de tiempo por encima del límite superior del rango objetivo (subdividido en nivel 1: 181-250 y nivel 2: >250 mg/dL)."),
        ("TBR — Time Below Range", "Porcentaje de tiempo por debajo del límite inferior del rango objetivo (nivel 1: 54-69, nivel 2: <54 mg/dL)."),
        ("GMI — Glucose Management Indicator", "Estimación de HbA1c a partir de la glucosa media de sensor, derivada del estudio ADAG."),
        ("SD — Desviación Estándar", "Medida de dispersión absoluta de los valores de glucosa respecto de su media, en mg/dL."),
        ("CV — Coeficiente de Variación", "Medida de dispersión relativa (SD/media, en %), métrica de variabilidad priorizada por el consenso ATTD."),
    ]
    for name, d in defs:
        story.append(h3_flow(name, styles))
        story.append(p(d, styles["body"]))

    story.append(h1_flow("A.3 Limitaciones de la interpretación", styles))
    story.append(bullets([
        f"El período analizado ({fnum(core['span_days'],0)} días) puede ser más corto que los 14-90 días "
        "recomendados para algunas métricas (en particular el GMI como aproximación de HbA1c).",
        "Este informe no incorpora datos de insulina, alimentación ni actividad física salvo que estén presentes "
        "en el CSV de origen, por lo que no es posible establecer relaciones causales.",
        "La definición de \"episodio\" mediante agrupación con tolerancia de 15 minutos es una convención "
        "metodológica; otros criterios podrían generar recuentos de episodios distintos.",
        "Los datos provienen de glucosa intersticial (sensor), que puede diferir de la glucosa capilar/plasmática, "
        "especialmente durante cambios rápidos.",
        "Este documento fue generado mediante procesamiento automatizado y no constituye un diagnóstico médico "
        "ni una indicación de tratamiento.",
    ], styles["bullet"]))

    story.append(h1_flow("A.4 Referencias a recomendaciones internacionales", styles))
    story.append(bullets([
        "Battelino T, Danne T, Bergenstal RM, et al. \"Clinical Targets for CGM Data Interpretation: International "
        "Consensus on Time in Range.\" Diabetes Care, 2019.",
        "Danne T, Nimri R, Battelino T, et al. \"International Consensus on Use of Continuous Glucose Monitoring.\" "
        "Diabetes Care, 2017.",
        "Bergenstal RM, et al. \"Glucose Management Indicator (GMI): A New Term for Estimating A1C From CGM.\" "
        "Diabetes Care, 2018.",
        "American Diabetes Association. \"Standards of Care in Diabetes\" (sección de monitoreo continuo de glucosa), edición vigente.",
    ], styles["bullet"]))

    doc = ReportDocTemplate(output_path, period_label)
    doc.multiBuild(story)

    shutil.rmtree(tmpdir, ignore_errors=True)
    return output_path


def h3_flow(text, styles):
    return Paragraph(text, styles["h3"])


# ============================================================
# 10. CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Genera un informe clínico en PDF a partir de un CSV exportado de LibreView."
    )
    parser.add_argument("csv_path", help="Ruta al CSV exportado de LibreView")
    parser.add_argument("--days", type=int, default=15,
                         help="Cantidad de días (contados hacia atrás desde el último registro) a incluir en el análisis. "
                              "Usar 0 para incluir todo el archivo. Default: 15")
    parser.add_argument("--output", default=None, help="Ruta del PDF de salida (default: informe_cgm.pdf)")
    args = parser.parse_args()

    days = None if args.days == 0 else args.days

    print(f"Cargando datos de: {args.csv_path}")
    df = load_data(args.csv_path, days=days)

    first_ts, last_ts = df["ts"].min(), df["ts"].max()
    period_label = f"{first_ts.strftime('%d/%m/%Y')} – {last_ts.strftime('%d/%m/%Y')}"
    generated_on = datetime.now().strftime("%d/%m/%Y")

    output_path = args.output or "informe_cgm.pdf"

    print(f"Período: {period_label}  ·  {fint(len(df))} lecturas")
    print("Generando gráficos y armando PDF...")
    build_pdf(df, output_path, period_label, generated_on, args.days)
    print(f"Listo. Informe generado en: {output_path}")


if __name__ == "__main__":
    main()

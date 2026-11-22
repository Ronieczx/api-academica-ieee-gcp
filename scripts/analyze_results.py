"""
Analisis estadistico reproducible desde los CSV crudos de k6 (Clases 7 y 8).
- Lee todos los archivos datos/raw_<stage>_<batch_size>.csv
- Descarta exactamente las primeras 5 iteraciones de calentamiento por archivo
- Verifica n=30 corridas validas por condicion
- Calcula Mediana (p50), p95, p99, IQR, reduccion vs M0 (ms y %)
- Ejecuta prueba U de Mann-Whitney (no parametrica), Delta de Cliff
  e IC 95% por bootstrap (10 000 remuestreos, semilla fija)
- Genera figuras IEEE (caja y bigotes con puntos, curva de escalado y
  diagnostico por orden de corrida) y tabla LaTeX/Markdown lista para el articulo.
"""
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

WARMUP_DISCARD = 5
EXPECTED_MEASURED = 30
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 2026
THRESHOLD_MS = 1000.0
STAGES_ORDER = ["m0", "m1", "m2", "m3"]
STAGE_LABELS = {
    "m0": "M0 (Base)",
    "m1": "M1 (Lote sin N+1)",
    "m2": "M2 (Indice + Sargable)",
    "m3": "M3 (Cache en memoria)",
}


def parse_k6_csv(csv_path: Path, metric_name: str = "tiempo_servidor") -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    sub = df[df["metric_name"] == metric_name].copy()
    if sub.empty:
        raise ValueError(f"No se encontro la metrica '{metric_name}' en {csv_path}")

    sub["timestamp"] = pd.to_numeric(sub["timestamp"], errors="coerce")
    sub["metric_value"] = pd.to_numeric(sub["metric_value"], errors="coerce")
    sub = sub.dropna(subset=["timestamp", "metric_value"]).sort_values("timestamp", kind="mergesort").reset_index(drop=True)
    sub["run_index"] = np.arange(1, len(sub) + 1)
    sub["is_warmup"] = sub["run_index"] <= WARMUP_DISCARD
    return sub


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Delta de Cliff: positivo indica que x tiende a ser mayor que y."""
    diff = x[:, None] - y[None, :]
    greater = np.sum(diff > 0)
    less = np.sum(diff < 0)
    return float((greater - less) / (len(x) * len(y)))


def interpret_cliffs_delta(delta: float) -> str:
    ad = abs(delta)
    if ad < 0.147:
        return "despreciable"
    if ad < 0.33:
        return "pequeno"
    if ad < 0.474:
        return "mediano"
    return "grande"


def bootstrap_median_ci(values: np.ndarray, rng: np.random.Generator) -> Tuple[float, float]:
    n = len(values)
    idx = rng.integers(0, n, size=(BOOTSTRAP_RESAMPLES, n))
    meds = np.median(values[idx], axis=1)
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return float(lo), float(hi)


def bootstrap_diff_medians_ci(
    base_vals: np.ndarray,
    comp_vals: np.ndarray,
    rng: np.random.Generator,
) -> Tuple[float, float]:
    idx_b = rng.integers(0, len(base_vals), size=(BOOTSTRAP_RESAMPLES, len(base_vals)))
    idx_c = rng.integers(0, len(comp_vals), size=(BOOTSTRAP_RESAMPLES, len(comp_vals)))
    diffs = np.median(base_vals[idx_b], axis=1) - np.median(comp_vals[idx_c], axis=1)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def discover_files(data_dir: Path) -> List[Tuple[str, int, Path]]:
    pattern = re.compile(r"^raw_(m[0-3])_(\d+)\.csv$")
    found = []
    for p in sorted(data_dir.glob("raw_*.csv")):
        m = pattern.match(p.name)
        if m:
            found.append((m.group(1), int(m.group(2)), p))
    if not found:
        raise FileNotFoundError(
            f"No se encontraron archivos raw_m<0-3>_<tamano>.csv en {data_dir}"
        )
    return found


def generate_figures(
    all_measured: pd.DataFrame,
    all_runs: pd.DataFrame,
    summary_df: pd.DataFrame,
    out_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    sizes = sorted(all_measured["batch_size"].unique())
    max_size = max(sizes)

    # Figura A: Caja y bigotes + puntos individuales en el mayor tamano de lote (escala log)
    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=300)
    sub_max = all_measured[all_measured["batch_size"] == max_size]
    stages_present = [s for s in STAGES_ORDER if s in sub_max["stage"].unique()]
    data_groups = [sub_max[sub_max["stage"] == s]["metric_value"].values for s in stages_present]

    bp = ax.boxplot(
        data_groups,
        positions=np.arange(1, len(stages_present) + 1),
        widths=0.45,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#111111", "linewidth": 1.6},
    )
    colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B3"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.35)

    rng_plot = np.random.default_rng(42)
    for i, vals in enumerate(data_groups, start=1):
        jitter = rng_plot.normal(0, 0.06, size=len(vals))
        ax.scatter(
            np.full(len(vals), i) + jitter,
            vals,
            s=14,
            alpha=0.75,
            color=colors[(i - 1) % len(colors)],
            edgecolors="none",
        )

    ax.axhline(THRESHOLD_MS, color="#B22222", linestyle="--", linewidth=1.2, label="Umbral p95 = 1000 ms")
    ax.set_yscale("log")
    ax.set_xticks(np.arange(1, len(stages_present) + 1))
    ax.set_xticklabels([STAGE_LABELS[s] for s in stages_present], fontsize=9)
    ax.set_ylabel("Latencia en servidor (ms, escala log)")
    ax.set_title(f"Distribucion de latencia por etapa (lote = {max_size} registros, n = 30)")
    ax.grid(True, which="both", axis="y", linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_boxplot_etapas.png")
    plt.close(fig)

    # Figura B: Curva de escalado p95 por tamano de lote
    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=300)
    markers = {"m0": "o", "m1": "s", "m2": "^", "m3": "D"}
    for idx, stage in enumerate(stages_present):
        s_df = summary_df[summary_df["stage"] == stage].sort_values("batch_size")
        ax.plot(
            s_df["batch_size"],
            s_df["p95_ms"],
            marker=markers[stage],
            linewidth=1.8,
            color=colors[idx % len(colors)],
            label=STAGE_LABELS[stage],
        )
    ax.axhline(THRESHOLD_MS, color="#B22222", linestyle="--", linewidth=1.2, label="Umbral p95 = 1000 ms")
    ax.set_yscale("log")
    ax.set_xlabel("Tamano del lote (registros consolidados por solicitud)")
    ax.set_ylabel("Latencia p95 en servidor (ms, escala log)")
    ax.set_title("Escalado de la latencia p95 segun tamano del lote")
    ax.set_xticks(sizes)
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_escalado_p95.png")
    plt.close(fig)

    # Figura C: Diagnostico de calentamiento y deriva por orden de corrida (mayor lote)
    fig, axes = plt.subplots(1, len(stages_present), figsize=(11.0, 3.2), dpi=250, sharey=False)
    if len(stages_present) == 1:
        axes = [axes]
    sub_all = all_runs[all_runs["batch_size"] == max_size]
    for ax, stage in zip(axes, stages_present):
        df_s = sub_all[sub_all["stage"] == stage].sort_values("run_index")
        warm = df_s[df_s["is_warmup"]]
        meas = df_s[~df_s["is_warmup"]]
        ax.plot(df_s["run_index"], df_s["metric_value"], color="#999999", linewidth=0.8)
        ax.scatter(warm["run_index"], warm["metric_value"], color="#D95F02", s=16, label="Warm-up (descartado)")
        ax.scatter(meas["run_index"], meas["metric_value"], color="#1B9E77", s=16, label="Medido (n=30)")
        ax.axvline(WARMUP_DISCARD + 0.5, color="#333333", linestyle=":", linewidth=1.0)
        ax.set_title(STAGE_LABELS[stage], fontsize=8.5)
        ax.set_xlabel("Iteracion", fontsize=8)
        ax.grid(True, linestyle=":", alpha=0.4)
    axes[0].set_ylabel("Latencia servidor (ms)", fontsize=8)
    axes[-1].legend(fontsize=7, loc="upper right")
    fig.suptitle(f"Diagnostico por orden de ejecucion (lote = {max_size})", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(out_dir / "fig_diagnostico_corridas.png")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis estadistico de CSV crudos de k6")
    parser.add_argument("--data-dir", type=Path, default=Path("datos"))
    parser.add_argument("--out-dir", type=Path, default=Path("resultados_resumen"))
    parser.add_argument("--metric", type=str, default="tiempo_servidor")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    discovered = discover_files(args.data_dir)
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    all_runs_list = []
    measured_map: Dict[Tuple[str, int], np.ndarray] = {}

    for stage, size, path in discovered:
        df_runs = parse_k6_csv(path, metric_name=args.metric)
        df_runs["stage"] = stage
        df_runs["batch_size"] = size
        df_runs["source_file"] = path.name
        all_runs_list.append(df_runs)

        meas = df_runs[~df_runs["is_warmup"]]["metric_value"].to_numpy(dtype=float)
        if len(meas) < EXPECTED_MEASURED:
            print(
                f"[ADVERTENCIA] {path.name}: se esperaban {EXPECTED_MEASURED} corridas "
                f"tras descartar {WARMUP_DISCARD} de calentamiento, se encontraron {len(meas)}."
            )
        measured_map[(stage, size)] = meas

    all_runs = pd.concat(all_runs_list, ignore_index=True)
    all_measured = all_runs[~all_runs["is_warmup"]].copy()

    summary_rows = []
    pairwise_rows = []

    sizes = sorted({size for _, size, _ in discovered})
    for size in sizes:
        m0_vals = measured_map.get(("m0", size))
        m0_med = float(np.median(m0_vals)) if m0_vals is not None else np.nan

        for stage in STAGES_ORDER:
            vals = measured_map.get((stage, size))
            if vals is None:
                continue
            p50 = float(np.median(vals))
            p25, p75 = np.percentile(vals, [25, 75])
            iqr = float(p75 - p25)
            p95 = float(np.percentile(vals, 95))
            p99 = float(np.percentile(vals, 99))
            ci_lo, ci_hi = bootstrap_median_ci(vals, rng)
            red_ms = float(m0_med - p50) if not np.isnan(m0_med) else np.nan
            red_pct = float((red_ms / m0_med) * 100.0) if (not np.isnan(m0_med) and m0_med > 0) else np.nan

            summary_rows.append(
                {
                    "batch_size": size,
                    "stage": stage,
                    "n": len(vals),
                    "p50_ms": round(p50, 3),
                    "p50_ci95_lo": round(ci_lo, 3),
                    "p50_ci95_hi": round(ci_hi, 3),
                    "iqr_ms": round(iqr, 3),
                    "p95_ms": round(p95, 3),
                    "p99_ms": round(p99, 3),
                    "red_vs_m0_ms": round(red_ms, 3) if stage != "m0" else 0.0,
                    "red_vs_m0_pct": round(red_pct, 2) if stage != "m0" else 0.0,
                    "cumple_umbral_1000ms": bool(p95 <= THRESHOLD_MS),
                }
            )

        # Comparaciones por pares clave: vs M0 y pasos consecutivos (M0->M1, M1->M2, M2->M3)
        pairs = [("m0", "m1"), ("m1", "m2"), ("m2", "m3"), ("m0", "m3")]
        for a, b in pairs:
            if (a, size) not in measured_map or (b, size) not in measured_map:
                continue
            va = measured_map[(a, size)]
            vb = measured_map[(b, size)]
            stat, p_val = mannwhitneyu(va, vb, alternative="two-sided")
            delta = cliffs_delta(va, vb)
            diff_med = float(np.median(va) - np.median(vb))
            d_lo, d_hi = bootstrap_diff_medians_ci(va, vb, rng)
            pairwise_rows.append(
                {
                    "batch_size": size,
                    "comparison": f"{a}_vs_{b}",
                    "diff_median_ms": round(diff_med, 3),
                    "diff_ci95_lo": round(d_lo, 3),
                    "diff_ci95_hi": round(d_hi, 3),
                    "mann_whitney_U": round(float(stat), 2),
                    "p_value": float(p_val),
                    "cliffs_delta": round(delta, 4),
                    "effect_magnitude": interpret_cliffs_delta(delta),
                }
            )

    summary_df = pd.DataFrame(summary_rows)
    pairwise_df = pd.DataFrame(pairwise_rows)

    summary_df.to_csv(args.out_dir / "resumen_etapas.csv", index=False)
    pairwise_df.to_csv(args.out_dir / "comparaciones_estadisticas.csv", index=False)

    # Exportar resumen JSON para trazabilidad exacta
    report_json = {
        "metric": args.metric,
        "warmup_discarded": WARMUP_DISCARD,
        "threshold_ms": THRESHOLD_MS,
        "summary": summary_rows,
        "pairwise": pairwise_rows,
    }
    (args.out_dir / "resumen_completo.json").write_text(
        json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Generar figuras IEEE
    generate_figures(all_measured, all_runs, summary_df, args.out_dir / "figuras")

    # Imprimir salida en consola sin adjetivos interpretativos
    print("=== RESUMEN POR ETAPA Y TAMANO ===")
    print(summary_df.to_string(index=False))
    print("\n=== COMPARACIONES NO PARAMETRICAS (MANN-WHITNEY U + CLIFF + BOOTSTRAP IC 95%) ===")
    print(pairwise_df.to_string(index=False))


if __name__ == "__main__":
    main()

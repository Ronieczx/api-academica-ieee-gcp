# Datos crudos de la campana experimental

Esta carpeta almacena los 16 archivos CSV crudos generados directamente por `k6` desde el flujo `.github/workflows/benchmark.yml` en GitHub Actions:

- `raw_m0_10.csv`, `raw_m0_50.csv`, `raw_m0_200.csv`, `raw_m0_500.csv`
- `raw_m1_10.csv`, `raw_m1_50.csv`, `raw_m1_200.csv`, `raw_m1_500.csv`
- `raw_m2_10.csv`, `raw_m2_50.csv`, `raw_m2_200.csv`, `raw_m2_500.csv`
- `raw_m3_10.csv`, `raw_m3_50.csv`, `raw_m3_200.csv`, `raw_m3_500.csv`

No edite manualmente estos archivos. Una vez descargado el artefacto `evidencia-experimental-<commit>` desde GitHub Actions, copie los 16 CSV aqui, haga commit y ejecute:

```bash
python scripts/analyze_results.py --data-dir datos --out-dir resultados_resumen
```

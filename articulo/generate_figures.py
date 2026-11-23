"""
Generación de figuras técnicas de alta calidad (300 DPI) para el artículo IEEE:
- Fig 1: Modelo conceptual (sin nombres comerciales de tecnologías, con signos (+), (-), (?))
- Fig 2: Diagrama de componentes (con frontera del sistema, ubicación de VI y punto de medición del cronómetro)
- Fig 3: Diagrama de despliegue en entorno cloud controlado (GitHub Actions runner, loopback, puertos, contenedor postgres:16)
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = Path(r"C:\Users\RONI\Desktop\Tarea Itec\articulo\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de estilo IEEE
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "figure.autolayout": False,
})


def generate_fig1_conceptual_model():
    fig, ax = plt.subplots(figsize=(8.0, 3.8), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Colores sobrios científicos
    box_color_vi = "#EBF3FB"
    box_color_vd = "#FDE8E8"
    box_color_vm = "#FEF3D6"
    box_color_vc = "#F3F4F6"
    border_color = "#374151"

    # 1. VI: Etapa de Optimización por Capas
    vi_box = patches.FancyBboxPatch(
        (0.03, 0.44), 0.30, 0.50, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec=border_color, fc=box_color_vi, lw=1.5
    )
    ax.add_patch(vi_box)
    ax.text(0.18, 0.88, "VARIABLE INDEPENDIENTE (VI)", ha="center", va="center", weight="bold", fontsize=8.2, color="#1E3A8A")
    ax.text(0.18, 0.79, "Intervención Incremental por Capas\n[Factor discreto ordinal de 4 niveles]", ha="center", va="center", weight="semibold", fontsize=7.6)
    vi_desc = (
        "• M0: Base sin optimizar (N+1, no sargable)\n"
        "• M1: Agrupación en aplicación (ANY hash)\n"
        "• M2: Predicado sargable + índice compuesto\n"
        "• M3: M2 + Caché volátil en memoria (TTL)"
    )
    ax.text(0.045, 0.58, vi_desc, ha="left", va="center", fontsize=7.0, linespacing=1.3)

    # 2. VD: Comportamiento Temporal (Latencia)
    vd_box = patches.FancyBboxPatch(
        (0.67, 0.44), 0.30, 0.50, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec=border_color, fc=box_color_vd, lw=1.5
    )
    ax.add_patch(vd_box)
    ax.text(0.82, 0.88, "VARIABLE DEPENDIENTE (VD)", ha="center", va="center", weight="bold", fontsize=8.2, color="#991B1B")
    ax.text(0.82, 0.79, "Comportamiento Temporal\n[Eficiencia de Desempeño ISO 25010]", ha="center", va="center", weight="semibold", fontsize=7.6)
    vd_desc = (
        "• Latencia interna de servidor (ms)\n"
        "  - Percentil 50 (Mediana) [ms]\n"
        "  - Percentil 95 (p95) [ms]\n"
        "  - Percentil 99 (p99) [ms]\n"
        "  - Rango intercuartílico (IQR) [ms]\n"
        "• Umbral operacional: p95 <= 1000 ms"
    )
    ax.text(0.685, 0.58, vd_desc, ha="left", va="center", fontsize=7.0, linespacing=1.3)

    # Flecha Principal VI -> VD con signo (-)
    ax.annotate(
        "", xy=(0.66, 0.69), xytext=(0.34, 0.69),
        arrowprops=dict(arrowstyle="->", lw=2.2, color="#1F2937", shrinkA=2, shrinkB=2)
    )
    bbox_white = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#D1D5DB", lw=0.8)
    ax.text(0.50, 0.74, "Efecto Directo Principal (-)", ha="center", va="bottom", weight="bold", fontsize=8.2, color="#111827", bbox=bbox_white)
    ax.text(0.50, 0.63, "Hipótesis H1: Reducción >= 80 % y p95 <= 1,0 s", ha="center", va="top", style="italic", fontsize=7.0, color="#374151", bbox=bbox_white)

    # 3. Variable Moderadora (VM): Tamaño de Lote
    vm_box = patches.FancyBboxPatch(
        (0.35, 0.16), 0.30, 0.32, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec=border_color, fc=box_color_vm, lw=1.5
    )
    ax.add_patch(vm_box)
    ax.text(0.50, 0.43, "VARIABLE MODERADORA (VM)", ha="center", va="center", weight="bold", fontsize=8.0, color="#92400E")
    ax.text(0.50, 0.34, "Tamaño de Lote de Solicitud\n[10, 50, 200, 500 registros/req]", ha="center", va="center", weight="semibold", fontsize=7.5)
    ax.text(0.50, 0.22, "Carga de trabajo por invocación", ha="center", va="center", fontsize=7.0, style="italic")

    # Flecha Moderadora VM -> Flecha Principal (?)
    ax.annotate(
        "", xy=(0.50, 0.60), xytext=(0.50, 0.49),
        arrowprops=dict(arrowstyle="->", lw=1.8, color="#92400E", ls="--")
    )
    ax.text(0.50, 0.54, "(?) Moderación de escala", ha="center", va="center", fontsize=7.4, weight="bold", color="#92400E", bbox=bbox_white)

    # Flecha VM -> VD (+)
    ax.annotate(
        "", xy=(0.67, 0.45), xytext=(0.65, 0.36),
        arrowprops=dict(arrowstyle="->", lw=1.5, color="#92400E", ls=":")
    )
    ax.text(0.67, 0.37, "(+)", ha="center", va="center", fontsize=8.0, weight="bold", color="#92400E", bbox=bbox_white)

    # 4. Variables de Control (VC)
    vc_box = patches.FancyBboxPatch(
        (0.03, 0.04), 0.30, 0.34, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#9CA3AF", fc=box_color_vc, lw=1.0
    )
    ax.add_patch(vc_box)
    ax.text(0.18, 0.33, "VARIABLES DE CONTROL (VC)", ha="center", va="center", weight="bold", fontsize=7.8, color="#374151")
    vc_desc = (
        "• Concurrencia fija: 1 usuario secuencial (1 VU)\n"
        "• Historial persistente: 200 000 filas (SEED=2026)\n"
        "• Catálogo estático: 500 cursos normalizados\n"
        "• Entorno de ejecución: runner en nube idéntico\n"
        "• Calentamiento: 5 corridas descartadas/condición"
    )
    ax.text(0.045, 0.17, vc_desc, ha="left", va="center", fontsize=6.7, linespacing=1.25)

    fig.savefig(OUT_DIR / "fig1_modelo_conceptual.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 1 regenerada en fig1_modelo_conceptual.png")


def generate_fig2_component_diagram():
    fig, ax = plt.subplots(figsize=(8.2, 4.0), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    bbox_label = dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#9CA3AF", lw=0.7)

    # Frontera del Sistema
    sys_border = patches.FancyBboxPatch(
        (0.24, 0.04), 0.74, 0.92, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#1E40AF", fc="#F8FAFC", lw=1.8, ls="--"
    )
    ax.add_patch(sys_border)
    ax.text(0.27, 0.92, "FRONTERA DEL SISTEMA (Servidor de API Académica)", fontsize=8.5, weight="bold", color="#1E40AF")

    # 1. Cliente externo (Generador de Carga k6)
    cli_box = patches.FancyBboxPatch(
        (0.02, 0.34), 0.17, 0.44, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#FEF3C7", lw=1.4
    )
    ax.add_patch(cli_box)
    ax.text(0.105, 0.72, "Cliente de Carga\n(k6 Test Runner)", ha="center", va="center", weight="bold", fontsize=7.8)
    cli_desc = (
        "• 1 VU secuencial\n"
        "• 35 iteraciones\n"
        "• Mide: tiempo_e2e\n"
        "• Extrae cabecera:\n"
        "  X-Process-Time-Ms"
    )
    ax.text(0.105, 0.50, cli_desc, ha="center", va="center", fontsize=6.8, linespacing=1.25)

    # 2. Capa de Presentación / Controladores REST
    pres_box = patches.FancyBboxPatch(
        (0.27, 0.32), 0.19, 0.54, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#EFF6FF", lw=1.4
    )
    ax.add_patch(pres_box)
    ax.text(0.365, 0.81, "Capa de Presentación\n(Controlador REST)", ha="center", va="center", weight="bold", fontsize=7.8, color="#1E3A8A")
    ax.text(0.365, 0.67, "POST /api/v1/consolidate\nGET /api/v1/health\nGET /api/v1/explain", ha="center", va="center", fontsize=6.6, family="monospace")

    # Marcador del Cronómetro del Servidor
    timer_box = patches.FancyBboxPatch(
        (0.285, 0.36), 0.16, 0.18, boxstyle="round,pad=0.015,rounding_size=0.015",
        ec="#DC2626", fc="#FEE2E2", lw=1.2
    )
    ax.add_patch(timer_box)
    ax.text(0.365, 0.45, "MEDICIÓN DE LA VD\nt0 = perf_counter()\n[X-Process-Time-Ms]\nSin latencia de red", ha="center", va="center", weight="bold", fontsize=6.5, color="#991B1B")

    # Flechas Cliente <-> Presentación con bbox blanco
    ax.annotate("", xy=(0.265, 0.62), xytext=(0.195, 0.62), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937"))
    ax.text(0.23, 0.66, "HTTP POST", ha="center", va="bottom", fontsize=6.6, weight="bold", bbox=bbox_label)

    ax.annotate("", xy=(0.195, 0.52), xytext=(0.265, 0.52), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937", ls="--"))
    ax.text(0.23, 0.48, "Header X-Proc", ha="center", va="top", fontsize=6.2, bbox=bbox_label)

    # 3. Capa de Lógica de Negocio / Aplicación (VI: M0, M1, M3)
    app_box = patches.FancyBboxPatch(
        (0.50, 0.32), 0.22, 0.54, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#F0FDF4", lw=1.4
    )
    ax.add_patch(app_box)
    ax.text(0.61, 0.81, "Capa de Aplicación\n(Servicio Consolidación)", ha="center", va="center", weight="bold", fontsize=7.8, color="#166534")
    app_desc = (
        "UBICACIÓN DE LA VI:\n"
        "• M0: Antipatrón N+1 y\n"
        "  búsqueda lineal O(N)\n"
        "• M1: Consulta en lote ANY\n"
        "  + HashMap O(1) en RAM\n"
        "• M3: Catálogo en Caché RAM\n"
        "  con TTL = 300 segundos"
    )
    ax.text(0.51, 0.53, app_desc, ha="left", va="center", fontsize=6.7, linespacing=1.25)

    # Flecha Presentación -> Aplicación con bbox
    ax.annotate("", xy=(0.495, 0.59), xytext=(0.465, 0.59), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937"))
    ax.text(0.48, 0.63, "DTO", ha="center", va="bottom", fontsize=6.2, weight="bold", bbox=bbox_label)

    # 4. Capa de Persistencia y Datos (VI: M0, M1, M2)
    db_box = patches.FancyBboxPatch(
        (0.76, 0.08), 0.20, 0.78, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#FAF5FF", lw=1.4
    )
    ax.add_patch(db_box)
    ax.text(0.86, 0.81, "Capa de Persistencia\ny Almacenamiento", ha="center", va="center", weight="bold", fontsize=7.8, color="#6B21A8")
    db_desc = (
        "UBICACIÓN DE LA VI:\n"
        "• M0/M1: No sargable:\n"
        "  UPPER(student_code)\n"
        "  [Seq Scan en 200k filas]\n\n"
        "• M2/M3: Sargable directo:\n"
        "  student_code = ANY(%s)\n"
        "  [Bitmap Index Scan]\n\n"
        "TABLAS & ÍNDICES:\n"
        "• courses (500 filas)\n"
        "• enrollments (200k filas)\n"
        "• idx_enrollments_student\n"
        "  (student_code, term_code)"
    )
    ax.text(0.77, 0.44, db_desc, ha="left", va="center", fontsize=6.3, linespacing=1.18)

    # Flecha Aplicación -> Persistencia con bbox
    ax.annotate("", xy=(0.755, 0.59), xytext=(0.725, 0.59), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937"))
    ax.text(0.74, 0.63, "SQL", ha="center", va="bottom", fontsize=6.2, weight="bold", bbox=bbox_label)

    fig.savefig(OUT_DIR / "fig2_diagrama_componentes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 2 regenerada en fig2_diagrama_componentes.png")


def generate_fig3_deployment_diagram():
    fig, ax = plt.subplots(figsize=(8.2, 3.8), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    bbox_label = dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor="#9CA3AF", lw=0.7)

    # Contenedor Runner GitHub Actions
    runner_box = patches.FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#2563EB", fc="#F8FAFC", lw=1.8
    )
    ax.add_patch(runner_box)
    ax.text(0.05, 0.91, "ENTORNO CLOUD CONTROLADO: GitHub Actions Runner (ubuntu-latest, 2 vCPU, 7 GB RAM)", fontsize=8.4, weight="bold", color="#1E40AF")
    ax.text(0.05, 0.85, "Variables de control fijas: Kernel Linux 6.8, Python 3.12 congelado, sin fluctuación de red pública, volcado determinístico SEED=2026", fontsize=6.8, color="#4B5563")

    # 1. Proceso Cliente k6
    k6_box = patches.FancyBboxPatch(
        (0.05, 0.22), 0.18, 0.56, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#D97706", fc="#FEF3C7", lw=1.3
    )
    ax.add_patch(k6_box)
    ax.text(0.14, 0.72, "Proceso Cliente\n(k6 Test Runner)", ha="center", va="center", weight="bold", fontsize=7.8)
    k6_desc = (
        "• 1 VU secuencial\n"
        "• 35 repeticiones\n"
        "• 5 warm-up (descarte)\n"
        "• 30 mediciones válidas\n"
        "• Exportación de CSV\n"
        "  crudo coincidente"
    )
    ax.text(0.14, 0.48, k6_desc, ha="center", va="center", fontsize=6.8, linespacing=1.25)

    # 2. Servidores de Aplicación (Micro-Entornos en Puertos Aislados)
    api_group_box = patches.FancyBboxPatch(
        (0.33, 0.10), 0.35, 0.68, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#10B981", fc="#ECFDF5", lw=1.3
    )
    ax.add_patch(api_group_box)
    ax.text(0.505, 0.73, "Servidores de Aplicación (Mismo Commit SHA)", ha="center", va="center", weight="bold", fontsize=8.0, color="#065F46")

    stages = [
        ("M0 Base (N+1, no sargable)", ":8000", "#FEE2E2"),
        ("M1 Aplicación (Agrupado ANY)", ":8001", "#FEF3C7"),
        ("M2 Persistencia (Sargable + idx)", ":8002", "#EFF6FF"),
        ("M3 Caché RAM (TTL 300s)", ":8003", "#DCFCE7"),
    ]
    y_pos = 0.61
    for label, port, col in stages:
        s_box = patches.FancyBboxPatch(
            (0.35, y_pos - 0.04), 0.31, 0.08, boxstyle="round,pad=0.01,rounding_size=0.01",
            ec="#4B5563", fc=col, lw=0.9
        )
        ax.add_patch(s_box)
        ax.text(0.365, y_pos, label, ha="left", va="center", fontsize=6.7, weight="semibold")
        ax.text(0.645, y_pos, port, ha="right", va="center", fontsize=6.7, family="monospace", weight="bold")
        y_pos -= 0.12

    # 3. Servicio Contenedor PostgreSQL 16
    pg_box = patches.FancyBboxPatch(
        (0.75, 0.14), 0.20, 0.64, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#7C3AED", fc="#F5F3FF", lw=1.4
    )
    ax.add_patch(pg_box)
    ax.text(0.85, 0.72, "Servicio Contenedor\nPostgreSQL 16", ha="center", va="center", weight="bold", fontsize=7.8, color="#5B21B6")
    pg_desc = (
        "• Puerto: :5432\n"
        "• Base: academica_db\n"
        "• 500 cursos\n"
        "• 200 000 matrículas\n"
        "• Shared buffers: 128 MB\n"
        "• Índice B-tree compuesto:\n"
        "  idx_enrollments_\n"
        "  student_term"
    )
    ax.text(0.76, 0.44, pg_desc, ha="left", va="center", fontsize=6.6, linespacing=1.22)

    # Conexiones con etiquetas sobre fondo blanco
    ax.annotate("", xy=(0.325, 0.50), xytext=(0.235, 0.50), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937"))
    ax.text(0.28, 0.50, "loopback\n127.0.0.1", ha="center", va="center", fontsize=6.5, weight="bold", bbox=bbox_label)

    ax.annotate("", xy=(0.745, 0.50), xytext=(0.685, 0.50), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1F2937"))
    ax.text(0.715, 0.50, "TCP socket\nlocalhost:5432", ha="center", va="center", fontsize=6.5, weight="bold", bbox=bbox_label)

    fig.savefig(OUT_DIR / "fig3_diagrama_despliegue.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 3 regenerada en fig3_diagrama_despliegue.png")


if __name__ == "__main__":
    generate_fig1_conceptual_model()
    generate_fig2_component_diagram()
    generate_fig3_deployment_diagram()

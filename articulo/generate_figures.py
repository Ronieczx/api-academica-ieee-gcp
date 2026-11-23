"""
Generación de figuras técnicas de alta calidad (300 DPI) para el artículo IEEE:
- Fig 1: Modelo conceptual (según Clase 04 lámina 29, sin marcas comerciales, con signos (+), (-), (?))
- Fig 2: Diagrama de componentes (frontera del sistema, ubicación de VI y punto de medición del cronómetro)
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
    "font.size": 9.5,
    "axes.titlesize": 10,
    "axes.labelsize": 9.5,
    "figure.autolayout": False,
})


def generate_fig1_conceptual_model():
    # Lienzo amplio según Clase 04 lámina 29
    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Colores sobrios científicos
    box_color_vi = "#EBF3FB"
    box_color_vd = "#FDE8E8"
    box_color_vm = "#FEF3D6"
    box_color_vc = "#F3F4F6"
    border_color = "#374151"

    bbox_label = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#D1D5DB", lw=0.9)

    # 1. VARIABLE MODERADORA (VM) - Arriba Centro (borde punteado)
    vm_box = patches.FancyBboxPatch(
        (0.32, 0.76), 0.36, 0.18, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#B45309", fc=box_color_vm, lw=1.6, ls="--"
    )
    ax.add_patch(vm_box)
    ax.text(0.50, 0.88, "VARIABLE MODERADORA (VM)", ha="center", va="center", weight="bold", fontsize=9.2, color="#92400E")
    ax.text(0.50, 0.82, "Tamaño de Lote de Solicitud\n[10, 50, 200, 500 registros]", ha="center", va="center", weight="semibold", fontsize=8.6)
    ax.text(0.50, 0.74, "(Carga de trabajo por invocación sincrónica)", ha="center", va="center", fontsize=7.8, style="italic", color="#78350F")

    # 2. VARIABLE INDEPENDIENTE (VI) - Centro Izquierda
    vi_box = patches.FancyBboxPatch(
        (0.03, 0.32), 0.30, 0.38, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec=border_color, fc=box_color_vi, lw=1.6
    )
    ax.add_patch(vi_box)
    ax.text(0.18, 0.65, "VARIABLE INDEPENDIENTE (VI)", ha="center", va="center", weight="bold", fontsize=9.2, color="#1E3A8A")
    ax.text(0.18, 0.58, "Intervención Incremental por Capas", ha="center", va="center", weight="semibold", fontsize=8.6)
    vi_desc = (
        "• M0: Línea base (N+1, no sargable)\n"
        "• M1: Consulta agrupada (OE2)\n"
        "• M2: Predicado sargable + índice (OE3)\n"
        "• M3: Caché en memoria con TTL (OE3)"
    )
    ax.text(0.05, 0.43, vi_desc, ha="left", va="center", fontsize=8.0, linespacing=1.35)

    # 3. VARIABLE DEPENDIENTE (VD) - Centro Derecha
    vd_box = patches.FancyBboxPatch(
        (0.67, 0.32), 0.30, 0.38, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec=border_color, fc=box_color_vd, lw=1.6
    )
    ax.add_patch(vd_box)
    ax.text(0.82, 0.65, "VARIABLE DEPENDIENTE (VD)", ha="center", va="center", weight="bold", fontsize=9.2, color="#991B1B")
    ax.text(0.82, 0.58, "Comportamiento Temporal\n(ISO/IEC 25010:2011)", ha="center", va="center", weight="semibold", fontsize=8.6)
    vd_desc = (
        "• Latencia en servidor [ms]\n"
        "• Estadísticos: p50, p95, p99, IQR\n"
        "• Umbral: p95 <= 1000 ms (1,0 s)"
    )
    ax.text(0.69, 0.43, vd_desc, ha="left", va="center", fontsize=8.0, linespacing=1.35)

    # Flecha Principal Horizontal VI -> VD
    ax.annotate(
        "", xy=(0.67, 0.51), xytext=(0.33, 0.51),
        arrowprops=dict(arrowstyle="->", lw=2.4, color="#1F2937", shrinkA=2, shrinkB=2)
    )
    ax.text(0.50, 0.56, "Reduce latencia (-)", ha="center", va="bottom", weight="bold", fontsize=9.0, color="#111827", bbox=bbox_label)
    ax.text(0.50, 0.46, "H1: Reducción >= 80 % y p95 <= 1,0 s", ha="center", va="top", style="italic", fontsize=8.0, color="#374151", bbox=bbox_label)

    # Flecha Vertical VM -> Flecha Principal Central (?)
    ax.annotate(
        "", xy=(0.50, 0.60), xytext=(0.50, 0.76),
        arrowprops=dict(arrowstyle="->", lw=2.0, color="#B45309", ls="--", shrinkA=2, shrinkB=2)
    )
    ax.text(0.50, 0.68, "Modera magnitud (?)", ha="center", va="center", fontsize=8.4, weight="bold", color="#B45309", bbox=bbox_label)

    # 4. VARIABLES DE CONTROL (VC) - Abajo Centro
    vc_box = patches.FancyBboxPatch(
        (0.24, 0.05), 0.52, 0.20, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#9CA3AF", fc=box_color_vc, lw=1.2
    )
    ax.add_patch(vc_box)
    ax.text(0.50, 0.20, "VARIABLES DE CONTROL (VC)", ha="center", va="center", weight="bold", fontsize=8.8, color="#374151")
    vc_desc = "1 VU secuencial · n=30 · 5 warm-ups descartados · Historial 200 000 filas\nPostgreSQL 16 · Python 3.12 · Mismo commit inmutable (f19645a)"
    ax.text(0.50, 0.11, vc_desc, ha="center", va="center", fontsize=8.0, linespacing=1.3)

    # Flecha VC -> Flecha Principal
    ax.annotate(
        "", xy=(0.50, 0.42), xytext=(0.50, 0.25),
        arrowprops=dict(arrowstyle="->", lw=1.4, color="#6B7280", ls=":", shrinkA=2, shrinkB=2)
    )
    ax.text(0.50, 0.335, "Condiciones de control fijas", ha="center", va="center", fontsize=7.6, color="#4B5563", bbox=bbox_label)

    fig.savefig(OUT_DIR / "fig1_modelo_conceptual.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 1 generada exitosamente según Clase 04 lámina 29.")


def generate_fig2_component_diagram():
    fig, ax = plt.subplots(figsize=(10.5, 5.0), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    bbox_label = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#9CA3AF", lw=0.8)

    # Frontera del Sistema
    sys_border = patches.FancyBboxPatch(
        (0.23, 0.04), 0.75, 0.92, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#1E40AF", fc="#F8FAFC", lw=1.8, ls="--"
    )
    ax.add_patch(sys_border)
    ax.text(0.26, 0.92, "FRONTERA DEL SISTEMA (Servidor de API Académica)", fontsize=9.0, weight="bold", color="#1E40AF")

    # 1. Cliente externo (Generador de Carga k6)
    cli_box = patches.FancyBboxPatch(
        (0.02, 0.30), 0.17, 0.48, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#FEF3C7", lw=1.4
    )
    ax.add_patch(cli_box)
    ax.text(0.105, 0.71, "Cliente de Carga\n(k6 Test Runner)", ha="center", va="center", weight="bold", fontsize=8.2)
    cli_desc = (
        "• 1 VU secuencial\n"
        "• 35 iteraciones\n"
        "• Mide: tiempo_e2e\n"
        "• Extrae cabecera:\n"
        "  X-Process-Time-Ms"
    )
    ax.text(0.105, 0.48, cli_desc, ha="center", va="center", fontsize=7.4, linespacing=1.3)

    # 2. Capa de Presentación / Controladores REST
    pres_box = patches.FancyBboxPatch(
        (0.26, 0.28), 0.19, 0.58, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#EFF6FF", lw=1.4
    )
    ax.add_patch(pres_box)
    ax.text(0.355, 0.80, "Capa de Presentación\n(Controlador REST)", ha="center", va="center", weight="bold", fontsize=8.2, color="#1E3A8A")
    ax.text(0.355, 0.65, "POST /api/v1/consolidate\nGET /api/v1/health\nGET /api/v1/explain", ha="center", va="center", fontsize=7.2, family="monospace")

    # Marcador del Cronómetro del Servidor
    timer_box = patches.FancyBboxPatch(
        (0.275, 0.32), 0.16, 0.20, boxstyle="round,pad=0.015,rounding_size=0.015",
        ec="#DC2626", fc="#FEE2E2", lw=1.2
    )
    ax.add_patch(timer_box)
    ax.text(0.355, 0.42, "MEDICIÓN DE LA VD\nt0 = perf_counter()\n[X-Process-Time-Ms]\nSin latencia de red", ha="center", va="center", weight="bold", fontsize=7.0, color="#991B1B")

    # Flechas Cliente <-> Presentación con bbox blanco
    ax.annotate("", xy=(0.255, 0.60), xytext=(0.195, 0.60), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937"))
    ax.text(0.225, 0.64, "HTTP POST", ha="center", va="bottom", fontsize=7.0, weight="bold", bbox=bbox_label)

    ax.annotate("", xy=(0.195, 0.50), xytext=(0.255, 0.50), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937", ls="--"))
    ax.text(0.225, 0.46, "Header X-Proc", ha="center", va="top", fontsize=6.8, bbox=bbox_label)

    # 3. Capa de Lógica de Negocio / Aplicación (VI: M0, M1, M3)
    app_box = patches.FancyBboxPatch(
        (0.50, 0.28), 0.22, 0.58, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#F0FDF4", lw=1.4
    )
    ax.add_patch(app_box)
    ax.text(0.61, 0.80, "Capa de Aplicación\n(Servicio Consolidación)", ha="center", va="center", weight="bold", fontsize=8.2, color="#166534")
    app_desc = (
        "UBICACIÓN DE LA VI:\n"
        "• M0: Antipatrón N+1 y\n"
        "  búsqueda lineal O(N)\n"
        "• M1: Consulta en lote ANY\n"
        "  + HashMap O(1) en RAM\n"
        "• M3: Catálogo en Caché RAM\n"
        "  con TTL = 300 segundos"
    )
    ax.text(0.51, 0.50, app_desc, ha="left", va="center", fontsize=7.2, linespacing=1.3)

    # Flecha Presentación -> Aplicación con bbox
    ax.annotate("", xy=(0.495, 0.57), xytext=(0.455, 0.57), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937"))
    ax.text(0.475, 0.62, "DTO", ha="center", va="bottom", fontsize=7.0, weight="bold", bbox=bbox_label)

    # 4. Capa de Persistencia y Datos (VI: M0, M1, M2)
    db_box = patches.FancyBboxPatch(
        (0.77, 0.08), 0.19, 0.78, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#374151", fc="#FAF5FF", lw=1.4
    )
    ax.add_patch(db_box)
    ax.text(0.865, 0.80, "Capa de Persistencia\ny Almacenamiento", ha="center", va="center", weight="bold", fontsize=8.2, color="#6B21A8")
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
    ax.text(0.78, 0.43, db_desc, ha="left", va="center", fontsize=6.8, linespacing=1.2)

    # Flecha Aplicación -> Persistencia con bbox
    ax.annotate("", xy=(0.765, 0.57), xytext=(0.725, 0.57), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937"))
    ax.text(0.745, 0.62, "SQL", ha="center", va="bottom", fontsize=7.0, weight="bold", bbox=bbox_label)

    fig.savefig(OUT_DIR / "fig2_diagrama_componentes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 2 generada exitosamente.")


def generate_fig3_deployment_diagram():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    bbox_label = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#9CA3AF", lw=0.8)

    # Contenedor Runner GitHub Actions
    runner_box = patches.FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#2563EB", fc="#F8FAFC", lw=1.8
    )
    ax.add_patch(runner_box)
    ax.text(0.05, 0.91, "ENTORNO CLOUD CONTROLADO: GitHub Actions Runner (ubuntu-latest, 2 vCPU, 7 GB RAM)", fontsize=8.8, weight="bold", color="#1E40AF")
    ax.text(0.05, 0.85, "Variables fijas: Kernel Linux 6.8, Python 3.12 congelado, sin fluctuación de red pública, volcado determinístico SEED=2026", fontsize=7.4, color="#4B5563")

    # 1. Proceso Cliente k6
    k6_box = patches.FancyBboxPatch(
        (0.05, 0.20), 0.18, 0.58, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#D97706", fc="#FEF3C7", lw=1.3
    )
    ax.add_patch(k6_box)
    ax.text(0.14, 0.72, "Proceso Cliente\n(k6 Test Runner)", ha="center", va="center", weight="bold", fontsize=8.2)
    k6_desc = (
        "• 1 VU secuencial\n"
        "• 35 repeticiones\n"
        "• 5 warm-up (descarte)\n"
        "• 30 mediciones válidas\n"
        "• Exportación de CSV\n"
        "  crudo coincidente"
    )
    ax.text(0.14, 0.46, k6_desc, ha="center", va="center", fontsize=7.4, linespacing=1.3)

    # 2. Servidores de Aplicación (Micro-Entornos en Puertos Aislados)
    api_group_box = patches.FancyBboxPatch(
        (0.33, 0.10), 0.35, 0.68, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#10B981", fc="#ECFDF5", lw=1.3
    )
    ax.add_patch(api_group_box)
    ax.text(0.505, 0.73, "Servidores de Aplicación (Mismo Commit SHA: f19645a)", ha="center", va="center", weight="bold", fontsize=8.2, color="#065F46")

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
        ax.text(0.365, y_pos, label, ha="left", va="center", fontsize=7.2, weight="semibold")
        ax.text(0.645, y_pos, port, ha="right", va="center", fontsize=7.2, family="monospace", weight="bold")
        y_pos -= 0.12

    # 3. Servicio Contenedor PostgreSQL 16
    pg_box = patches.FancyBboxPatch(
        (0.76, 0.14), 0.19, 0.64, boxstyle="round,pad=0.02,rounding_size=0.02",
        ec="#7C3AED", fc="#F5F3FF", lw=1.4
    )
    ax.add_patch(pg_box)
    ax.text(0.855, 0.72, "Servicio Contenedor\nPostgreSQL 16", ha="center", va="center", weight="bold", fontsize=8.2, color="#5B21B6")
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
    ax.text(0.77, 0.44, pg_desc, ha="left", va="center", fontsize=7.0, linespacing=1.25)

    # Conexiones con etiquetas sobre fondo blanco
    ax.annotate("", xy=(0.325, 0.50), xytext=(0.235, 0.50), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937"))
    ax.text(0.28, 0.50, "loopback\n127.0.0.1", ha="center", va="center", fontsize=7.0, weight="bold", bbox=bbox_label)

    ax.annotate("", xy=(0.755, 0.50), xytext=(0.685, 0.50), arrowprops=dict(arrowstyle="->", lw=1.6, color="#1F2937"))
    ax.text(0.72, 0.50, "TCP socket\nlocalhost:5432", ha="center", va="center", fontsize=7.0, weight="bold", bbox=bbox_label)

    fig.savefig(OUT_DIR / "fig3_diagrama_despliegue.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK] Fig 3 generada exitosamente.")


if __name__ == "__main__":
    generate_fig1_conceptual_model()
    generate_fig2_component_diagram()
    generate_fig3_deployment_diagram()

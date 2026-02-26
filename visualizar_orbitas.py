"""
Visualizador de órbitas planetarias
Autor: generado con Claude
Requisitos: pip install matplotlib pandas numpy
Uso: coloca este script en la misma carpeta que orbits.csv y ejecuta con python
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# -------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------
CSV_FILE = "orbits.csv"   # debe estar en la misma carpeta que este script
ANIMATION_INTERVAL = 20   # ms entre frames (más bajo = más rápido)
TRAIL_LENGTH = 150        # cuántos puntos de estela muestra cada planeta
SHOW_INNER = True         # mostrar planetas interiores (Mercurio a Marte)
SHOW_OUTER = True         # mostrar planetas exteriores (Júpiter a Neptuno)

# -------------------------------------------------------
# DATOS DE CADA PLANETA: nombre, color, tamaño del punto
# -------------------------------------------------------
PLANETS = [
    {"name": "Sol",      "color": "#FFD700", "size": 18, "zorder": 10},
    {"name": "Mercurio", "color": "#B5B5B5", "size": 5,  "zorder": 5},
    {"name": "Venus",    "color": "#E8C46A", "size": 7,  "zorder": 5},
    {"name": "Tierra",   "color": "#4FA3E0", "size": 7,  "zorder": 5},
    {"name": "Marte",    "color": "#C1440E", "size": 6,  "zorder": 5},
    {"name": "Jupiter",  "color": "#C88B3A", "size": 12, "zorder": 5},
    {"name": "Saturno",  "color": "#E4D191", "size": 11, "zorder": 5},
    {"name": "Urano",    "color": "#7DE8E8", "size": 9,  "zorder": 5},
    {"name": "Neptuno",  "color": "#4B70DD", "size": 9,  "zorder": 5},
]

# -------------------------------------------------------
# CARGAR DATOS
# -------------------------------------------------------
print(f"Cargando datos de {CSV_FILE}...")
df = pd.read_csv(CSV_FILE)
print(f"  Pasos cargados: {len(df)}")
print(f"  Tiempo total: {df['t'].iloc[-1] / (86400*365):.2f} años")

# Convertir posiciones de metros a UA (Unidades Astronómicas) para mejor visualización
AU = 1.496e11
for p in PLANETS:
    name = p["name"]
    df[f"{name}_x_au"] = df[f"{name}_x"] / AU
    df[f"{name}_y_au"] = df[f"{name}_y"] / AU

N_FRAMES = len(df)

# -------------------------------------------------------
# REDUCIR FRAMES si hay demasiados (para que la animación no sea lenta)
# -------------------------------------------------------
MAX_FRAMES = 600
if N_FRAMES > MAX_FRAMES:
    step = N_FRAMES // MAX_FRAMES
    df_anim = df.iloc[::step].reset_index(drop=True)
    print(f"  Reduciendo a {len(df_anim)} frames para la animación (1 de cada {step} pasos)")
else:
    df_anim = df
N_FRAMES = len(df_anim)

# -------------------------------------------------------
# FIGURA CON DOS PANELES: sistema interior y exterior
# -------------------------------------------------------
fig = plt.figure(figsize=(16, 8), facecolor="#0A0A1A")
fig.suptitle("Simulación del Sistema Solar", color="white", fontsize=16, fontweight="bold", y=0.97)

# Panel izquierdo: planetas interiores (hasta Marte ~1.5 AU)
ax_inner = fig.add_subplot(1, 2, 1, facecolor="#0A0A1A")
ax_inner.set_xlim(-2, 2)
ax_inner.set_ylim(-2, 2)
ax_inner.set_aspect("equal")
ax_inner.set_title("Planetas Interiores", color="white", fontsize=12, pad=8)
ax_inner.set_xlabel("x (AU)", color="#AAAAAA", fontsize=9)
ax_inner.set_ylabel("y (AU)", color="#AAAAAA", fontsize=9)
ax_inner.tick_params(colors="#555555")
for spine in ax_inner.spines.values():
    spine.set_edgecolor("#222244")

# Panel derecho: sistema solar completo (hasta Neptuno ~30 AU)
ax_outer = fig.add_subplot(1, 2, 2, facecolor="#0A0A1A")
ax_outer.set_xlim(-32, 32)
ax_outer.set_ylim(-32, 32)
ax_outer.set_aspect("equal")
ax_outer.set_title("Sistema Solar Completo", color="white", fontsize=12, pad=8)
ax_outer.set_xlabel("x (AU)", color="#AAAAAA", fontsize=9)
ax_outer.set_ylabel("y (AU)", color="#AAAAAA", fontsize=9)
ax_outer.tick_params(colors="#555555")
for spine in ax_outer.spines.values():
    spine.set_edgecolor("#222244")

# Añadir cuadrículas sutiles
for ax in [ax_inner, ax_outer]:
    ax.grid(True, color="#111133", linewidth=0.5, linestyle="--", alpha=0.5)

# Etiqueta de tiempo
time_text_inner = ax_inner.text(0.02, 0.97, '', transform=ax_inner.transAxes,
                                 color='white', fontsize=9, va='top')
time_text_outer = ax_outer.text(0.02, 0.97, '', transform=ax_outer.transAxes,
                                 color='white', fontsize=9, va='top')

# -------------------------------------------------------
# INICIALIZAR OBJETOS GRÁFICOS POR PLANETA
# -------------------------------------------------------
inner_planets_idx = [0, 1, 2, 3, 4]   # Sol, Mercurio, Venus, Tierra, Marte
outer_planets_idx = list(range(9))     # Todos

dots_inner = []
trails_inner = []
labels_inner = []

dots_outer = []
trails_outer = []
labels_outer = []

for idx in inner_planets_idx:
    p = PLANETS[idx]
    dot, = ax_inner.plot([], [], 'o', color=p["color"], markersize=p["size"],
                          zorder=p["zorder"], label=p["name"])
    trail, = ax_inner.plot([], [], '-', color=p["color"], linewidth=0.8,
                            alpha=0.4, zorder=p["zorder"] - 1)
    label = ax_inner.text(0, 0, p["name"], color=p["color"], fontsize=7,
                           va='bottom', ha='left', zorder=p["zorder"] + 1)
    dots_inner.append(dot)
    trails_inner.append(trail)
    labels_inner.append(label)

for idx in outer_planets_idx:
    p = PLANETS[idx]
    dot, = ax_outer.plot([], [], 'o', color=p["color"], markersize=p["size"] * 0.8,
                          zorder=p["zorder"], label=p["name"])
    trail, = ax_outer.plot([], [], '-', color=p["color"], linewidth=0.6,
                            alpha=0.35, zorder=p["zorder"] - 1)
    dots_outer.append(dot)
    trails_outer.append(trail)

ax_inner.legend(loc='lower right', fontsize=7, facecolor='#111122',
                 edgecolor='#333355', labelcolor='white', markerscale=0.8)
ax_outer.legend(loc='lower right', fontsize=7, facecolor='#111122',
                 edgecolor='#333355', labelcolor='white', markerscale=0.8)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# -------------------------------------------------------
# FUNCIÓN DE ANIMACIÓN
# -------------------------------------------------------
def init():
    for dot in dots_inner + dots_outer:
        dot.set_data([], [])
    for trail in trails_inner + trails_outer:
        trail.set_data([], [])
    for label in labels_inner:
        label.set_text('')
    time_text_inner.set_text('')
    time_text_outer.set_text('')
    return dots_inner + trails_inner + dots_outer + trails_outer + labels_inner + [time_text_inner, time_text_outer]

def update(frame):
    # Calcular rango de la estela
    start = max(0, frame - TRAIL_LENGTH)
    rows = df_anim.iloc[start:frame + 1]
    current = df_anim.iloc[frame]

    # Actualizar planetas interiores
    for i, idx in enumerate(inner_planets_idx):
        name = PLANETS[idx]["name"]
        x = current[f"{name}_x_au"]
        y = current[f"{name}_y_au"]
        dots_inner[i].set_data([x], [y])
        trails_inner[i].set_data(rows[f"{name}_x_au"].values, rows[f"{name}_y_au"].values)
        if name != "Sol":
            labels_inner[i].set_position((x + 0.05, y + 0.05))
            labels_inner[i].set_text(name)

    # Actualizar todos los planetas en vista exterior
    for i, idx in enumerate(outer_planets_idx):
        name = PLANETS[idx]["name"]
        x = current[f"{name}_x_au"]
        y = current[f"{name}_y_au"]
        dots_outer[i].set_data([x], [y])
        trails_outer[i].set_data(rows[f"{name}_x_au"].values, rows[f"{name}_y_au"].values)

    # Actualizar tiempo
    t_years = current["t"] / (86400 * 365)
    time_text_inner.set_text(f"t = {t_years:.2f} años")
    time_text_outer.set_text(f"t = {t_years:.2f} años")

    return dots_inner + trails_inner + dots_outer + trails_outer + labels_inner + [time_text_inner, time_text_outer]

# -------------------------------------------------------
# EJECUTAR ANIMACIÓN
# -------------------------------------------------------
print("Iniciando animación...")
print("  Cierra la ventana para terminar.")
ani = animation.FuncAnimation(fig, update, frames=N_FRAMES,
                               init_func=init, blit=True,
                               interval=ANIMATION_INTERVAL, repeat=True)

plt.show()

"""
Visualizador de órbitas planetarias (dinámico)
Requisitos: pip install matplotlib pandas numpy
Uso: coloca este script en la misma carpeta que orbits.csv y ejecuta con python
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------
CSV_FILE = "orbits.csv"   # debe estar en la misma carpeta que este script
ANIMATION_INTERVAL = 20   # ms entre frames (más bajo = más rápido)
TRAIL_LENGTH = 150        # cuántos puntos de estela muestra cada cuerpo
INNER_LIMIT_AU = 2.0      # AU para la vista interior
MAX_FRAMES = 600

# -------------------------------------------------------
# CARGAR DATOS
# -------------------------------------------------------
print(f"Cargando datos de {CSV_FILE}...")
df = pd.read_csv(CSV_FILE)
print(f"  Pasos cargados: {len(df)}")
print(f"  Tiempo total: {df['t'].iloc[-1] / (86400*365):.2f} años")

AU = 1.496e11

# Detectar nombres de cuerpos desde las columnas del CSV (columnas terminan en _x/_y/_z)
body_names = []
for col in df.columns:
    if col.endswith('_x'):
        body_names.append(col[:-2])

if len(body_names) == 0:
    raise RuntimeError('No se detectaron cuerpos en el CSV (columnas *_x)')

# Reducir frames si hay demasiados (para la animación no sea lenta)
N_FRAMES = len(df)
if N_FRAMES > MAX_FRAMES:
    step = max(1, N_FRAMES // MAX_FRAMES)
    df_anim = df.iloc[::step].reset_index(drop=True)
    print(f"  Reduciendo a {len(df_anim)} frames para la animación (1 de cada {step} pasos)")
else:
    df_anim = df
N_FRAMES = len(df_anim)

# Convertir posiciones a AU para todos los cuerpos detectados
for name in body_names:
    df_anim[f"{name}_x_au"] = df_anim[f"{name}_x"] / AU
    df_anim[f"{name}_y_au"] = df_anim[f"{name}_y"] / AU

# Figura y ejes
fig = plt.figure(figsize=(16, 8), facecolor="#0A0A1A")
fig.suptitle("Simulación del Sistema Solar", color="white", fontsize=16, fontweight="bold", y=0.97)

ax_inner = fig.add_subplot(1, 2, 1, facecolor="#0A0A1A")
ax_inner.set_xlim(-INNER_LIMIT_AU, INNER_LIMIT_AU)
ax_inner.set_ylim(-INNER_LIMIT_AU, INNER_LIMIT_AU)
ax_inner.set_aspect("equal")
ax_inner.set_title("Vista Interior (~{:.1f} AU)".format(INNER_LIMIT_AU), color="white", fontsize=12, pad=8)
ax_inner.set_xlabel("x (AU)", color="#AAAAAA", fontsize=9)
ax_inner.set_ylabel("y (AU)", color="#AAAAAA", fontsize=9)
ax_inner.tick_params(colors="#555555")
for spine in ax_inner.spines.values():
    spine.set_edgecolor("#222244")

ax_outer = fig.add_subplot(1, 2, 2, facecolor="#0A0A1A")
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

# INICIALIZAR OBJETOS GRÁFICOS DINÁMICAMENTE
N_BODIES = len(body_names)

# Generar una paleta de colores para todos los cuerpos
cmap = plt.cm.get_cmap('hsv', max(12, N_BODIES))
colors = [cmap(i) for i in range(N_BODIES)]

dots_inner = []
trails_inner = []
labels_inner = []

dots_outer = []
trails_outer = []

# Determinar índices de cuerpos interiores (distancia inicial menor que INNER_LIMIT_AU)
initial = df_anim.iloc[0]
initial_radii = []
for name in body_names:
    r = np.sqrt(initial[f"{name}_x_au"]**2 + initial[f"{name}_y_au"]**2)
    initial_radii.append(r)

inner_planets_idx = [i for i, r in enumerate(initial_radii) if r <= INNER_LIMIT_AU]
if len(inner_planets_idx) == 0:
    inner_planets_idx = list(range(min(5, N_BODIES)))

# Calcular límite exterior (max radio en todo el conjunto animado)
max_radius = 0.0
for name in body_names:
    radii = np.sqrt(df_anim[f"{name}_x_au"]**2 + df_anim[f"{name}_y_au"]**2)
    rmax = radii.max()
    if rmax > max_radius:
        max_radius = rmax
lim = max(32, np.ceil(max_radius * 1.1))
ax_outer.set_xlim(-lim, lim)
ax_outer.set_ylim(-lim, lim)

# Crear objetos gráficos para interiores
for idx in inner_planets_idx:
    name = body_names[idx]
    color = colors[idx]
    dot, = ax_inner.plot([], [], 'o', color=color, markersize=6, zorder=5, label=name)
    trail, = ax_inner.plot([], [], '-', color=color, linewidth=0.6, alpha=0.4, zorder=4)
    label = ax_inner.text(0, 0, name, color=color, fontsize=7, va='bottom', ha='left', zorder=6)
    dots_inner.append(dot)
    trails_inner.append(trail)
    labels_inner.append(label)

# Crear objetos gráficos para la vista exterior (todos los cuerpos)
for idx in range(N_BODIES):
    name = body_names[idx]
    color = colors[idx]
    dot, = ax_outer.plot([], [], 'o', color=color, markersize=3, zorder=3)
    trail, = ax_outer.plot([], [], '-', color=color, linewidth=0.5, alpha=0.3, zorder=2)
    dots_outer.append(dot)
    trails_outer.append(trail)

# Añadir leyenda solo para los cuerpos principales si existen
known = ["Sol", "Mercurio", "Venus", "Tierra", "Marte", "Jupiter", "Saturno", "Urano", "Neptuno"]
handles = []
labels = []
for k in known:
    if k in body_names:
        i = body_names.index(k)
        handles.append(plt.Line2D([0], [0], marker='o', color=colors[i], markersize=6, linestyle=''))
        labels.append(k)
if handles:
    ax_outer.legend(handles, labels, loc='lower right', fontsize=7, facecolor='#111122',
                    edgecolor='#333355')

plt.tight_layout(rect=[0, 0, 1, 0.95])

# FUNCIÓN DE ANIMACIÓN
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
        name = body_names[idx]
        x = current[f"{name}_x_au"]
        y = current[f"{name}_y_au"]
        dots_inner[i].set_data([x], [y])
        trails_inner[i].set_data(rows[f"{name}_x_au"].values, rows[f"{name}_y_au"].values)
        if name != "Sol":
            labels_inner[i].set_position((x + 0.05, y + 0.05))
            labels_inner[i].set_text(name)

    # Actualizar todos los cuerpos en vista exterior
    for i in range(N_BODIES):
        name = body_names[i]
        x = current[f"{name}_x_au"]
        y = current[f"{name}_y_au"]
        dots_outer[i].set_data([x], [y])
        trails_outer[i].set_data(rows[f"{name}_x_au"].values, rows[f"{name}_y_au"].values)

    # Actualizar tiempo
    t_years = current["t"] / (86400 * 365)
    time_text_inner.set_text(f"t = {t_years:.2f} años")
    time_text_outer.set_text(f"t = {t_years:.2f} años")

    return dots_inner + trails_inner + dots_outer + trails_outer + labels_inner + [time_text_inner, time_text_outer]

# EJECUTAR ANIMACIÓN
print("Iniciando animación...")
print("  Cierra la ventana para terminar.")
ani = animation.FuncAnimation(fig, update, frames=N_FRAMES,
                               init_func=init, blit=True,
                               interval=ANIMATION_INTERVAL, repeat=True)

plt.show()

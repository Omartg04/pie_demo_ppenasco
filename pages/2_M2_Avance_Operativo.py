"""
M2 — Avance Operativo de Tierra
PIE Demo · Puerto Peñasco, Sonora · Alan Rentería · MC 2027
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="M2 · Avance Operativo | Puerto Peñasco",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guardia de autenticación ──────────────────────────────────────────────────
if not st.session_state.get("autenticado", False):
    st.warning("Sesión no iniciada. Regresa al inicio.")
    st.stop()

# ── Rutas — resolución robusta para st.navigation ────────────────────────────
# __file__ puede ser inconsistente en páginas bajo st.navigation.
# Usamos sys.argv[0] (el Home.py que lanzó streamlit) como ancla del proyecto.
import sys

def _find_project_root() -> str:
    """Devuelve la carpeta raíz del proyecto (donde vive Home.py)."""
    # Opción 1: sys.argv[0] apunta al Home.py lanzado por streamlit
    argv0 = os.path.abspath(sys.argv[0])
    if os.path.isfile(argv0):
        return os.path.dirname(argv0)
    # Opción 2: __file__ relativo a pages/ → subir un nivel
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    if os.path.isdir(os.path.join(parent, "data")):
        return parent
    # Opción 3: directorio de trabajo actual
    return os.getcwd()

_ROOT          = _find_project_root()
_DATA          = os.path.join(_ROOT, "data")
RUTA_CONTACTOS = os.path.join(_DATA, "contactos_pp.csv")
RUTA_SPT       = os.path.join(_DATA, "spt_secciones_pp.csv")
RUTA_GEOJSON   = os.path.join(_DATA, "pp_secciones.geojson")

# ── Puerto Peñasco: coordenadas centro del municipio ─────────────────────────
LAT_PP = 31.3167
LON_PP = -113.5350
FECHA_CORTE = "26 mar 2026"

# ── Secciones sin cobertura activa ────────────────────────────────────────────
SECCIONES_SIN_COB = {634, 635, 648, 637, 1587}

# ── Paleta ────────────────────────────────────────────────────────────────────
COLORES = {
    "Prioritaria":   "#e63946",
    "Consolidacion": "#f4a261",
    "Mantenimiento": "#2a9d8f",
}

COLORES_SEGMENTO = {
    "Multiplicadores":  "#1a7a4a",
    "Activación":       "#007cab",
    "Persuasión":       "#d97706",
    "Primer contacto":  "#475569",
}

ICONOS_SEG = {
    "Multiplicadores":  "⭐",
    "Activación":       "🎯",
    "Persuasión":       "🤝",
    "Primer contacto":  "👋",
}

ETIQUETAS_ZONA = {
    "Prioritaria":   "🔴 Zona de máxima atención",
    "Consolidacion": "🟡 Zona de trabajo activo",
    "Mantenimiento": "🟢 Zona de base sólida",
}

ETIQUETAS_AMBITO = {
    "urbano":         "🏙️ Urbano",
    "rural_media":    "🌾 Rural costero",
    "rural_marginal": "🏜️ Rural marginal",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.metrica-card {
    background: #ffffff; border-radius: 10px;
    padding: 16px 20px; border: 1px solid #e2e8f0;
    border-top: 4px solid var(--accent);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metrica-card .label {
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px;
    color: #64748b; margin-bottom: 6px;
}
.metrica-card .valor {
    font-size: 1.9rem; font-weight: 700; color: #1e293b;
    line-height: 1; font-family: 'IBM Plex Mono', monospace;
}
.metrica-card .contexto { font-size: 0.78rem; color: #64748b; margin-top: 4px; }

.alerta-critica {
    background: #FDEDEC; border: 1px solid #e63946;
    border-left: 5px solid #e63946; border-radius: 8px;
    padding: 12px 16px; margin: 12px 0;
}
.alerta-critica .titulo { font-weight: 700; color: #c0392b; font-size: 0.85rem; }
.alerta-critica .detalle { color: #7f1d1d; font-size: 0.82rem; margin-top: 3px; }

.leyenda-puntos {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 12px 16px; font-size: 0.8rem;
}
.leyenda-puntos .dot {
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 6px; vertical-align: middle;
}

[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #004a6e !important; border-color: #007cab !important;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():
    contactos = pd.read_csv(RUTA_CONTACTOS)
    spt       = pd.read_csv(RUTA_SPT)

    # Normalizar celular: NaN = sin celular
    contactos["tiene_celular"] = contactos["celular"].notna()

    # Fecha de contacto
    contactos["fecha_contacto"] = pd.to_datetime(contactos["fecha_contacto"], errors="coerce")

    # Semana operativa desde la fecha más antigua
    fecha_min = contactos["fecha_contacto"].min()
    contactos["semana_num"] = ((contactos["fecha_contacto"] - fecha_min).dt.days // 7 + 1).clip(lower=1)

    # Enriquecer con clasificación SPT
    spt_dict = spt.set_index("seccion")[["clasificacion", "SPT", "ambito_iter", "arq_dominante", "tactica_recomendada"]].to_dict("index")
    contactos["clasificacion"] = contactos["seccion"].map(lambda s: spt_dict.get(s, {}).get("clasificacion", "Sin datos"))
    contactos["SPT"]           = contactos["seccion"].map(lambda s: spt_dict.get(s, {}).get("SPT", 0))
    contactos["ambito"]        = contactos["seccion"].map(lambda s: spt_dict.get(s, {}).get("ambito_iter", ""))
    contactos["arq"]           = contactos["seccion"].map(lambda s: spt_dict.get(s, {}).get("arq_dominante", ""))
    contactos["tactica"]       = contactos["seccion"].map(lambda s: spt_dict.get(s, {}).get("tactica_recomendada", ""))

    return contactos, spt, spt_dict


def cargar_geojson():
    """Carga el GeoJSON de secciones reales. Sin cache — evita stale None."""
    # Intentar múltiples rutas por si el root no resolvió bien
    rutas = [
        RUTA_GEOJSON,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "pp_secciones.geojson"),
        os.path.join(os.getcwd(), "data", "pp_secciones.geojson"),
    ]
    for ruta in rutas:
        ruta = os.path.normpath(ruta)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def resumen_por_seccion(df, spt_dict):
    grp = df.groupby("seccion").agg(
        total        =("seccion", "count"),
        con_celular  =("tiene_celular", "sum"),
        multiplicadores=("segmento", lambda x: (x == "Multiplicadores").sum()),
        activacion   =("segmento", lambda x: (x == "Activación").sum()),
        persuasion   =("segmento", lambda x: (x == "Persuasión").sum()),
        primer_c     =("segmento", lambda x: (x == "Primer contacto").sum()),
        ultima_fecha =("fecha_contacto", "max"),
    ).reset_index()

    grp["pct_celular"]  = (grp["con_celular"] / grp["total"] * 100).round(1)
    grp["seg_top"]      = grp[["multiplicadores", "activacion", "persuasion", "primer_c"]].idxmax(axis=1).map({
        "multiplicadores": "Multiplicadores",
        "activacion":      "Activación",
        "persuasion":      "Persuasión",
        "primer_c":        "Primer contacto",
    })
    grp["clasificacion"] = grp["seccion"].map(lambda s: spt_dict.get(s, {}).get("clasificacion", "Sin datos"))
    grp["SPT"]           = grp["seccion"].map(lambda s: spt_dict.get(s, {}).get("SPT", 0))
    grp["ambito"]        = grp["seccion"].map(lambda s: spt_dict.get(s, {}).get("ambito_iter", ""))
    grp["tactica"]       = grp["seccion"].map(lambda s: spt_dict.get(s, {}).get("tactica_recomendada", ""))

    return grp.sort_values("SPT", ascending=False)


# ════════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL MAPA
# ════════════════════════════════════════════════════════════════════════════════
def color_seg(seg):
    return COLORES_SEGMENTO.get(seg, "#94a3b8")


def construir_mapa_pp(df_f, resumen_sec, mostrar_puntos, mostrar_heatmap, spt_dict, geojson=None):
    m = folium.Map(
        location=[LAT_PP, LON_PP],
        zoom_start=13,
        tiles="CartoDB positron",
        control_scale=True,
    )
    Fullscreen(
        position="topleft",
        title="Pantalla completa",
        title_cancel="Salir",
        force_separate_button=True,
    ).add_to(m)

    # ── Lookup directo: seccion del GeoJSON = seccion real = clave en spt_dict ──
    # Con 27 secciones reales del INE no hay mapeo ficticio→real
    resumen_dict = resumen_sec.set_index("seccion").to_dict("index")

    # Pre-calcular rango SPT para opacidad
    spt_vals   = [v.get("SPT", 40) for v in spt_dict.values() if "SPT" in v]
    spt_min_m2 = min(spt_vals) if spt_vals else 30
    spt_max_m2 = max(spt_vals) if spt_vals else 75
    spt_rng_m2 = max(spt_max_m2 - spt_min_m2, 1)

    # ── Polígonos GeoJSON reales ──
    if geojson:
        for feature in geojson.get("features", []):
            sec     = int(feature["properties"].get("seccion", 0))
            datos   = spt_dict.get(sec, {})
            res     = resumen_dict.get(sec, {})
            clasif  = datos.get("clasificacion", "")
            spt_val = datos.get("SPT", 0)
            n       = int(res.get("total", 0))
            tactica = datos.get("tactica_recomendada", datos.get("tactica", ""))
            sin_cob = sec in SECCIONES_SIN_COB
            sec_fic = sec  # son la misma cosa

            color      = COLORES.get(clasif, "#94a3b8")
            fill_op    = 0.0 if sin_cob else max(0.12, min(0.45, 0.12 + (spt_val / 100) * 0.33))
            dash_array = "6 4" if sin_cob else None

            tooltip_html = (
                f"<div style='font-family:DM Sans,sans-serif;padding:4px 2px;'>"
                f"<b>§ {sec_fic}</b>"
                + (" &nbsp;<span style='background:#e63946;color:white;border-radius:10px;"
                   "padding:1px 7px;font-size:11px;'>⚠️ Sin cobertura</span>" if sin_cob else "")
                + f"<br><span style='color:#64748b;font-size:12px;'>{clasif} · SPT {spt_val:.1f}</span>"
                + (f"<br><span style='color:#475569;font-size:12px;'>{n} contactos</span>" if n > 0 else "")
                + f"<br><span style='color:#94a3b8;font-size:11px;'>{tactica}</span>"
                + "</div>"
            )

            fill_op = 0.10 if sin_cob else round(
                0.15 + ((spt_val - spt_min_m2) / spt_rng_m2) * 0.45, 2
            )

            style = {
                "fillColor":   color,
                "color":       "#e63946" if sin_cob else color,
                "weight":      2.5 if sin_cob else 1.8,
                "fillOpacity": fill_op,
                "opacity":     0.9,
                "dashArray":   dash_array,
            }

            folium.GeoJson(
                feature,
                style_function=lambda f, s=style: s,
                tooltip=folium.Tooltip(tooltip_html, sticky=True),
                name=f"§ {sec_fic}",
            ).add_to(m)

    else:
        # Fallback sin GeoJSON: círculos
        for _, row in resumen_sec.iterrows():
            sec   = int(row["seccion"])
            color = COLORES.get(row["clasificacion"], "#94a3b8")
            lat_c = df_f[df_f["seccion"] == sec]["latitud"].mean()
            lon_c = df_f[df_f["seccion"] == sec]["longitud"].mean()
            if pd.isna(lat_c):
                continue
            folium.Circle(
                location=[lat_c, lon_c], radius=min(600, max(100, int(row["total"]) * 1.2)),
                color=color, fill=True, fill_color=color, fill_opacity=0.18, weight=2.5,
                tooltip=f"§ {sec} · SPT {row['SPT']:.1f} · {int(row['total'])} contactos",
            ).add_to(m)

        # Marcadores fallback para sin cobertura
        for sec in SECCIONES_SIN_COB:
            datos = spt_dict.get(sec, {})
            coords_fallback = {1501:[31.319,-113.531], 1511:[31.270,-113.490], 1517:[31.240,-113.450]}
            loc = coords_fallback.get(sec, [LAT_PP, LON_PP])
            folium.Marker(
                location=loc,
                icon=folium.DivIcon(
                    html=(f"<div style='background:#e63946;color:white;border-radius:50%;"
                          f"width:34px;height:34px;display:flex;align-items:center;justify-content:center;"
                          f"font-size:16px;font-weight:700;border:2px solid white;'>⚠️</div>"),
                    icon_size=(34, 34), icon_anchor=(17, 17),
                ),
                tooltip=f"⚠️ § {sec} — SIN COBERTURA · SPT {datos.get('SPT',0):.1f}",
            ).add_to(m)

    # ── Heatmap ──
    if mostrar_heatmap:
        coords_h = df_f.dropna(subset=["latitud", "longitud"])[["latitud", "longitud"]].values.tolist()
        if coords_h:
            HeatMap(
                coords_h, radius=18, blur=15, min_opacity=0.3,
                gradient={"0.4": "#007cab", "0.65": "#f4a261", "1": "#e63946"},
            ).add_to(m)

    # ── Puntos individuales ──
    if mostrar_puntos:
        cluster = MarkerCluster(
            name="Contactos",
            options={"maxClusterRadius": 40, "spiderfyOnMaxZoom": True},
        )
        df_coords = df_f.dropna(subset=["latitud", "longitud"])

        for _, row in df_coords.iterrows():
            seg   = row.get("segmento", "Sin dato")
            color = color_seg(seg)
            icono = ICONOS_SEG.get(seg, "•")
            cel   = row.get("celular", "")
            tiene_cel = pd.notna(cel)

            cel_html = (
                f"<div style='margin:5px 0;'>"
                f"<a href='https://wa.me/52{int(cel)}' target='_blank' "
                f"style='color:#25D366;font-weight:700;text-decoration:none;font-size:13px;'>"
                f"📲 {int(cel)} · WhatsApp</a></div>"
                if tiene_cel else
                "<div style='color:#94a3b8;font-size:11px;margin:5px 0;'>📱 Sin celular registrado</div>"
            )

            popup_html = f"""
            <div style='font-family:"DM Sans",sans-serif;min-width:200px;max-width:250px;'>
                <div style='background:#f8fafc;border-radius:8px 8px 0 0;
                            padding:10px 12px;border-bottom:1px solid #e2e8f0;'>
                    <span style='background:{color};color:#fff;padding:2px 9px;
                                 border-radius:12px;font-size:11px;font-weight:700;'>
                        {icono} {seg}
                    </span>
                </div>
                <div style='padding:10px 12px;'>
                    <div style='font-weight:700;font-size:13px;color:#1e293b;margin-bottom:4px;'>
                        {row.get('nombre','Contacto')}
                    </div>
                    <div style='color:#64748b;font-size:11px;margin-bottom:4px;'>
                        § {int(row.get('seccion',0))} · {row.get('colonia','Puerto Peñasco')}
                    </div>
                    {cel_html}
                    <div style='color:#94a3b8;font-size:10px;margin-top:6px;'>
                        {str(row.get('fecha_contacto',''))[:10]}
                    </div>
                </div>
            </div>
            """
            folium.CircleMarker(
                location=[row["latitud"], row["longitud"]],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.82,
                weight=1.5,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{icono} {row.get('nombre','').split()[0]} · § {int(row.get('seccion',0))}",
            ).add_to(cluster)

        cluster.add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    return m


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════

# ── Carga ─────────────────────────────────────────────────────────────────────
with st.spinner("Cargando padrón de Puerto Peñasco..."):
    df, spt_df, spt_dict = cargar_datos()
    geojson = cargar_geojson()

# Enriquecer spt_dict con seccion_ine
for _, row in spt_df.iterrows():
    sec = int(row["seccion"])
    if sec in spt_dict and "seccion_ine" in spt_df.columns:
        spt_dict[sec]["seccion_ine"] = int(row.get("seccion_ine", 0))

total_contactos = len(df)
ultima_fecha    = df["fecha_contacto"].max()

# ── Sidebar — filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.05rem;font-weight:700;margin-bottom:14px;'>🔎 Filtros del mapa</div>",
        unsafe_allow_html=True,
    )

    clasif_opts = ["Prioritaria", "Consolidacion", "Mantenimiento"]
    clasif_sel  = st.multiselect(
        "Tipo de zona",
        options=clasif_opts,
        default=clasif_opts,
    )

    seg_opts = ["Multiplicadores", "Activación", "Persuasión", "Primer contacto"]
    seg_sel  = st.multiselect(
        "Segmento operativo",
        options=seg_opts,
        default=seg_opts,
    )

    secciones_disp = sorted(df["seccion"].dropna().unique().astype(int))
    opciones_sec   = ["Todas las secciones"] + [f"{s}" for s in secciones_disp]
    seleccion_sec  = st.selectbox("Ver ficha de sección", opciones_sec)

    st.markdown("---")
    st.markdown("**🗺️ Opciones del mapa**")
    mostrar_puntos  = st.toggle("Contactos individuales", value=True)
    mostrar_heatmap = st.toggle("Densidad (heatmap)",     value=False)

    st.markdown("---")
    with st.expander("ℹ️ Cómo leer el mapa"):
        st.markdown("""
**M2 — Avance Operativo**

Muestra dónde van las brigadas y si el esfuerzo coincide con las zonas prioritarias.

- **Círculos grandes:** secciones — radio ∝ contactos levantados
  - 🔴 Máxima atención · 🟡 Trabajo activo · 🟢 Base sólida
- **⚠️ Marcador rojo:** sección prioritaria sin cobertura
- **Puntos pequeños:** contactos individuales coloreados por segmento
- **Heatmap:** densidad de trabajo de campo

*Corte operativo: 26 mar 2026*
        """)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
     border-radius:16px;padding:28px 32px 24px;margin-bottom:24px;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div>
    <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
         color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>
      Tu mapa de decisiones · Puerto Peñasco, Sonora
    </div>
    <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
      ¿Cómo vamos en campo?
    </div>
    <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-top:6px;'>
      Corte al {FECHA_CORTE} · Alan Rentería · MC 2027 · {total_contactos:,} contactos en padrón
    </div>
    <div style='margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.15);'>
      <div style='font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.50);
           text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px;'>
        Qué muestra este módulo
      </div>
      <div style='display:flex;flex-wrap:wrap;gap:7px;margin-bottom:10px;'>
        <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
             border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
          📍 Mapa de contactos levantados por brigadas
        </span>
        <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
             border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
          📈 Avance semanal de cobertura territorial
        </span>
        <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
             border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
          🔴 Alertas de secciones prioritarias sin contactos
        </span>
        <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
             border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
          🧩 Segmentos de votante por sección
        </span>
      </div>
      <div style='font-size:0.82rem;color:rgba(255,255,255,0.75);line-height:1.55;
           background:rgba(0,0,0,0.15);border-radius:10px;padding:10px 14px;'>
        <strong style='color:#ffffff;'>Para qué sirve:</strong>
        Ver en tiempo real cuánto terreno lleva cubierto la campaña y dónde están los huecos.
        Cada punto en el mapa es una persona contactada por una brigada.
        Las secciones en rojo son prioritarias y aún no tienen operativo —
        son la instrucción más urgente para el coordinador de campo.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Alertas críticas ──────────────────────────────────────────────────────────
secciones_con_contacto = set(df["seccion"].dropna().astype(int))
todas_secciones        = set(spt_dict.keys())
secciones_sin_contacto = todas_secciones - secciones_con_contacto

prioritarias_sin_cob = [
    (s, spt_dict[s]["SPT"])
    for s in SECCIONES_SIN_COB
    if s in spt_dict
]

if prioritarias_sin_cob:
    detalle = " · ".join([
        f"§ {s} (SPT {spt:.0f} · 0 contactos)"
        for s, spt in sorted(prioritarias_sin_cob, key=lambda x: -x[1])
    ])
    st.markdown(f"""
    <div class='alerta-critica'>
        <div class='titulo'>⚠️ {len(prioritarias_sin_cob)} secciones prioritarias sin cobertura — brigada urgente</div>
        <div class='detalle'>{detalle} — Estas zonas tienen el mayor potencial electoral de Puerto Peñasco
        y no han recibido visita de brigadas.</div>
    </div>
    """, unsafe_allow_html=True)

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df_f = df[
    df["clasificacion"].isin(clasif_sel) &
    df["segmento"].isin(seg_sel)
].copy()

resumen_sec = resumen_por_seccion(df_f, spt_dict)

# ── Tarjetas de métricas ──────────────────────────────────────────────────────
n_filtrado       = len(df_f)
pct_celular_f    = df_f["tiene_celular"].mean() * 100
alcance_f        = int(n_filtrado * 3.2)
n_sin_cob_total  = len(secciones_sin_contacto)

seg_counts = df["segmento"].value_counts()
n_mult   = seg_counts.get("Multiplicadores", 0)
n_activ  = seg_counts.get("Activación",      0)
n_pers   = seg_counts.get("Persuasión",      0)
n_primer = seg_counts.get("Primer contacto", 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metrica-card' style='--accent:#007cab;'>
        <div class='label'>Contactos en padrón</div>
        <div class='valor'>{n_filtrado:,}</div>
        <div class='contexto'>de {total_contactos:,} totales · corte {FECHA_CORTE}</div>
        <div style='margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;
             font-size:0.75rem;color:#0891b2;font-weight:600;'>
            ~{alcance_f:,} personas · alcance estimado (3.2x hogar)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    color_sec = "#2a9d8f" if n_sin_cob_total == 0 else "#e63946"
    n_cubiertas = len(todas_secciones) - n_sin_cob_total
    st.markdown(f"""
    <div class='metrica-card' style='--accent:{color_sec};'>
        <div class='label'>Secciones con presencia</div>
        <div class='valor'>{n_cubiertas}<span style='font-size:1rem;color:#94a3b8'> / {len(todas_secciones)}</span></div>
        <div class='contexto'>{n_sin_cob_total} sección(es) aún sin operativo activo</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color_cel = "#2a9d8f" if pct_celular_f >= 60 else "#f4a261"
    st.markdown(f"""
    <div class='metrica-card' style='--accent:{color_cel};'>
        <div class='label'>Con celular válido</div>
        <div class='valor'>{pct_celular_f:.0f}<span style='font-size:1rem;color:#94a3b8'>%</span></div>
        <div class='contexto'>{int(df_f['tiene_celular'].sum()):,} contactos activables por WhatsApp/SMS</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    base = max(total_contactos, 1)
    st.markdown(f"""
    <div class='metrica-card' style='--accent:#1a7a4a;'>
        <div class='label'>Segmentos identificados</div>
        <div style='margin-top:8px;font-size:0.84rem;line-height:1.9;'>
            <div>
                <span style='color:#1a7a4a;font-weight:700;font-family:"IBM Plex Mono",monospace;'>
                    {n_mult:,}</span>
                <span style='color:#64748b;margin-left:6px;'>⭐ Multiplicadores</span>
            </div>
            <div>
                <span style='color:#007cab;font-weight:700;font-family:"IBM Plex Mono",monospace;'>
                    {n_activ:,}</span>
                <span style='color:#64748b;margin-left:6px;'>🎯 Activación</span>
            </div>
            <div>
                <span style='color:#d97706;font-weight:700;font-family:"IBM Plex Mono",monospace;'>
                    {n_pers:,}</span>
                <span style='color:#64748b;margin-left:6px;'>🤝 Persuasión</span>
            </div>
            <div>
                <span style='color:#475569;font-weight:700;font-family:"IBM Plex Mono",monospace;'>
                    {n_primer:,}</span>
                <span style='color:#64748b;margin-left:6px;'>👋 Primer contacto</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Mapa ──────────────────────────────────────────────────────────────────────
col_mapa, col_leyenda = st.columns([4, 1])

with col_leyenda:
    st.markdown("""
    <div class='leyenda-puntos'>
        <div style='font-weight:700;font-size:0.8rem;margin-bottom:10px;color:#1e293b;'>LEYENDA</div>
        <div style='font-weight:600;font-size:0.72rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:6px;'>Zona (SPT)</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'>
            <span class='dot' style='background:#e63946'></span>Máxima atención</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'>
            <span class='dot' style='background:#f4a261'></span>Trabajo activo</div>
        <div style='margin-bottom:12px;font-size:0.8rem;'>
            <span class='dot' style='background:#2a9d8f'></span>Base sólida</div>
        <div style='font-weight:600;font-size:0.72rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:6px;'>Segmento</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'>
            <span class='dot' style='background:#1a7a4a'></span>⭐ Multiplicadores</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'>
            <span class='dot' style='background:#007cab'></span>🎯 Activación</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'>
            <span class='dot' style='background:#d97706'></span>🤝 Persuasión</div>
        <div style='margin-bottom:12px;font-size:0.8rem;'>
            <span class='dot' style='background:#475569'></span>👋 Primer contacto</div>
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.4;'>
            ⚠️ = sección prioritaria sin cobertura · requiere brigada urgente
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_mapa:
    with st.spinner("Construyendo mapa de Puerto Peñasco..."):
        mapa = construir_mapa_pp(
            df_f, resumen_sec, mostrar_puntos, mostrar_heatmap, spt_dict, geojson
        )
        st_folium(mapa, width="100%", height=520, returned_objects=[])

# ── Ficha de sección ──────────────────────────────────────────────────────────
if seleccion_sec != "Todas las secciones":
    sec_id  = int(seleccion_sec)
    spt_d   = spt_dict.get(sec_id, {})

    df_sec      = df[df["seccion"] == sec_id]
    n_sec       = len(df_sec)
    pct_cel_sec = df_sec["tiene_celular"].mean() * 100 if n_sec > 0 else 0

    clasif   = spt_d.get("clasificacion", "")
    spt_val  = spt_d.get("SPT", 0)
    color_z  = COLORES.get(clasif, "#94a3b8")
    etiq_z   = ETIQUETAS_ZONA.get(clasif, clasif)
    ambito_z = ETIQUETAS_AMBITO.get(spt_d.get("ambito_iter", ""), "")
    arq      = spt_d.get("arq_dominante", "")
    tactica  = spt_d.get("tactica_recomendada", "")

    sin_operativo  = n_sec == 0
    es_prioritaria = clasif == "Prioritaria"

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#004a6e,#007cab);
                border-radius:12px;padding:20px 24px;margin-bottom:8px;
                border-left:5px solid {color_z};'>
        <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
            <div>
                <div style='color:#94a3b8;font-size:0.72rem;font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;'>SECCIÓN</div>
                <div style='color:#fff;font-size:2.2rem;font-weight:700;
                            font-family:"IBM Plex Mono",monospace;line-height:1;'>{sec_id}</div>
            </div>
            <div style='flex:1;'>
                <span style='background:{color_z};color:#fff;padding:4px 12px;
                             border-radius:20px;font-size:0.78rem;font-weight:700;'>{etiq_z}</span>
                <span style='background:rgba(255,255,255,0.1);color:#94a3b8;
                             padding:4px 12px;border-radius:20px;font-size:0.78rem;margin-left:6px;'>{ambito_z}</span>
                <div style='color:#cbd5e1;font-size:0.85rem;margin-top:8px;'>
                    SPT <b style='color:#fff'>{spt_val:.1f}</b> &nbsp;·&nbsp;
                    Arquetipo <b style='color:#fff'>{arq}</b> &nbsp;·&nbsp; {tactica}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if es_prioritaria and sin_operativo:
        st.markdown("""
        <div class='alerta-critica'>
            <div class='titulo'>⚠️ Sección prioritaria sin contactos registrados</div>
            <div class='detalle'>Esta sección tiene el mayor potencial electoral de Puerto Peñasco
            y no ha recibido visita del operativo. Requiere atención inmediata.</div>
        </div>
        """, unsafe_allow_html=True)
    elif n_sec > 0:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='metrica-card' style='--accent:#007cab;'>
                <div class='label'>Contactos levantados</div>
                <div class='valor'>{n_sec:,}</div>
                <div class='contexto'>en esta sección</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='metrica-card' style='--accent:#7c3aed;'>
                <div class='label'>Con celular</div>
                <div class='valor'>{pct_cel_sec:.0f}<span style='font-size:1rem;color:#94a3b8'>%</span></div>
                <div class='contexto'>{int(df_sec['tiene_celular'].sum()):,} activables</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            seg_dom = df_sec["segmento"].value_counts().index[0] if n_sec > 0 else "—"
            icono_dom = ICONOS_SEG.get(seg_dom, "•")
            color_dom = COLORES_SEGMENTO.get(seg_dom, "#94a3b8")
            st.markdown(f"""
            <div class='metrica-card' style='--accent:{color_dom};'>
                <div class='label'>Segmento dominante</div>
                <div class='valor' style='font-size:1.4rem;'>{icono_dom} {seg_dom}</div>
                <div class='contexto'>{(df_sec['segmento'] == seg_dom).sum():,} contactos en este perfil</div>
            </div>
            """, unsafe_allow_html=True)

        # Distribución de segmentos
        seg_dist = df_sec["segmento"].value_counts().reset_index()
        seg_dist.columns = ["Segmento", "Contactos"]
        seg_dist["Color"] = seg_dist["Segmento"].map(COLORES_SEGMENTO)

        fig_seg = px.bar(
            seg_dist, x="Contactos", y="Segmento", orientation="h",
            color="Segmento",
            color_discrete_map=COLORES_SEGMENTO,
            title=f"Distribución de segmentos · § {sec_id}",
        )
        fig_seg.update_layout(
            height=220, showlegend=False,
            margin=dict(l=0, r=20, t=40, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans"),
            title_font_size=13,
        )
        fig_seg.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig_seg.update_yaxes(showgrid=False)
        st.plotly_chart(fig_seg, use_container_width=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Tabla de secciones ────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:1.0rem;font-weight:700;color:#1e293b;"
    "border-bottom:2px solid #e2e8f0;padding-bottom:8px;margin-bottom:16px;'>"
    "📋 Resumen por sección</div>",
    unsafe_allow_html=True,
)

tabla = resumen_sec[["seccion", "clasificacion", "SPT", "total", "con_celular", "pct_celular", "seg_top", "tactica"]].copy()
tabla.columns = ["Sección", "Clasificación", "SPT", "Contactos", "Con celular", "% celular", "Segmento top", "Táctica"]
tabla["Sección"] = tabla["Sección"].apply(lambda x: f"§ {int(x)}")
tabla["SPT"]     = tabla["SPT"].round(1)

st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True,
    column_config={
        "SPT":         st.column_config.NumberColumn(format="%.1f"),
        "% celular":   st.column_config.NumberColumn(format="%.1f %%"),
        "Contactos":   st.column_config.NumberColumn(format="%d"),
        "Con celular": st.column_config.NumberColumn(format="%d"),
    },
)

# ── Gráfico avance por semana ─────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:1.0rem;font-weight:700;color:#1e293b;"
    "border-bottom:2px solid #e2e8f0;padding-bottom:8px;margin:24px 0 16px;'>"
    "📈 Avance semanal del operativo</div>",
    unsafe_allow_html=True,
)

semana_labels = {
    1: "Sem 1 · 15-21 ene",
    2: "Sem 2 · 22-28 ene",
    3: "Sem 3 · 29 ene-4 feb",
    4: "Sem 4 · 5-11 feb",
    5: "Sem 5 · 12-18 feb",
    6: "Sem 6 · 19-25 feb",
    7: "Sem 7 · 26 feb-4 mar",
    8: "Sem 8 · 5-11 mar",
    9: "Sem 9 · 12-18 mar",
    10: "Sem 10 · 19-25 mar",
}

semanal = (
    df.groupby(["semana_num", "segmento"])
    .size()
    .reset_index(name="n")
)
semanal["semana_label"] = semanal["semana_num"].map(semana_labels).fillna(
    semanal["semana_num"].map(lambda x: f"Sem {x}")
)

fig_sem = px.bar(
    semanal,
    x="semana_label", y="n", color="segmento",
    color_discrete_map=COLORES_SEGMENTO,
    labels={"semana_label": "Semana", "n": "Contactos", "segmento": "Segmento"},
    title="Contactos levantados por semana · Puerto Peñasco",
    barmode="stack",
)
fig_sem.update_layout(
    height=320,
    margin=dict(l=0, r=0, t=50, b=60),
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
    title_font_size=14,
)
fig_sem.update_xaxes(showgrid=False, tickangle=-30)
fig_sem.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
st.plotly_chart(fig_sem, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:32px;padding-top:14px;border-top:1px solid #e2e8f0;
     text-align:center;font-size:0.73rem;color:#94a3b8;'>
    Data & AI Inclusion Tech · PIE Demo · Alan Rentería · MC · Puerto Peñasco 2027 · Confidencial
</div>
""", unsafe_allow_html=True)
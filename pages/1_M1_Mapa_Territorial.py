"""
M1 — Mapa Territorial · ¿A dónde voy primero?
PIE Demo · Puerto Peñasco, Sonora · Alan Rentería · MC 2027
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import json, os, sys

# ── Configuración ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M1 · Mapa Territorial | Puerto Peñasco",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guardia de autenticación ──────────────────────────────────────────────────
if not st.session_state.get("autenticado", False):
    st.warning("Sesión no iniciada. Regresa al inicio.")
    st.stop()

# ── Rutas robustas ────────────────────────────────────────────────────────────
def _find_root():
    argv0 = os.path.abspath(sys.argv[0])
    if os.path.isfile(argv0):
        return os.path.dirname(argv0)
    here   = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    if os.path.isdir(os.path.join(parent, "data")):
        return parent
    return os.getcwd()

_ROOT        = _find_root()
_DATA        = os.path.join(_ROOT, "data")
RUTA_SPT     = os.path.join(_DATA, "spt_secciones_pp.csv")
RUTA_GEOJSON = os.path.join(_DATA, "pp_secciones.geojson")

LAT_PP = 31.318
LON_PP = -113.530
FECHA_CORTE = "26 mar 2026"

SECCIONES_SIN_COB = {634, 635, 648, 637, 1587}

# ── Paleta SPT — gradiente azul PIE ──────────────────────────────────────────
# Prioritaria: rojo · Consolidación: naranja · Mantenimiento: verde
# Opacidad de relleno proporcional al SPT dentro de cada grupo

COLOR_CLASIF = {
    "Prioritaria":   "#e63946",
    "Consolidacion": "#f4a261",
    "Mantenimiento": "#2a9d8f",
}
BG_CLASIF = {
    "Prioritaria":   "#fef2f2",
    "Consolidacion": "#fffbeb",
    "Mantenimiento": "#f0fdf4",
}
ICONO_AMBITO = {
    "urbano":         "🏙️",
    "rural_media":    "🌾",
    "rural_marginal": "🏜️",
}
LABEL_CLASIF = {
    "Prioritaria":   "🔴 Máxima atención",
    "Consolidacion": "🟡 Trabajo activo",
    "Mantenimiento": "🟢 Base sólida",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #004a6e !important; border-color: #007cab !important;
}

.ranking-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 10px;
    margin-bottom: 6px; cursor: pointer;
    border-left: 4px solid transparent;
    background: #f8fafc; transition: background 0.15s;
}
.ranking-row:hover { background: #f1f5f9; }
.rank-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; font-weight: 600;
    color: #94a3b8; min-width: 20px;
}
.rank-sec {
    font-size: 1.0rem; font-weight: 700;
    color: #004a6e; min-width: 44px;
}
.rank-spt {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem; font-weight: 600;
    color: white; border-radius: 20px;
    padding: 2px 9px; min-width: 52px;
    text-align: center;
}
.rank-ambito { font-size: 0.76rem; color: #64748b; flex: 1; }
.rank-alerta {
    font-size: 0.68rem; background: #e63946; color: white;
    border-radius: 20px; padding: 1px 7px; font-weight: 600;
    white-space: nowrap;
}

.ficha-header {
    background: linear-gradient(135deg, #004a6e, #007cab);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 14px;
}
.ficha-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem; font-weight: 700; color: white; line-height: 1;
}
.ficha-badge {
    display: inline-block; border-radius: 20px;
    padding: 3px 12px; font-size: 0.78rem; font-weight: 700;
    color: white; margin: 6px 4px 0 0;
}
.score-bar-wrap {
    background: #e2e8f0; border-radius: 6px; height: 8px;
    overflow: hidden; margin-top: 4px;
}
.score-bar-fill {
    height: 8px; border-radius: 6px;
    background: linear-gradient(90deg, #007cab, #00c0ff);
}
.score-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
}
.score-label {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; color: #64748b; margin-bottom: 4px;
}
.score-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem; font-weight: 600; color: #1e293b; line-height: 1;
}

.section-hdr {
    font-size: 1.0rem; font-weight: 700; color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px; margin: 24px 0 16px;
}

.leyenda-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.80rem; margin-bottom: 6px;
}
.leyenda-dot {
    width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():
    spt = pd.read_csv(RUTA_SPT).sort_values("SPT", ascending=False).reset_index(drop=True)
    spt["rank"] = range(1, len(spt) + 1)
    return spt

@st.cache_data(ttl=3600, show_spinner=False)
def cargar_geojson():
    if not os.path.exists(RUTA_GEOJSON):
        return None
    with open(RUTA_GEOJSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ════════════════════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL MAPA
# ════════════════════════════════════════════════════════════════════════════════
def construir_mapa_m1(spt_df, geojson, seccion_sel=None):
    m = folium.Map(
        location=[LAT_PP, LON_PP],
        zoom_start=13,
        tiles="CartoDB positron",
        control_scale=True,
    )
    Fullscreen(position="topleft", title="Pantalla completa",
               title_cancel="Salir", force_separate_button=True).add_to(m)

    if geojson is None:
        return m

    # Lookup sec -> datos SPT
    spt_dict = spt_df.set_index("seccion").to_dict("index")
    spt_min  = spt_df["SPT"].min()
    spt_max  = spt_df["SPT"].max()
    spt_rng  = max(spt_max - spt_min, 1)

    for feature in geojson.get("features", []):
        sec   = int(feature["properties"].get("seccion", 0))
        datos = spt_dict.get(sec, {})
        if not datos:
            continue

        clasif   = datos.get("clasificacion", "Consolidacion")
        spt_val  = datos.get("SPT", 40)
        sin_cob  = sec in SECCIONES_SIN_COB
        selected = (seccion_sel is not None and sec == seccion_sel)

        color    = COLOR_CLASIF.get(clasif, "#94a3b8")
        # Opacidad proporcional al SPT — más urgente = más intenso
        fill_op  = 0.10 if sin_cob else round(0.15 + ((spt_val - spt_min) / spt_rng) * 0.50, 2)
        weight   = 3.5 if selected else (2.5 if sin_cob else 1.8)
        border_c = "#1e293b" if selected else ("#e63946" if sin_cob else color)
        dash     = "6 4" if sin_cob else None

        ambito   = datos.get("ambito_iter", "")
        tactica  = datos.get("tactica_recomendada", "")
        rank     = datos.get("rank", "—")

        tooltip_html = (
            f"<div style='font-family:DM Sans,sans-serif;min-width:180px;padding:2px;'>"
            f"<div style='font-size:1.1rem;font-weight:700;color:#004a6e;margin-bottom:4px;'>"
            f"§ {sec}"
            + (f" &nbsp;<span style='background:#e63946;color:white;border-radius:10px;"
               f"padding:1px 7px;font-size:10px;font-weight:700;'>⚠️ Sin cobertura</span>"
               if sin_cob else "") +
            f"</div>"
            f"<div style='display:flex;gap:6px;margin-bottom:6px;flex-wrap:wrap;'>"
            f"<span style='background:{color};color:white;border-radius:12px;"
            f"padding:2px 9px;font-size:11px;font-weight:700;'>{clasif}</span>"
            f"<span style='background:#e2e8f0;color:#475569;border-radius:12px;"
            f"padding:2px 9px;font-size:11px;'>SPT {spt_val:.1f}</span>"
            f"<span style='background:#e2e8f0;color:#475569;border-radius:12px;"
            f"padding:2px 9px;font-size:11px;'>#{rank}</span>"
            f"</div>"
            f"<div style='font-size:11px;color:#475569;'>{ICONO_AMBITO.get(ambito,'')} {ambito.replace('_',' ').title()}</div>"
            f"<div style='font-size:11px;color:#94a3b8;margin-top:4px;'>{tactica}</div>"
            f"</div>"
        )

        style = {
            "fillColor":   color,
            "color":       border_c,
            "weight":      weight,
            "fillOpacity": fill_op,
            "opacity":     0.95,
            "dashArray":   dash,
        }

        folium.GeoJson(
            feature,
            style_function=lambda f, s=style: s,
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
        ).add_to(m)

    # Si hay sección seleccionada, zoom a ella
    if seccion_sel and geojson:
        for feat in geojson["features"]:
            if int(feat["properties"]["seccion"]) == seccion_sel:
                from shapely.geometry import shape
                poly = shape(feat["geometry"])
                c    = poly.centroid
                m.location = [c.y, c.x]
                m.zoom_start = 15
                break

    return m


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
with st.spinner("Cargando mapa territorial..."):
    spt_df  = cargar_datos()
    geojson = cargar_geojson()

n_secciones    = len(spt_df)
n_prioritarias = (spt_df["clasificacion"] == "Prioritaria").sum()
n_sin_cob      = len(SECCIONES_SIN_COB)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.05rem;font-weight:700;margin-bottom:16px;'>🗺️ Opciones</div>",
        unsafe_allow_html=True,
    )

    clasif_opts = ["Todas", "Prioritaria", "Consolidacion", "Mantenimiento"]
    clasif_fil  = st.selectbox("Filtrar por zona", clasif_opts)

    ambito_opts = ["Todos", "urbano", "rural_media", "rural_marginal"]
    ambito_fil  = st.selectbox("Filtrar por ámbito", ambito_opts,
                               format_func=lambda x: x if x == "Todos"
                               else ICONO_AMBITO.get(x,"") + " " + x.replace("_"," ").title())

    st.markdown("---")
    st.markdown("**Seleccionar sección**")
    secs_disp = ["— Ver todas —"] + [f"§ {int(r.seccion)}" for _, r in spt_df.iterrows()]
    sec_pick  = st.selectbox("Ir a sección", secs_disp, label_visibility="collapsed")
    sec_sel   = None if sec_pick == "— Ver todas —" else int(sec_pick.replace("§ ",""))

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem;color:#94a3b8;line-height:1.6;'>
    <b style='color:#e8edf5;'>Cómo leer el mapa</b><br>
    Color = clasificación SPT<br>
    Intensidad = urgencia relativa<br>
    Borde punteado = sin cobertura<br><br>
    🔴 Máxima atención<br>
    🟡 Trabajo activo<br>
    🟢 Base sólida<br>
    ⚠️ Sin brigada activa
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
     border-radius:16px;padding:28px 32px 24px;margin-bottom:24px;
     position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
       color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>
    Tu línea base propia · Puerto Peñasco, Sonora
  </div>
  <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
    ¿A dónde voy primero?
  </div>
  <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-top:6px;'>
    {n_secciones} secciones electorales · {n_prioritarias} prioritarias ·
    {n_sin_cob} sin cobertura · corte {FECHA_CORTE}
  </div>
  <div style='margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.15);'>
    <div style='font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.50);
         text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px;'>
      Qué muestra este módulo
    </div>
    <div style='display:flex;flex-wrap:wrap;gap:7px;margin-bottom:10px;'>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
        🗺️ Mapa coroplético de prioridad por sección
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
        📊 Score SPT: encuesta + historial + demografía
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
        🔴 Alertas de zonas sin operativo activo
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#e0f2fe;font-weight:600;'>
        📋 Ficha detallada por sección al hacer clic
      </span>
    </div>
    <div style='font-size:0.82rem;color:rgba(255,255,255,0.75);line-height:1.55;
         background:rgba(0,0,0,0.15);border-radius:10px;padding:10px 14px;'>
      <strong style='color:#ffffff;'>Para qué sirve:</strong>
      Saber exactamente a qué sección mandar las brigadas primero.
      El mapa combina intención de voto, solidez electoral histórica y perfil demográfico
      en un solo número — el SPT. Las secciones más oscuras son las más urgentes.
      Las marcadas en rojo no tienen ningún contacto levantado todavía.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Aplicar filtros al ranking ────────────────────────────────────────────────
df_fil = spt_df.copy()
if clasif_fil != "Todas":
    df_fil = df_fil[df_fil["clasificacion"] == clasif_fil]
if ambito_fil != "Todos":
    df_fil = df_fil[df_fil["ambito_iter"] == ambito_fil]

# ── Layout: mapa | ranking ────────────────────────────────────────────────────
col_mapa, col_ranking = st.columns([3, 1], gap="medium")

with col_mapa:
    with st.spinner("Construyendo mapa..."):
        mapa = construir_mapa_m1(spt_df, geojson, sec_sel)
        mapa_data = st_folium(mapa, width="100%", height=540,
                              returned_objects=["last_object_clicked_tooltip"])

with col_ranking:
    # ── Cards de resumen por clasificación ──
    for clasif in ["Prioritaria", "Consolidacion", "Mantenimiento"]:
        sub    = df_fil[df_fil["clasificacion"] == clasif]
        n_sub  = len(sub)
        if n_sub == 0:
            continue
        color  = COLOR_CLASIF[clasif]
        label  = LABEL_CLASIF[clasif]
        n_alerta = sub["seccion"].isin(SECCIONES_SIN_COB).sum()
        spt_top  = sub["SPT"].max()
        badge_html = (
            f"<span style='background:#e63946;color:white;font-size:0.68rem;"
            f"border-radius:10px;padding:1px 7px;margin-left:6px;'>"
            f"⚠️ {n_alerta} sin brigada</span>"
            if n_alerta > 0 else ""
        )
        card_html = (
            f'<div style="background:{color}0f;border:1px solid {color}40;'
            f'border-left:4px solid {color};border-radius:10px;'
            f'padding:12px 14px;margin-bottom:10px;">'
            f'<div style="font-size:0.80rem;font-weight:700;color:{color};'
            f'margin-bottom:2px;">{label}</div>'
            f'<div style="display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;">'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:1.6rem;'
            f'font-weight:700;color:{color};">{n_sub}</span>'
            f'<span style="font-size:0.75rem;color:#64748b;">secciones</span>'
            f'{badge_html}'
            f'</div>'
            f'<div style="font-size:0.72rem;color:#94a3b8;margin-top:4px;">'
            f'SPT m&aacute;x: <b style="color:#1e293b;">{spt_top:.0f}</b>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Tabla compacta de prioritarias ──
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#475569;"
        "text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>"
        "Prioritarias — ir primero</div>",
        unsafe_allow_html=True,
    )
    prio = df_fil[df_fil["clasificacion"] == "Prioritaria"].sort_values("SPT", ascending=False)
    for _, row in prio.iterrows():
        sec    = int(row["seccion"])
        alerta = sec in SECCIONES_SIN_COB
        ambito = ICONO_AMBITO.get(row["ambito_iter"], "")
        alerta_html = "<span style='font-size:0.72rem;'>⚠️</span>" if alerta else ""
        row_html = (
            f'<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;'
            f'border-radius:8px;background:#fef2f2;margin-bottom:4px;'
            f'border-left:3px solid #e63946;">'
            f'<span style="font-size:0.90rem;font-weight:700;color:#004a6e;min-width:40px;">'
            f'§ {sec}</span>'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.75rem;'
            f'font-weight:600;background:#e63946;color:white;'
            f'border-radius:10px;padding:1px 7px;">{row["SPT"]:.0f}</span>'
            f'<span style="font-size:0.78rem;color:#64748b;flex:1;">{ambito}</span>'
            f'{alerta_html}'
            f'</div>'
        )
        st.markdown(row_html, unsafe_allow_html=True)

# ── Ficha de sección ──────────────────────────────────────────────────────────
if sec_sel is not None:
    row = spt_df[spt_df["seccion"] == sec_sel]
    if not row.empty:
        r        = row.iloc[0]
        clasif   = r["clasificacion"]
        color    = COLOR_CLASIF.get(clasif, "#94a3b8")
        bg       = BG_CLASIF.get(clasif, "#f8fafc")
        sin_cob  = sec_sel in SECCIONES_SIN_COB
        ambito_l = r["ambito_iter"].replace("_"," ").title()
        label_c  = LABEL_CLASIF.get(clasif, clasif)

        st.markdown("<div class='section-hdr'>📋 Ficha de sección</div>", unsafe_allow_html=True)

        if sin_cob:
            st.markdown(f"""
            <div style='background:#fef2f2;border:1px solid #fca5a5;
                 border-left:5px solid #e63946;border-radius:10px;
                 padding:12px 18px;margin-bottom:14px;font-size:0.88rem;'>
                ⚠️ <strong>Sección sin operativo activo</strong> — brigada urgente requerida.
                Esta sección tiene alto potencial electoral y cero contactos registrados.
            </div>
            """, unsafe_allow_html=True)

        # Header ficha
        st.markdown(f"""
        <div class="ficha-header" style="border-left:5px solid {color};">
            <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
                <div>
                    <div style="color:#94a3b8;font-size:0.68rem;font-weight:700;
                                text-transform:uppercase;letter-spacing:1px;">SECCIÓN</div>
                    <div class="ficha-num">§ {sec_sel}</div>
                </div>
                <div style="flex:1;">
                    <span class="ficha-badge" style="background:{color};">{label_c}</span>
                    <span class="ficha-badge" style="background:rgba(255,255,255,0.15);">
                        {ICONO_AMBITO.get(r['ambito_iter'],'')} {ambito_l}
                    </span>
                    <span class="ficha-badge" style="background:rgba(255,255,255,0.12);color:#94a3b8;">
                        #{int(r['rank'])} de {n_secciones}
                    </span>
                    <div style="color:#cbd5e1;font-size:0.88rem;margin-top:10px;">
                        {r['tactica_recomendada']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Scores
        f1, f2, f3 = st.columns(3)

        with f1:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-label">SPT · Prioridad total</div>
                <div class="score-val">{r['SPT']:.1f}</div>
                <div class="score-bar-wrap">
                    <div class="score-bar-fill" style="width:{r['SPT']:.0f}%;
                         background:linear-gradient(90deg,{color},{color}aa);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with f2:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-label">Score Electoral</div>
                <div class="score-val">{r['score_electoral_norm']:.1f}</div>
                <div class="score-bar-wrap">
                    <div class="score-bar-fill"
                         style="width:{r['score_electoral_norm']:.0f}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with f3:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-label">Score Demográfico</div>
                <div class="score-val">{r['score_demografico']:.1f}</div>
                <div class="score-bar-wrap">
                    <div class="score-bar-fill"
                         style="width:{r['score_demografico']:.0f}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Segmentación operativa
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        segs = [
            (s1, "⭐", "Multiplicadores", r['pct_nucleo_duro'],    "#1a7a4a"),
            (s2, "🎯", "Activación",      r['pct_persuadibles'],   "#007cab"),
            (s3, "🤝", "Persuasión",      r['pct_persuadibles'],   "#d97706"),
            (s4, "👋", "Primer contacto", r['pct_no_alcanzados'],  "#475569"),
        ]
        for col, icono, seg, pct, color_s in segs:
            with col:
                st.markdown(f"""
                <div style='background:{color_s}10;border:1px solid {color_s}30;
                     border-radius:10px;padding:12px 14px;text-align:center;'>
                    <div style='font-size:1.3rem;'>{icono}</div>
                    <div style='font-size:1.2rem;font-weight:700;color:{color_s};
                                font-family:"IBM Plex Mono",monospace;'>{pct:.0f}%</div>
                    <div style='font-size:0.72rem;color:#64748b;margin-top:2px;
                                line-height:1.3;'>{seg}</div>
                </div>
                """, unsafe_allow_html=True)

        # Fuente
        fuente_txt = "Encuesta directa" if r.get("fuente_arquetipos") == "encuesta" else "Proyección por modelo"
        entrevistas = int(r.get("entrevistas", 0))
        st.markdown(f"""
        <div style='margin-top:12px;padding:10px 14px;background:#f8fafc;
             border-radius:8px;font-size:0.78rem;color:#64748b;'>
            📊 Fuente: <strong>{fuente_txt}</strong>
            {f" · {entrevistas} entrevistas" if entrevistas > 0 else " · datos proyectados"}
            &nbsp;·&nbsp; Arquetipo dominante: <strong>{r.get('arq_dominante','—')}</strong>
        </div>
        """, unsafe_allow_html=True)

# ── Gráfico resumen SPT todas las secciones ───────────────────────────────────
st.markdown("<div class='section-hdr'>📊 SPT por sección — todas las zonas</div>",
            unsafe_allow_html=True)

# Etiqueta legible: "§647 · Prioritaria" — evita el hueco numérico
df_chart = spt_df.sort_values("SPT", ascending=True).copy()
df_chart["label"] = df_chart.apply(
    lambda r: f"§{int(r['seccion'])}  {ICONO_AMBITO.get(r['ambito_iter'],'')}",
    axis=1
)
df_chart["alerta"] = df_chart["seccion"].isin(SECCIONES_SIN_COB)

fig = go.Figure()

for clasif, color in COLOR_CLASIF.items():
    sub = df_chart[df_chart["clasificacion"] == clasif]
    if sub.empty:
        continue
    fig.add_trace(go.Bar(
        x=sub["SPT"],
        y=sub["label"],
        orientation="h",
        name=LABEL_CLASIF[clasif],
        marker_color=color,
        marker_opacity=0.85,
        text=sub["SPT"].apply(lambda v: f"{v:.0f}"),
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color="#475569"),
        hovertemplate="<b>%{y}</b><br>SPT: %{x:.1f}<extra></extra>",
    ))

# Línea de referencia — umbral Prioritaria (SPT mínimo de ese grupo)
spt_min_prio = df_chart[df_chart["clasificacion"] == "Prioritaria"]["SPT"].min()
fig.add_vline(
    x=spt_min_prio, line_dash="dot", line_color="#e63946", line_width=1.5,
    annotation_text=f"Umbral prioritaria ({spt_min_prio:.0f})",
    annotation_position="top right",
    annotation_font_size=10, annotation_font_color="#e63946",
)

# Anotaciones ⚠️ para sin cobertura
for _, row_c in df_chart[df_chart["alerta"]].iterrows():
    fig.add_annotation(
        x=row_c["SPT"] + 2, y=row_c["label"],
        text="⚠️ sin cobertura", showarrow=False,
        font=dict(size=9, color="#e63946"),
        xanchor="left",
    )

fig.update_layout(
    height=580,
    barmode="overlay",
    margin=dict(l=10, r=80, t=30, b=30),
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=11),
    legend=dict(orientation="h", yanchor="bottom", y=-0.08, xanchor="left", x=0),
    xaxis=dict(
        title="Score de Prioridad Territorial",
        showgrid=True, gridcolor="#f1f5f9",
        range=[35, 78],   # arrancar en 35, no en 0 — elimina espacio vacío
    ),
    yaxis=dict(showgrid=False, tickfont=dict(family="IBM Plex Mono", size=11)),
)

st.plotly_chart(fig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:32px;padding-top:14px;border-top:1px solid #e2e8f0;
     text-align:center;font-size:0.73rem;color:#94a3b8;'>
    Data & AI Inclusion Tech · PIE Demo · Alan Rentería · MC · Puerto Peñasco 2027 · Confidencial
</div>
""", unsafe_allow_html=True)
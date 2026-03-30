"""
M5 — Base de Contactos Segmentada
PIE Demo · Puerto Peñasco, Sonora · Alan Rentería · MC 2027
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="M5 · Base de Contactos | Puerto Peñasco",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guardia de autenticación ──────────────────────────────────────────────────
if not st.session_state.get("autenticado", False):
    st.warning("Sesión no iniciada. Regresa al inicio.")
    st.stop()

# ── Rutas — resolución robusta para st.navigation ────────────────────────────
import sys

def _find_project_root() -> str:
    argv0 = os.path.abspath(sys.argv[0])
    if os.path.isfile(argv0):
        return os.path.dirname(argv0)
    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    if os.path.isdir(os.path.join(parent, "data")):
        return parent
    return os.getcwd()

_ROOT          = _find_project_root()
_DATA          = os.path.join(_ROOT, "data")
RUTA_CONTACTOS = os.path.join(_DATA, "contactos_pp.csv")
RUTA_SPT       = os.path.join(_DATA, "spt_secciones_pp.csv")

FECHA_CORTE          = "26 mar 2026"
SECCIONES_SIN_COB    = {634, 635, 648, 637, 1587}
ALCANCE_MULTIPLIER   = 3.2

COLORES_SEG = {
    "Multiplicadores": "#1a7a4a",
    "Activación":      "#007cab",
    "Persuasión":      "#d97706",
    "Primer contacto": "#475569",
}
ICONOS_SEG = {
    "Multiplicadores": "⭐",
    "Activación":      "🎯",
    "Persuasión":      "🤝",
    "Primer contacto": "👋",
}
INSTRUCCION_SEG = {
    "Multiplicadores": "Ya conocen a Alan y votarían por él. Convertirlos en promotores activos.",
    "Activación":      "Votarían por Alan pero aún no lo conocen bien. Reforzar presencia.",
    "Persuasión":      "Conocen a Alan pero no han decidido. El trabajo es convencer.",
    "Primer contacto": "No conocen a Alan o no han decidido. Presentarlo, causar buena impresión.",
}
MENSAJE_TIPO_SEG = {
    "Multiplicadores": "Hola [nombre], sabemos que conoces a Alan Rentería y confías en él. ¿Podrías ayudarnos a compartir su propuesta con tus vecinos? Cada voz cuenta en Puerto Peñasco.",
    "Activación":      "Hola [nombre], queremos que conozcas la propuesta de Alan Rentería para Puerto Peñasco. Él tiene un plan claro para el agua potable, las calles y la economía local.",
    "Persuasión":      "Hola [nombre], ya conoces a Alan Rentería. ¿Sabías que su propuesta incluye [propuesta concreta]? Estaremos en tu colonia el [fecha] — te esperamos.",
    "Primer contacto": "Hola [nombre], te contactamos para presentarte a Alan Rentería, candidato a presidente municipal. Tiene propuestas concretas para [problema local]. ¿Te gustaría saber más?",
}
CANAL_ICONO = {
    "WhatsApp": "📲",
    "SMS":      "💬",
    "Email":    "📧",
    "Visita":   "🚪",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #2e1065 !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #2e1065 !important; border-color: #7c3aed !important;
}

.seg-card {
    border-radius: 12px; padding: 18px 16px; text-align: center;
    border: 1px solid rgba(0,0,0,0.08);
}
.seg-val  { font-size: 1.8rem; font-weight: 800; line-height: 1.0; }
.seg-name { font-size: 0.86rem; font-weight: 700; margin: 4px 0; }
.seg-sub  { font-size: 0.74rem; color: #64748b; line-height: 1.3; }
.seg-msg  { font-size: 0.72rem; color: #475569; margin-top: 8px;
             background: rgba(255,255,255,0.7); border-radius: 8px;
             padding: 8px 10px; line-height: 1.45; text-align: left; }

.metric-card {
    background: #f8fafc; border-radius: 10px;
    padding: 16px 20px; border-left: 4px solid #7c3aed;
}
.metric-card.green  { border-left-color: #1a7a4a; }
.metric-card.blue   { border-left-color: #007cab; }
.metric-card.orange { border-left-color: #d97706; }
.metric-card.red    { border-left-color: #dc2626; }
.metric-val { font-size: 2rem; font-weight: 800; color: #1e293b;
              line-height: 1; font-family: 'IBM Plex Mono', monospace; }
.metric-lbl { font-size: 0.8rem; color: #64748b; margin-top: 4px; }

.alerta-red  {
    background: #fef2f2; border: 1px solid #fca5a5;
    border-left: 4px solid #dc2626;
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
    font-size: 0.84rem;
}
.section-hdr {
    font-size: 1.0rem; font-weight: 700; color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px; margin: 28px 0 16px;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():
    df  = pd.read_csv(RUTA_CONTACTOS)
    spt = pd.read_csv(RUTA_SPT)

    df["tiene_cel"]     = df["celular"].notna()
    df["celular_fmt"]   = df["celular"].apply(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )
    df["fecha_contacto"] = pd.to_datetime(df["fecha_contacto"], errors="coerce")
    df["gps_link"] = df.apply(
        lambda r: f"https://maps.google.com/?q={r['latitud']},{r['longitud']}"
        if pd.notna(r["latitud"]) else None,
        axis=1,
    )
    df["wa_link"] = df["celular_fmt"].apply(
        lambda c: f"https://wa.me/52{c}" if c else None
    )

    # Enriquecer con clasificación
    spt_dict = spt.set_index("seccion")[["clasificacion", "SPT", "tactica_recomendada"]].to_dict("index")
    df["clasificacion"] = df["seccion"].map(lambda s: spt_dict.get(s, {}).get("clasificacion", "Sin datos"))
    df["SPT"]           = df["seccion"].map(lambda s: spt_dict.get(s, {}).get("SPT", 0))

    return df, spt, spt_dict


# ── Carga ─────────────────────────────────────────────────────────────────────
with st.spinner("Cargando padrón..."):
    df_raw, spt_df, spt_dict = cargar_datos()

total_base = len(df_raw)

# ── Sidebar — filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.05rem;font-weight:700;margin-bottom:14px;'>🔎 Filtros</div>",
        unsafe_allow_html=True,
    )

    seg_opts = ["Todos los segmentos"] + list(COLORES_SEG.keys())
    seg_sel  = st.selectbox("Segmento operativo", seg_opts)

    canal_opts = ["Todos los canales", "WhatsApp", "SMS", "Email", "Visita"]
    canal_sel  = st.selectbox("Canal preferente", canal_opts)

    secciones_disp = sorted(df_raw["seccion"].dropna().unique().astype(int))
    sec_opts       = ["Todas las secciones"] + [str(s) for s in secciones_disp]
    sec_sel        = st.selectbox("Sección electoral", sec_opts)

    solo_celular = st.checkbox("Solo con celular válido", value=False)

    st.markdown("---")
    with st.expander("ℹ️ ¿Qué es cada segmento?"):
        for seg, instruc in INSTRUCCION_SEG.items():
            icono = ICONOS_SEG[seg]
            color = COLORES_SEG[seg]
            st.markdown(
                f"<div style='margin-bottom:10px;'>"
                f"<span style='color:{color};font-weight:700;'>{icono} {seg}</span><br>"
                f"<span style='font-size:0.81rem;color:#475569;'>{instruc}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df_f = df_raw.copy()
if seg_sel   != "Todos los segmentos":   df_f = df_f[df_f["segmento"]     == seg_sel]
if canal_sel != "Todos los canales":     df_f = df_f[df_f["canal"]        == canal_sel]
if sec_sel   != "Todas las secciones":   df_f = df_f[df_f["seccion"]      == int(sec_sel)]
if solo_celular:                         df_f = df_f[df_f["tiene_cel"]]

total_filtro = len(df_f)
con_cel      = int(df_f["tiene_cel"].sum())
pct_cel      = con_cel / max(total_filtro, 1) * 100
alcance_est  = int(total_filtro * ALCANCE_MULTIPLIER)

sin_cobertura = sorted([
    s for s in SECCIONES_SIN_COB
    if len(df_raw[df_raw["seccion"] == s]) == 0
])

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#2e1065 0%,#4c1d95 60%,#7c3aed 100%);
     border-radius:16px;padding:28px 32px 24px;margin-bottom:24px;
     position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
       color:#c4b5fd;text-transform:uppercase;margin-bottom:4px;'>
    Tu operación activada · Puerto Peñasco, Sonora
  </div>
  <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
    ¿A quién le mando el mensaje?
  </div>
  <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-top:6px;'>
    Base de contactos segmentada · Alan Rentería · MC 2027 · corte {FECHA_CORTE}
  </div>
  <div style='margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.15);'>
    <div style='font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.50);
         text-transform:uppercase;letter-spacing:0.10em;margin-bottom:8px;'>
      Qué muestra este módulo
    </div>
    <div style='display:flex;flex-wrap:wrap;gap:7px;margin-bottom:10px;'>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#ede9fe;font-weight:600;'>
        👥 Padrón completo segmentado por perfil de votante
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#ede9fe;font-weight:600;'>
        💬 Mensaje tipo por segmento y canal asignado
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#ede9fe;font-weight:600;'>
        📱 WhatsApp · SMS · correo según disponibilidad
      </span>
      <span style='background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.20);
           border-radius:20px;padding:3px 12px;font-size:0.76rem;color:#ede9fe;font-weight:600;'>
        📡 Proyección de alcance con el padrón actual
      </span>
    </div>
    <div style='font-size:0.82rem;color:rgba(255,255,255,0.75);line-height:1.55;
         background:rgba(0,0,0,0.15);border-radius:10px;padding:10px 14px;'>
      <strong style='color:#ffffff;'>Para qué sirve:</strong>
      Convertir el trabajo de campo en activación digital concreta.
      Cada persona en el padrón tiene asignado un segmento — Multiplicadores, Activación,
      Persuasión o Primer contacto — con el mensaje que corresponde a su perfil
      y el canal por el que se le puede llegar. El sistema no solo guarda los contactos:
      dice exactamente qué hacer con cada uno.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Alertas ───────────────────────────────────────────────────────────────────
if sin_cobertura:
    st.markdown(
        f"<div class='alerta-red'>🔴 <strong>Secciones prioritarias sin contactos: "
        f"{', '.join(['§ '+str(s) for s in sin_cobertura])}</strong><br>"
        f"<span style='color:#7f1d1d;'>Enviar brigada antes de cualquier activación digital.</span></div>",
        unsafe_allow_html=True,
    )

# ── Tarjetas de métricas ──────────────────────────────────────────────────────
suffix = f" de {total_base:,}" if (
    seg_sel != "Todos los segmentos" or sec_sel != "Todas las secciones" or
    canal_sel != "Todos los canales" or solo_celular
) else ""

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class='metric-card blue'>
        <div class='metric-val'>{total_filtro:,}</div>
        <div class='metric-lbl'>Contactos accionables{suffix}</div>
        <div style='margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;
             font-size:0.75rem;color:#0891b2;font-weight:600;'>
            ~{alcance_est:,} personas · alcance estimado ({ALCANCE_MULTIPLIER}x hogar)
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    col_cel = "green" if pct_cel >= 60 else "orange"
    st.markdown(f"""
    <div class='metric-card {col_cel}'>
        <div class='metric-val'>{con_cel:,}</div>
        <div class='metric-lbl'>Con celular válido · {pct_cel:.0f}%</div>
        <div style='margin-top:4px;font-size:0.75rem;color:#64748b;'>
            listos para WhatsApp o SMS
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    col_al = "red" if sin_cobertura else "green"
    icono  = "🔴" if sin_cobertura else "✅"
    al_txt = f"{len(sin_cobertura)} sin cobertura" if sin_cobertura else "Cobertura completa"
    st.markdown(f"""
    <div class='metric-card {col_al}'>
        <div class='metric-val'>{icono}</div>
        <div class='metric-lbl'>Secciones prioritarias · {al_txt}</div>
        <div style='margin-top:4px;font-size:0.75rem;color:#64748b;'>
            §634 · §635 · §648 · §637 · §1587 — brigada urgente
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Distribución por segmento ─────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>Distribución por segmento</div>", unsafe_allow_html=True)

cols_seg = st.columns(4)
for i, (seg, color) in enumerate(COLORES_SEG.items()):
    n_seg   = len(df_f[df_f["segmento"] == seg])
    pct_seg = n_seg / max(total_filtro, 1) * 100
    cel_seg = int(df_f[df_f["segmento"] == seg]["tiene_cel"].sum())
    canal_top = df_f[df_f["segmento"] == seg]["canal"].value_counts().index[0] if n_seg > 0 else "—"
    icono_canal = CANAL_ICONO.get(canal_top, "")
    with cols_seg[i]:
        st.markdown(f"""
        <div class='seg-card' style='background:{color}0d;border-color:{color}30;'>
            <div class='seg-val' style='color:{color};'>{n_seg:,}</div>
            <div class='seg-name' style='color:{color};'>{ICONOS_SEG[seg]} {seg}</div>
            <div class='seg-sub'>{pct_seg:.0f}% del total · {cel_seg:,} con cel.</div>
            <div class='seg-sub' style='margin-top:4px;'>
                Canal top: {icono_canal} {canal_top}
            </div>
            <div class='seg-msg'>{INSTRUCCION_SEG[seg]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════════
tab_listas, tab_mensajes, tab_graficos = st.tabs([
    "📋 Lista de contactos",
    "✉️ Mensajes tipo por segmento",
    "📊 Análisis de canal y alcance",
])


# ── TAB 1 — Lista de contactos ────────────────────────────────────────────────
with tab_listas:
    if total_filtro == 0:
        st.warning("No hay contactos con los filtros seleccionados.")
    else:
        n_gps = int(df_f["gps_link"].notna().sum())
        st.markdown(
            f"**{total_filtro:,} contactos** · {con_cel:,} con celular "
            f"({pct_cel:.0f}%) · {n_gps:,} con GPS registrado"
        )

        df_tabla = df_f[[
            "nombre", "celular_fmt", "seccion", "colonia",
            "segmento", "canal", "gps_link",
        ]].copy()
        df_tabla.columns = [
            "Nombre", "Celular", "Sección", "Colonia",
            "Segmento", "Canal", "📍 Ubicación",
        ]
        df_tabla["Sección"] = df_tabla["Sección"].apply(
            lambda x: f"§ {int(x)}" if pd.notna(x) else "Sin sección"
        )

        # Colorear columna Segmento
        def color_seg_cell(val):
            c = COLORES_SEG.get(val, "#94a3b8")
            return f"background-color: {c}20; color: {c}; font-weight: 600;"

        st.dataframe(
            df_tabla,
            use_container_width=True,
            height=440,
            hide_index=True,
            column_config={
                "📍 Ubicación": st.column_config.LinkColumn(
                    "📍 Ubicación",
                    help="Abre Google Maps",
                    display_text="📍 Ver",
                ),
                "Celular": st.column_config.TextColumn("Celular"),
            },
        )


# ── TAB 2 — Mensajes tipo ─────────────────────────────────────────────────────
with tab_mensajes:
    st.markdown(
        "<div style='font-size:0.88rem;color:#475569;margin-bottom:20px;'>"
        "Cada segmento tiene asignado un canal prioritario y un mensaje tipo. "
        "La lógica de activación está lista — el mensaje sale cuando el padrón lo indica."
        "</div>",
        unsafe_allow_html=True,
    )

    for seg in COLORES_SEG:
        color   = COLORES_SEG[seg]
        icono   = ICONOS_SEG[seg]
        n_seg   = len(df_f[df_f["segmento"] == seg])
        cel_seg = int(df_f[df_f["segmento"] == seg]["tiene_cel"].sum())
        msg     = MENSAJE_TIPO_SEG[seg]

        canal_seg = df_f[df_f["segmento"] == seg]["canal"].value_counts()
        canal_top = canal_seg.index[0] if len(canal_seg) else "—"
        canal_pct = canal_seg.iloc[0] / max(n_seg, 1) * 100 if len(canal_seg) else 0

        st.markdown(f"""
        <div style='border:1px solid {color}40;border-left:5px solid {color};
             border-radius:10px;padding:18px 20px;margin-bottom:14px;
             background:{color}08;'>
            <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px;'>
                <span style='font-size:1.5rem;'>{icono}</span>
                <div>
                    <div style='font-size:1.0rem;font-weight:700;color:{color};'>{seg}</div>
                    <div style='font-size:0.78rem;color:#64748b;'>
                        {n_seg:,} contactos · {cel_seg:,} con celular ·
                        canal top: {CANAL_ICONO.get(canal_top,'')} <strong>{canal_top}</strong>
                        ({canal_pct:.0f}%)
                    </div>
                </div>
            </div>
            <div style='font-size:0.80rem;font-weight:600;color:#475569;
                        text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;'>
                Instrucción operativa
            </div>
            <div style='font-size:0.88rem;color:#1e293b;margin-bottom:12px;'>
                {INSTRUCCION_SEG[seg]}
            </div>
            <div style='font-size:0.80rem;font-weight:600;color:#475569;
                        text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>
                Mensaje tipo · {CANAL_ICONO.get(canal_top,'')} {canal_top}
            </div>
            <div style='background:white;border:1px solid {color}30;border-radius:8px;
                        padding:12px 14px;font-size:0.88rem;color:#1e293b;
                        line-height:1.55;font-family:"IBM Plex Mono",monospace;'>
                {msg}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── TAB 3 — Análisis de canal y alcance ──────────────────────────────────────
with tab_graficos:
    g1, g2 = st.columns(2)

    # Gráfico 1 — distribución de canal
    with g1:
        canal_df = df_f["canal"].value_counts().reset_index()
        canal_df.columns = ["Canal", "Contactos"]
        canal_df["Icono"] = canal_df["Canal"].map(CANAL_ICONO)
        canal_df["Label"] = canal_df.apply(lambda r: f"{r['Icono']} {r['Canal']}", axis=1)

        fig_canal = px.pie(
            canal_df, names="Label", values="Contactos",
            color="Canal",
            color_discrete_map={
                "WhatsApp": "#25D366",
                "SMS":      "#007cab",
                "Email":    "#d97706",
                "Visita":   "#7c3aed",
            },
            title="Distribución por canal preferente",
            hole=0.45,
        )
        fig_canal.update_layout(
            height=300, margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="DM Sans"), title_font_size=13,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        )
        fig_canal.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig_canal, use_container_width=True)

    # Gráfico 2 — segmento × canal (stacked bar)
    with g2:
        cross = (
            df_f.groupby(["segmento", "canal"])
            .size()
            .reset_index(name="n")
        )
        fig_cross = px.bar(
            cross, x="segmento", y="n", color="canal",
            color_discrete_map={
                "WhatsApp": "#25D366",
                "SMS":      "#007cab",
                "Email":    "#d97706",
                "Visita":   "#7c3aed",
            },
            labels={"segmento": "Segmento", "n": "Contactos", "canal": "Canal"},
            title="Canal por segmento",
            barmode="stack",
        )
        fig_cross.update_layout(
            height=300, margin=dict(l=0, r=0, t=50, b=60),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans", size=11),
            title_font_size=13,
            xaxis_tickangle=-15,
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
        )
        fig_cross.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_cross, use_container_width=True)

    # Proyección de alcance
    st.markdown("<div class='section-hdr'>📡 Proyección de alcance digital</div>", unsafe_allow_html=True)

    wa_total  = int(df_f[df_f["canal"] == "WhatsApp"]["tiene_cel"].sum())
    sms_total = int(df_f[df_f["canal"] == "SMS"]["tiene_cel"].sum())
    email_t   = int(df_f[df_f["canal"] == "Email"]["tiene_cel"].sum())
    visita_t  = len(df_f[df_f["canal"] == "Visita"])

    p1, p2, p3, p4 = st.columns(4)
    for col, canal, n, color, icono in [
        (p1, "WhatsApp", wa_total,  "#25D366", "📲"),
        (p2, "SMS",      sms_total, "#007cab", "💬"),
        (p3, "Email",    email_t,   "#d97706", "📧"),
        (p4, "Visita",   visita_t,  "#7c3aed", "🚪"),
    ]:
        alcance = int(n * ALCANCE_MULTIPLIER)
        with col:
            st.markdown(f"""
            <div style='background:{color}10;border:1px solid {color}30;
                 border-radius:10px;padding:14px 16px;text-align:center;'>
                <div style='font-size:1.5rem;'>{icono}</div>
                <div style='font-size:1.3rem;font-weight:700;color:{color};
                            font-family:"IBM Plex Mono",monospace;'>{n:,}</div>
                <div style='font-size:0.78rem;font-weight:600;color:#475569;margin:3px 0;'>
                    {canal}
                </div>
                <div style='font-size:0.72rem;color:#94a3b8;'>
                    ~{alcance:,} personas alcance
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Barra de proyección total
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    alcance_total = int(total_filtro * ALCANCE_MULTIPLIER)
    pct_padrón = min(100, total_filtro / 20_000 * 100)  # 18,000 = padrón electoral PP aprox.

    st.markdown(f"""
    <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:20px 24px;'>
        <div style='font-size:0.80rem;font-weight:700;color:#475569;
                    text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;'>
            Proyección de alcance total con padrón actual
        </div>
        <div style='display:flex;align-items:baseline;gap:10px;margin-bottom:12px;'>
            <div style='font-size:2.2rem;font-weight:800;color:#004a6e;
                        font-family:"IBM Plex Mono",monospace;'>
                ~{alcance_total:,}
            </div>
            <div style='font-size:1.0rem;color:#64748b;'>personas alcanzables con {total_filtro:,} contactos</div>
        </div>
        <div style='background:#e2e8f0;border-radius:6px;height:10px;overflow:hidden;margin-bottom:8px;'>
            <div style='background:linear-gradient(90deg,#007cab,#00c0ff);
                        height:10px;width:{pct_padrón:.1f}%;border-radius:6px;'></div>
        </div>
        <div style='font-size:0.78rem;color:#64748b;'>
            {pct_padrón:.1f}% del padrón electoral de Puerto Peñasco cubierto
            &nbsp;·&nbsp; objetivo: 80% cobertura para máximo alcance
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:32px;padding-top:14px;border-top:1px solid #e2e8f0;
     text-align:center;font-size:0.73rem;color:#94a3b8;'>
    Data & AI Inclusion Tech · PIE Demo · Alan Rentería · MC · Puerto Peñasco 2027 · Confidencial
</div>
""", unsafe_allow_html=True)
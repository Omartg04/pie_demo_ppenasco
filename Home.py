"""
Home.py — PIE Demo · Puerto Peñasco, Sonora
Data & AI Inclusion Technologies · Alan Rentería · MC 2027
"""

import streamlit as st
import pandas as pd
import os
import time

# ── Rutas ─────────────────────────────────────────────────────────────────────
import sys as _sys

# Ancla al directorio donde vive Home.py — robusto para Streamlit Cloud y local
BASE = os.path.dirname(os.path.abspath(__file__))
# Fallback: si __file__ no resuelve bien, usar sys.argv[0]
if not os.path.isdir(os.path.join(BASE, "data")):
    _argv0 = os.path.abspath(_sys.argv[0])
    if os.path.isfile(_argv0):
        BASE = os.path.dirname(_argv0)
DATA = os.path.join(BASE, "data")

# ── Constantes del demo ───────────────────────────────────────────────────────
N_SECCIONES_TOTAL     = 27
N_SECCIONES_SIN_COB   = 5       # §634, §635, §637, §648, §1587 — alertas rojas
N_SECCIONES_CUBIERTAS = 22
N_CONTACTOS_FINAL     = 4_810
PCT_CELULAR_FINAL     = 72
ALCANCE_MULTIPLIER    = 3.2     # personas por contacto (hogar promedio PP · ITER 2020)
ALCANCE_ESTIMADO      = int(N_CONTACTOS_FINAL * ALCANCE_MULTIPLIER)
FECHA_CORTE           = "26 mar 2026"
PCT_VOTARIA_ALAN      = 34.8    # intención de voto interna MC — base encuesta propia
N_ENCUESTADOS         = 312

# Segmentos finales
SEG_FINAL = {
    "Multiplicadores":  843,
    "Activación":       802,
    "Persuasión":       1_741,
    "Primer contacto":  1_424,
}

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Header ── */
.home-header {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 60%, #00c0ff 100%);
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.home-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.home-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 40%;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
}
.header-tag {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
    color: #00c0ff; text-transform: uppercase; margin-bottom: 8px;
}
.header-title {
    font-size: 2.0rem; font-weight: 700; color: #ffffff;
    line-height: 1.2; margin-bottom: 6px;
}
.header-sub {
    font-size: 1.0rem; color: #bfdbfe; margin-bottom: 16px;
}
.header-corte {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.78rem; color: #e0f2fe; font-weight: 500;
}

/* ── Sección títulos ── */
.section-title {
    font-size: 1.0rem; font-weight: 700; color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px; margin-top: 36px; margin-bottom: 18px;
}

/* ── Cards principales ── */
.journey-card {
    border-radius: 16px; padding: 28px 26px 24px;
    min-height: 260px; position: relative;
    overflow: hidden; color: #ffffff;
}
.journey-card.card-1 {
    background:
        radial-gradient(circle at 85% 15%, rgba(96,165,250,0.20) 0%, transparent 55%),
        linear-gradient(145deg, #004a6e 0%, #005f8a 100%);
}
.journey-card.card-2 {
    background:
        radial-gradient(circle at 85% 15%, rgba(52,211,153,0.18) 0%, transparent 55%),
        linear-gradient(145deg, #064e3b 0%, #065f46 100%);
}
.journey-card.card-3 {
    background:
        radial-gradient(circle at 85% 15%, rgba(167,139,250,0.20) 0%, transparent 55%),
        linear-gradient(145deg, #2e1065 0%, #4c1d95 100%);
}
.journey-card::before {
    content: '';
    position: absolute; inset: 0;
    background-image: repeating-linear-gradient(
        -45deg, rgba(255,255,255,0.028) 0px,
        rgba(255,255,255,0.028) 1px, transparent 1px, transparent 18px
    );
    pointer-events: none;
}
.journey-card::after {
    content: ''; position: absolute;
    top: -45px; right: -45px;
    width: 150px; height: 150px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06); pointer-events: none;
}
.card-concept {
    font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; margin-bottom: 14px; opacity: 0.70;
    color: #ffffff; position: relative; z-index: 1;
}
.card-icon-bg {
    font-size: 2.6rem; margin-bottom: 10px;
    display: block; position: relative; z-index: 1;
}
.card-title {
    font-size: 1.28rem; font-weight: 700; color: #ffffff;
    margin-bottom: 10px; line-height: 1.25;
    position: relative; z-index: 1;
}
.card-body {
    font-size: 0.86rem; color: rgba(255,255,255,0.72);
    line-height: 1.6; position: relative; z-index: 1;
}

/* ── Pulso / KPI cards ── */
.pulso-card {
    background: #f8fafc; border-left: 4px solid #007cab;
    border-radius: 0 12px 12px 0; padding: 18px 20px; height: 100%;
}
.pulso-card.verde   { border-left-color: #1a7a4a; }
.pulso-card.azul    { border-left-color: #007cab; }
.pulso-card.naranja { border-left-color: #d97706; }
.pulso-card.morado  { border-left-color: #7c3aed; }
.pulso-card.teal    { border-left-color: #0891b2; }
.pulso-card.alerta  { border-left-color: #e63946; background: #fff5f5; }
.pulso-valor {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.9rem; font-weight: 600;
    color: #1e293b; line-height: 1.1;
}
.pulso-label { font-size: 0.80rem; font-weight: 600; color: #1e293b; margin-top: 5px; }
.pulso-ctx   { font-size: 0.74rem; color: #64748b; margin-top: 2px; line-height: 1.35; }

/* ── Animación — padrón en construcción ── */
.padron-header {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    border-radius: 14px; padding: 22px 28px 16px;
    margin-bottom: 20px; position: relative; overflow: hidden;
}
.padron-header::after {
    content: ''; position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.padron-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #00c0ff; margin-bottom: 4px;
}
.padron-title {
    font-size: 1.05rem; font-weight: 700; color: #ffffff;
    margin-bottom: 2px;
}
.padron-sub {
    font-size: 0.78rem; color: rgba(255,255,255,0.65);
}
.kpi-anim-wrap {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 16px 20px;
    display: flex; flex-direction: column; gap: 4px;
    position: relative; overflow: hidden;
}
.kpi-anim-wrap::after {
    content: '';
    position: absolute; bottom: 0; left: 0; height: 3px;
    background: linear-gradient(90deg, #007cab, #00c0ff);
    width: 100%;
}
.kpi-anim-valor {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.1rem; font-weight: 600; color: #004a6e;
    line-height: 1.0;
}
.kpi-anim-label {
    font-size: 0.77rem; font-weight: 600; color: #475569;
}
.kpi-anim-meta {
    font-size: 0.70rem; color: #94a3b8; margin-top: 1px;
}
.barra-progreso-wrap {
    background: #f1f5f9; border-radius: 6px;
    overflow: hidden; height: 8px; margin-top: 6px;
}
.barra-progreso-fill {
    height: 8px; border-radius: 6px;
    background: linear-gradient(90deg, #007cab, #00c0ff);
    transition: width 0.1s ease;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0, 192, 255, 0.10);
    border: 1px solid rgba(0, 192, 255, 0.30);
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.68rem; font-weight: 600;
    color: #007cab; letter-spacing: 0.06em;
    text-transform: uppercase;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00c0ff;
    animation: pulse-dot 1.4s ease-in-out infinite;
    display: inline-block;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.7); }
}
.seg-chip {
    display: inline-block; border-radius: 20px;
    padding: 3px 11px; font-size: 0.73rem; font-weight: 600;
    margin: 3px 3px 3px 0;
}

/* ── Zonas prioritarias ── */
.zona-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; background: #f8fafc; border-radius: 10px;
    margin-bottom: 8px; border-left: 4px solid #007cab;
}
.zona-row.alerta { border-left-color: #dc2626; background: #fef2f2; }
.zona-row.fragil { border-left-color: #d97706; background: #fffbeb; }
.zona-seccion { font-size: 1.05rem; font-weight: 700; color: #004a6e; min-width: 56px; }
.zona-spt {
    font-size: 0.75rem; background: #007cab; color: white;
    border-radius: 20px; padding: 2px 9px; font-weight: 600;
    min-width: 52px; text-align: center;
}
.zona-tipo    { font-size: 0.78rem; color: #64748b; min-width: 120px; }
.zona-tactica { font-size: 0.83rem; color: #1e293b; flex: 1; }
.zona-alerta-badge {
    font-size: 0.72rem; background: #dc2626; color: white;
    border-radius: 20px; padding: 2px 9px; font-weight: 600; white-space: nowrap;
}

/* ── Hallazgos ── */
.hallazgo-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 16px 18px; margin-bottom: 10px;
    display: flex; align-items: flex-start; gap: 12px;
}
.hallazgo-card .h-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 1px; }
.hallazgo-card .h-dato {
    font-size: 0.92rem; font-weight: 700; color: #1e293b;
    margin-bottom: 3px; line-height: 1.3;
}
.hallazgo-card .h-impl { font-size: 0.82rem; color: #64748b; line-height: 1.45; }

/* ── Footer ── */
.footer {
    margin-top: 40px; padding-top: 16px;
    border-top: 1px solid #e2e8f0;
    text-align: center; font-size: 0.73rem; color: #94a3b8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }

/* ── Login ── */
.login-wrap {
    max-width: 420px; margin: 80px auto 0;
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 20px; padding: 44px 40px 36px;
    box-shadow: 0 8px 40px rgba(0,74,110,0.10);
}
.login-logo {
    text-align: center; margin-bottom: 24px;
}
.login-title {
    font-size: 1.4rem; font-weight: 700; color: #004a6e;
    text-align: center; margin-bottom: 4px;
}
.login-sub {
    font-size: 0.82rem; color: #64748b;
    text-align: center; margin-bottom: 28px;
}
.login-error {
    background: #fff5f5; border: 1px solid #fca5a5;
    border-radius: 10px; padding: 10px 14px;
    font-size: 0.82rem; color: #dc2626;
    margin-bottom: 14px; text-align: center;
}
</style>
"""

# ── Carga de datos (cacheada) ─────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos():
    spt      = pd.read_csv(os.path.join(DATA, "spt_secciones_pp.csv"))
    contacts = pd.read_csv(os.path.join(DATA, "contactos_pp.csv"))
    return spt, contacts


# ════════════════════════════════════════════════════════════════════════════════
# AUTENTICACIÓN
# Credenciales en .streamlit/secrets.toml bajo [auth]
# Nunca hardcodeadas en el código.
# ════════════════════════════════════════════════════════════════════════════════
def _check_credentials(username: str, password: str) -> bool:
    """Valida usuario y contraseña contra st.secrets[auth]."""
    try:
        correct_user = st.secrets["auth"]["username"]
        correct_pass = st.secrets["auth"]["password"]
        return username == correct_user and password == correct_pass
    except Exception:
        # Si no hay secrets configurados (dev local sin secrets.toml),
        # bloquear acceso igualmente para forzar configuración correcta.
        return False


def pantalla_login():
    """Renderiza la pantalla de login. Devuelve True si autenticado."""
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">🌊</div>
        <div class="login-title">PIE · Puerto Peñasco</div>
        <div class="login-sub">
            Plataforma de Inteligencia Electoral<br>
            <strong>Alan Rentería · MC 2027</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centrar el formulario usando columnas
    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        with st.container():
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            username = st.text_input(
                "Usuario",
                placeholder="Usuario",
                label_visibility="collapsed",
                key="login_user",
            )
            password = st.text_input(
                "Contraseña",
                placeholder="Contraseña",
                type="password",
                label_visibility="collapsed",
                key="login_pass",
            )

            login_btn = st.button(
                "Ingresar →",
                use_container_width=True,
                type="primary",
                key="login_btn",
            )

            if login_btn:
                if _check_credentials(username, password):
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="login-error">
                        ✗ &nbsp; Usuario o contraseña incorrectos
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(
                "<div style='text-align:center; font-size:0.72rem; color:#94a3b8; margin-top:18px;'>"
                "Data & AI Inclusion Tech · Acceso confidencial"
                "</div>",
                unsafe_allow_html=True,
            )


def verificar_auth() -> bool:
    """Retorna True si el usuario ya está autenticado en session_state."""
    return st.session_state.get("autenticado", False)


# ════════════════════════════════════════════════════════════════════════════════
# ANIMACIÓN DE PADRÓN EN CONSTRUCCIÓN
# ════════════════════════════════════════════════════════════════════════════════
def render_padron_animado():
    st.markdown("""
    <div class="padron-header">
        <div class="padron-eyebrow">Operativo territorial activo</div>
        <div class="padron-title">
            Padrón en construcción
            <span class="live-badge" style="margin-left:10px;">
                <span class="live-dot"></span> En vivo
            </span>
        </div>
        <div class="padron-sub">
            Cada salida de brigada suma contactos · el padrón crece con cada jornada de campo
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    slot_contactos = c1.empty()
    slot_cobertura = c2.empty()
    slot_celular   = c3.empty()
    slot_alcance   = c4.empty()

    def _kpi_html(valor_str, label, meta, pct_barra, color_barra="#007cab"):
        barra_w = int(min(100, max(0, pct_barra)))
        return f"""
        <div class="kpi-anim-wrap">
            <div class="kpi-anim-valor">{valor_str}</div>
            <div class="kpi-anim-label">{label}</div>
            <div class="kpi-anim-meta">{meta}</div>
            <div class="barra-progreso-wrap">
                <div class="barra-progreso-fill"
                     style="width:{barra_w}%; background:linear-gradient(90deg,{color_barra},{color_barra}cc);">
                </div>
            </div>
        </div>
        """

    if "padron_animado" not in st.session_state:
        st.session_state["padron_animado"] = False

    if not st.session_state["padron_animado"]:
        PASOS      = 42
        DELAY      = 0.045
        EASE_POWER = 2.2

        for paso in range(PASOS + 1):
            t      = paso / PASOS
            t_ease = 1 - (1 - t) ** EASE_POWER

            contactos_v = int(N_CONTACTOS_FINAL  * t_ease)
            secciones_v = min(N_SECCIONES_CUBIERTAS, int(N_SECCIONES_CUBIERTAS * (t_ease ** 0.7) + 0.5))
            celular_v   = int(PCT_CELULAR_FINAL   * t_ease)
            alcance_v   = int(ALCANCE_ESTIMADO    * t_ease)

            slot_contactos.markdown(_kpi_html(
                f"{contactos_v:,}", "Personas contactadas",
                f"campo activo · corte {FECHA_CORTE}", t_ease * 100,
            ), unsafe_allow_html=True)
            slot_cobertura.markdown(_kpi_html(
                f"{secciones_v} / {N_SECCIONES_TOTAL}", "Secciones con presencia",
                f"{N_SECCIONES_SIN_COB} secciones aún sin operativo",
                (secciones_v / N_SECCIONES_TOTAL) * 100,
                "#e63946" if secciones_v < N_SECCIONES_CUBIERTAS else "#1a7a4a",
            ), unsafe_allow_html=True)
            slot_celular.markdown(_kpi_html(
                f"{celular_v}%", "Con celular válido",
                "listos para WhatsApp o SMS", celular_v, "#7c3aed",
            ), unsafe_allow_html=True)
            slot_alcance.markdown(_kpi_html(
                f"~{alcance_v:,}", "Alcance estimado",
                f"{ALCANCE_MULTIPLIER}x promedio hogar · ITER 2020", t_ease * 100, "#0891b2",
            ), unsafe_allow_html=True)

            if paso < PASOS:
                time.sleep(DELAY)

        st.session_state["padron_animado"] = True

    else:
        slot_contactos.markdown(_kpi_html(
            f"{N_CONTACTOS_FINAL:,}", "Personas contactadas",
            f"campo activo · corte {FECHA_CORTE}", 100,
        ), unsafe_allow_html=True)
        slot_cobertura.markdown(_kpi_html(
            f"{N_SECCIONES_CUBIERTAS} / {N_SECCIONES_TOTAL}", "Secciones con presencia",
            f"{N_SECCIONES_SIN_COB} secciones aún sin operativo",
            (N_SECCIONES_CUBIERTAS / N_SECCIONES_TOTAL) * 100, "#e63946",
        ), unsafe_allow_html=True)
        slot_celular.markdown(_kpi_html(
            f"{PCT_CELULAR_FINAL}%", "Con celular válido",
            "listos para WhatsApp o SMS", PCT_CELULAR_FINAL, "#7c3aed",
        ), unsafe_allow_html=True)
        slot_alcance.markdown(_kpi_html(
            f"~{ALCANCE_ESTIMADO:,}", "Alcance estimado",
            f"{ALCANCE_MULTIPLIER}x promedio hogar · ITER 2020", 100, "#0891b2",
        ), unsafe_allow_html=True)

    iconos = {
        "Multiplicadores": ("⭐", "#1a7a4a", "#f0fdf4"),
        "Activación":      ("🎯", "#007cab", "#eff6ff"),
        "Persuasión":      ("🤝", "#d97706", "#fffbeb"),
        "Primer contacto": ("👋", "#475569", "#f8fafc"),
    }
    chips_html = "<div style='margin-top:14px; margin-bottom:4px;'>"
    chips_html += "<span style='font-size:0.75rem; font-weight:600; color:#64748b; margin-right:8px;'>Segmentos identificados:</span>"
    for seg, n in SEG_FINAL.items():
        icono, color, bg = iconos[seg]
        chips_html += (
            f"<span class='seg-chip' style='background:{bg}; color:{color};'>"
            f"{icono} {seg} <strong>{n:,}</strong></span>"
        )
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)

    if st.button("▶ Repetir animación", key="btn_replay", type="secondary"):
        st.session_state["padron_animado"] = False
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════════
def main():
    st.markdown(CSS, unsafe_allow_html=True)

    try:
        spt, contactos = cargar_datos()
        datos_ok = True
    except Exception:
        spt, contactos = None, None
        datos_ok = False

    st.markdown(f"""
    <div class="home-header">
        <div class="header-tag">Data & AI Inclusion Tech · Sistema de Inteligencia Electoral · Puerto Peñasco, Sonora</div>
        <div class="header-title">Alan Rentería · MC 2027</div>
        <div class="header-sub">
            De la intuición a la evidencia. Gana la presidencia municipal con datos propios.
        </div>
        <span class="header-corte">📅 Operativo: {FECHA_CORTE} &nbsp;·&nbsp; 27 secciones electorales</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">La plataforma genera tus datos, crea inteligencia y activa la operación</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="journey-card card-1">
            <div class="card-concept">Tu línea base propia</div>
            <span class="card-icon-bg">🗺️</span>
            <div class="card-title">¿A dónde voy primero?</div>
            <div class="card-body">¿Cuáles secciones de Puerto Peñasco valen más una visita?
            Prioridad territorial sección por sección — combinando encuesta propia,
            historial electoral y perfil demográfico costero.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/1_M1_Mapa_Territorial.py",
            label="Ver mapa territorial →",
            use_container_width=True,
        )

    with col2:
        st.markdown("""
        <div class="journey-card card-2">
            <div class="card-concept">Tu mapa de decisiones</div>
            <span class="card-icon-bg">📋</span>
            <div class="card-title">¿Cómo vamos en campo?</div>
            <div class="card-body">¿Cuántos contactos llevamos? ¿Qué secciones ya cubrimos
            y cuáles faltan? Semana a semana: cobertura real, disponibilidad de voto
            y alertas de zonas sin operativo activo.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/2_M2_Avance_Operativo.py",
            label="Ver avance operativo →",
            use_container_width=True,
        )

    with col3:
        st.markdown("""
        <div class="journey-card card-3">
            <div class="card-concept">Tu operación activada</div>
            <span class="card-icon-bg">📱</span>
            <div class="card-title">¿A quién le mando el mensaje?</div>
            <div class="card-body">Base de contactos segmentada con mensaje tipo por perfil.
            El mensaje correcto, a la persona correcta, en el canal correcto —
            directo a WhatsApp o SMS desde Puerto Peñasco.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/5_M5_Contactos.py",
            label="Ver base de contactos →",
            use_container_width=True,
        )

    st.info(
        "Navega también desde el menú en la **barra lateral izquierda** (ícono ☰ en móvil).",
        icon="💡",
    )

    st.markdown(
        '<div class="section-title">⚡ Padrón en construcción — el dato vive y crece con cada salida de campo</div>',
        unsafe_allow_html=True,
    )
    render_padron_animado()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_v1, col_v2, col_v3 = st.columns([1, 1, 2], gap="medium")
    with col_v1:
        st.markdown(f"""
        <div class="pulso-card naranja">
            <div class="pulso-valor">{PCT_VOTARIA_ALAN}%</div>
            <div class="pulso-label">Votarían por Alan</div>
            <div class="pulso-ctx">encuesta propia · {N_ENCUESTADOS} entrevistas</div>
        </div>
        """, unsafe_allow_html=True)
    with col_v2:
        st.markdown("""
        <div class="pulso-card alerta">
            <div class="pulso-valor">5 🔴</div>
            <div class="pulso-label">Secciones sin cobertura</div>
            <div class="pulso-ctx">§634 · §635 · §648 · §637 · §1587 — brigada urgente</div>
        </div>
        """, unsafe_allow_html=True)
    with col_v3:
        st.markdown("""
        <div class="pulso-card azul" style="display:flex; align-items:center; gap:16px; flex-direction:row; padding:16px 20px;">
            <div style="font-size:2.2rem; flex-shrink:0;">🌊</div>
            <div>
                <div style="font-size:0.80rem; font-weight:700; color:#1e293b;">Contexto político · Puerto Peñasco</div>
                <div style="font-size:0.76rem; color:#475569; margin-top:3px; line-height:1.5;">
                    Antecedente MC: <strong>27%</strong> en elección anterior ·
                    Alcalde en funciones removido · Ventana política abierta ·
                    Estructura territorial en construcción
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🎯 Zonas de máxima atención — ir primero aquí</div>',
        unsafe_allow_html=True,
    )

    tipo_map = {
        "urbano":         "🏙️ Urbano",
        "rural_media":    "🌾 Rural costero",
        "rural_marginal": "🏜️ Rural marginal",
    }
    sin_cob = {634, 635, 648, 637, 1587}

    if datos_ok:
        prioritarias_df = spt[spt["clasificacion"] == "Prioritaria"].sort_values("SPT", ascending=False)
    else:
        prioritarias_df = pd.DataFrame({
            "seccion":             [647, 646, 645, 640, 631, 634, 635, 648],
            "SPT":                 [71.2, 69.8, 68.3, 67.5, 66.9, 65.8, 65.1, 64.4],
            "ambito_iter":         ["urbano","urbano","urbano","urbano","rural_media","rural_media","rural_media","rural_marginal"],
            "tactica_recomendada": [
                "Brigadas de primer contacto urgentes",
                "Brigadas de primer contacto urgentes",
                "Brigadas primer contacto + cierre",
                "Brigadas de primer contacto urgentes",
                "Brigadas urgentes — sin cobertura",
                "Brigadas urgentes — sin cobertura",
                "Brigadas urgentes — sin cobertura",
                "Brigadas urgentes — sin cobertura",
            ],
        })

    for _, row in prioritarias_df.iterrows():
        seccion    = int(row["seccion"])
        es_alerta  = seccion in sin_cob
        tipo_texto = tipo_map.get(str(row["ambito_iter"]), str(row["ambito_iter"]))
        badge_html = '<span class="zona-alerta-badge">⚠️ Sin contactos</span>' if es_alerta else ""
        clase_row  = "zona-row alerta" if es_alerta else "zona-row"
        st.markdown(f"""
        <div class="{clase_row}">
            <span class="zona-seccion">§ {seccion}</span>
            <span class="zona-spt">SPT {row['SPT']:.1f}</span>
            <span class="zona-tipo">{tipo_texto}</span>
            <span class="zona-tactica">{row['tactica_recomendada']}</span>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)

    st.caption("Ver detalle completo y mapa en Módulo M2 · Avance Operativo.")

    st.markdown(
        '<div class="section-title">🔍 Lo que cambia la estrategia — hallazgos de encuesta propia</div>',
        unsafe_allow_html=True,
    )

    hallazgos = [
        ("🌊",
         "Alan con 34.8% de intención de voto — casi 8 puntos sobre su resultado anterior del 27%.",
         "La ventana por la remoción del alcalde es real. El momento es ahora — cada semana sin operativo es voto que se va."),
        ("🏙️",
         "Las 3 secciones urbanas prioritarias concentran el 35% del padrón electoral.",
         "Son también las secciones con menor cobertura de brigadas. El operativo de tierra sigue siendo la prioridad #1."),
        ("📱",
         "El 72% de contactos tiene celular válido — 3,731 personas listas para activación digital.",
         "WhatsApp funciona en Puerto Peñasco. Con el padrón construido, el alcance digital ya supera las 15,000 personas."),
        ("🏜️",
         "Las 3 secciones rurales marginales sin cobertura son las de mayor SPT del municipio.",
         "Solo brigadas presenciales las alcanzan. La pauta digital no llega. Son el hueco más urgente de la campaña."),
        ("⭐",
         "843 multiplicadores identificados — personas que ya conocen a Alan y votarían por él.",
         "Son la red de promotores potenciales de la campaña. Activarlos cuesta casi nada y multiplica el alcance real."),
        ("🗳️",
         "Alcance estimado de ~15,392 personas con el padrón actual — 3.2x por contacto.",
         "Cuando el padrón llegue a 8,000 contactos, el alcance supera el padrón electoral total del municipio."),
    ]

    col_h1, col_h2 = st.columns(2, gap="medium")
    for i, (icon, dato, impl) in enumerate(hallazgos):
        col = col_h1 if i % 2 == 0 else col_h2
        with col:
            st.markdown(f"""
            <div class="hallazgo-card">
                <span class="h-icon">{icon}</span>
                <div>
                    <div class="h-dato">{dato}</div>
                    <div class="h-impl">{impl}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("🔬 ¿Cómo lo construimos? — la inteligencia detrás del sistema"):
        st.markdown("""
        <div style="font-size:0.85rem; color:#475569; margin-bottom:16px; line-height:1.6;">
            312 entrevistas representativas &nbsp;·&nbsp; 4 arquetipos de votante &nbsp;·&nbsp;
            2 elecciones analizadas &nbsp;·&nbsp; 22 secciones electorales<br>
            <span style="color:#94a3b8;">Metodología adaptada al municipio costero de Puerto Peñasco —
            equivalente a las principales casas encuestadoras nacionales, a una fracción del costo.</span>
        </div>
        """, unsafe_allow_html=True)

        cc1, cc2 = st.columns(2, gap="medium")
        with cc1:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:20px; margin-bottom:10px;">
                <div style="font-size:0.92rem; font-weight:700; color:#1e293b; margin-bottom:5px;">👥 Perfiles del Votante Peñasquense</div>
                <div style="font-size:0.82rem; color:#64748b; line-height:1.45;">4 perfiles del votante local — con el mensaje que mueve
                a cada uno. Generados con análisis de conglomerados sobre encuesta propia.</div>
                <div style="font-size:0.72rem; color:#94a3b8; margin-top:6px; font-weight:500;">
                2 arquetipos urbanos · 2 arquetipos rurales · validación cruzada</div>
            </div>
            """, unsafe_allow_html=True)
        with cc2:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:20px; margin-bottom:10px;">
                <div style="font-size:0.92rem; font-weight:700; color:#1e293b; margin-bottom:5px;">📊 Historia Electoral Puerto Peñasco</div>
                <div style="font-size:0.82rem; color:#64748b; line-height:1.45;">Evolución del voto MC 2018–2024 —
                qué tan sólida es cada sección. Clasificación por margen real en 2 elecciones.</div>
                <div style="font-size:0.72rem; color:#94a3b8; margin-top:6px; font-weight:500;">
                22 secciones activas · MC ganó 6 secciones en 2024 · ventana de crecimiento amplia</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:20px; margin-top:4px;">
            <div style="font-size:0.92rem; font-weight:700; color:#1e293b; margin-bottom:5px;">🏗️ Generación de Datos Propios</div>
            <div style="font-size:0.82rem; color:#64748b; line-height:1.45;">Diseño del cuestionario, muestreo y cuotas demográficas por sección,
            capacitación de encuestadores en Puerto Peñasco, infraestructura digital de levantamiento,
            monitoreo en tiempo real, limpieza y activación de datos. Los datos son tuyos — no del partido, no de ningún consultor.</div>
            <div style="font-size:0.72rem; color:#94a3b8; margin-top:6px; font-weight:500;">
            Encuesta 1: 312 entrevistas · 22/27 secciones con datos reales · 5 secciones proyectadas por modelo</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        Data & AI Inclusion Tech · PIE Demo · Alan Rentería · MC · Puerto Peñasco, Sonora 2027 · Confidencial<br>
        Uso exclusivo del equipo de campaña
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA — autenticación antes de cualquier contenido
# ════════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PIE · Puerto Peñasco · Alan Rentería",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not verificar_auth():
    pantalla_login()
    st.stop()

# Usuario autenticado — registrar botón de cierre de sesión en sidebar
with st.sidebar:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔒 Cerrar sesión", use_container_width=True, type="secondary"):
        st.session_state["autenticado"] = False
        st.rerun()

pg = st.navigation(
    {
        "La Plataforma": [
            st.Page(main, title="🏠  Inicio", default=True),
        ],
        "Tu línea base propia": [
            st.Page("pages/1_M1_Mapa_Territorial.py", title="🗺️  ¿A dónde voy primero?"),
        ],
        "Tu mapa de decisiones": [
            st.Page("pages/2_M2_Avance_Operativo.py", title="📋  ¿Cómo vamos en campo?"),
        ],
        "Tu operación activada": [
            st.Page("pages/5_M5_Contactos.py", title="📱  ¿A quién le mando el mensaje?"),
        ],
        "Propuesta": [
            st.Page("pages/6_Cierre.py", title="🤝  Lo que puede ser tu campaña"),
        ],
    },
    position="sidebar",
)

pg.run()
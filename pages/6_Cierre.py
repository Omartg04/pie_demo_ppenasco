"""
6_Cierre.py — Pantalla de Cierre Comercial
PIE Demo · Puerto Peñasco, Sonora · Alan Rentería · MC 2027
Data & AI Inclusion Technologies
"""

import streamlit as st
import os
import sys

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Tu Campaña · PIE | Puerto Peñasco",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guardia de autenticación ──────────────────────────────────────────────────
# Si el usuario llega directo a esta página sin pasar por Home.py,
# redirigir al login bloqueando el contenido.
if not st.session_state.get("autenticado", False):
    st.warning("Sesión no iniciada. Regresa al inicio.")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }

/* ── Hero de cierre ── */
.cierre-hero {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 55%, #00c0ff 100%);
    border-radius: 20px; padding: 52px 48px 44px;
    margin-bottom: 36px; position: relative; overflow: hidden;
    text-align: center;
}
.cierre-hero::before {
    content: ''; position: absolute;
    top: -80px; right: -80px;
    width: 300px; height: 300px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.cierre-hero::after {
    content: ''; position: absolute;
    bottom: -60px; left: 10%;
    width: 220px; height: 220px; border-radius: 50%;
    background: rgba(255,255,255,0.03);
}
.cierre-eyebrow {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em;
    color: #00c0ff; text-transform: uppercase;
    margin-bottom: 14px; position: relative; z-index: 1;
}
.cierre-titulo {
    font-size: 2.6rem; font-weight: 700; color: #ffffff;
    line-height: 1.18; margin-bottom: 16px;
    position: relative; z-index: 1;
}
.cierre-titulo span { color: #00c0ff; }
.cierre-sub {
    font-size: 1.08rem; color: rgba(255,255,255,0.78);
    max-width: 680px; margin: 0 auto 28px; line-height: 1.6;
    position: relative; z-index: 1;
}
.cierre-badge {
    display: inline-block;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 22px; padding: 6px 18px;
    font-size: 0.80rem; color: #e0f2fe; font-weight: 600;
    position: relative; z-index: 1; margin: 4px;
}

/* ── Resumen del demo ── */
.resumen-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 28px 24px;
    text-align: center; height: 100%;
    transition: box-shadow 0.2s;
}
.resumen-card:hover { box-shadow: 0 4px 24px rgba(0,74,110,0.10); }
.resumen-numero {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.6rem; font-weight: 600; color: #004a6e;
    line-height: 1.0; margin-bottom: 6px;
}
.resumen-label {
    font-size: 0.85rem; font-weight: 600; color: #1e293b;
    margin-bottom: 4px;
}
.resumen-ctx {
    font-size: 0.76rem; color: #64748b; line-height: 1.4;
}

/* ── Sección de valor ── */
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px; margin-top: 40px; margin-bottom: 22px;
}

/* ── Cards de propuesta ── */
.valor-card {
    border-radius: 16px; padding: 30px 28px;
    position: relative; overflow: hidden;
    height: 100%; color: #ffffff;
}
.valor-card.v1 {
    background: linear-gradient(145deg, #004a6e 0%, #005f8a 100%);
}
.valor-card.v2 {
    background: linear-gradient(145deg, #064e3b 0%, #065f46 100%);
}
.valor-card.v3 {
    background: linear-gradient(145deg, #7c2d12 0%, #9a3412 100%);
}
.valor-card::before {
    content: ''; position: absolute; inset: 0;
    background-image: repeating-linear-gradient(
        -45deg, rgba(255,255,255,0.025) 0px,
        rgba(255,255,255,0.025) 1px, transparent 1px, transparent 18px
    );
    pointer-events: none;
}
.valor-numero {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3.0rem; font-weight: 700;
    color: rgba(255,255,255,0.15); line-height: 1;
    margin-bottom: -10px;
}
.valor-icon { font-size: 2.2rem; margin-bottom: 10px; display: block; }
.valor-titulo {
    font-size: 1.18rem; font-weight: 700; color: #ffffff;
    margin-bottom: 10px; line-height: 1.2;
}
.valor-body {
    font-size: 0.86rem; color: rgba(255,255,255,0.75);
    line-height: 1.65;
}
.valor-bullets {
    margin-top: 14px; padding: 0; list-style: none;
}
.valor-bullets li {
    font-size: 0.83rem; color: rgba(255,255,255,0.80);
    padding: 4px 0; display: flex; align-items: flex-start; gap: 8px;
}
.valor-bullets li::before {
    content: '→'; color: rgba(255,255,255,0.45);
    flex-shrink: 0; margin-top: 1px;
}

/* ── Tabla antes / después ── */
.comparacion-wrap {
    border-radius: 16px; overflow: hidden;
    border: 1px solid #e2e8f0; margin-bottom: 12px;
}
.comparacion-header {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    background: #f1f5f9;
}
.comp-header-cell {
    padding: 10px 16px; font-size: 0.78rem;
    font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 0.08em;
}
.comparacion-row {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    border-top: 1px solid #e2e8f0;
}
.comparacion-row:nth-child(even) { background: #f8fafc; }
.comp-cell {
    padding: 12px 16px; font-size: 0.84rem; color: #1e293b;
    line-height: 1.4;
}
.comp-cell.antes { color: #94a3b8; }
.comp-cell.despues { color: #1a7a4a; font-weight: 600; }
.comp-cell.dimension { font-weight: 600; color: #334155; }

/* ── Pasos siguientes ── */
.paso-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 22px 20px;
    display: flex; gap: 16px; align-items: flex-start;
    margin-bottom: 10px;
}
.paso-numero {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem; font-weight: 700;
    color: #007cab; flex-shrink: 0; line-height: 1; margin-top: 2px;
}
.paso-titulo {
    font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 4px;
}
.paso-body { font-size: 0.82rem; color: #64748b; line-height: 1.5; }
.paso-tiempo {
    display: inline-block;
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 12px; padding: 2px 10px;
    font-size: 0.72rem; font-weight: 600; color: #1d4ed8;
    margin-top: 6px;
}

/* ── Contacto ── */
.contacto-wrap {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    border-radius: 20px; padding: 40px 44px;
    text-align: center; margin-top: 36px;
    position: relative; overflow: hidden;
}
.contacto-wrap::after {
    content: ''; position: absolute;
    top: -50px; right: -50px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.contacto-titulo {
    font-size: 1.7rem; font-weight: 700; color: #ffffff;
    margin-bottom: 8px;
}
.contacto-sub {
    font-size: 0.92rem; color: rgba(255,255,255,0.72);
    margin-bottom: 28px; line-height: 1.5;
}
.contacto-item {
    display: inline-block;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 22px; padding: 8px 22px;
    font-size: 0.88rem; color: #ffffff; font-weight: 600;
    margin: 6px; cursor: default;
}
.contacto-empresa {
    font-size: 0.76rem; color: rgba(255,255,255,0.50);
    margin-top: 20px; letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Footer ── */
.footer {
    margin-top: 44px; padding-top: 16px;
    border-top: 1px solid #e2e8f0;
    text-align: center; font-size: 0.73rem; color: #94a3b8;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cierre-hero">
    <div class="cierre-eyebrow">Data & AI Inclusion Technologies · PIE Demo · Puerto Peñasco</div>
    <div class="cierre-titulo">
        Lo que viste hoy<br>es lo que tu campaña<br><span>puede tener.</span>
    </div>
    <div class="cierre-sub">
        No es un prototipo. No es una promesa. Es el sistema operando con datos
        reales de Puerto Peñasco — listo para activarse en tu campaña desde el primer día.
    </div>
    <span class="cierre-badge">🗺️ 27 secciones electorales</span>
    <span class="cierre-badge">👥 4,810 contactos levantados</span>
    <span class="cierre-badge">📱 72% con celular activo</span>
    <span class="cierre-badge">~15,392 personas de alcance</span>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# RESUMEN DEL DEMO — QUÉ VISTE HOY
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📊 Lo que viste hoy — en números</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5, gap="medium")

resumen_items = [
    ("3", "Módulos operativos", "Territorial · Brigadas · Contactos"),
    ("27", "Secciones electorales", "Municipio completo · INE · WGS84"),
    ("4,810", "Contactos en padrón", "Levantados en campo · ficticios representativos"),
    ("~15,392", "Personas de alcance", "3.2× por contacto · ITER 2020"),
    ("4", "Segmentos de votante", "Multiplicadores · Activación · Persuasión · Primer contacto"),
]

for col, (num, label, ctx) in zip([c1, c2, c3, c4, c5], resumen_items):
    with col:
        st.markdown(f"""
        <div class="resumen-card">
            <div class="resumen-numero">{num}</div>
            <div class="resumen-label">{label}</div>
            <div class="resumen-ctx">{ctx}</div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PROPUESTA DE VALOR — 3 PILARES
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">🎯 Por qué esto cambia la campaña — los 3 pilares</div>',
    unsafe_allow_html=True,
)

cv1, cv2, cv3 = st.columns(3, gap="medium")

with cv1:
    st.markdown("""
    <div class="valor-card v1">
        <div class="valor-numero">01</div>
        <span class="valor-icon">🔬</span>
        <div class="valor-titulo">Datos propios.<br>No los del partido.</div>
        <div class="valor-body">
            Encuesta diseñada para Puerto Peñasco. Padrón levantado
            por tus brigadas. Análisis específico de tu municipio.
            La inteligencia es tuya — y se queda contigo cuando termine la campaña.
        </div>
        <ul class="valor-bullets">
            <li>312 entrevistas propias · 22 secciones con dato real</li>
            <li>4 perfiles de votante peñasquense · validados en campo</li>
            <li>Historial electoral MC 2018–2024 · sección por sección</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with cv2:
    st.markdown("""
    <div class="valor-card v2">
        <div class="valor-numero">02</div>
        <span class="valor-icon">🚀</span>
        <div class="valor-titulo">Operación activada.<br>Cada brigada cuenta.</div>
        <div class="valor-body">
            Cada jornada de campo construye el padrón. Cada contacto
            levantado tiene segmento, canal y mensaje asignado.
            El sistema dirige la operación — no la reporta después.
        </div>
        <ul class="valor-bullets">
            <li>Alertas de secciones sin cobertura en tiempo real</li>
            <li>Segmentación automática por perfil de votante</li>
            <li>Canal asignado: WhatsApp · SMS · correo · presencial</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with cv3:
    st.markdown("""
    <div class="valor-card v3">
        <div class="valor-numero">03</div>
        <span class="valor-icon">⚡</span>
        <div class="valor-titulo">Decisiones en tiempo real.<br>No en el siguiente corte.</div>
        <div class="valor-body">
            El sistema vive y crece con cada salida de campo.
            Adrián ve lo mismo que Alan. Las decisiones se toman
            con el dato de hoy — no con la intuición de ayer.
        </div>
        <ul class="valor-bullets">
            <li>Dashboard actualizado con cada carga de campo</li>
            <li>Proyección de alcance a medida que crece el padrón</li>
            <li>Acceso seguro desde cualquier dispositivo</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# ANTES / DESPUÉS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">🔄 La diferencia — intuición vs. inteligencia</div>',
    unsafe_allow_html=True,
)

comparaciones = [
    ("Prioridad territorial",
     "¿A dónde mando las brigadas? — por experiencia o referencia",
     "SPT por sección: encuesta + historial + demografía · ordenado y visible"),
    ("Cobertura de campo",
     "Nadie sabe exactamente cuántas casas se tocaron esta semana",
     "Contactos por sección en tiempo real · alertas de zonas sin operativo"),
    ("Perfil del votante",
     "\"El peñasquense es así\" — generalizaciones sin dato",
     "4 segmentos con mensaje tipo · canal asignado · listo para activar"),
    ("Activación digital",
     "Lista de contactos en Excel · sin segmentación · sin mensaje definido",
     "Padrón segmentado · 3,471 con celular · WhatsApp / SMS desde la plataforma"),
    ("Alcance real",
     "Calculado a ojo · número que nadie puede defender",
     "~15,392 personas · 3.2x por contacto · metodología ITER 2020"),
    ("Toma de decisiones",
     "Reunión de equipo con impresiones subjetivas del fin de semana",
     "Dashboard con dato de hoy · Adrián y Alan ven lo mismo · decisión en minutos"),
]

header_html = """
<div class="comparacion-wrap">
<div class="comparacion-header">
    <div class="comp-header-cell">Dimensión</div>
    <div class="comp-header-cell">Sin PIE</div>
    <div class="comp-header-cell">Con PIE</div>
</div>
"""
rows_html = ""
for dim, antes, despues in comparaciones:
    rows_html += f"""
<div class="comparacion-row">
    <div class="comp-cell dimension">{dim}</div>
    <div class="comp-cell antes">✗ &nbsp;{antes}</div>
    <div class="comp-cell despues">✓ &nbsp;{despues}</div>
</div>
"""

st.markdown(header_html + rows_html + "</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# PRÓXIMOS PASOS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📋 De aquí a campaña activa — próximos pasos</div>',
    unsafe_allow_html=True,
)

col_p1, col_p2 = st.columns(2, gap="medium")

pasos = [
    ("01", "Encuesta propia · n > 600", "Levantamiento representativo en Puerto Peñasco. Cuotas por sección, género y edad. 312 entrevistas ya ejecutadas — ampliar para mayor precisión estadística.", "2–3 semanas"),
    ("02", "Padrón real · meta 8,000 contactos", "Con el sistema operando en campo, cada brigada carga datos directamente. El padrón crece solo — sin trabajo técnico adicional del equipo.", "Continuo · desde semana 1"),
    ("03", "Activación digital del padrón", "Con 3,471 celulares válidos, el alcance digital supera las 15,000 personas. WhatsApp y SMS segmentados por perfil — mensaje correcto, persona correcta.", "Semana 3–4"),
    ("04", "Plataforma en producción · acceso completo", "Sistema desplegado en la nube con acceso seguro para Alan y el equipo estratégico. Datos actualizados en tiempo real. Sin dependencia técnica del equipo.", "1 semana después de contrato"),
]

for i, (num, titulo, body, tiempo) in enumerate(pasos):
    col = col_p1 if i % 2 == 0 else col_p2
    with col:
        st.markdown(f"""
        <div class="paso-card">
            <div class="paso-numero">{num}</div>
            <div>
                <div class="paso-titulo">{titulo}</div>
                <div class="paso-body">{body}</div>
                <span class="paso-tiempo">⏱ {tiempo}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# CONTACTO
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="contacto-wrap">
    <div class="contacto-titulo">¿Arrancamos?</div>
    <div class="contacto-sub">
        Una reunión de 30 minutos para definir el alcance, los entregables y la propuesta económica.<br>
        Todo lo que viste hoy puede estar activo en tu campaña en menos de una semana.
    </div>
    <span class="contacto-item">📧 omar.tellez@socialinclusiontech.com</span>
    <span class="contacto-item">📱 52 55 2885 6227 </span>
    <span class="contacto-item">🌐 dat-ai-tech-c06576.webflow.io</span>
    <div class="contacto-empresa">
        Data & AI Inclusion Technologies · México · 2027
    </div>
</div>
""", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Data & AI Inclusion Tech · PIE Demo · Alan Rentería · MC · Puerto Peñasco, Sonora 2027 · Confidencial<br>
    Uso exclusivo del equipo de campaña · Sin exportación de datos
</div>
""", unsafe_allow_html=True)

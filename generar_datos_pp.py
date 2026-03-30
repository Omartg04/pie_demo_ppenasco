"""
generar_datos_pp.py  v4
27 secciones REALES del INE · Puerto Peñasco, Sonora
Sin geopandas — usa pyshp + pyproj + shapely

Instalar:
    python3 -m pip install pyshp shapely pyproj

Ejecutar desde la raiz del proyecto:
    python3 generar_datos_pp.py
"""

import os, random, json
import numpy as np
import pandas as pd
import shapefile
from shapely.geometry import shape, Point, Polygon, mapping
from pyproj import Transformer

random.seed(42)
np.random.seed(42)

BASE     = os.path.dirname(os.path.abspath(__file__))
OUT      = os.path.join(BASE, "data")
SHP_PATH = os.path.join(BASE, "data", "SECCION.shp")
if not os.path.exists(SHP_PATH):
    SHP_PATH = "/mnt/user-data/uploads/SECCION.shp"
os.makedirs(OUT, exist_ok=True)

# ── 0. Leer shapefile → polígonos WGS84 ──────────────────────────────────────
print("Cargando shapefile...")
sf     = shapefile.Reader(SHP_PATH)
fields = [f[0] for f in sf.fields[1:]]
t      = Transformer.from_crs("EPSG:32612", "EPSG:4326", always_xy=True)

poly_dict        = {}   # sec_ine -> Polygon WGS84
geojson_features = []

for sr in sf.shapeRecords():
    rec = dict(zip(fields, sr.record))
    if rec['municipio'] != 53:
        continue
    sec      = int(rec['seccion'])
    raw_geom = shape(sr.shape.__geo_interface__)
    if raw_geom.geom_type == 'Polygon':
        coords = [t.transform(x, y) for x, y in raw_geom.exterior.coords]
        poly   = Polygon(coords)
    else:
        parts = [Polygon([t.transform(x,y) for x,y in g.exterior.coords]) for g in raw_geom.geoms]
        poly  = max(parts, key=lambda p: p.area)
    if not poly.is_valid:
        poly = poly.buffer(0)
    poly_dict[sec] = poly
    geojson_features.append({
        "type": "Feature",
        "properties": {"seccion": sec, "municipio": int(rec['municipio'])},
        "geometry": mapping(poly),
    })

with open(os.path.join(OUT, "pp_secciones.geojson"), "w", encoding="utf-8") as f:
    json.dump({"type":"FeatureCollection","features":geojson_features}, f)
print(f"  pp_secciones.geojson — {len(poly_dict)} secciones reales")

# ════════════════════════════════════════════════════════════════════════════════
# DEFINICIÓN DE LAS 27 SECCIONES REALES
# Criterio de ámbito:
#   urbano        — área < 0.00015 grados² (~1.5km²), zona central compacta
#   rural_media   — área 0.00015–0.01, zona periurbana o costera
#   rural_marginal — área > 0.01, zonas extensas (648 = ejido/desierto enorme)
#
# Distribución: 8 prioritarias · 13 consolidación · 6 mantenimiento
# Sin cobertura: 5 secciones — 3 prioritarias + 2 consolidación (máximo impacto)
# ════════════════════════════════════════════════════════════════════════════════

# (seccion, ambito, clasificacion, SPT, arq, tactica)
SECCIONES_DEF = [
    # ── PRIORITARIAS (8) ─────────────────────────────────────────────────────
    (647, "urbano",         "Prioritaria",   71.2, "C1", "Brigadas de primer contacto urgentes"),
    (646, "urbano",         "Prioritaria",   69.8, "C1", "Brigadas de primer contacto urgentes"),
    (645, "urbano",         "Prioritaria",   68.3, "C2", "Brigadas primer contacto + cierre"),
    (640, "urbano",         "Prioritaria",   67.5, "C2", "Brigadas de primer contacto urgentes"),
    (631, "rural_media",    "Prioritaria",   66.9, "R1", "Brigadas de primer contacto urgentes"),
    (634, "rural_media",    "Prioritaria",   65.8, "R1", "Brigadas urgentes — sin cobertura"),
    (635, "rural_media",    "Prioritaria",   65.1, "R1", "Brigadas urgentes — sin cobertura"),
    (648, "rural_marginal", "Prioritaria",   64.4, "R1", "Brigadas urgentes — sin cobertura"),
    # ── CONSOLIDACIÓN (13) ───────────────────────────────────────────────────
    (639, "urbano",         "Consolidacion", 58.7, "C2", "Activar multiplicadores + redes"),
    (641, "urbano",         "Consolidacion", 57.4, "C2", "Activar multiplicadores + redes"),
    (642, "urbano",         "Consolidacion", 56.1, "C3", "Brigadas de refuerzo de imagen"),
    (643, "urbano",         "Consolidacion", 54.8, "C3", "Mensajes SMS + WhatsApp masivo"),
    (636, "urbano",         "Consolidacion", 53.2, "C2", "Activar multiplicadores + redes"),
    (632, "rural_media",    "Consolidacion", 56.9, "R1", "Brigadas de refuerzo + primer contacto"),
    (1582,"rural_media",    "Consolidacion", 55.3, "R1", "Brigadas de refuerzo de imagen"),
    (1583,"rural_media",    "Consolidacion", 53.7, "R2", "Activar base + cierre de persuasion"),
    (1584,"rural_media",    "Consolidacion", 52.1, "R2", "Activar base + cierre de persuasion"),
    (1585,"rural_media",    "Consolidacion", 50.8, "R1", "Primer contacto + activacion"),
    (1586,"rural_marginal", "Consolidacion", 49.5, "R1", "Brigadas de primer contacto"),
    (637,  "urbano",        "Consolidacion", 51.4, "C3", "Brigadas de refuerzo — sin cobertura"),
    (1587, "rural_marginal","Consolidacion", 48.2, "R1", "Brigadas de primer contacto — sin cobertura"),
    # ── MANTENIMIENTO (6) ────────────────────────────────────────────────────
    (633, "urbano",         "Mantenimiento", 44.6, "C4", "Mantener contacto — no saturar"),
    (644, "rural_media",    "Mantenimiento", 43.8, "R2", "Mantener base — brigadas bimestrales"),
    (1588,"rural_media",    "Mantenimiento", 42.4, "R2", "Mantener contacto — no saturar"),
    (1589,"rural_marginal", "Mantenimiento", 41.1, "R2", "Mantener presencia — visitas periodicas"),
    (1590,"rural_marginal", "Mantenimiento", 40.3, "R2", "Mantener presencia — visitas periodicas"),
    (1591,"rural_marginal", "Mantenimiento", 39.2, "R2", "Mantener contacto — no saturar"),
]

# 5 secciones sin cobertura: 3 prioritarias + 2 consolidacion
SECCIONES_SIN_COB = {634, 635, 648, 637, 1587}

# ── 1. spt_secciones_pp.csv ───────────────────────────────────────────────────
rows_spt = []
for (sec, amb, clas, spt, arq, tact) in SECCIONES_DEF:
    if clas == "Prioritaria":
        pno=round(np.random.uniform(48,60),1); pper=round(np.random.uniform(28,38),1); pnd=round(np.random.uniform(3,8),1)
    elif clas == "Consolidacion":
        pno=round(np.random.uniform(30,48),1); pper=round(np.random.uniform(25,40),1); pnd=round(np.random.uniform(8,18),1)
    else:
        pno=round(np.random.uniform(15,30),1); pper=round(np.random.uniform(20,35),1); pnd=round(np.random.uniform(18,28),1)
    pnc = max(0, round(100-pno-pper-pnd, 1))
    rows_spt.append({
        "seccion": sec, "ambito_iter": amb, "activa": True,
        "SPT": round(spt,2), "clasificacion": clas, "tactica_recomendada": tact,
        "score_electoral_norm": round(min(100,max(0,spt+np.random.normal(2,5))),2),
        "score_demografico":    round(min(100,max(0,spt+np.random.normal(-3,8))),2),
        "score_arquetipos":     round(min(100,max(0,spt+np.random.normal(1,6))),2),
        "score_cobertura": 0.0 if sec in SECCIONES_SIN_COB else round(min(100,max(30,spt+np.random.normal(-5,12))),2),
        "pct_no_alcanzados":pno, "pct_persuadibles":pper,
        "pct_nucleo_duro":pnd, "pct_no_convertibles":pnc,
        "arq_dominante": arq,
        "entrevistas": 0 if sec in SECCIONES_SIN_COB else int(np.random.randint(12,45)),
        "fuente_arquetipos": "proyectado" if sec in SECCIONES_SIN_COB else "encuesta",
        "score_electoral_parcial": False,
    })

spt_df = pd.DataFrame(rows_spt)
spt_df.to_csv(os.path.join(OUT, "spt_secciones_pp.csv"), index=False)
print(f"  spt_secciones_pp.csv — {len(spt_df)} secciones")
print(f"  Clasificaciones: {spt_df['clasificacion'].value_counts().to_dict()}")
print(f"  Sin cobertura: {sorted(SECCIONES_SIN_COB)}")

# ── 2. contactos_pp.csv ───────────────────────────────────────────────────────
def punto_en_poligono(poly, intentos=300):
    minx,miny,maxx,maxy = poly.bounds
    for _ in range(intentos):
        p = Point(random.uniform(minx,maxx), random.uniform(miny,maxy))
        if poly.contains(p):
            return round(p.y,6), round(p.x,6)
    c = poly.centroid
    return round(c.y,6), round(c.x,6)

# Contactos por sección — proporcional a SPT, 0 para sin cobertura
# Total objetivo: ~5,200
CONTACTOS = {
    647:380, 646:350, 645:320, 640:300,       # prioritarias urbanas con cobertura
    631:260, 634:0,   635:0,   648:0,         # prioritarias rurales (3 sin cobertura)
    639:280, 641:260, 642:240, 643:220,        # consolidacion urbana
    636:200, 632:240, 1582:210, 1583:190,      # consolidacion
    1584:170, 1585:160, 1586:150,              # consolidacion
    637:0,   1587:0,                           # consolidacion sin cobertura
    633:180, 644:160, 1588:150, 1589:140,      # mantenimiento
    1590:130, 1591:120,                        # mantenimiento
}

NOMBRES   = ["Maria","Jose","Juan","Ana","Luis","Carmen","Carlos","Rosa","Miguel",
             "Guadalupe","Francisco","Patricia","Antonio","Margarita","Roberto",
             "Sofia","Alejandro","Veronica","Manuel","Elena","Jorge","Laura",
             "Sergio","Claudia","Ricardo","Norma","Eduardo","Adriana","Fernando",
             "Sandra","Oscar","Leticia","Ernesto","Diana","Hector","Monica"]
APELLIDOS = ["Garcia","Martinez","Lopez","Rodriguez","Gonzalez","Hernandez",
             "Perez","Sanchez","Ramirez","Torres","Flores","Reyes","Cruz",
             "Morales","Ortiz","Ramos","Vazquez","Mendoza","Jimenez","Ruiz",
             "Cardenas","Valenzuela","Bojorquez","Celaya","Gastelum","Zazueta",
             "Moreno","Ibarra","Esquer","Acosta","Ochoa","Lizarraga","Bernal"]
COLONIAS  = ["Centro","Las Conchas","Puerto Viejo","Playas de Encanto","El Cholla",
             "Fraccionamiento Penasco","Colonia Nuevo Penasco","El Mirador",
             "Fraccionamiento del Mar","La Marina","Villa Bonita","Ejido Coahuila",
             "Ejido Suviri","Colonia Pescadores","Barrio Antiguo","Los Medanos"]
SEG_DIST  = {
    "Prioritaria":  {"Primer contacto":0.42,"Persuasión":0.35,"Activación":0.15,"Multiplicadores":0.08},
    "Consolidacion":{"Persuasión":0.40,"Primer contacto":0.28,"Multiplicadores":0.18,"Activación":0.14},
    "Mantenimiento":{"Multiplicadores":0.32,"Persuasión":0.30,"Activación":0.22,"Primer contacto":0.16},
}
CANALES  = ["WhatsApp","SMS","Email","Visita"]
MENSAJES = {
    "Multiplicadores":"Invitarlo a ser promotor — ya conoce a Alan y votaria por el.",
    "Activación":     "Reforzar presencia de Alan — ya votaria pero aun no lo conoce.",
    "Persuasión":     "Cerrar el voto — conoce a Alan pero no ha decidido.",
    "Primer contacto":"Primera presentacion — no conoce a Alan ni ha decidido.",
}
clas_map = {r["seccion"]: r["clasificacion"] for r in rows_spt}

contactos = []
for sec, n_total in CONTACTOS.items():
    if n_total == 0:
        continue
    poly = poly_dict.get(sec)
    if poly is None:
        print(f"  WARNING: sin poligono para sec={sec}")
        continue
    clas = clas_map.get(sec, "Consolidacion")
    dist = SEG_DIST[clas]
    for i in range(n_total):
        seg = np.random.choice(list(dist.keys()), p=list(dist.values()))
        if   seg=="Multiplicadores": canal=np.random.choice(CANALES,p=[0.55,0.20,0.15,0.10])
        elif seg=="Primer contacto": canal=np.random.choice(CANALES,p=[0.25,0.20,0.10,0.45])
        else:                        canal=np.random.choice(CANALES,p=[0.45,0.25,0.15,0.15])
        tiene_cel = random.random() < 0.72
        lat,lon   = punto_en_poligono(poly)
        nombre    = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        contactos.append({
            "id":f"PP{sec}-{i+1:04d}", "nombre":nombre,
            "seccion":sec, "colonia":random.choice(COLONIAS), "municipio":"Puerto Penasco",
            "celular":f"638{random.randint(1000000,9999999)}" if tiene_cel else None,
            "email":f"{nombre.split()[0].lower()}.{random.randint(10,99)}@gmail.com" if random.random()<0.35 else None,
            "latitud":lat, "longitud":lon, "segmento":seg, "canal":canal,
            "mensaje_tipo":MENSAJES[seg],
            "fecha_contacto":pd.Timestamp("2026-01-15")+pd.Timedelta(days=random.randint(0,60)),
            "encuestador":f"Brigadista-{random.randint(1,12):02d}",
        })

df_c = pd.DataFrame(contactos)
df_c.to_csv(os.path.join(OUT, "contactos_pp.csv"), index=False)
print(f"  contactos_pp.csv — {len(df_c):,} contactos")
print(f"  Bbox lat: {df_c['latitud'].min():.4f} -> {df_c['latitud'].max():.4f}")
print(f"  Con celular: {df_c['celular'].notna().sum():,} ({df_c['celular'].notna().mean()*100:.1f}%)")
print(f"  Segmentos: {df_c['segmento'].value_counts().to_dict()}")
print("\nDone.")
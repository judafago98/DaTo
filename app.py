import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import datetime
import time
import uuid
import calendar
import os

# --- EJECUCIÓN INVISIBLE: Autocorrección de la Base de Datos ---
def auto_fix_db(cursor, conn):
    try:
        cursor.execute("ALTER TABLE Pagos MODIFY COLUMN tipo_pago VARCHAR(255)")
        conn.commit()
    except Exception: pass

# --- Configuración visual de la app ---
st.set_page_config(page_title="DaTo Workspace", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# --- CINTURÓN DE SEGURIDAD PARA ASSETS VISUALES ---
def renderizar_logo(es_sidebar=False):
    if os.path.exists("logo.png"):
        st.image("logo.png")
    else:
        alto = "120px" if es_sidebar else "250px"
        fuente = "2.5rem" if es_sidebar else "4.5rem"
        st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: center; height: {alto}; background: linear-gradient(135deg, rgba(0, 30, 60, 0.4), rgba(0, 0, 0, 0.8)); border-radius: 30px; border: 1px solid rgba(0, 198, 255, 0.3); box-shadow: 0 10px 40px rgba(0, 198, 255, 0.15), inset 0 0 20px rgba(0, 198, 255, 0.05); margin-bottom: 15px; backdrop-filter: blur(10px);'>
            <h1 style='color: transparent; font-size: {fuente}; font-weight: 800; text-transform: uppercase; letter-spacing: 4px; margin:0; background-image: linear-gradient(90deg, #00C6FF, #0066FF); -webkit-background-clip: text; text-shadow: 0px 0px 20px rgba(0, 198, 255, 0.4);'>⚡ DaTo</h1>
        </div>
        """, unsafe_allow_html=True)

# --- DISEÑO ULTRA PREMIUM Y RESPONSIVO (NIVEL DIOS - NEON GLASSMORPHISM) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        /* FORZAR VARIABLES GLOBALES DE STREAMLIT A LA PALETA AZUL/NEGRO */
        :root {
            --primary-color: #00E5FF !important;
            --background-color: #020617;
            --secondary-background-color: rgba(10, 20, 40, 0.6);
            --text-color: #FFFFFF;
        }

        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

        /* FONDO DINÁMICO AZUL PROFUNDO Y NEGRO */
        .stApp {
            background-color: #020617;
            background-image: radial-gradient(circle at top right, rgba(0, 102, 255, 0.12), transparent 45%),
                              radial-gradient(circle at bottom left, rgba(0, 229, 255, 0.08), transparent 45%);
            background-attachment: fixed;
            color: #F8FAFC;
        }
        
        #MainMenu, footer {display: none !important;}
        header, [data-testid="stHeader"] {background: transparent !important;}
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 198, 255, 0.2); border-radius: 20px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0, 198, 255, 0.8); }

        /* ==============================================================
           MUERTE A LOS ROJOS Y VERDES POR DEFECTO (EXTREMO)
           ============================================================== */
           
        /* ASESINATO DEL ROJO EN EL TOGGLE (Activar UI Pública) */
        [data-testid="stCheckbox"] div[data-checked="true"] {
            background-color: #00E5FF !important;
        }
        [data-testid="stCheckbox"] div[data-checked="true"] > div {
            background-color: #FFFFFF !important;
        }

        /* BOTONES DE INCREMENTO/DECREMENTO EN NUMBER_INPUT (Matando el rojo) */
        [data-testid="stNumberInput"] button {
            background-color: rgba(10, 20, 40, 0.8) !important;
            border: 1px solid rgba(0, 198, 255, 0.3) !important;
            color: #00E5FF !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stNumberInput"] button:hover {
            background-color: rgba(0, 198, 255, 0.2) !important;
            color: #FFFFFF !important;
            border-color: #00E5FF !important;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.4) !important;
        }
        [data-testid="stNumberInput"] button:active {
            background-color: #0066FF !important;
            color: white !important;
        }

        /* ALERTAS / SUCCESS BOX (Matando el verde plano) */
        [data-testid="stAlert"] {
            background: linear-gradient(90deg, rgba(0, 102, 255, 0.15), rgba(0, 198, 255, 0.05)) !important;
            border: 1px solid rgba(0, 198, 255, 0.3) !important;
            border-left: 5px solid #00E5FF !important;
            border-radius: 12px !important;
            backdrop-filter: blur(15px) !important;
            color: #FFFFFF !important;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.5) !important;
            padding: 1rem !important;
        }
        [data-testid="stAlert"] svg { fill: #00E5FF !important; }
        [data-testid="stAlert"] div { color: #FFFFFF !important; font-weight: 500 !important; }

        /* TABS (PESTAÑAS) FLUIDAS */
        [data-baseweb="tab-list"] { gap: 12px; background: transparent !important; border-bottom: none !important; }
        [data-baseweb="tab"] {
            background: rgba(4, 13, 30, 0.4) !important;
            border: 1px solid rgba(0, 198, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 10px 20px !important;
            transition: all 0.3s ease !important;
            color: #94A3B8 !important;
        }
        [data-baseweb="tab"]:hover { background: rgba(0, 198, 255, 0.1) !important; color: #FFFFFF !important; }
        [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 198, 255, 0.1)) !important;
            border: 1px solid rgba(0, 198, 255, 0.4) !important;
            color: #00E5FF !important;
            box-shadow: 0 5px 20px rgba(0, 198, 255, 0.2) !important;
        }
        [data-baseweb="tab-highlight"] { display: none !important; background-color: #00E5FF !important; }

        /* INPUTS REDONDEADOS */
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stSelectbox"] div[data-baseweb="select"],
        [data-testid="stNumberInput"] div[data-baseweb="input"],
        .stTextArea textarea {
            background: rgba(10, 20, 40, 0.6) !important;
            border: 1px solid rgba(0, 198, 255, 0.2) !important;
            border-radius: 12px !important; 
            backdrop-filter: blur(12px) !important;
            color: #FFFFFF !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
        [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within,
        [data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within,
        .stTextArea textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.2) !important;
            background: rgba(15, 30, 60, 0.9) !important;
        }

        /* BOTONES PRINCIPALES */
        .stButton>button {
            background: linear-gradient(135deg, #0044BB 0%, #0099FF 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(0, 198, 255, 0.3) !important;
            border-radius: 12px !important; 
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            padding: 0.8rem 2rem !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3) !important;
            width: 100% !important;
        }
        .stButton>button:hover {
            transform: translateY(-3px) scale(1.01) !important;
            box-shadow: 0 8px 25px rgba(0, 229, 255, 0.4) !important;
            background: linear-gradient(135deg, #0066FF 0%, #00E5FF 100%) !important;
            border-color: #00E5FF !important;
        }
        .stButton>button:active { transform: translateY(1px) scale(0.99) !important; }

        /* ==============================================================
           SIDEBAR NEON GLASSMORPHISM (BYE BYE RED CIRCLES)
           ============================================================== */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 15, 0.85) !important; 
            backdrop-filter: blur(30px);
            border-right: 1px solid rgba(0, 198, 255, 0.1);
        }
        
        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 8px !important;
        }
        
        /* ESTADO NEUTRO (Botón inactivo) */
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(10, 20, 40, 0.3) !important; 
            border: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-radius: 12px !important; 
            padding: 14px 16px !important; 
            margin: 2px 12px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer;
        }
        
        /* ¡ELIMINADOR DEFINITIVO DEL CÍRCULO ROJO/NATIVO DE STREAMLIT! */
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child,
        [data-testid="stSidebar"] div[role="radiogroup"] label > span:first-child,
        [data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            position: absolute !important;
        }
        
        /* Texto del botón inactivo */
        [data-testid="stSidebar"] div[role="radiogroup"] label p {
            color: #8B9BB4 !important; 
            font-size: 14px !important; 
            font-weight: 500 !important; 
            margin: 0 !important; 
            width: 100%;
            text-align: left;
            transition: all 0.3s ease;
        }
        
        /* ESTADO HOVER */
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(0, 229, 255, 0.05) !important; 
            border-color: rgba(0, 229, 255, 0.2) !important;
            transform: translateX(4px);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover p { 
            color: #FFFFFF !important; 
        }
        
        /* ESTADO ACTIVO (MODO NEON) */
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
        [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
            background: linear-gradient(90deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 102, 255, 0.05) 100%) !important;
            border-left: 4px solid #00E5FF !important;
            border-top: 1px solid rgba(0, 229, 255, 0.3) !important;
            border-bottom: 1px solid rgba(0, 229, 255, 0.3) !important;
            border-right: 1px solid rgba(0, 229, 255, 0.1) !important;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.2), inset 0 0 10px rgba(0, 229, 255, 0.1) !important;
            transform: scale(1.02) translateX(2px);
        }
        
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p,
        [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p { 
            color: #FFFFFF !important; 
            font-weight: 800 !important; 
            letter-spacing: 0.5px;
            text-shadow: 0 0 12px rgba(0, 229, 255, 0.8) !important;
        }
        
        /* KPIS METRICS */
        [data-testid="stMetric"] {
            background: rgba(10, 20, 40, 0.5); backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 20px;
            border-left: 4px solid #0066FF; transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover { 
            border-left: 4px solid #00E5FF; transform: translateY(-5px); 
            box-shadow: 0 10px 25px rgba(0, 102, 255, 0.15); 
        }

        h1, h2, h3 { color: #FFFFFF !important; font-weight: 700 !important; }
        .fade-in { animation: fadeIn 0.6s ease forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .anim-border-gradient {
            background: linear-gradient(45deg, #020617, #0066FF, #00C6FF, #020617);
            background-size: 400% 400%;
            animation: gradient-breathe 8s ease infinite;
            padding: 2px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 102, 255, 0.2);
            margin-bottom: 25px;
        }
        .anim-border-inner {
            background: rgba(4, 10, 20, 0.95);
            backdrop-filter: blur(25px);
            border-radius: 18px;
            padding: 30px;
            height: 100%;
        }
        @keyframes gradient-breathe { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛡️ FUNCIONES GLOBALES Y FORMATOS (ONLY BLUES)
# ==========================================
def fmt_cop(val):
    try: val_int = int(float(val))
    except (ValueError, TypeError): return "$0"
    s = f"{val_int:,}" 
    is_neg = val_int < 0
    if is_neg: s = s[1:]
    parts = s.split(',')
    if len(parts) == 3: res = f"{parts[0]}'{parts[1]}.{parts[2]}"
    elif len(parts) == 4: res = f"{parts[0]}.{parts[1]}'{parts[2]}.{parts[3]}"
    else: res = s.replace(',', '.')
    return f"-${res}" if is_neg else f"${res}"

def color_estado(val):
    if val in ['Pagado', 'Pagada', 'Completado']: return 'background-color: rgba(0, 229, 255, 0.1); color: #00E5FF; font-weight: 600; border-radius: 8px;'
    elif val in ['Activo', 'Pendiente']: return 'background-color: rgba(0, 102, 255, 0.1); color: #0066FF; font-weight: 600; border-radius: 8px;'
    elif val in ['Disponible']: return 'background-color: rgba(0, 198, 255, 0.15); color: #00C6FF; font-weight: 600; border-radius: 8px;'
    elif val in ['Vendido']: return 'background-color: rgba(255, 255, 255, 0.05); color: #94A3B8; font-weight: 600; border-radius: 8px;'
    return ''

def color_estado_cuota(val):
    if 'Pagada' in val: return 'background-color: rgba(0, 229, 255, 0.1); color: #00E5FF; font-weight: 600;'
    elif 'Parcial' in val: return 'background-color: rgba(0, 153, 255, 0.1); color: #0099FF; font-weight: 600;'
    else: return 'color: #0066FF; font-weight: 500;'

def color_ganancia_real(val):
    if '-' in str(val): return 'color: #94A3B8; font-weight: 500;'
    return 'color: #00E5FF; font-weight: 600;'

def sumar_meses_exactos(fecha_base, meses_a_sumar):
    mes = fecha_base.month - 1 + meses_a_sumar
    año = fecha_base.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha_base.day, calendar.monthrange(año, mes)[1])
    return datetime.date(año, mes, dia)

def generar_plan_pagos_real(id_credito, cursor):
    cursor.execute("SELECT * FROM Creditos WHERE id_credito=%s", (id_credito,))
    cred = cursor.fetchone()
    cursor.execute("SELECT monto_recibido, fecha_pago FROM Pagos WHERE id_credito=%s ORDER BY fecha_pago ASC", (id_credito,))
    pagos_hist = cursor.fetchall()
    
    pagado_total = sum([float(p['monto_recibido']) for p in pagos_hist])
    
    cursor.execute("SELECT * FROM Cuotas_Programadas WHERE id_credito=%s ORDER BY numero_cuota ASC", (id_credito,))
    cuotas_fijas = cursor.fetchall()
    plan, pagado_acum = [], pagado_total
    
    if cuotas_fijas:
        for idx, c in enumerate(cuotas_fijas):
            esperado = float(c['monto_esperado'])
            if pagado_acum >= esperado: 
                est, pagado_acum = '☑️ Pagada', pagado_acum - esperado
                f_pago_mostrar = pagos_hist[idx]['fecha_pago'].strftime('%Y-%m-%d') if idx < len(pagos_hist) else '---'
            elif pagado_acum > 0: 
                est, pagado_acum = f'🔷 Parcial (Abonó {fmt_cop(pagado_acum)})', 0
                f_pago_mostrar = pagos_hist[idx]['fecha_pago'].strftime('%Y-%m-%d') if idx < len(pagos_hist) else '---'
            else: 
                est, f_pago_mostrar = '🔹 Pendiente', '---'
            plan.append({'Cuota': f"Número {c['numero_cuota']}", 'Vencimiento Límite': c['fecha_vencimiento'], 'Valor Exigido': fmt_cop(esperado), 'Estado Actual': est, 'Fecha de Pago': f_pago_mostrar})
    else:
        plazo, valor, f_base = int(cred['plazo_meses']), float(cred['valor_cuota'] or 0), cred['fecha_primera_cuota']
        for i in range(1, plazo + 1):
            if not f_base: break
            f_venc = sumar_meses_exactos(f_base, i - 1)
            esperado = valor
            if pagado_acum >= esperado: 
                est, pagado_acum = '☑️ Pagada', pagado_acum - esperado
                f_pago_mostrar = pagos_hist[i-1]['fecha_pago'].strftime('%Y-%m-%d') if (i-1) < len(pagos_hist) else '---'
            elif pagado_acum > 0: 
                est, pagado_acum = f'🔷 Parcial (Abonó {fmt_cop(pagado_acum)})', 0
                f_pago_mostrar = pagos_hist[i-1]['fecha_pago'].strftime('%Y-%m-%d') if (i-1) < len(pagos_hist) else '---'
            else: 
                est, f_pago_mostrar = '🔹 Pendiente', '---'
            plan.append({'Cuota': f"Mes {i}", 'Vencimiento Límite': f_venc.strftime('%Y-%m-%d'), 'Valor Exigido': fmt_cop(esperado), 'Estado Actual': est, 'Fecha de Pago': f_pago_mostrar})
    return pd.DataFrame(plan)

CATALOGO = {
    "📱 Celular": {"Apple": ["iPhone 16 Pro Max", "iPhone 16 Pro", "iPhone 15 Pro Max", "iPhone 15", "iPhone 14 Pro Max", "iPhone 13", "iPhone 11", "Otro..."], "Samsung": ["Galaxy S24 Ultra", "Galaxy S23 FE", "Galaxy A55", "Galaxy Z Fold5", "Otro..."], "Xiaomi": ["Redmi Note 13 Pro+", "Poco X6 Pro", "Xiaomi 14", "Otro..."], "Motorola": ["Edge 50 Pro", "Moto G84", "Razr 40 Ultra", "Otro..."], "Otra Marca...": ["Escribir manual..."]},
    "💻 Computador": {"Lenovo": ["ThinkPad T14", "Legion Pro 5", "Otro..."], "ASUS": ["ROG Strix G16", "ZenBook 14", "Otro..."], "HP": ["EliteBook 840", "Victus 15", "Otro..."], "Apple": ["MacBook Air M3", "MacBook Pro M3 Pro", "Otro..."], "Otra Marca...": ["Escribir manual..."]},
    "📺 Electrodoméstico": {"Samsung": ["Televisor QLED", "Nevera Nevecón", "Lavadora", "Otro..."], "LG": ["Televisor OLED", "Torre de Lavado", "Otro..."], "Otra Marca...": ["Escribir manual..."]},
    "🎮 Consolas y Gaming": {"Sony": ["PlayStation 5", "PS VR2", "Otro..."], "Microsoft": ["Xbox Series X", "Xbox Series S", "Otro..."], "Nintendo": ["Switch OLED", "Otro..."], "Otra Marca...": ["Escribir manual..."]},
    "📦 Otros": {"Accesorios": ["AirPods Pro 2", "Apple Watch Series 9", "Otro..."], "Repuestos": ["Pantalla Original", "Batería", "Otro..."], "Otra Categoria...": ["Escribir manual..."]}
}
CAPACIDADES_MOVILES = ["64GB", "128GB", "256GB", "512GB", "1TB", "Otra..."]
CAPACIDADES_PC = ["8GB RAM / 256GB SSD", "16GB RAM / 512GB SSD", "16GB RAM / 1TB SSD", "32GB RAM / 1TB SSD", "Otra..."]
CAPACIDADES_ELECTRO = ["No Aplica", "32 Pulgadas", "50 Pulgadas", "65 Pulgadas", "Escribir manual..."]

# --- CONEXIÓN BLINDADA POR POOL ---
@st.cache_resource
def get_connection_pool():
    return pooling.MySQLConnectionPool(
        pool_name="dato_pool", pool_size=10, pool_reset_session=True,
        host="gateway01.us-east-1.prod.aws.tidbcloud.com", port=4000,
        user="2xRKoKTDAr4tRLF.root", password="7KGQVtKygobgy311",
        database="sistema_creditos", ssl_verify_cert=False,
        autocommit=True, connection_timeout=15, use_pure=True
    )

try:
    pool = get_connection_pool()
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    auto_fix_db(cursor, conn)
except Exception as e:
    st.error(f"🌐 El servidor de base de datos está inalcanzable. Espera 30 segundos y recarga (F5). Detalles: {e}")
    st.stop()

# ==========================================
# CINTURÓN DE SEGURIDAD
# ==========================================
try:
    if 'logeado' not in st.session_state: st.session_state['logeado'] = False
    if 'id_usuario' not in st.session_state: st.session_state['id_usuario'] = None
    if 'nombre_usuario' not in st.session_state: st.session_state['nombre_usuario'] = None
    if 'rol' not in st.session_state: st.session_state['rol'] = None

    if not st.session_state['logeado']:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        col_espacio1, col_izq, col_der, col_espacio2 = st.columns([0.5, 4, 4, 0.5], gap="large", vertical_alignment="center")
        
        with col_izq:
            st.markdown("<div class='fade-in' style='width: 100%;'>", unsafe_allow_html=True)
            renderizar_logo(es_sidebar=False)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_der:
            st.markdown("<div class='fade-in anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
            with st.form("form_login"):
                st.markdown("<h2 style='color: #00E5FF; font-weight: 800; margin-bottom: 5px; font-size: 2.2rem; letter-spacing:-0.5px;'>PORTAL CORPORATIVO</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color: #8B9BB4; margin-bottom: 30px; font-size: 1.05rem;'>Acceso exclusivo para personal operativo DaTo.</p>", unsafe_allow_html=True)
                usuario_input = st.text_input("Usuario")
                password_input = st.text_input("Contraseña", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("INGRESAR", width='stretch'):
                    try:
                        cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                        usuario_db = cursor.fetchone()
                        if usuario_db:
                            st.session_state['logeado'] = True
                            st.session_state['id_usuario'] = usuario_db['id_usuario']
                            st.session_state['nombre_usuario'] = usuario_db['nombre_completo']
                            st.session_state['rol'] = usuario_db['rol']
                            st.rerun()
                        else: st.error("Acceso denegado. Credenciales incorrectas.")
                    except Exception as e: st.error(f"Falla de conexión a Base de Datos: {e}")
            st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        es_admin = st.session_state['rol'] in ['Admin', 'Administrador']
        
        MODULOS_TOTALES = {
            "🔮 Cotizador y Simulación": "simulador",
            "📦 Gestión de Inventario": "inventario",
            "👥 Directorio de Clientes": "clientes",
            "📝 Originación de Créditos": "ventas",
            "💰 Centro de Recaudos": "pagos",
            "⏰ Control de Cartera y Mora": "vencimientos",
            "📱 Estados de Cuenta": "notificar",
            "📜 Auditoría de Operaciones": "historial",
            "💸 Control de Gastos": "egresos",
            "📈 Fondeo y Socios": "flujo",
            "📊 Inteligencia de Negocios (BI)": "reportes",
            "⚙️ Configuración y Seguridad": "config_roles"
        }

        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        with st.sidebar:
            renderizar_logo(es_sidebar=True)
        
        st.sidebar.markdown(f"""
            <div style='padding: 15px; background: linear-gradient(90deg, rgba(0, 102, 255, 0.1), rgba(0, 198, 255, 0.05)); border-radius: 16px; border: 1px solid rgba(0,198,255,0.2); margin-bottom: 20px; text-align: center; backdrop-filter: blur(10px);'>
                <b style='color:#FFFFFF; font-size: 16px; letter-spacing: 0.5px;'>{st.session_state['nombre_usuario']}</b><br>
                <span style='color:#00E5FF; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;'>{str(st.session_state['rol'])}</span>
            </div>
        """, unsafe_allow_html=True)
        
        menu_map = {"🏠 Panel Central": "inicio"} 
        if es_admin:
            menu_map.update(MODULOS_TOTALES)
        else:
            cursor.execute("SELECT m.nombre_interno FROM Modulos_Sistema m JOIN Permisos_Rol p ON m.id_modulo = p.id_modulo JOIN Roles r ON p.id_role = r.id_role WHERE r.nombre_rol = %s", (st.session_state['rol'],))
            for m in cursor.fetchall(): 
                for k, v in MODULOS_TOTALES.items():
                    if v == m['nombre_interno']: menu_map[k] = m['nombre_interno']
        
        menu_seleccionado_texto = st.sidebar.radio("Navegación", list(menu_map.keys()), label_visibility="collapsed")
        menu_seleccionado = menu_map[menu_seleccionado_texto]
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("CERRAR SESIÓN", width='stretch'):
            st.session_state['logeado'] = False; st.rerun()

        if menu_seleccionado == "inicio":
            st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Animación de Caricatura Divertida para el inicio (Gato Hacker)
                url_gif_divertido = "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif"
                st.markdown(f"""
                <div class="fade-in anim-border-gradient">
                    <div class="anim-border-inner" style="text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <img src="{url_gif_divertido}" style="border-radius: 20px; width: 100%; max-width: 350px; border: 2px solid rgba(0, 198, 255, 0.3); box-shadow: 0 10px 30px rgba(0, 198, 255, 0.2);">
                        <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 25px; margin-bottom: 0; color: #FFFFFF;'>HOLA, <span style='color: #00E5FF;'>{st.session_state['nombre_usuario'].split(" ")[0].upper()}</span></h1>
                        <p style='color: #8B9BB4; font-size: 1.1rem; font-weight: 300; margin-top: 10px;'>Es hora de poner a trabajar el ecosistema.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "simulador":
            st.markdown("<h2 class='fade-in' style='margin-bottom: 25px;'>🔮 Cotizador y Simulación Financiera</h2>", unsafe_allow_html=True)
            tab_sim, tab_paz = st.tabs(["📊 Simular Esquema de Cuotas", "🤝 Liquidación Paz y Salvo"])
            
            with tab_sim:
                st.markdown("<br>", unsafe_allow_html=True)
                
                modo_cliente = st.toggle("📸 Activar UI Pública (Vista Cliente)")
                if 'tasa_simulador' not in st.session_state:
                    st.session_state['tasa_simulador'] = 3.0
                    
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sim_precio = st.number_input("Valor Comercial del Activo ($)", min_value=0, step=10000, value=2000000)
                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom: 15px;'>{fmt_cop(sim_precio)}</div>", unsafe_allow_html=True)
                    sim_abono = st.number_input("Inyección de Capital Inicial ($)", min_value=0, step=10000, value=500000)
                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px;'>{fmt_cop(sim_abono)}</div>", unsafe_allow_html=True)
                with col_s2:
                    sim_plazo = st.number_input("Periodo de Amortización (Meses)", min_value=1, max_value=72, step=1, value=6)
                    
                    if not modo_cliente:
                        idx_tasa = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0].index(st.session_state['tasa_simulador']) if st.session_state['tasa_simulador'] in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] else 3
                        sim_tasa = st.selectbox("Tasa de Interés Efectiva (T.E.M) %", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=idx_tasa)
                        st.session_state['tasa_simulador'] = sim_tasa
                    else:
                        sim_tasa = st.session_state['tasa_simulador']
                    
                sim_capital = sim_precio - sim_abono
                if sim_capital > 0:
                    i_m = sim_tasa / 100.0
                    sim_cuota = sim_capital * (i_m * (1 + i_m)**sim_plazo) / (((1 + i_m)**sim_plazo) - 1) if sim_tasa > 0 else sim_capital / sim_plazo
                    st.success(f"🔹 **Proyección de Mensualidad:** {fmt_cop(int(round(sim_cuota)))}")
                else: st.info("El capital inicial liquida el activo en su totalidad.")
                st.markdown("</div></div>", unsafe_allow_html=True)

            with tab_paz:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.documento, i.modelo, c.monto_financiado, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
                creditos_act = cursor.fetchall()
                if not creditos_act: st.info("Cartera sana. Sin deudores activos.")
                else:
                    opc_paz = {f"{c['documento']} | {c['nombre_completo']} ({c['modelo']})": c for c in creditos_act}
                    sel_paz = st.selectbox("Extraer metadata del deudor:", list(opc_paz.keys()), index=None, placeholder="Buscar en la base de clientes...")
                    
                    if sel_paz:
                        datos_paz = opc_paz[sel_paz]
                        cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (datos_paz['id_credito'],))
                        res = cursor.fetchone()
                        saldo_capital = float(datos_paz['monto_financiado']) - float(res['cap'] if res and res['cap'] else 0.0)
                        interes_mes = saldo_capital * float(datos_paz['tasa_interes_mensual'])
                        
                        st.markdown(f"""
                        <div class="anim-border-gradient" style="margin-top: 20px;">
                            <div class="anim-border-inner" style="text-align: center;">
                                <h3 style="color:#00E5FF; margin:0; font-weight: 600; letter-spacing: 1.5px; font-size: 1.2rem;">MONTO EXACTO DE REDENCIÓN (PAZ Y SALVO)</h3>
                                <h1 style="color:white; font-size: 4rem; font-weight: 800; margin: 10px 0; text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);">{fmt_cop(saldo_capital + interes_mes)}</h1>
                                <p style="color:#8B9BB4; font-size: 15px; margin:0;">Base Capital ({fmt_cop(saldo_capital)}) + Tasa del Periodo ({fmt_cop(interes_mes)})</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        df_plan = generar_plan_pagos_real(datos_paz['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "inventario":
            st.markdown("<h2 class='fade-in'>Gestión de Inventario 📦</h2>", unsafe_allow_html=True)
            tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Matriz de Disponibilidad", "📥 Inyección de Hardware", "📜 Archivo de Salidas"])
            
            with tab_inv1:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT imei AS 'Serial/IMEI', categoria AS 'Tipo', marca AS 'Modelo/Marca', modelo AS 'Detalle', tipo_ingreso AS 'Condición', costo_adquisicion AS 'Costo Compra', precio_venta_contado AS 'Precio Sugerido' FROM Inventario WHERE estado = 'Disponible'")
                df_inventario = pd.DataFrame(cursor.fetchall())
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📦 Activos Físicos", f"{len(df_inventario)}")
                if not df_inventario.empty:
                    c2.metric("💰 Fondo Bloqueado en Stock", fmt_cop(df_inventario['Costo Compra'].sum()))
                    c3.metric("💎 Proyección de Venta Bruta", fmt_cop(df_inventario['Precio Sugerido'].sum()))
                    df_inventario['Costo Compra'] = df_inventario['Costo Compra'].apply(fmt_cop)
                    df_inventario['Precio Sugerido'] = df_inventario['Precio Sugerido'].apply(fmt_cop)
                    st.dataframe(df_inventario, width='stretch')
                else: st.info("Bodegas vacías a nivel sistema.")

            with tab_inv2:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_bolsa, nombre_bolsa, saldo_actual FROM Bolsas_Capital")
                opc_bolsas = {f"{b['nombre_bolsa']} (Liquidez: {fmt_cop(b['saldo_actual'])})": b for b in cursor.fetchall()}

                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: cat_sel = st.selectbox("Clasificación de Hardware", list(CATALOGO.keys()), index=None, placeholder="Seleccione Categoría...")
                
                if cat_sel:
                    with c2: marca_sel = st.selectbox("Fabricante", list(CATALOGO[cat_sel].keys()), index=None, placeholder="Seleccione Marca...")
                    
                    if marca_sel:
                        c3, c4 = st.columns(2)
                        with c3:
                            marca_fin = st.text_input("Ingresar Marca Manual:") if marca_sel == "Otra Marca..." else marca_sel
                            mod = st.selectbox("Denominación Técnica", CATALOGO[cat_sel][marca_sel], index=None, placeholder="Seleccione Modelo...")
                            if mod:
                                mod_fin = st.text_input("Ingresar Modelo Manual:") if mod in ["Otro...", "Escribir manual..."] else mod
                        with c4:
                            if mod:
                                opc_cap = CAPACIDADES_PC if "Cómputo" in cat_sel or "💻" in cat_sel else (CAPACIDADES_ELECTRO if "Electrónica" in cat_sel or "📺" in cat_sel else CAPACIDADES_MOVILES)
                                cap = st.selectbox("Arquitectura / Capacidad", opc_cap, index=None, placeholder="Seleccione Especificaciones...")
                                if cap:
                                    cap_fin = "" if cap == "No Aplica" else (st.text_input("Escribe el detalle:") if cap == "Escribir manual..." else cap)

                        if mod and cap:
                            c5, c6 = st.columns(2)
                            with c5:
                                imei_in = f"SYS-{str(uuid.uuid4())[:8].upper()}" if st.checkbox("Autogenerar Hash Interno") else st.text_input("Serial / IMEI Físico")
                                cond = st.selectbox("Estado de Conservación", ["Nuevo", "Usado", "Retoma"], index=None, placeholder="Seleccione Estado...")
                            with c6:
                                if cond:
                                    bolsa = st.selectbox("Fondo Originador de la Compra", options=list(opc_bolsas.keys()), index=None, placeholder="Seleccione Caja...")
                                    if bolsa:
                                        costo = st.number_input("Desembolso Real de Compra ($)", min_value=0, step=10000, value=0)
                                        st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:10px;'>{fmt_cop(costo)}</div>", unsafe_allow_html=True)
                                        precio = st.number_input("Target de Venta Sugerido ($)", min_value=0, step=10000, value=0)
                                        st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(precio)}</div>", unsafe_allow_html=True)

                                        if st.button("Sellar Bloque en Inventario", width='stretch'):
                                            dat_b = opc_bolsas[bolsa]
                                            if costo > float(dat_b['saldo_actual']): st.error("Fondos insuficientes en la caja origen.")
                                            elif not imei_in or not mod_fin: st.warning("El código de rastreo (IMEI/Serial) es obligatorio.")
                                            else:
                                                cursor.execute("INSERT INTO Inventario (imei, categoria, marca, modelo, tipo_ingreso, id_bolsa, costo_adquisicion, precio_venta_contado, estado, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Disponible', %s)", (imei_in, cat_sel.split(" ")[1] if " " in cat_sel else cat_sel, marca_fin, f"{mod_fin} {cap_fin}".strip(), cond, dat_b['id_bolsa'], costo, precio, st.session_state['id_usuario']))
                                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s WHERE id_bolsa = %s", (costo, dat_b['id_bolsa']))
                                                conn.commit(); st.toast('Bloque indexado.', icon='💠'); time.sleep(1.5); st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

            with tab_inv3:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT i.imei AS 'Serial/IMEI', CONCAT(i.marca, ' ', i.modelo) AS 'Equipo', i.costo_adquisicion AS 'Costo Real', IFNULL(cr.precio_venta, 0) AS 'Precio de Venta (Final)', i.estado AS 'Estado Físico', IFNULL(c.nombre_completo, 'En Bodega') AS 'Cliente Final', IFNULL(cr.fecha_inicio, 'N/A') AS 'Fecha de Despacho'
                    FROM Inventario i LEFT JOIN Creditos cr ON i.imei = cr.imei LEFT JOIN Clientes c ON cr.id_cliente = c.id_cliente ORDER BY i.estado ASC, cr.fecha_inicio DESC
                """)
                df_hist = pd.DataFrame(cursor.fetchall())
                if not df_hist.empty:
                    df_hist['Costo Real'] = df_hist['Costo Real'].apply(fmt_cop)
                    df_hist['Precio de Venta (Final)'] = df_hist['Precio de Venta (Final)'].apply(lambda x: fmt_cop(x) if x > 0 else 'N/A')
                    st.dataframe(df_hist.style.map(color_estado, subset=['Estado Físico']), width='stretch')
                else: st.info("Registro de despachos vacío.")

        elif menu_seleccionado == "clientes":
            st.markdown("<h2 class='fade-in'>Directorio de Clientes 👥</h2>", unsafe_allow_html=True)
            st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
            with st.form("f_cli"):
                doc = st.text_input("Documento de Identidad (C.C.)")
                nom = st.text_input("Nombre Jurídico / Completo")
                tel = st.text_input("Enlace Móvil")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Añadir Nodo al Sistema", width='stretch'):
                    if doc and nom:
                        try:
                            cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, id_usuario_registro) VALUES (%s, %s, %s, %s)", (doc, nom, tel, st.session_state['id_usuario']))
                            conn.commit(); st.toast("Perfil sincronizado.", icon='💠'); time.sleep(1); st.rerun()
                        except mysql.connector.Error: st.error("Identidad ya existente en el clúster.")
                    else: st.warning("Se requieren métricas básicas (C.C. y Nombre).")
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            st.divider()
            cursor.execute("SELECT documento AS 'Documento ID', nombre_completo AS 'Identidad Oficial', telefono AS 'Línea de Contacto' FROM Clientes")
            df_clientes = pd.DataFrame(cursor.fetchall())
            if not df_clientes.empty: st.dataframe(df_clientes, width='stretch')

        elif menu_seleccionado == "ventas":
            st.markdown("<h2 class='fade-in'>Originación de Operaciones 📝</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
            clientes = cursor.fetchall()
            cursor.execute("SELECT imei, categoria, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
            inventario = cursor.fetchall()
            
            if not clientes or not inventario: st.warning("Error de dependencia: El nodo comercial requiere clientes registrados y stock en bodega.")
            else:
                opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                opc_eq = {f"[{e['categoria']}] {e['marca']} {e['modelo']} (S/N: {e['imei']})": e for e in inventario}
                
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                tipo_v = st.selectbox("Arquitectura del Contrato:", ["Crédito Financiado (Amortización con Interés)", "Plan Separé / Cuotas Fijas (Sin Interés)", "Liquidación de Contado Directo"], index=None, placeholder="Definir modalidad de cierre...")
                st.divider()
                
                if tipo_v:
                    c1, c2 = st.columns(2)
                    with c1: cli_sel = st.selectbox("Asignación de Titularidad", list(opc_cli.keys()), index=None, placeholder="Seleccionar Entidad de Cliente...")
                    with c2: eq_sel = st.selectbox("Extracción de Stock", list(opc_eq.keys()), index=None, placeholder="Seleccionar Hardware a despachar...")
                    
                    if cli_sel and eq_sel:
                        st.markdown("<div style='background: linear-gradient(90deg, rgba(0, 102, 255, 0.1), transparent); padding: 20px; border-radius: 16px; border-left: 4px solid #00E5FF; margin: 25px 0;'><p style='color:#00E5FF; font-size:15px; margin-bottom:15px; font-weight: 700; letter-spacing: 1px;'>TIMELINE CONTRACTUAL</p>", unsafe_allow_html=True)
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: fecha_venta = st.date_input("Día 0 (Apertura de Operación)", value=datetime.date.today())
                        with c_f2: f_cuota = st.date_input("Proyección de Primera Facturación", value=sumar_meses_exactos(fecha_venta, 1))
                        st.markdown("</div>", unsafe_allow_html=True)

                        c3, c4 = st.columns(2)
                        c_pers, c_fija = [], 0
                        
                        if "Financiado" in tipo_v:
                            with c3:
                                p_final = st.number_input("Valor Comercial Pactado ($)", min_value=1, value=1000000, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                                ab_init = st.number_input("Inyección de Liquidez Inicial ($)", min_value=0, value=0, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(ab_init)}</div>", unsafe_allow_html=True)
                                plazo = st.number_input("Ciclos de Amortización (Meses)", min_value=1, value=6)
                            with c4:
                                st.write("Métricas Internas de Costo")
                                cx1, cx2 = st.columns([1,2])
                                with cx1: 
                                    comis = st.number_input("Bono Operador ($)", min_value=0, step=10000, value=0)
                                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px;'>{fmt_cop(comis)}</div>", unsafe_allow_html=True)
                                with cx2: ase_nom = st.text_input("Operador/Asesor en Turno")
                                tasa = st.selectbox("Tasa Efectiva Mensual (T.E.M) %", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                            
                            m_f = p_final - ab_init
                            if m_f > 0 and plazo > 0:
                                i_m = tasa / 100.0
                                c_fija = int(round(m_f * (i_m * (1 + i_m)**plazo) / (((1 + i_m)**plazo) - 1))) if tasa > 0 else int(round(m_f / plazo))
                                st.info(f"🔹 **Flujo de Caja Mensual Exigible:** {fmt_cop(c_fija)}")
                        
                        elif "Separé" in tipo_v:
                            with c3:
                                p_final = st.number_input("Valor Comercial Bloqueado ($)", min_value=1, value=1000000, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                                ab_init = st.number_input("Aseguramiento de Stock ($)", min_value=0, value=0, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(ab_init)}</div>", unsafe_allow_html=True)
                                plazo = st.number_input("Número de Tramos de Pago", min_value=1, value=2)
                            with c4:
                                st.write("Métricas Internas de Costo")
                                cx1, cx2 = st.columns([1,2])
                                with cx1: 
                                    comis = st.number_input("Bono Operador ($)", min_value=0, step=10000, value=0)
                                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px;'>{fmt_cop(comis)}</div>", unsafe_allow_html=True)
                                with cx2: ase_nom = st.text_input("Operador/Asesor en Turno")
                            tasa, s_dif, s_cuotas = 0.0, p_final - ab_init, 0
                            st.write(f"Masa monetaria pendiente a dispersar: {fmt_cop(s_dif)}")
                            for idx in range(plazo):
                                x1, x2 = st.columns(2)
                                with x1:
                                    v_c = st.number_input(f"Volumen Tramo {idx+1}", min_value=0, value=int(s_dif/plazo), step=10000, key=f"v_{idx}")
                                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px;'>{fmt_cop(v_c)}</div>", unsafe_allow_html=True)
                                    s_cuotas += v_c
                                with x2: 
                                    f_c = st.date_input(f"Límite Contractual Tramo {idx+1}", value=sumar_meses_exactos(f_cuota, idx), key=f"f_{idx}")
                                c_pers.append((idx+1, v_c, f_c))
                        else:
                            p_final = st.number_input("Liquidación Inmediata Obtenida ($)", min_value=1, value=1000000, step=10000)
                            st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom:15px;'>{fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                            ab_init, plazo, tasa, comis, ase_nom = p_final, 0, 0.0, 0, ""

                        st.divider()
                        if st.button("Sellar Contrato Inteligente en DB", width='stretch'):
                            valido = True
                            if comis > 0 and not ase_nom: st.error("No se puede emitir bono sin un hash de operador válido."); valido = False
                            if "Separé" in tipo_v and s_cuotas != (p_final - ab_init): st.error("Fuga detectada: La matriz de pagos no cuadra con la deuda neta."); valido = False

                            if valido:
                                m_f = p_final - ab_init if "Contado" not in tipo_v else 0
                                e_f = 'Activo' if "Contado" not in tipo_v else 'Pagado'
                                v_c_bd = c_fija if "Financiado" in tipo_v else (c_pers[0][1] if "Separé" in tipo_v else 0)
                                cursor.execute("""INSERT INTO Creditos (id_cliente, imei, precio_venta, abono_inicial, monto_financiado, tasa_interes_mensual, plazo_meses, valor_cuota, estado, fecha_inicio, fecha_primera_cuota, valor_comision, asesor_comision, estado_comision, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (opc_cli[cli_sel], opc_eq[eq_sel]['imei'], p_final, ab_init, m_f, tasa/100.0, plazo, v_c_bd, e_f, fecha_venta.strftime('%Y-%m-%d'), f_cuota.strftime('%Y-%m-%d'), comis, ase_nom, 'Pendiente' if comis > 0 else 'No Aplica', st.session_state['id_usuario']))
                                id_cr = cursor.lastrowid
                                if "Separé" in tipo_v:
                                    for n_c, v_c, f_c in c_pers: cursor.execute("INSERT INTO Cuotas_Programadas (id_credito, numero_cuota, monto_esperado, fecha_vencimiento) VALUES (%s, %s, %s, %s)", (id_cr, n_c, v_c, f_c.strftime('%Y-%m-%d')))
                                cursor.execute("UPDATE Inventario SET estado = 'Vendido' WHERE imei = %s", (opc_eq[eq_sel]['imei'],))
                                if ("Contado" not in tipo_v and ab_init > 0) or "Contado" in tipo_v: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (ab_init if "Contado" not in tipo_v else p_final,))
                                conn.commit(); st.toast("Contrato minado en Base de Datos.", icon='💠'); time.sleep(1.5); st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

        elif menu_seleccionado == "pagos":
            st.markdown("<h2 class='fade-in'>Hub de Tesorería y Recaudos 💰</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.imei, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota, c.plazo_meses, i.marca, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("El sistema no detecta flujos pendientes de entrada.")
            else:
                opc_c = {f"{c['nombre_completo']} (ID Activo: {c['marca']} {c['modelo']})": c for c in activos}
                sel_titular = st.selectbox("Extraer nodo de deudor:", list(opc_c.keys()), index=None, placeholder="Escanear red de clientes...")
                
                if sel_titular:
                    dat = opc_c[sel_titular]
                    
                    cursor.execute("SELECT id_pago, monto_recibido, fecha_pago, tipo_pago, capital_abonado, interes_cobrado FROM Pagos WHERE id_credito = %s ORDER BY fecha_pago DESC", (dat['id_credito'],))
                    hist = cursor.fetchall()
                    
                    cap_pagado = sum([float(p['capital_abonado']) for p in hist])
                    s_pend = float(dat['monto_financiado']) - cap_pagado
                    v_cuota_bd = int(dat['valor_cuota']) if dat['valor_cuota'] else 0
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Deuda Neta Flotante", fmt_cop(s_pend))
                    c2.metric("Mensualidad Ordinaria", fmt_cop(v_cuota_bd))
                    c3.metric("Última Inyección de Caja", f"🗓️ {hist[0]['fecha_pago'].strftime('%Y-%m-%d')}" if hist else "Sin historial", fmt_cop(hist[0]['monto_recibido']) if hist else "$0")
                    
                    st.markdown("<div class='anim-border-gradient' style='margin-top:20px;'><div class='anim-border-inner'>", unsafe_allow_html=True)
                    st.markdown("<h3 style='color:#00E5FF; margin-top:0;'>📥 Procesar Entrada de Efectivo</h3>", unsafe_allow_html=True)
                    with st.form("f_pago"):
                        x1, x2 = st.columns(2)
                        with x1: 
                            monto = st.number_input("Masa Monetaria Entregada ($)", value=0, min_value=0, step=10000)
                            st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size:13px; margin-top: -10px; margin-bottom:15px;'>Monto a Procesar: {fmt_cop(monto)}</div>", unsafe_allow_html=True)
                        with x2: fecha_pago_efectiva = st.date_input("Timestamp de Transacción Físíca", value=None)
                        
                        tipo = st.selectbox("Distribución del Flujo", ["Cuota Ordinaria Mensual", "Abono Extra a Capital (Forzar Reducción de Cuota)", "Abono Extra a Capital (Forzar Cierre Anticipado)"], index=None, placeholder="Asignar protocolo financiero...")
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Ejecutar Sello Bancario", width='stretch'):
                            if monto <= 0: st.error("Monto de inyección inválido (Cero absoluto).")
                            elif not tipo: st.error("Falta clasificar el tipo de flujo monetario.")
                            elif fecha_pago_efectiva is None: st.error("Timestamp de caja no definido.")
                            else:
                                interes = round(s_pend * float(dat['tasa_interes_mensual']), 2)
                                cap_abono = 0.0 if monto <= interes else monto - interes
                                
                                cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s)", (dat['id_credito'], monto, tipo, cap_abono, min(monto, interes), fecha_pago_efectiva.strftime('%Y-%m-%d %H:%M:%S'), st.session_state['id_usuario']))
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (monto,))
                                
                                nuevo_saldo = s_pend - cap_abono
                                if nuevo_saldo <= 0: 
                                    cursor.execute("UPDATE Creditos SET estado = 'Pagado' WHERE id_credito = %s", (dat['id_credito'],))
                                else:
                                    if "Reducir Cuota Mensual" in tipo:
                                        cursor.execute("SELECT COUNT(*) as pagadas FROM Pagos WHERE id_credito = %s AND tipo_pago LIKE '%%Ordinaria%%'", (dat['id_credito'],))
                                        pag_res = cursor.fetchone()
                                        pagadas = int(pag_res['pagadas']) if pag_res and pag_res['pagadas'] else 0
                                        meses_restantes = dat['plazo_meses'] - pagadas
                                        if meses_restantes <= 0: meses_restantes = 1
                                        i_m = float(dat['tasa_interes_mensual'])
                                        nueva_cuota = nuevo_saldo * (i_m * (1 + i_m)**meses_restantes) / (((1 + i_m)**meses_restantes) - 1) if i_m > 0 else nuevo_saldo / meses_restantes
                                        cursor.execute("UPDATE Creditos SET valor_cuota = %s WHERE id_credito = %s", (int(round(nueva_cuota)), dat['id_credito']))
                                
                                conn.commit(); st.toast("Caja sincronizada con éxito.", icon='💠'); time.sleep(1.5); st.rerun()
                    st.markdown("</div></div>", unsafe_allow_html=True)

                    st.markdown("<br>### 💸 Registro en el Ledger", unsafe_allow_html=True)
                    if hist:
                        df_trans = pd.DataFrame(hist)
                        df_trans.rename(columns={'fecha_pago': 'Timestamp', 'tipo_pago': 'Protocolo', 'monto_recibido': 'Masa Entrante', 'capital_abonado': 'Deducción Capital', 'interes_cobrado': 'Retención Interés'}, inplace=True)
                        for col in ['Masa Entrante', 'Deducción Capital', 'Retención Interés']: df_trans[col] = df_trans[col].apply(fmt_cop)
                        st.dataframe(df_trans[['Timestamp', 'Protocolo', 'Masa Entrante', 'Deducción Capital', 'Retención Interés']], width='stretch')
                    else:
                        st.info("Sin registros de inyección de caja.")

                    st.markdown("<br>### 🧾 Simulación en Vivo (Plan Teórico)", unsafe_allow_html=True)
                    df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                    st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "vencimientos":
            st.markdown("<h2 class='fade-in'>Gestor de Cartera y Mora ⏰</h2>", unsafe_allow_html=True)
            cursor.execute("""
                SELECT cl.nombre_completo AS 'Titular', cl.telefono AS 'Enlace Móvil', c.valor_cuota AS 'Carga Mensual', c.fecha_primera_cuota AS 'Timestamp de Corte', 
                (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Exposición Capital',
                c.estado AS 'Calificación', c.tasa_interes_mensual
                FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo' ORDER BY c.fecha_primera_cuota ASC
            """)
            df = pd.DataFrame(cursor.fetchall())
            if df.empty: st.info("Matriz de exposición en ceros. No hay carteras activas.")
            else:
                df['Extracción Total (Paz y Salvo)'] = df.apply(lambda r: float(r['Exposición Capital']) + (float(r['Exposición Capital']) * float(r['tasa_interes_mensual'])), axis=1)
                for c in ['Carga Mensual', 'Exposición Capital', 'Extracción Total (Paz y Salvo)']: df[c] = df[c].apply(fmt_cop)
                df = df.drop(columns=['tasa_interes_mensual'])
                st.dataframe(df.style.map(color_estado, subset=['Calificación']), width='stretch')

        elif menu_seleccionado == "notificar":
            st.markdown("<h2 class='fade-in'>Emisor de Estados de Cuenta 📱</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.telefono, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, i.modelo, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("El buffer de notificaciones está vacío.")
            else:
                opc_n = {f"{c['nombre_completo']} (Sistema Atado: {c['modelo']})": c for c in activos}
                sel_cli = st.selectbox("Seleccionar Terminal Destino", list(opc_n.keys()), index=None, placeholder="Mapear identidad de cliente...")
                
                if sel_cli:
                    dat = opc_n[sel_cli]
                    cursor.execute("SELECT SUM(capital_abonado) as cap, MAX(monto_recibido) as last_val, MAX(fecha_pago) as last_date FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    res_pag = cursor.fetchone()
                    cap_pag = float(res_pag['cap']) if res_pag and res_pag['cap'] else 0
                    last_val = float(res_pag['last_val']) if res_pag and res_pag['last_val'] else 0
                    last_date = res_pag['last_date'] if res_pag and res_pag['last_date'] else None

                    s_act = float(dat['monto_financiado']) - cap_pag
                    paz_y_salvo = s_act + (s_act * float(dat['tasa_interes_mensual']))
                    
                    msg = f"Buen día {dat['nombre_completo']}. Resumen encriptado de tu vínculo con DaTo:\n\n💵 *Compromiso Base:* {fmt_cop(dat['valor_cuota'])}\n📉 *Capital Neto Expuesto:* {fmt_cop(s_act)}\n💳 *Última Interacción:* {fmt_cop(last_val) if last_val else '$0'} ejecutado en {last_date.strftime('%Y-%m-%d') if last_date else 'N/A'}\n\n*💰 Algoritmo de Cierre Inmediato (Paz y Salvo): {fmt_cop(paz_y_salvo)}*\n\nEl sistema marcará la fecha de corte el día {str(dat['fecha_primera_cuota'].day)} de cada mes. Fin de la transmisión."
                    
                    st.markdown("<div class='anim-border-gradient' style='margin-top:20px;'><div class='anim-border-inner'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    with c1: st.text_area("Carga de texto para API WhatsApp", value=msg, height=350)
                    with c2:
                        st.markdown("<h4 style='color:#00E5FF; margin-top:0;'>Simulador del Crédito Actual</h4>", unsafe_allow_html=True)
                        df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')
                    st.markdown("</div></div>", unsafe_allow_html=True)

        elif menu_seleccionado == "historial":
            st.markdown("<h2 class='fade-in'>Auditoría de Root 📜</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Acceso denegado. Se requiere bandera de Administrador de Sistema."); st.stop()
            
            tab_v, tab_r = st.tabs(["📋 Consola Universal de Contratos", "⚠️ Módulo Override (Anulación Dura)"])
            
            with tab_v:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT c.id_credito, cl.nombre_completo AS 'Identidad Oficial', i.modelo AS 'Activo Cedido', c.estado AS 'Status Quo', 
                           i.costo_adquisicion AS 'Costo Real Base', c.precio_venta AS 'Margen Proyectado',
                           IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) AS 'Absorción Dinámica',
                           (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Capital en la Calle',
                           c.valor_comision AS 'Fuga por Comisiones',
                           (IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) - i.costo_adquisicion - c.valor_comision) AS 'GANANCIA LIQUIDA DE RED'
                    FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.fecha_inicio DESC
                """)
                df_cart = pd.DataFrame(cursor.fetchall())
                if not df_cart.empty:
                    for col in ['Costo Real Base', 'Margen Proyectado', 'Absorción Dinámica', 'Capital en la Calle', 'Fuga por Comisiones', 'GANANCIA LIQUIDA DE RED']: 
                        df_cart[col] = df_cart[col].apply(fmt_cop)
                    st.dataframe(df_cart.style.map(color_estado, subset=['Status Quo']).map(color_ganancia_real, subset=['GANANCIA LIQUIDA DE RED']), width='stretch')
                else: st.info("Logs transaccionales en blanco.")

            with tab_r:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("<h4 style='color:#00E5FF;'>📥 Revertir Inyección de Caja</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT p.id_pago, cl.nombre_completo, p.monto_recibido, p.fecha_pago, p.tipo_pago FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY p.id_pago DESC LIMIT 50")
                    pagos_db = cursor.fetchall()
                    if pagos_db:
                        opc_pagos = {f"[{p['fecha_pago'].strftime('%Y-%m-%d')}] {p['nombre_completo']} ({fmt_cop(p['monto_recibido'])}) - {p['tipo_pago']}": p for p in pagos_db}
                        with st.form("f_anular_pago"):
                            pago_sel = st.selectbox("Apuntar transacción a destruir", list(opc_pagos.keys()), index=None, placeholder="Localizar hash...")
                            if st.form_submit_button("Forzar Purga de Base de Datos", width='stretch') and pago_sel:
                                dat_p = opc_pagos[pago_sel]
                                cursor.execute("SELECT id_credito FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                id_c = cursor.fetchone()['id_credito']
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (dat_p['monto_recibido'],))
                                cursor.execute("DELETE FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                cursor.execute("UPDATE Creditos SET estado = 'Activo' WHERE id_credito = %s", (id_c,))
                                conn.commit(); st.toast("Transacción desintegrada.", icon='⚡'); time.sleep(1.5); st.rerun()
                    else: st.info("Ledger sin inyecciones para revertir.")

                with c2:
                    st.markdown("<h4 style='color:#00C6FF;'>🚨 Colapso de Operación Comercial</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT c.id_credito, cl.nombre_completo, i.modelo, c.imei, c.abono_inicial FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.id_credito DESC")
                    creds_db = cursor.fetchall()
                    if creds_db:
                        opc_creds = {f"[Contrato Maestro: {c['id_credito']}] {c['nombre_completo']} - {c['modelo']}": c for c in creds_db}
                        with st.form("f_anular_venta"):
                            cred_sel = st.selectbox("Seleccionar contrato objetivo", list(opc_creds.keys()), index=None, placeholder="Rastrear bloque...")
                            if st.form_submit_button("Desintegrar Contrato y Liberar Stock", width='stretch') and cred_sel:
                                dat_c = opc_creds[cred_sel]
                                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                                cursor.execute("SELECT SUM(monto_recibido) as t FROM Pagos WHERE id_credito = %s", (dat_c['id_credito'],))
                                res_t = cursor.fetchone()
                                plata_a_restar = float(dat_c['abono_inicial']) + float(res_t['t'] if res_t and res_t['t'] else 0)
                                if plata_a_restar > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (plata_a_restar,))
                                cursor.execute("UPDATE Inventario SET estado = 'Disponible' WHERE imei = %s", (dat_c['imei'],))
                                cursor.execute("DELETE FROM Cuotas_Programadas WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("DELETE FROM Pagos WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("DELETE FROM Creditos WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                                conn.commit(); st.toast("Contrato purgado. El sistema recupera el activo.", icon='⚡'); time.sleep(1.5); st.rerun()
                    else: st.info("Bloques comerciales en ceros.")
                    
                with c3:
                    st.markdown("<h4 style='color:#0099FF;'>📦 Destrucción de Inventario</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT imei, marca, modelo, costo_adquisicion, id_bolsa FROM Inventario WHERE estado = 'Disponible'")
                    inv_db = cursor.fetchall()
                    if inv_db:
                        opc_inv = {f"{i['marca']} {i['modelo']} ({i['imei']})": i for i in inv_db}
                        with st.form("f_anular_hardware"):
                            inv_sel = st.selectbox("Aislar nodo de hardware", list(opc_inv.keys()), index=None, placeholder="Inspeccionar bodega...")
                            if st.form_submit_button("Exiliar Hardware y Reinyectar Capital", width='stretch') and inv_sel:
                                dat_i = opc_inv[inv_sel]
                                if float(dat_i['costo_adquisicion']) > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s WHERE id_bolsa = %s", (dat_i['costo_adquisicion'], dat_i['id_bolsa']))
                                cursor.execute("DELETE FROM Inventario WHERE imei = %s", (dat_i['imei'],))
                                conn.commit(); st.toast("Hardware extraído de la matrix.", icon='💠'); time.sleep(1.5); st.rerun()
                    else: st.info("La bodega no arroja falsos positivos.")
                st.markdown("</div></div>", unsafe_allow_html=True)

        elif menu_seleccionado == "egresos":
            st.markdown("<h2 class='fade-in'>Hub de Egresos Operativos 💸</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Línea restringida por política de CFO."); st.stop()
            
            tab_com, tab_gas = st.tabs(["🤝 Dispersión de Nómina a Nodos (Asesores)", "🧾 Fugas de Capital Estructural (Arriendos, Luz)"])
            with tab_com:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo AS 'Titular', cl.telefono AS 'Celular', i.modelo AS 'Activo', c.asesor_comision AS 'Asesor Comercial', c.valor_comision AS 'Bono a Pagar' FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado_comision = 'Pendiente'")
                pends = cursor.fetchall()
                if pends:
                    df_p = pd.DataFrame(pends)
                    df_p['Bono a Pagar'] = df_p['Bono a Pagar'].apply(fmt_cop)
                    st.dataframe(df_p, width='stretch')
                    st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                    with st.form("f_com"):
                        sel = st.selectbox("Extraer metadata del operador", list({f"[{x['Asesor Comercial']}] Liquidación en Contrato: {x['Titular']} ({x['Celular']}) -> {fmt_cop(x['Bono a Pagar'])}": x['id_credito'] for x in pends}.keys()), index=None, placeholder="Fijar blanco de dispersión...")
                        if st.form_submit_button("Autorizar Desvío de Caja", width='stretch') and sel:
                            id_c = {f"[{x['Asesor Comercial']}] Liquidación en Contrato: {x['Titular']} ({x['Celular']}) -> {fmt_cop(x['Bono a Pagar'])}": x['id_credito'] for x in pends}[sel]
                            cursor.execute("SELECT valor_comision FROM Creditos WHERE id_credito = %s", (id_c,))
                            val = float(cursor.fetchone()['valor_comision'])
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (val,))
                            cursor.execute("UPDATE Creditos SET estado_comision = 'Pagada', fecha_pago_comision = %s WHERE id_credito = %s", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_c))
                            conn.commit(); st.toast("Fondo transferido al operador.", icon='💠'); time.sleep(1.5); st.rerun()
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else: st.info("El sistema de operadores está al día.")
                
            with tab_gas:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei")
                opc_eq = {"Vaciado Directo desde Caja Maestra (Gastos Base)": None}
                for x in cursor.fetchall(): opc_eq[f"Fijar costo oculto a la cuenta de: {x['nombre_completo']} ({x['modelo']})"] = x['id_credito']
                
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                with st.form("f_g"):
                    desc = st.text_input("Nomenclatura de Fuga (Ej: Alquiler de Red, Servicios Físicos, Repuestos)")
                    cred_cc = st.selectbox("Apuntar Sistema de Retención", list(opc_eq.keys()), index=None, placeholder="Mapeo de Caja Fuerte...")
                    m_g = st.number_input("Valor de Sustracción ($)", min_value=0, step=10000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size:13px; margin-top: -10px; margin-bottom:15px;'>Monto Final: {fmt_cop(m_g)}</div>", unsafe_allow_html=True)
                    if st.form_submit_button("Sellar Gasto en la Nube", width='stretch') and cred_cc:
                        cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, id_usuario_registro) VALUES (%s, %s, %s, %s)", (desc, m_g, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                        cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (m_g,))
                        conn.commit(); st.toast("Sustracción asentada.", icon='💠'); time.sleep(1); st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

        elif menu_seleccionado == "flujo":
            st.markdown("<h2 class='fade-in'>Backbone de Capitales y Fondeo 📈</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Acceso crítico denegado."); st.stop()
            
            tab_dash, tab_in, tab_out = st.tabs(["📊 Radar de Deuda Estructural", "📥 Asimilar Inyección Externa", "📤 Autorizar Retorno de Dividendos"])
            
            with tab_dash:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT prestamista AS 'Fondo Inversor', monto_prestado AS 'Capital Inyectado', monto_total_pagar AS 'Rendimiento Acordado', (monto_total_pagar - saldo_pendiente) AS 'Retorno Ejecutado', saldo_pendiente AS 'Saldo Vivo Exigible', fecha_prestamo AS 'Fecha de Ingreso' FROM Deudas_Fondeo ORDER BY fecha_prestamo DESC")
                df_inversores = pd.DataFrame(cursor.fetchall())
                
                cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
                res_cap = cursor.fetchone()
                cap = float(res_cap['cap']) if res_cap and res_cap['cap'] else 0
                
                deuda = df_inversores['Saldo Vivo Exigible'].sum() if not df_inversores.empty else 0
                
                c1, c2 = st.columns(2)
                c1.metric("💵 Poder de Fuego Neto (Caja)", fmt_cop(cap))
                c2.metric("📉 Pasivo Total Exigible (Socios)", fmt_cop(deuda))
                
                st.markdown("<br><h4 style='color:#00E5FF; font-size: 1.1rem;'>📜 Matriz de Entidades Fondeadoras</h4>", unsafe_allow_html=True)
                if not df_inversores.empty:
                    for c in ['Capital Inyectado', 'Rendimiento Acordado', 'Retorno Ejecutado', 'Saldo Vivo Exigible']: df_inversores[c] = df_inversores[c].apply(fmt_cop)
                    st.dataframe(df_inversores, width='stretch')
                else: st.info("No existen socios inyectando capital en este momento.")

                st.markdown("<br><h4 style='color:#00C6FF; font-size: 1.1rem;'>🧾 Auditoría de Desviación de Cajas hacia Socios</h4>", unsafe_allow_html=True)
                cursor.execute("SELECT p.fecha_pago AS 'Timestamp', d.prestamista AS 'Recibidor Final', p.monto_pagado AS 'Valor Extraído' FROM Pagos_Deuda p JOIN Deudas_Fondeo d ON p.id_deuda = d.id_deuda ORDER BY p.fecha_pago DESC")
                df_hist_deuda = pd.DataFrame(cursor.fetchall())
                if not df_hist_deuda.empty:
                    df_hist_deuda['Valor Extraído'] = df_hist_deuda['Valor Extraído'].apply(fmt_cop)
                    st.dataframe(df_hist_deuda, width='stretch')

            with tab_in:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                with st.form("f_f_in"):
                    prov = st.text_input("Identidad de la Entidad Originadora")
                    iny = st.number_input("Inyección Bruta Registrada ($)", min_value=0, step=100000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size:13px; margin-top: -10px; margin-bottom:15px;'>Masa de Inyección: {fmt_cop(iny)}</div>", unsafe_allow_html=True)
                    ret = st.number_input("Monto Futuro de Retorno Cifrado ($)", min_value=0, step=100000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size:13px; margin-top: -10px; margin-bottom:15px;'>Masa de Retorno Exigible: {fmt_cop(ret)}</div>", unsafe_allow_html=True)
                    if st.form_submit_button("Indexar Poder Fiduciario", width='stretch'):
                        if prov and iny > 0:
                            cursor.execute("INSERT INTO Deudas_Fondeo (prestamista, monto_prestado, monto_total_pagar, saldo_pendiente, fecha_prestamo, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s)", (prov, iny, ret, ret, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (iny,))
                            conn.commit(); st.toast("Suministro de energía indexado en caja.", icon='⚡'); time.sleep(1); st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

            with tab_out:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_deuda, prestamista, saldo_pendiente FROM Deudas_Fondeo WHERE saldo_pendiente > 0")
                deudas = cursor.fetchall()
                if deudas:
                    opc_d = {f"{d['prestamista']} (Riesgo Abierto: {fmt_cop(d['saldo_pendiente'])})": d for d in deudas}
                    st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                    with st.form("f_d_out"):
                        d_sel = st.selectbox("Mapear Nodo del Inversor", list(opc_d.keys()), index=None, placeholder="Rastrear deuda corporativa...")
                        ab = st.number_input("Desvío de Capital hacia Entidad ($)", min_value=0, step=100000, value=0)
                        st.markdown(f"<div style='text-align: right; color: #00E5FF; font-weight: 600; font-size:13px; margin-top: -10px; margin-bottom:15px;'>Monto de Retorno: {fmt_cop(ab)}</div>", unsafe_allow_html=True)
                        if st.form_submit_button("Sellar Salida Corporativa", width='stretch') and d_sel:
                            id_d = opc_d[d_sel]['id_deuda']
                            cursor.execute("INSERT INTO Pagos_Deuda (id_deuda, monto_pagado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s)", (id_d, ab, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Deudas_Fondeo SET saldo_pendiente = saldo_pendiente - %s WHERE id_deuda = %s", (ab, id_d))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (ab,))
                            conn.commit(); st.toast("Dividendos extraídos del hub central.", icon='⚡'); time.sleep(1); st.rerun()
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else: st.info("Estructura libre de pasivos.")

        elif menu_seleccionado == "reportes":
            st.markdown("<h2 class='fade-in'>Sistema de Inteligencia DaTo (BI) 📊</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Módulo encriptado. Privilegio superior no detectado."); st.stop()
            
            tab_bi, tab_graf, tab_riesgo, tab_eficiencia = st.tabs(["🌐 Matriz Ejecutiva", "📈 Algoritmo de Flujo", "⚖️ Stress Test de Cartera", "💸 Analítica de Rendimiento Puro"])
            
            # --- EXTRACCIÓN BLINDADA DE DATA ---
            cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
            res_cap = cursor.fetchone()
            cap = float(res_cap['cap']) if res_cap and res_cap['cap'] else 0
            
            cursor.execute("SELECT SUM(saldo_pendiente) as deu FROM Deudas_Fondeo")
            res_deu = cursor.fetchone()
            deuda = float(res_deu['deu']) if res_deu and res_deu['deu'] else 0
            
            cursor.execute("SELECT SUM(monto_financiado) as mf FROM Creditos WHERE estado = 'Activo'")
            res_mf = cursor.fetchone()
            cartera_colocada = float(res_mf['mf']) if res_mf and res_mf['mf'] else 0
            
            cursor.execute("SELECT SUM(capital_abonado) as ca FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito WHERE c.estado = 'Activo'")
            res_ca = cursor.fetchone()
            cartera_recaudada = float(res_ca['ca']) if res_ca and res_ca['ca'] else 0
            
            cartera_neta_calle = cartera_colocada - cartera_recaudada
            patrimonio_neto = cap + cartera_neta_calle - deuda

            cursor.execute("SELECT SUM(cr.precio_venta - i.costo_adquisicion) as gan_equipos FROM Creditos cr JOIN Inventario i ON cr.imei = i.imei")
            res_geq = cursor.fetchone()
            ganancia_por_venta = float(res_geq['gan_equipos']) if res_geq and res_geq['gan_equipos'] else 0
            
            cursor.execute("SELECT SUM(interes_cobrado) as interes FROM Pagos")
            res_int = cursor.fetchone()
            ganancia_por_interes = float(res_int['interes']) if res_int and res_int['interes'] else 0
            
            cursor.execute("SELECT SUM(monto) as gastos FROM Gastos_Operativos")
            res_gast = cursor.fetchone()
            gastos_totales = float(res_gast['gastos']) if res_gast and res_gast['gastos'] else 0

            cursor.execute("SELECT SUM(valor_comision) as coms FROM Creditos WHERE estado_comision = 'Pagada'")
            res_coms = cursor.fetchone()
            comisiones_totales = float(res_coms['coms']) if res_coms and res_coms['coms'] else 0

            # GANANCIA NETA PURA DE CAJA
            cursor.execute("SELECT SUM(monto_recibido) as t_rec FROM Pagos")
            total_recaudo_hist = float(cursor.fetchone()['t_rec'] or 0)
            cursor.execute("SELECT SUM(i.costo_adquisicion) as t_costo FROM Creditos c JOIN Inventario i ON c.imei = i.imei")
            total_costo_equipos = float(cursor.fetchone()['t_costo'] or 0)
            
            ganancia_neta_100 = total_recaudo_hist - total_costo_equipos - comisiones_totales - gastos_totales
            
            cursor.execute("SELECT COUNT(*) as t_ventas FROM Creditos")
            total_ventas = int(cursor.fetchone()['t_ventas'] or 0)
            ticket_promedio = (cartera_colocada + cartera_recaudada) / total_ventas if total_ventas > 0 else 0

            with tab_bi:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="neon-kpi-box">
                    <h3 style="color:#00E5FF; margin:0; font-weight: 700; letter-spacing: 2.5px;">EVALUACIÓN PATRIMONIAL DEL ECOSISTEMA</h3>
                    <h1 style="color:white; font-size: 4.5rem; font-weight: 800; margin: 10px 0; text-shadow: 0 0 25px rgba(0, 198, 255, 0.4);">{fmt_cop(patrimonio_neto)}</h1>
                    <p style="color:#8B9BB4; font-size: 15px; margin:0;">Base Líquida Local ({fmt_cop(cap)}) + Capital Expuesto en Nodos ({fmt_cop(cartera_neta_calle)}) - Fondeo Externo Exigible ({fmt_cop(deuda)})</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("✅ Rentabilidad Pura Desbloqueada (Caja)", fmt_cop(ganancia_neta_100))
                c_m2.metric("💳 Masa Crítica Expuesta (Zona Riesgo)", fmt_cop(cartera_neta_calle))
                c_m3.metric("📊 Ticket Estadístico / LTV", fmt_cop(ticket_promedio))

            with tab_graf:
                st.markdown("<br>", unsafe_allow_html=True)
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown("<h4 style='color:#00E5FF;'>📅 Vector Histórico de Retorno (Cash-In)</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT DATE_FORMAT(fecha_pago, '%Y-%m') as mes, SUM(monto_recibido) as total FROM Pagos GROUP BY mes ORDER BY mes ASC")
                    recaudos_mes = cursor.fetchall()
                    if recaudos_mes:
                        df_chart_rec = pd.DataFrame(recaudos_mes)
                        df_chart_rec.columns = ['Mes', 'Efectivo Recaudado']
                        df_chart_rec.set_index('Mes', inplace=True)
                        st.bar_chart(df_chart_rec, color="#00E5FF")
                    else: st.info("Módulo silenciado por falta de data.")
                    
                with col_g2:
                    st.markdown("<h4 style='color:#00C6FF;'>📈 Curva de Despliegue Comercial (Ventas)</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT DATE_FORMAT(fecha_inicio, '%Y-%m') as mes, SUM(precio_venta) as total FROM Creditos GROUP BY mes ORDER BY mes ASC")
                    ventas_mes = cursor.fetchall()
                    if ventas_mes:
                        df_chart_ven = pd.DataFrame(ventas_mes)
                        df_chart_ven.columns = ['Mes', 'Monto de Ventas']
                        df_chart_ven.set_index('Mes', inplace=True)
                        st.area_chart(df_chart_ven, color="#0066FF")
                    else: st.info("Módulo silenciado.")

            with tab_riesgo:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT estado, COUNT(*) as cantidad FROM Creditos GROUP BY estado")
                estados_credito = cursor.fetchall()
                
                c_r1, c_r2 = st.columns([1.5, 1])
                with c_r1:
                    st.markdown("<h4 style='color:#00E5FF;'>⚖️ Analítica de Exposición Dinámica</h4>", unsafe_allow_html=True)
                    recup_perc = (cartera_recaudada / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Tasa de Recuperación Total:** {recup_perc:.1f}%")
                    st.progress(min(int(recup_perc), 100))
                    
                    mora_perc = ((cartera_colocada - cartera_recaudada) / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Riesgo Activo de Incobrabilidad:** {mora_perc:.1f}%")
                    st.progress(min(int(mora_perc), 100))
                
                with c_r2:
                    st.markdown("<h4 style='color:#00E5FF;'>📋 Mapa de Estados Finales</h4>", unsafe_allow_html=True)
                    if estados_credito:
                        df_est = pd.DataFrame(estados_credito)
                        df_est.columns = ['Status Operacional', 'Cantidad']
                        df_est.set_index('Status Operacional', inplace=True)
                        st.bar_chart(df_est, color="#00C6FF")

            with tab_eficiencia:
                st.markdown("<br>", unsafe_allow_html=True)
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    st.markdown("<h4 style='color:#00E5FF;'>💎 Composición Bruta del Beneficio</h4>", unsafe_allow_html=True)
                    df_ingresos = pd.DataFrame([
                        {"Vectores": "Margen de Venta de Equipo Físico", "Score": ganancia_por_venta},
                        {"Vectores": "Recaudo Real por Intereses T.E.M", "Score": ganancia_por_interes}
                    ])
                    if not df_ingresos.empty:
                        df_ingresos.set_index("Vectores", inplace=True)
                        st.bar_chart(df_ingresos, color="#00C6FF")

                with col_e2:
                    st.markdown("<h4 style='color:#0066FF;'>💸 Análisis Forense de Fugas</h4>", unsafe_allow_html=True)
                    df_egresos = pd.DataFrame([
                        {"Vectores": "Gastos Estructurales Base", "Score": gastos_totales},
                        {"Vectores": "Fuga por Bonos y Comisiones", "Score": comisiones_totales}
                    ])
                    if not df_egresos.empty:
                        df_egresos.set_index("Vectores", inplace=True)
                        st.bar_chart(df_egresos, color="#0066FF")
                        
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(4, 13, 30, 0.8), rgba(2, 6, 15, 0.9)); border: 1px solid rgba(0, 198, 255, 0.2); border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(0, 198, 255, 0.05); backdrop-filter: blur(15px); margin-top: 30px;">
                    <h4 style="color:#00E5FF; margin:0; font-weight: 600; letter-spacing: 1.5px;">PROYECCIÓN DE RENDIMIENTO (ROI) GLOBAL</h4>
                    <h1 style="color:white; font-size: 3.5rem; font-weight: 800; margin: 10px 0; text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);">{((ganancia_por_venta + ganancia_por_interes) / (total_costo_equipos if total_costo_equipos > 0 else 1) * 100):.1f}%</h1>
                    <p style="color:#8B9BB4; font-size: 15px; margin:0;">Métrica predictiva de retorno de inversión por cada punto de liquidez convertido en hardware.</p>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "config_roles":
            st.markdown("<h2 class='fade-in'>Sistema Root de Perímetros ⚙️</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Violación de nivel de seguridad. Conexión rechazada."); st.stop()
            
            tab_c1, tab_c2, tab_c3 = st.tabs(["👤 Matriz de Nodos (Usuarios)", "🛡️ Cifrado de Accesos", "➕ Orquestación de Permisos"])
            cursor.execute("SELECT * FROM Roles")
            opc_r = [r['nombre_rol'] for r in cursor.fetchall()]
            
            with tab_c1:
                st.markdown("<br>", unsafe_allow_html=True)
                col_u1, col_u2, col_u3 = st.columns(3)
                with col_u1:
                    st.markdown("**✨ Generar Clave Identitaria**")
                    with st.form("f_newUser"):
                        n_user = st.text_input("Alias Transaccional")
                        n_pass = st.text_input("Hash de Seguridad (Token)", type="password")
                        n_nombre = st.text_input("Identidad Biométrica / Oficial")
                        n_rol = st.selectbox("Arquitectura del Rol", opc_r)
                        if st.form_submit_button("✅ Sellar Entidad", width='stretch'):
                            if n_user and n_pass and n_nombre:
                                try:
                                    cursor.execute("INSERT INTO Usuarios (username, password_hash, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_user, n_pass, n_nombre, n_rol))
                                    conn.commit(); st.toast("Entidad cargada a la matrix.", icon='⚡'); time.sleep(1.5); st.rerun()
                                except mysql.connector.Error: st.error("Colisión de Hash.")
                            else: st.warning("Datos estructurales faltantes.")
                with col_u2:
                    st.markdown("**🔄 Desplazamiento de Privilegios**")
                    with st.form("f_change_rol"):
                        cursor.execute("SELECT username FROM Usuarios")
                        users_db = [u['username'] for u in cursor.fetchall()]
                        if users_db:
                            u_rol = st.selectbox("Selección de Alias", users_db, index=None, placeholder="Interrogar DB...")
                            new_rol = st.selectbox("Nuevo Vector de Acceso", opc_r, index=None, placeholder="Determinar rango...")
                            if st.form_submit_button("Sobrescribir Root", width='stretch') and u_rol and new_rol:
                                cursor.execute("UPDATE Usuarios SET rol = %s WHERE username = %s", (new_rol, u_rol))
                                conn.commit(); st.toast("Rango modificado.", icon='⚡'); time.sleep(1.5); st.rerun()
                with col_u3:
                    st.markdown("**🔑 Purga de Credenciales**")
                    with st.form("f_reset"):
                        if users_db:
                            u_reset = st.selectbox("Rastrear Alias Fallido", users_db, index=None, placeholder="Interrogar DB...")
                            p_reset = st.text_input("Forzar Nuevo Token de Seguridad", type="password")
                            if st.form_submit_button("Crackear y Reasignar", width='stretch') and u_reset and p_reset:
                                cursor.execute("UPDATE Usuarios SET password_hash = %s WHERE username = %s", (p_reset, u_reset))
                                conn.commit(); st.toast("Bypass exitoso. Clave reconfigurada.", icon='⚡'); time.sleep(1.5); st.rerun()

            with tab_c2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='anim-border-gradient'><div class='anim-border-inner'>", unsafe_allow_html=True)
                role_sel = st.selectbox("Seleccione el Arquitecto (Rol) a Inspeccionar:", opc_r, index=None, placeholder="Buscar roles estructurales...")
                if role_sel:
                    cursor.execute("SELECT * FROM Modulos_Sistema")
                    todos_modulos = cursor.fetchall()
                    cursor.execute("SELECT id_modulo FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                    activos_rol = [x['id_modulo'] for x in cursor.fetchall()]
                    
                    st.write(f"Puertos abiertos para el nodo **{role_sel}**:")
                    with st.form("form_permisos"):
                        check_resultados = {m['id_modulo']: st.checkbox(m['nombre_visible'], value=(m['id_modulo'] in activos_rol)) for m in todos_modulos}
                        if st.form_submit_button("Compilar Sello de Seguridad", width='stretch'):
                            cursor.execute("DELETE FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                            cursor.execute("SELECT id_role FROM Roles WHERE nombre_rol = %s", (role_sel,))
                            id_r_actual = cursor.fetchone()['id_role']
                            for id_mod, marcado in check_resultados.items():
                                if marcado: cursor.execute("INSERT INTO Permisos_Rol (id_role, id_modulo) VALUES (%s, %s)", (id_r_actual, id_mod))
                            conn.commit(); st.toast("Perímetro blindado en memoria.", icon='⚡'); time.sleep(1); st.rerun()
                st.markdown("</div></div>", unsafe_allow_html=True)

            with tab_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("form_nuevo_rol"):
                    nuevo_rol_nombre = st.text_input("Definir Nuevo Nivel de Jerarquía (Rol):")
                    if st.form_submit_button("Minar Nuevo Nivel de Seguridad", width='stretch'):
                        if nuevo_rol_nombre:
                            try:
                                cursor.execute("SELECT nombre_rol FROM Roles WHERE nombre_rol = %s", (nuevo_rol_nombre.strip(),))
                                if cursor.fetchone(): st.error("Error: Ese nivel de jerarquía ya ha sido minado.")
                                else:
                                    cursor.execute("INSERT INTO Roles (nombre_rol) VALUES (%s)", (nuevo_rol_nombre.strip(),))
                                    conn.commit(); st.toast("Nivel agregado al Kernel."); time.sleep(1); st.rerun()
                            except Exception as e: st.error(f"Falla fatal en Kernel: {e}")

finally:
    # === SEGURO ANTI-FUGAS DE MEMORIA ===
    try:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn and conn.is_connected(): conn.close()
    except Exception:
        pass

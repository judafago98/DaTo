import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import datetime
import time
import uuid
import calendar

# --- EJECUCIÓN INVISIBLE: Autocorrección de la Base de Datos ---
def auto_fix_db(cursor, conn):
    try:
        cursor.execute("ALTER TABLE Pagos MODIFY COLUMN tipo_pago VARCHAR(255)")
        conn.commit()
    except Exception: pass

# --- Configuración visual de la app ---
st.set_page_config(page_title="DaTo Workspace", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# --- DISEÑO ULTRA PREMIUM Y RESPONSIVO (BLACK & BLUE EDITION) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

        /* FONDO DE REDES Y CIRCUITOS CIBERNÉTICOS (NEGRO/AZUL) */
        .stApp {
            background-color: #000000;
            background-image: 
                linear-gradient(rgba(0, 198, 255, 0.07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 198, 255, 0.07) 1px, transparent 1px),
                radial-gradient(circle at 50% 50%, rgba(0, 30, 60, 0.6), #000000);
            background-size: 35px 35px, 35px 35px, 100% 100%;
            background-position: center center;
            background-attachment: fixed;
            color: #F8FAFC;
        }
        
        #MainMenu, footer {display: none !important;}
        header, [data-testid="stHeader"] {background: transparent !important;}
        
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 198, 255, 0.3); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0, 198, 255, 0.8); }

        [data-testid="stImage"] { display: flex; align-items: center; justify-content: center; }
        [data-testid="stImage"] img {
            border-radius: 24px !important;
            box-shadow: 0 0 35px rgba(0, 198, 255, 0.3), inset 0 0 15px rgba(0, 198, 255, 0.2) !important;
            border: 2px solid #00C6FF !important; transition: all 0.4s ease !important;
            max-height: 400px; object-fit: cover; width: 100% !important; max-width: 400px;
        }
        [data-testid="stImage"] img:hover { box-shadow: 0 0 50px rgba(0, 198, 255, 0.6) !important; transform: scale(1.02) !important; }

        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.95) !important; backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 198, 255, 0.15);
        }
        
        [data-testid="stSidebar"] div[role="radiogroup"] { gap: 6px; padding: 10px 0; }
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background: transparent !important; border: 1px solid transparent !important;
            border-radius: 10px !important; padding: 12px 16px !important; margin: 2px 8px !important;
            transition: all 0.2s ease !important; cursor: pointer !important; display: flex !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #94A3B8 !important; font-size: 14.5px !important; font-weight: 500 !important; margin: 0 !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(0, 198, 255, 0.05) !important; transform: translateX(4px); }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover p { color: #FFFFFF !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(0,198,255,0.15) 0%, transparent 100%) !important;
            border-left: 4px solid #00C6FF !important; border-radius: 4px 10px 10px 4px !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p { color: #00C6FF !important; font-weight: 700 !important; }

        .login-wrapper { display: flex; align-items: center; justify-content: center; height: 100%; }

        [data-testid="stForm"] {
            background: rgba(4, 13, 30, 0.7) !important; backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(0, 198, 255, 0.2) !important; border-radius: 20px !important;
            padding: 40px 30px !important; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
            display: flex; flex-direction: column; justify-content: center; height: 100%;
        }

        [data-testid="stMetric"] {
            background: rgba(4, 10, 20, 0.8); backdrop-filter: blur(15px);
            border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 24px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5); border-top: 3px solid #0066FF; transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover { border-top: 3px solid #00E5FF; transform: translateY(-3px); box-shadow: 0 15px 30px rgba(0, 198, 255, 0.15); }
        
        /* BOTONES ULTRA PREMIUM AZULES */
        .stButton>button {
            background: linear-gradient(135deg, #001E3C 0%, #0066FF 50%, #00C6FF 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(0, 198, 255, 0.4) !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            padding: 0.8rem 2rem !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 6px 20px rgba(0, 102, 255, 0.3), inset 0 2px 5px rgba(255, 255, 255, 0.3) !important;
            position: relative !important;
            overflow: hidden !important;
            z-index: 1 !important;
            width: 100% !important;
        }
        .stButton>button::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            transform: skewX(-25deg); transition: left 0.7s ease; z-index: -1;
        }
        .stButton>button:hover::before { left: 150%; }
        .stButton>button:hover {
            transform: translateY(-5px) scale(1.02) !important;
            box-shadow: 0 12px 30px rgba(0, 198, 255, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.4) !important;
            border-color: #00E5FF !important;
        }
        .stButton>button:active {
            transform: translateY(2px) scale(0.98) !important;
            box-shadow: 0 2px 10px rgba(0, 102, 255, 0.4), inset 0 4px 8px rgba(0, 0, 0, 0.5) !important;
        }
        
        input, select, textarea {
            background-color: rgba(2, 6, 15, 0.8) !important; color: white !important;
            border: 1px solid rgba(0, 198, 255, 0.3) !important; border-radius: 10px !important; padding: 12px !important;
        }
        input:focus, select:focus, textarea:focus { border-color: #00E5FF !important; box-shadow: 0 0 15px rgba(0, 198, 255, 0.4) !important; background-color: rgba(4, 13, 30, 0.9) !important; }

        h1, h2, h3 { color: #FFFFFF !important; font-weight: 600 !important; }
        .fade-in { animation: fadeIn 0.6s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .kpi-card {
            background: linear-gradient(135deg, rgba(0,198,255,0.05) 0%, rgba(0,102,255,0.1) 100%);
            border: 1px solid rgba(0, 198, 255, 0.3); border-radius: 16px; padding: 25px;
            text-align: center; box-shadow: 0 10px 30px rgba(0,198,255,0.05); margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            .login-wrapper { flex-direction: column !important; gap: 20px !important; margin-top: 2vh !important; }
            [data-testid="stImage"] img { max-height: 180px !important; border-radius: 15px !important; }
            [data-testid="stForm"] { padding: 25px 20px !important; }
            h1 { font-size: 2.2rem !important; }
            .kpi-card h1 { font-size: 2.5rem !important; }
        }
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
    if val in ['Pagado', 'Pagada', 'Completado']: return 'background-color: rgba(0, 229, 255, 0.1); color: #00E5FF; font-weight: 600;'
    elif val in ['Activo', 'Pendiente']: return 'background-color: rgba(0, 102, 255, 0.1); color: #0066FF; font-weight: 600;'
    elif val in ['Disponible']: return 'background-color: rgba(0, 198, 255, 0.15); color: #00C6FF; font-weight: 600;'
    elif val in ['Vendido']: return 'background-color: rgba(255, 255, 255, 0.05); color: #94A3B8; font-weight: 600;'
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
    st.error(f"🌐 El servidor de base de datos está hibernando o inalcanzable. Espera 30 segundos y recarga la página (F5). Detalles: {e}")
    st.stop()

# ==========================================
# CINTURÓN DE SEGURIDAD (TRY / FINALLY) PARA CERRAR FUGAS
# ==========================================
try:
    if 'logeado' not in st.session_state: st.session_state['logeado'] = False
    if 'id_usuario' not in st.session_state: st.session_state['id_usuario'] = None
    if 'nombre_usuario' not in st.session_state: st.session_state['nombre_usuario'] = None
    if 'rol' not in st.session_state: st.session_state['rol'] = None

    if not st.session_state['logeado']:
        st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
        col_espacio1, col_izq, col_der, col_espacio2 = st.columns([0.5, 4, 4, 0.5], gap="large", vertical_alignment="center")
        
        with col_izq:
            st.markdown("<div class='login-wrapper fade-in'>", unsafe_allow_html=True)
            st.image("image_b3d241.jpg")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_der:
            st.markdown("<div class='fade-in' style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
            with st.form("form_login"):
                st.markdown("<h2 style='color: #00E5FF; font-weight: 700; margin-bottom: 5px; font-size: 2.4rem;'>Portal de Acceso</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color: #94A3B8; margin-bottom: 25px; font-size: 1.1rem;'>Identifícate para entrar al ecosistema operativo.</p>", unsafe_allow_html=True)
                usuario_input = st.text_input("👤 Usuario Corporativo")
                password_input = st.text_input("🔒 Clave de Seguridad", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Ingresar al Sistema", width='stretch'):
                    try:
                        cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                        usuario_db = cursor.fetchone()
                        if usuario_db:
                            st.session_state['logeado'] = True
                            st.session_state['id_usuario'] = usuario_db['id_usuario']
                            st.session_state['nombre_usuario'] = usuario_db['nombre_completo']
                            st.session_state['rol'] = usuario_db['rol']
                            st.rerun()
                        else: st.error("❌ Credenciales incorrectas. Acceso denegado.")
                    except Exception as e: st.error(f"Error de base de datos: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

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
        st.sidebar.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.sidebar.image("image_b3d241.jpg")
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
            <div style='padding: 12px; background: rgba(0, 198, 255, 0.03); border-radius: 12px; border: 1px solid rgba(0,198,255,0.1); margin-bottom: 15px; text-align: center;'>
                <b style='color:#F8FAFC; font-size: 15px;'>{st.session_state['nombre_usuario']}</b><br>
                <span style='color:#00E5FF; font-size: 11px; font-weight: 500; letter-spacing: 1px;'>{str(st.session_state['rol']).upper()}</span>
            </div>
        """, unsafe_allow_html=True)
        
        menu_map = {"🏠 Panel de Inicio": "inicio"} 
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
        if st.sidebar.button("🚪 Cerrar Sesión", width='stretch'):
            st.session_state['logeado'] = False; st.rerun()

        if menu_seleccionado == "inicio":
            st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("image_b3d241.jpg")
                st.markdown(f"""
                <div class="fade-in" style="text-align: center; margin-top: 20px;">
                    <h1 style='font-size: 3.5rem; font-weight: 700; margin-bottom: 0;'>Bienvenido a <span style='color: #00C6FF;'>DaTo</span></h1>
                    <p style='color: #94A3B8; font-size: 1.2rem; font-weight: 300; margin-top: 10px;'>El ecosistema financiero está sincronizado y operativo.</p>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "simulador":
            st.markdown("<h2 class='fade-in'>Cotizador y Simulación 🔮</h2>", unsafe_allow_html=True)
            tab_sim, tab_paz = st.tabs(["📊 Simular Cuotas", "🤝 Calcular Paz y Salvo (Pago Total)"])
            
            with tab_sim:
                st.markdown("<br>", unsafe_allow_html=True)
                
                modo_cliente = st.toggle("📸 Activar Vista para Cliente")
                if 'tasa_simulador' not in st.session_state:
                    st.session_state['tasa_simulador'] = 3.0
                    
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sim_precio = st.number_input("Precio del Equipo ($)", min_value=0, step=10000, value=2000000)
                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: 600; margin-top: -15px;'>Visualización: {fmt_cop(sim_precio)}</div>", unsafe_allow_html=True)
                    sim_abono = st.number_input("Abono Inicial Cliente ($)", min_value=0, step=10000, value=500000)
                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: 600; margin-top: -15px;'>Visualización: {fmt_cop(sim_abono)}</div>", unsafe_allow_html=True)
                with col_s2:
                    sim_plazo = st.number_input("Meses a Financiar", min_value=1, max_value=72, step=1, value=6)
                    
                    if not modo_cliente:
                        idx_tasa = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0].index(st.session_state['tasa_simulador']) if st.session_state['tasa_simulador'] in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] else 3
                        sim_tasa = st.selectbox("Tasa Efectiva Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=idx_tasa)
                        st.session_state['tasa_simulador'] = sim_tasa
                    else:
                        sim_tasa = st.session_state['tasa_simulador']
                    
                sim_capital = sim_precio - sim_abono
                if sim_capital > 0:
                    i_m = sim_tasa / 100.0
                    sim_cuota = sim_capital * (i_m * (1 + i_m)**sim_plazo) / (((1 + i_m)**sim_plazo) - 1) if sim_tasa > 0 else sim_capital / sim_plazo
                    st.success(f"💸 **Cuota Mensual Sugerida: {fmt_cop(int(round(sim_cuota)))}**")
                else: st.warning("El abono inicial cubre el total del equipo.")

            with tab_paz:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.documento, i.modelo, c.monto_financiado, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
                creditos_act = cursor.fetchall()
                if not creditos_act: st.info("Ningún cliente debe dinero actualmente.")
                else:
                    opc_paz = {f"{c['documento']} | {c['nombre_completo']} ({c['modelo']})": c for c in creditos_act}
                    sel_paz = st.selectbox("Seleccione el titular a consultar:", list(opc_paz.keys()), index=None, placeholder="Seleccione un cliente de la lista...")
                    
                    if sel_paz:
                        datos_paz = opc_paz[sel_paz]
                        cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (datos_paz['id_credito'],))
                        res = cursor.fetchone()
                        saldo_capital = float(datos_paz['monto_financiado']) - float(res['cap'] if res and res['cap'] else 0.0)
                        interes_mes = saldo_capital * float(datos_paz['tasa_interes_mensual'])
                        
                        st.markdown(f"""
                        <div class="kpi-card">
                            <h3 style="color:#00E5FF; margin:0; font-weight: 500; font-size: 1.1rem;">LIQUIDACIÓN TOTAL CON DESCUENTO (PAZ Y SALVO)</h3>
                            <h1 style="color:white; font-size: 3.5rem; margin: 0;">{fmt_cop(saldo_capital + interes_mes)}</h1>
                            <p style="color:#94A3B8; font-size: 14px; margin-top: 5px;">Capital restante ({fmt_cop(saldo_capital)}) + Interés de este mes ({fmt_cop(interes_mes)}).</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        df_plan = generar_plan_pagos_real(datos_paz['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "inventario":
            st.markdown("<h2 class='fade-in'>Gestión de Inventario 📦</h2>", unsafe_allow_html=True)
            tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Unidades Disponibles", "📥 Ingresar Nuevo Equipo", "📜 Equipos Vendidos"])
            
            with tab_inv1:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT imei AS 'Serial/IMEI', categoria AS 'Tipo', marca AS 'Marca', modelo AS 'Modelo', tipo_ingreso AS 'Condición', costo_adquisicion AS 'Costo Compra', precio_venta_contado AS 'Precio Sugerido' FROM Inventario WHERE estado = 'Disponible'")
                df_inventario = pd.DataFrame(cursor.fetchall())
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📦 Equipos en Bodega", f"{len(df_inventario)}")
                if not df_inventario.empty:
                    c2.metric("💰 Dinero Invertido en Stock", fmt_cop(df_inventario['Costo Compra'].sum()))
                    c3.metric("💎 Proyección si se vende", fmt_cop(df_inventario['Precio Sugerido'].sum()))
                    df_inventario['Costo Compra'] = df_inventario['Costo Compra'].apply(fmt_cop)
                    df_inventario['Precio Sugerido'] = df_inventario['Precio Sugerido'].apply(fmt_cop)
                    st.dataframe(df_inventario, width='stretch')
                else: st.info("No hay equipos en bodega.")

            with tab_inv2:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_bolsa, nombre_bolsa, saldo_actual FROM Bolsas_Capital")
                opc_bolsas = {f"{b['nombre_bolsa']} (Liquidez en cuenta: {fmt_cop(b['saldo_actual'])})": b for b in cursor.fetchall()}

                c1, c2 = st.columns(2)
                with c1: cat_sel = st.selectbox("Categoría del Activo", list(CATALOGO.keys()), index=None, placeholder="Seleccione Categoría...")
                
                if cat_sel:
                    with c2: marca_sel = st.selectbox("Marca Comercial", list(CATALOGO[cat_sel].keys()), index=None, placeholder="Seleccione Marca...")
                    
                    if marca_sel:
                        c3, c4 = st.columns(2)
                        with c3:
                            marca_fin = st.text_input("Ingresar Marca Manual:") if marca_sel == "Otra Marca..." else marca_sel
                            mod = st.selectbox("Modelo Exacto", CATALOGO[cat_sel][marca_sel], index=None, placeholder="Seleccione Modelo...")
                            if mod:
                                mod_fin = st.text_input("Ingresar Modelo Manual:") if mod in ["Otro...", "Escribir manual..."] else mod
                        with c4:
                            if mod:
                                opc_cap = CAPACIDADES_PC if "Cómputo" in cat_sel or "💻" in cat_sel else (CAPACIDADES_ELECTRO if "Electrónica" in cat_sel or "📺" in cat_sel else CAPACIDADES_MOVILES)
                                cap = st.selectbox("Especificaciones Técnicas", opc_cap, index=None, placeholder="Seleccione Capacidad...")
                                if cap:
                                    cap_fin = "" if cap == "No Aplica" else (st.text_input("Escribe el detalle:") if cap == "Escribir manual..." else cap)

                        if mod and cap:
                            c5, c6 = st.columns(2)
                            with c5:
                                imei_in = f"SYS-{str(uuid.uuid4())[:8].upper()}" if st.checkbox("Generar Serial Interno de Sistema") else st.text_input("Serial / IMEI Físico")
                                cond = st.selectbox("Condición Físíca", ["Nuevo", "Usado", "Retoma"], index=None, placeholder="Seleccione Estado...")
                            with c6:
                                if cond:
                                    bolsa = st.selectbox("Origen de Fondos para comprarlo", options=list(opc_bolsas.keys()), index=None, placeholder="Seleccione Caja...")
                                    if bolsa:
                                        costo = st.number_input("Costo de Compra Real ($)", min_value=0, step=10000, value=0)
                                        st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: 600; margin-top: -15px;'>Visualización: {fmt_cop(costo)}</div>", unsafe_allow_html=True)
                                        precio = st.number_input("Precio de Venta Sugerido ($)", min_value=0, step=10000, value=0)
                                        st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: 600; margin-top: -15px;'>Visualización: {fmt_cop(precio)}</div>", unsafe_allow_html=True)

                                        if st.button("💾 Guardar y Asentar en Inventario", width='stretch'):
                                            dat_b = opc_bolsas[bolsa]
                                            if costo > float(dat_b['saldo_actual']): st.error("❌ La caja seleccionada no tiene fondos suficientes.")
                                            elif not imei_in or not mod_fin: st.warning("⚠️ Serial y modelo son obligatorios.")
                                            else:
                                                cursor.execute("INSERT INTO Inventario (imei, categoria, marca, modelo, tipo_ingreso, id_bolsa, costo_adquisicion, precio_venta_contado, estado, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Disponible', %s)", (imei_in, cat_sel.split(" ")[1] if " " in cat_sel else cat_sel, marca_fin, f"{mod_fin} {cap_fin}".strip(), cond, dat_b['id_bolsa'], costo, precio, st.session_state['id_usuario']))
                                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s WHERE id_bolsa = %s", (costo, dat_b['id_bolsa']))
                                                conn.commit(); st.toast('Hardware registrado.', icon='📦'); time.sleep(1.5); st.rerun()
                            
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
                else: st.info("Ningún movimiento registrado.")

        elif menu_seleccionado == "clientes":
            st.markdown("<h2 class='fade-in'>Directorio de Clientes 👥</h2>", unsafe_allow_html=True)
            with st.form("f_cli"):
                doc = st.text_input("Cédula de Ciudadanía")
                nom = st.text_input("Nombre y Apellido Completo")
                tel = st.text_input("Teléfono Celular")
                if st.form_submit_button("Crear Titular en la Base de Datos", width='stretch'):
                    if doc and nom:
                        try:
                            cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, id_usuario_registro) VALUES (%s, %s, %s, %s)", (doc, nom, tel, st.session_state['id_usuario']))
                            conn.commit(); st.toast("Cliente Registrado.", icon='👥'); time.sleep(1); st.rerun()
                        except mysql.connector.Error: st.error("Esta cédula ya está registrada en el sistema.")
                    else: st.warning("La cédula y el nombre no pueden estar vacíos.")
            
            st.divider()
            cursor.execute("SELECT documento AS 'Cédula', nombre_completo AS 'Nombre Registrado', telefono AS 'Línea Celular' FROM Clientes")
            df_clientes = pd.DataFrame(cursor.fetchall())
            if not df_clientes.empty: st.dataframe(df_clientes, width='stretch')

        elif menu_seleccionado == "ventas":
            st.markdown("<h2 class='fade-in'>Originación de Créditos 📝</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
            clientes = cursor.fetchall()
            cursor.execute("SELECT imei, categoria, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
            inventario = cursor.fetchall()
            
            if not clientes or not inventario: st.warning("Se requiere registrar al menos un Cliente y tener Equipos Disponibles en Inventario.")
            else:
                opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                opc_eq = {f"[{e['categoria']}] {e['marca']} {e['modelo']} (S/N: {e['imei']})": e for e in inventario}
                
                tipo_v = st.selectbox("Seleccione la modalidad de venta:", ["Crédito Financiado (Amortización con Interés)", "Plan Separé / Cuotas Fijas (Sin Interés)", "Venta de Contado Directo"], index=None, placeholder="Seleccione modalidad...")
                st.divider()
                
                if tipo_v:
                    c1, c2 = st.columns(2)
                    with c1: cli_sel = st.selectbox("¿A quién le vendemos?", list(opc_cli.keys()), index=None, placeholder="Seleccione el Cliente...")
                    with c2: eq_sel = st.selectbox("¿Qué equipo se despacha?", list(opc_eq.keys()), index=None, placeholder="Seleccione el Equipo...")
                    
                    if cli_sel and eq_sel:
                        st.markdown("<div style='background: rgba(0,198,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(0,198,255,0.2); margin: 15px 0;'><p style='color:#00C6FF; font-size:14px; margin-bottom:10px; font-weight: 600;'>📅 Ajuste de Tiempos Contractuales</p>", unsafe_allow_html=True)
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: fecha_venta = st.date_input("Fecha real en que se cerró la venta", value=datetime.date.today())
                        with c_f2: f_cuota = st.date_input("Fecha pactada para la primera cuota", value=sumar_meses_exactos(fecha_venta, 1))
                        st.markdown("</div>", unsafe_allow_html=True)

                        c3, c4 = st.columns(2)
                        c_pers, c_fija = [], 0
                        
                        if "Financiado" in tipo_v:
                            with c3:
                                p_final = st.number_input("Precio Final Pactado con el Cliente ($)", min_value=1, value=1000000, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Visualización: {fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                                ab_init = st.number_input("Plata Inicial Entregada ($)", min_value=0, value=0, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Visualización: {fmt_cop(ab_init)}</div>", unsafe_allow_html=True)
                                plazo = st.number_input("Meses a Financiar el Resto", min_value=1, value=6)
                            with c4:
                                st.write("Datos Internos Comerciales")
                                cx1, cx2 = st.columns([1,2])
                                with cx1: 
                                    comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>{fmt_cop(comis)}</div>", unsafe_allow_html=True)
                                with cx2: ase_nom = st.text_input("Vendedor a cargo")
                                tasa = st.selectbox("Tasa Efectiva Mensual Aplicada (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                            
                            m_f = p_final - ab_init
                            if m_f > 0 and plazo > 0:
                                i_m = tasa / 100.0
                                c_fija = int(round(m_f * (i_m * (1 + i_m)**plazo) / (((1 + i_m)**plazo) - 1))) if tasa > 0 else int(round(m_f / plazo))
                                st.info(f"📊 **Cuota Mensual Exacta para el Cliente:** {fmt_cop(c_fija)}")
                        
                        elif "Separé" in tipo_v:
                            with c3:
                                p_final = st.number_input("Precio Total del Equipo ($)", min_value=1, value=1000000, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Visualización: {fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                                ab_init = st.number_input("Abono Inicial ($)", min_value=0, value=0, step=10000)
                                st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Visualización: {fmt_cop(ab_init)}</div>", unsafe_allow_html=True)
                                plazo = st.number_input("Cantidad de Cuotas", min_value=1, value=2)
                            with c4:
                                st.write("Datos Internos Comerciales")
                                cx1, cx2 = st.columns([1,2])
                                with cx1: 
                                    comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>{fmt_cop(comis)}</div>", unsafe_allow_html=True)
                                with cx2: ase_nom = st.text_input("Vendedor a cargo")
                            tasa, s_dif, s_cuotas = 0.0, p_final - ab_init, 0
                            st.write(f"Saldo pendiente a distribuir: {fmt_cop(s_dif)}")
                            for idx in range(plazo):
                                x1, x2 = st.columns(2)
                                with x1:
                                    v_c = st.number_input(f"Valor para la Cuota {idx+1}", min_value=0, value=int(s_dif/plazo), step=10000, key=f"v_{idx}")
                                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>{fmt_cop(v_c)}</div>", unsafe_allow_html=True)
                                    s_cuotas += v_c
                                with x2: 
                                    f_c = st.date_input(f"Día Límite de Pago {idx+1}", value=sumar_meses_exactos(f_cuota, idx), key=f"f_{idx}")
                                c_pers.append((idx+1, v_c, f_c))
                        else:
                            p_final = st.number_input("Dinero Completo Recibido ($)", min_value=1, value=1000000, step=10000)
                            st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Visualización: {fmt_cop(p_final)}</div>", unsafe_allow_html=True)
                            ab_init, plazo, tasa, comis, ase_nom = p_final, 0, 0.0, 0, ""

                        st.divider()
                        if st.button("🚀 Procesar Originación y Archivar", width='stretch'):
                            valido = True
                            if comis > 0 and not ase_nom: st.error("❌ Requiere nombre de vendedor si se asignó comisión."); valido = False
                            if "Separé" in tipo_v and s_cuotas != (p_final - ab_init): st.error("❌ Las cuotas de abajo no suman el saldo neto de la deuda."); valido = False

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
                                conn.commit(); st.toast("Venta formalizada.", icon='🚀'); time.sleep(1.5); st.rerun()

        elif menu_seleccionado == "pagos":
            st.markdown("<h2 class='fade-in'>Centro de Recaudos 💰</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.imei, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota, c.plazo_meses, i.marca, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay carteras activas pendientes de pago.")
            else:
                opc_c = {f"{c['nombre_completo']} (Cuenta Equipo: {c['marca']} {c['modelo']})": c for c in activos}
                sel_titular = st.selectbox("¿Qué titular enviará el dinero?", list(opc_c.keys()), index=None, placeholder="Busque y seleccione el Titular...")
                
                if sel_titular:
                    dat = opc_c[sel_titular]
                    
                    cursor.execute("SELECT id_pago, monto_recibido, fecha_pago, tipo_pago, capital_abonado, interes_cobrado FROM Pagos WHERE id_credito = %s ORDER BY fecha_pago DESC", (dat['id_credito'],))
                    hist = cursor.fetchall()
                    
                    cap_pagado = sum([float(p['capital_abonado']) for p in hist])
                    s_pend = float(dat['monto_financiado']) - cap_pagado
                    v_cuota_bd = int(dat['valor_cuota']) if dat['valor_cuota'] else 0
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Saldo Neto a Capital", fmt_cop(s_pend))
                    c2.metric("Valor Cuota Fija Mensual", fmt_cop(v_cuota_bd))
                    c3.metric("Fecha del Último Abono", f"🗓️ {hist[0]['fecha_pago'].strftime('%Y-%m-%d')}" if hist else "Sin historial", fmt_cop(hist[0]['monto_recibido']) if hist else "$0")
                    
                    st.markdown("### 💵 Asentar Recaudo de Caja")
                    with st.form("f_pago"):
                        x1, x2 = st.columns(2)
                        with x1: 
                            monto = st.number_input("Dinero Exacto que entregó ($)", value=0, min_value=0, step=10000)
                            st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold; margin-top: -15px;'>Monto a Procesar: {fmt_cop(monto)}</div>", unsafe_allow_html=True)
                        with x2: fecha_pago_efectiva = st.date_input("Día exacto que ingresó el dinero", value=None)
                        
                        tipo = st.selectbox("Aplicación Financiera del Pago", ["Cuota Ordinaria Mensual", "Abono Extra a Capital (Reducir Cuota Mensual)", "Abono Extra a Capital (Reducir el Tiempo del Crédito)"], index=None, placeholder="Seleccione concepto del recaudo...")
                        
                        if st.form_submit_button("✅ Sellar Transacción de Caja", width='stretch'):
                            if monto <= 0: st.error("❌ El monto no puede ser cero.")
                            elif not tipo: st.error("❌ Indique la aplicación del pago.")
                            elif fecha_pago_efectiva is None: st.error("❌ Especifique el día del pago.")
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
                                
                                conn.commit(); st.toast("Recaudo indexado con éxito.", icon='✅'); time.sleep(1.5); st.rerun()

                    st.markdown("<br>### 💸 Historial de Transacciones Físicas", unsafe_allow_html=True)
                    if hist:
                        df_trans = pd.DataFrame(hist)
                        df_trans.rename(columns={'fecha_pago': 'Fecha', 'tipo_pago': 'Concepto', 'monto_recibido': 'Monto Recibido', 'capital_abonado': 'Al Capital', 'interes_cobrado': 'A Intereses'}, inplace=True)
                        for col in ['Monto Recibido', 'Al Capital', 'A Intereses']: df_trans[col] = df_trans[col].apply(fmt_cop)
                        st.dataframe(df_trans[['Fecha', 'Concepto', 'Monto Recibido', 'Al Capital', 'A Intereses']], width='stretch')
                    else:
                        st.info("Sin registros físicos.")

                    st.markdown("<br>### 🧾 Plan de Amortización Teórico", unsafe_allow_html=True)
                    df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                    st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "vencimientos":
            st.markdown("<h2 class='fade-in'>Control de Cartera y Mora ⏰</h2>", unsafe_allow_html=True)
            cursor.execute("""
                SELECT cl.nombre_completo AS 'Titular', cl.telefono AS 'Celular', c.valor_cuota AS 'Mensualidad', c.fecha_primera_cuota AS 'Fecha de Corte', 
                (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Capital Pendiente',
                c.estado AS 'Estatus', c.tasa_interes_mensual
                FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo' ORDER BY c.fecha_primera_cuota ASC
            """)
            df = pd.DataFrame(cursor.fetchall())
            if df.empty: st.info("Índice de cartera vencida en ceros.")
            else:
                df['Liquidación Inmediata (Paz y Salvo)'] = df.apply(lambda r: float(r['Capital Pendiente']) + (float(r['Capital Pendiente']) * float(r['tasa_interes_mensual'])), axis=1)
                for c in ['Mensualidad', 'Capital Pendiente', 'Liquidación Inmediata (Paz y Salvo)']: df[c] = df[c].apply(fmt_cop)
                df = df.drop(columns=['tasa_interes_mensual'])
                st.dataframe(df.style.map(color_estado, subset=['Estatus']), width='stretch')

        elif menu_seleccionado == "notificar":
            st.markdown("<h2 class='fade-in'>Estados de Cuenta Mensuales 📱</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.telefono, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, i.modelo, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay extractos pendientes por despachar.")
            else:
                opc_n = {f"{c['nombre_completo']} (Hardware: {c['modelo']})": c for c in activos}
                sel_cli = st.selectbox("Elija al Cliente para emitir el Extracto", list(opc_n.keys()), index=None, placeholder="Seleccione Titular...")
                
                if sel_cli:
                    dat = opc_n[sel_cli]
                    cursor.execute("SELECT SUM(capital_abonado) as cap, MAX(monto_recibido) as last_val, MAX(fecha_pago) as last_date FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    res_pag = cursor.fetchone()
                    cap_pag = float(res_pag['cap']) if res_pag and res_pag['cap'] else 0
                    last_val = float(res_pag['last_val']) if res_pag and res_pag['last_val'] else 0
                    last_date = res_pag['last_date'] if res_pag and res_pag['last_date'] else None

                    s_act = float(dat['monto_financiado']) - cap_pag
                    paz_y_salvo = s_act + (s_act * float(dat['tasa_interes_mensual']))
                    
                    msg = f"Buen día {dat['nombre_completo']}. Resumen de tu obligación con DaTo:\n\n💵 *Mensualidad Ordinaria:* {fmt_cop(dat['valor_cuota'])}\n📉 *Saldo Neto Pendiente:* {fmt_cop(s_act)}\n💳 *Última Tranascción:* {fmt_cop(last_val) if last_val else '$0'} el día {last_date.strftime('%Y-%m-%d') if last_date else 'N/A'}\n\n*💰 Si deseas pagar tu equipo en su totalidad (Paz y Salvo): {fmt_cop(paz_y_salvo)}*\n\nTe recordamos que tu fecha límite son los {str(dat['fecha_primera_cuota'].day)} de cada mes. ¡Muchas gracias!"
                    
                    c1, c2 = st.columns([1, 1])
                    with c1: st.text_area("Texto para WhatsApp Comercial", value=msg, height=300)
                    with c2:
                        st.subheader("Verificación Visual del Crédito")
                        df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "historial":
            st.markdown("<h2 class='fade-in'>Auditoría de Operaciones 📜</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("🔒 Privilegio directivo requerido."); st.stop()
            
            tab_v, tab_r = st.tabs(["📋 Libro Mayor de Operaciones", "⚠️ Módulo de Corrección (Zona Crítica)"])
            
            with tab_v:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT c.id_credito, cl.nombre_completo AS 'Titular', i.modelo AS 'Activo Entregado', c.estado AS 'Calificación', 
                           i.costo_adquisicion AS 'Costo Hardware', c.precio_venta AS 'Precio Acordado',
                           IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) AS 'Recaudo Acumulado',
                           (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Capital en la Calle',
                           c.valor_comision AS 'Comisión Emitida',
                           (IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) - i.costo_adquisicion - c.valor_comision) AS 'GANANCIA NETA EN EFECTIVO'
                    FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.fecha_inicio DESC
                """)
                df_cart = pd.DataFrame(cursor.fetchall())
                if not df_cart.empty:
                    for col in ['Costo Hardware', 'Precio Acordado', 'Recaudo Acumulado', 'Capital en la Calle', 'Comisión Emitida', 'GANANCIA NETA EN EFECTIVO']: 
                        df_cart[col] = df_cart[col].apply(fmt_cop)
                    st.dataframe(df_cart.style.map(color_estado, subset=['Calificación']).map(color_ganancia_real, subset=['GANANCIA NETA EN EFECTIVO']), width='stretch')
                else: st.info("El log de auditoría no arroja resultados.")

            with tab_r:
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("<h4 style='color:#00E5FF;'>🗑️ Anular un Recibo de Pago</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT p.id_pago, cl.nombre_completo, p.monto_recibido, p.fecha_pago, p.tipo_pago FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY p.id_pago DESC LIMIT 50")
                    pagos_db = cursor.fetchall()
                    if pagos_db:
                        opc_pagos = {f"[{p['fecha_pago'].strftime('%Y-%m-%d')}] {p['nombre_completo']} ({fmt_cop(p['monto_recibido'])}) - {p['tipo_pago']}": p for p in pagos_db}
                        with st.form("f_anular_pago"):
                            pago_sel = st.selectbox("Elegir la transacción a borrar", list(opc_pagos.keys()), index=None, placeholder="Seleccionar transacción...")
                            if st.form_submit_button("Anular y Descontar de Caja", width='stretch') and pago_sel:
                                dat_p = opc_pagos[pago_sel]
                                cursor.execute("SELECT id_credito FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                id_c = cursor.fetchone()['id_credito']
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (dat_p['monto_recibido'],))
                                cursor.execute("DELETE FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                cursor.execute("UPDATE Creditos SET estado = 'Activo' WHERE id_credito = %s", (id_c,))
                                conn.commit(); st.toast("Recibo extraído de la base.", icon='🚨'); time.sleep(1.5); st.rerun()
                    else: st.info("No hay historial de recibos.")

                with c2:
                    st.markdown("<h4 style='color:#00C6FF;'>🚨 Echar Atrás una Venta Entera</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT c.id_credito, cl.nombre_completo, i.modelo, c.imei, c.abono_inicial FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.id_credito DESC")
                    creds_db = cursor.fetchall()
                    if creds_db:
                        opc_creds = {f"[Factura: {c['id_credito']}] {c['nombre_completo']} - {c['modelo']}": c for c in creds_db}
                        with st.form("f_anular_venta"):
                            cred_sel = st.selectbox("Identificar la venta a destruir", list(opc_creds.keys()), index=None, placeholder="Seleccionar contrato...")
                            if st.form_submit_button("Eliminar Completamente", width='stretch') and cred_sel:
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
                                conn.commit(); st.toast("Venta purgada. Hardware libre.", icon='🚨'); time.sleep(1.5); st.rerun()
                    else: st.info("Facturación limpia.")
                    
                with c3:
                    st.markdown("<h4 style='color:#0099FF;'>📦 Eliminar Hardware de Bodega</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT imei, marca, modelo, costo_adquisicion, id_bolsa FROM Inventario WHERE estado = 'Disponible'")
                    inv_db = cursor.fetchall()
                    if inv_db:
                        opc_inv = {f"{i['marca']} {i['modelo']} ({i['imei']})": i for i in inv_db}
                        with st.form("f_anular_hardware"):
                            inv_sel = st.selectbox("Elegir dispositivo a purgar", list(opc_inv.keys()), index=None, placeholder="Seleccionar hardware...")
                            if st.form_submit_button("Borrar y Reembolsar Costo", width='stretch') and inv_sel:
                                dat_i = opc_inv[inv_sel]
                                if float(dat_i['costo_adquisicion']) > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s WHERE id_bolsa = %s", (dat_i['costo_adquisicion'], dat_i['id_bolsa']))
                                cursor.execute("DELETE FROM Inventario WHERE imei = %s", (dat_i['imei'],))
                                conn.commit(); st.toast("Hardware borrado.", icon='✅'); time.sleep(1.5); st.rerun()
                    else: st.info("Sin inventario para anular.")

        elif menu_seleccionado == "egresos":
            st.markdown("<h2 class='fade-in'>Control de Gastos Operativos 💸</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("🔒 Privilegio confidencial."); st.stop()
            
            tab_com, tab_gas = st.tabs(["🤝 Nómina Comercial (Asesores)", "🧾 Egresos del Negocio (Arriendos, Luz, etc)"])
            with tab_com:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo AS 'Titular', cl.telefono AS 'Celular', i.modelo AS 'Activo', c.asesor_comision AS 'Asesor Comercial', c.valor_comision AS 'Bono a Pagar' FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado_comision = 'Pendiente'")
                pends = cursor.fetchall()
                if pends:
                    df_p = pd.DataFrame(pends)
                    df_p['Bono a Pagar'] = df_p['Bono a Pagar'].apply(fmt_cop)
                    st.dataframe(df_p, width='stretch')
                    with st.form("f_com"):
                        sel = st.selectbox("Seleccionar liquidación de Asesor", list({f"[{x['Asesor Comercial']}] Venta a: {x['Titular']} ({x['Celular']}) -> {fmt_cop(x['Bono a Pagar'])}": x['id_credito'] for x in pends}.keys()), index=None, placeholder="Seleccione Pase...")
                        if st.form_submit_button("Aprobar Desembolso de Caja", width='stretch') and sel:
                            id_c = {f"[{x['Asesor Comercial']}] Venta a: {x['Titular']} ({x['Celular']}) -> {fmt_cop(x['Bono a Pagar'])}": x['id_credito'] for x in pends}[sel]
                            cursor.execute("SELECT valor_comision FROM Creditos WHERE id_credito = %s", (id_c,))
                            val = float(cursor.fetchone()['valor_comision'])
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (val,))
                            cursor.execute("UPDATE Creditos SET estado_comision = 'Pagada', fecha_pago_comision = %s WHERE id_credito = %s", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_c))
                            conn.commit(); st.toast("Saldado correctamente.", icon='✅'); time.sleep(1.5); st.rerun()
                else: st.info("Matriz de nómina comercial sin pasivos.")
                
            with tab_gas:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei")
                opc_eq = {"Gasto Administrativo General (No atado a ninguna venta)": None}
                for x in cursor.fetchall(): opc_eq[f"Atar costo a la venta de: {x['nombre_completo']} ({x['modelo']})"] = x['id_credito']
                with st.form("f_g"):
                    desc = st.text_input("Concepto del Gasto (Ej: Arriendo, Local, Repuesto, Publicidad)")
                    cred_cc = st.selectbox("Elegir Centro de Costo", list(opc_eq.keys()), index=None, placeholder="Seleccione C.C. ...")
                    m_g = st.number_input("Valor a Extraer de la Caja ($)", min_value=0, step=10000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold;'>Visualización: {fmt_cop(m_g)}</div>", unsafe_allow_html=True)
                    if st.form_submit_button("Asentar Gasto", width='stretch') and cred_cc:
                        cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, id_usuario_registro) VALUES (%s, %s, %s, %s)", (desc, m_g, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                        cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (m_g,))
                        conn.commit(); st.toast("Gasto debitado de caja matriz.", icon='✅'); time.sleep(1); st.rerun()

        elif menu_seleccionado == "flujo":
            st.markdown("<h2 class='fade-in'>Tesorería y Socios (Fondeo) 📈</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("🔒 Área Confidencial."); st.stop()
            
            tab_dash, tab_in, tab_out = st.tabs(["📊 Libro Mayor de Inversionistas", "📥 Recibir Inyección de Fondeo", "📤 Realizar Pago a Socios"])
            
            with tab_dash:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT prestamista AS 'Fondo Inversor', monto_prestado AS 'Capital Inyectado', monto_total_pagar AS 'Rendimiento Acordado', (monto_total_pagar - saldo_pendiente) AS 'Retorno Ejecutado', saldo_pendiente AS 'Saldo Vivo Exigible', fecha_prestamo AS 'Fecha de Ingreso' FROM Deudas_Fondeo ORDER BY fecha_prestamo DESC")
                df_inversores = pd.DataFrame(cursor.fetchall())
                
                cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
                res_cap = cursor.fetchone()
                cap = float(res_cap['cap']) if res_cap and res_cap['cap'] else 0
                
                deuda = df_inversores['Saldo Vivo Exigible'].sum() if not df_inversores.empty else 0
                
                c1, c2 = st.columns(2)
                c1.metric("💵 Liquidez Operativa Central", fmt_cop(cap))
                c2.metric("📉 Fondeo Total Exigible", fmt_cop(deuda))
                
                st.markdown("<br><h4 style='color:#E2E8F0; font-size: 1.1rem;'>📜 Estado de Cuenta General de Socios</h4>", unsafe_allow_html=True)
                if not df_inversores.empty:
                    for c in ['Capital Inyectado', 'Rendimiento Acordado', 'Retorno Ejecutado', 'Saldo Vivo Exigible']: df_inversores[c] = df_inversores[c].apply(fmt_cop)
                    st.dataframe(df_inversores, width='stretch')
                else: st.info("Registro institucional en blanco.")

                st.markdown("<br><h4 style='color:#E2E8F0; font-size: 1.1rem;'>🧾 Registro de Dispersiones</h4>", unsafe_allow_html=True)
                cursor.execute("SELECT p.fecha_pago AS 'Fecha de Operación', d.prestamista AS 'Recibidor', p.monto_pagado AS 'Valor Desembolsado' FROM Pagos_Deuda p JOIN Deudas_Fondeo d ON p.id_deuda = d.id_deuda ORDER BY p.fecha_pago DESC")
                df_hist_deuda = pd.DataFrame(cursor.fetchall())
                if not df_hist_deuda.empty:
                    df_hist_deuda['Valor Desembolsado'] = df_hist_deuda['Valor Desembolsado'].apply(fmt_cop)
                    st.dataframe(df_hist_deuda, width='stretch')

            with tab_in:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("f_f_in"):
                    prov = st.text_input("Inversionista / Socio Originador")
                    iny = st.number_input("Inyección de Fondeo ($)", min_value=0, step=100000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold;'>Visualización: {fmt_cop(iny)}</div>", unsafe_allow_html=True)
                    ret = st.number_input("Monto Total de Retorno Pactado ($)", min_value=0, step=100000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold;'>Visualización: {fmt_cop(ret)}</div>", unsafe_allow_html=True)
                    if st.form_submit_button("Contabilizar Fondeo", width='stretch'):
                        if prov and iny > 0:
                            cursor.execute("INSERT INTO Deudas_Fondeo (prestamista, monto_prestado, monto_total_pagar, saldo_pendiente, fecha_prestamo, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s)", (prov, iny, ret, ret, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (iny,))
                            conn.commit(); st.toast("Capital indexado a la caja.", icon='✅'); time.sleep(1); st.rerun()

            with tab_out:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_deuda, prestamista, saldo_pendiente FROM Deudas_Fondeo WHERE saldo_pendiente > 0")
                deudas = cursor.fetchall()
                if deudas:
                    opc_d = {f"{d['prestamista']} (Línea Exigible: {fmt_cop(d['saldo_pendiente'])})": d for d in deudas}
                    with st.form("f_d_out"):
                        d_sel = st.selectbox("Pasivo Estructural a Afectar", list(opc_d.keys()), index=None, placeholder="Seleccione Pasivo...")
                        ab = st.number_input("Liberación de Caja ($)", min_value=0, step=100000, value=0)
                        st.markdown(f"<div style='text-align: right; color: #00C6FF; font-weight: bold;'>Visualización: {fmt_cop(ab)}</div>", unsafe_allow_html=True)
                        if st.form_submit_button("Generar Dispersión Fiduciaria", width='stretch') and d_sel:
                            id_d = opc_d[d_sel]['id_deuda']
                            cursor.execute("INSERT INTO Pagos_Deuda (id_deuda, monto_pagado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s)", (id_d, ab, datetime.date.today().strftime('%Y-%m-%d'), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Deudas_Fondeo SET saldo_pendiente = saldo_pendiente - %s WHERE id_deuda = %s", (ab, id_d))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (ab,))
                            conn.commit(); st.toast("Transferencia completada.", icon='✅'); time.sleep(1); st.rerun()
                else: st.info("Estructura libre de pasivos.")

        elif menu_seleccionado == "reportes":
            st.markdown("<h2 class='fade-in'>Inteligencia de Negocios (BI) 📊</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("🔒 Sistema Exclusivo."); st.stop()
            
            tab_bi, tab_graf, tab_riesgo, tab_eficiencia = st.tabs(["🌐 Resumen Ejecutivo", "📈 Dinámica de Flujo", "⚖️ Riesgo de Cartera", "💸 ROI y Eficiencia"])
            
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
                <div class="kpi-card">
                    <h3 style="color:#00C6FF; margin:0; font-weight: 500; letter-spacing: 2px;">VALOR PATRIMONIAL DEL ECOSISTEMA</h3>
                    <h1 style="color:white; font-size: 3.8rem; margin: 5px 0;">{fmt_cop(patrimonio_neto)}</h1>
                    <p style="color:#8B9BB4; font-size: 14px; margin:0;">Caja Líquida ({fmt_cop(cap)}) + Cartera Viva en la Calle ({fmt_cop(cartera_neta_calle)}) - Fondeo de Socios Exigible ({fmt_cop(deuda)})</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("✅ Ganancia Pura Limpia (En Caja)", fmt_cop(ganancia_neta_100))
                c_m2.metric("💳 Riesgo de Capital (Calle)", fmt_cop(cartera_neta_calle))
                c_m3.metric("📊 Ticket Promedio por Cliente", fmt_cop(ticket_promedio))

            with tab_graf:
                st.markdown("<br>", unsafe_allow_html=True)
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown("#### 📅 Tendencia Histórica de Recaudos (Cash-In)")
                    cursor.execute("SELECT DATE_FORMAT(fecha_pago, '%Y-%m') as mes, SUM(monto_recibido) as total FROM Pagos GROUP BY mes ORDER BY mes ASC")
                    recaudos_mes = cursor.fetchall()
                    if recaudos_mes:
                        df_chart_rec = pd.DataFrame(recaudos_mes)
                        df_chart_rec.columns = ['Mes', 'Efectivo Recaudado']
                        df_chart_rec.set_index('Mes', inplace=True)
                        st.bar_chart(df_chart_rec, color="#00C6FF")
                    else: st.info("Gráfico inactivo. No hay recaudos.")
                    
                with col_g2:
                    st.markdown("#### 📈 Crecimiento Comercial (Ventas Colocadas)")
                    cursor.execute("SELECT DATE_FORMAT(fecha_inicio, '%Y-%m') as mes, SUM(precio_venta) as total FROM Creditos GROUP BY mes ORDER BY mes ASC")
                    ventas_mes = cursor.fetchall()
                    if ventas_mes:
                        df_chart_ven = pd.DataFrame(ventas_mes)
                        df_chart_ven.columns = ['Mes', 'Monto de Ventas']
                        df_chart_ven.set_index('Mes', inplace=True)
                        st.area_chart(df_chart_ven, color="#0066FF")
                    else: st.info("Gráfico inactivo.")

            with tab_riesgo:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT estado, COUNT(*) as cantidad FROM Creditos GROUP BY estado")
                estados_credito = cursor.fetchall()
                
                c_r1, c_r2 = st.columns([1.5, 1])
                with c_r1:
                    st.markdown("#### ⚖️ Medidor de Riesgo Global")
                    recup_perc = (cartera_recaudada / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Porcentaje de Capital de Calle Recuperado:** {recup_perc:.1f}%")
                    st.progress(min(int(recup_perc), 100))
                    
                    mora_perc = ((cartera_colocada - cartera_recaudada) / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Porcentaje de Capital en Riesgo Operativo:** {mora_perc:.1f}%")
                    st.progress(min(int(mora_perc), 100))
                
                with c_r2:
                    st.markdown("#### 📋 Distribución de Operaciones")
                    if estados_credito:
                        df_est = pd.DataFrame(estados_credito)
                        df_est.columns = ['Estado del Contrato', 'Cantidad']
                        df_est.set_index('Estado del Contrato', inplace=True)
                        st.bar_chart(df_est, color="#00E5FF")

            with tab_eficiencia:
                st.markdown("<br>", unsafe_allow_html=True)
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    st.markdown("#### 💎 Composición de la Utilidad Bruta")
                    df_ingresos = pd.DataFrame([
                        {"Core de Negocio": "Margen de Comercialización Pura", "Valor": ganancia_por_venta},
                        {"Core de Negocio": "Intereses Reales Recaudados", "Valor": ganancia_por_interes}
                    ])
                    if not df_ingresos.empty:
                        df_ingresos.set_index("Core de Negocio", inplace=True)
                        st.bar_chart(df_ingresos, color="#00C6FF")

                with col_e2:
                    st.markdown("#### 💸 Fugas y Análisis de Egresos")
                    df_egresos = pd.DataFrame([
                        {"Fuga de Capital": "Gastos Administrativos / Overhead", "Valor": gastos_totales},
                        {"Fuga de Capital": "Nómina y Comisiones Pagadas", "Valor": comisiones_totales}
                    ])
                    if not df_egresos.empty:
                        df_egresos.set_index("Fuga de Capital", inplace=True)
                        st.bar_chart(df_egresos, color="#001E3C")
                        
                st.markdown(f"""
                <div class="kpi-card" style="margin-top: 20px;">
                    <h4 style="color:#8B9BB4; margin:0; font-weight: 500;">Retorno sobre la Inversión (ROI) Aproximado</h4>
                    <h1 style="color:white; font-size: 2.5em; margin: 5px 0;">{((ganancia_por_venta + ganancia_por_interes) / (total_costo_equipos if total_costo_equipos > 0 else 1) * 100):.1f}%</h1>
                    <p style="color:#475569; font-size: 13px; margin:0;">Retorno proyectado por cada peso invertido en adquisición de equipos.</p>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "config_roles":
            st.markdown("<h2 class='fade-in'>Configuración y Seguridad ⚙️</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("🔒 Área Restringida al Panel Directivo."); st.stop()
            
            tab_c1, tab_c2, tab_c3 = st.tabs(["👤 Asignación de Roles", "🛡️ Políticas y Perímetros", "➕ Creación Organizacional"])
            cursor.execute("SELECT * FROM Roles")
            opc_r = [r['nombre_rol'] for r in cursor.fetchall()]
            
            with tab_c1:
                st.markdown("<br>", unsafe_allow_html=True)
                col_u1, col_u2, col_u3 = st.columns(3)
                with col_u1:
                    st.markdown("**✨ Nuevo Alta Organizacional**")
                    with st.form("f_newUser"):
                        n_user = st.text_input("Usuario (Login corto)")
                        n_pass = st.text_input("Clave de Ingreso", type="password")
                        n_nombre = st.text_input("Identidad Formal")
                        n_rol = st.selectbox("Clasificación de Seguridad", opc_r)
                        if st.form_submit_button("✅ Proveer Acceso", width='stretch'):
                            if n_user and n_pass and n_nombre:
                                try:
                                    cursor.execute("INSERT INTO Usuarios (username, password_hash, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_user, n_pass, n_nombre, n_rol))
                                    conn.commit(); st.toast("Contratado e indexado.", icon='✅'); time.sleep(1.5); st.rerun()
                                except mysql.connector.Error: st.error("❌ Conflicto de credenciales.")
                            else: st.warning("⚠️ Llenar matriz obligatoria.")
                with col_u2:
                    st.markdown("**🔄 Modificación de Perímetro**")
                    with st.form("f_change_rol"):
                        cursor.execute("SELECT username FROM Usuarios")
                        users_db = [u['username'] for u in cursor.fetchall()]
                        if users_db:
                            u_rol = st.selectbox("Selección de Nodo", users_db, index=None, placeholder="Seleccionar...")
                            new_rol = st.selectbox("Nueva Clasificación", opc_r, index=None, placeholder="Seleccionar...")
                            if st.form_submit_button("Aplicar Parámetro", width='stretch') and u_rol and new_rol:
                                cursor.execute("UPDATE Usuarios SET rol = %s WHERE username = %s", (new_rol, u_rol))
                                conn.commit(); st.toast("Parámetro ejecutado.", icon='✅'); time.sleep(1.5); st.rerun()
                with col_u3:
                    st.markdown("**🔑 Intervención de Seguridad**")
                    with st.form("f_reset"):
                        if users_db:
                            u_reset = st.selectbox("Selección de Credencial", users_db, index=None, placeholder="Seleccionar...")
                            p_reset = st.text_input("Token de Respaldo", type="password")
                            if st.form_submit_button("Sobreescribir", width='stretch') and u_reset and p_reset:
                                cursor.execute("UPDATE Usuarios SET password_hash = %s WHERE username = %s", (p_reset, u_reset))
                                conn.commit(); st.toast("Clave reestructurada.", icon='✅'); time.sleep(1.5); st.rerun()

            with tab_c2:
                st.markdown("<br>", unsafe_allow_html=True)
                role_sel = st.selectbox("Evaluación de Clasificación:", opc_r, index=None, placeholder="Seleccione el Rol...")
                if role_sel:
                    cursor.execute("SELECT * FROM Modulos_Sistema")
                    todos_modulos = cursor.fetchall()
                    cursor.execute("SELECT id_modulo FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                    activos_rol = [x['id_modulo'] for x in cursor.fetchall()]
                    
                    st.write(f"Áreas con acceso para **{role_sel}**:")
                    with st.form("form_permisos"):
                        check_resultados = {m['id_modulo']: st.checkbox(m['nombre_visible'], value=(m['id_modulo'] in activos_rol)) for m in todos_modulos}
                        if st.form_submit_button("Ejecutar Sello de Permisos", width='stretch'):
                            cursor.execute("DELETE FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                            cursor.execute("SELECT id_role FROM Roles WHERE nombre_rol = %s", (role_sel,))
                            id_r_actual = cursor.fetchone()['id_role']
                            for id_mod, marcado in check_resultados.items():
                                if marcado: cursor.execute("INSERT INTO Permisos_Rol (id_role, id_modulo) VALUES (%s, %s)", (id_r_actual, id_mod))
                            conn.commit(); st.toast("Sistema blindado.", icon='✅'); time.sleep(1); st.rerun()

            with tab_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("form_nuevo_rol"):
                    nuevo_rol_nombre = st.text_input("Asignación Organizacional:")
                    if st.form_submit_button("Inyectar Clasificación", width='stretch'):
                        if nuevo_rol_nombre:
                            try:
                                cursor.execute("SELECT nombre_rol FROM Roles WHERE nombre_rol = %s", (nuevo_rol_nombre.strip(),))
                                if cursor.fetchone(): st.error("Clasificación en conflicto (Ya existe).")
                                else:
                                    cursor.execute("INSERT INTO Roles (nombre_rol) VALUES (%s)", (nuevo_rol_nombre.strip(),))
                                    conn.commit(); st.toast("Clasificación registrada."); time.sleep(1); st.rerun()
                            except Exception as e: st.error(f"Falla Crítica de Base de Datos: {e}")

finally:
    # === SEGURO ANTI-FUGAS DE MEMORIA ===
    try:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn and conn.is_connected(): conn.close()
    except Exception:
        pass

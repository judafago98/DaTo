import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import datetime
import time
import uuid
import calendar
import os
import base64

# ==========================================
# 🛠️ AUTO-MIGRACIÓN ROBUSTA DE BASE DE DATOS (NIVEL ERP)
# ==========================================
def auto_fix_db(cursor, conn):
    # Asegurar que las columnas antiguas no den error "Truncated"
    try: cursor.execute("ALTER TABLE Pagos MODIFY COLUMN tipo_pago VARCHAR(255)"); conn.commit()
    except Exception: pass
    try: cursor.execute("ALTER TABLE Creditos MODIFY COLUMN estado_comision VARCHAR(255) DEFAULT 'No Aplica'"); conn.commit()
    except Exception: pass
    
    # 1. Cuentas Bancarias Dinámicas (Radar DIAN)
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Cuentas_Bancarias (id_cuenta INT AUTO_INCREMENT PRIMARY KEY, nombre_cuenta VARCHAR(255) UNIQUE)"); conn.commit()
    except Exception: pass
    cuentas_default = ["Efectivo - Caja Fija", "Nequi - Daniel", "Daviplata - Juan", "Llave - CARMACELL", "Llave - Fondo Suárez", "Bold"]
    for cta in cuentas_default:
        try: cursor.execute("INSERT IGNORE INTO Cuentas_Bancarias (nombre_cuenta) VALUES (%s)", (cta,)); conn.commit()
        except Exception: pass

    # 2. Clientes (Directorio Premium)
    cols_clientes = ["ADD COLUMN direccion VARCHAR(255)", "ADD COLUMN barrio VARCHAR(255)", "ADD COLUMN ciudad VARCHAR(255)", "ADD COLUMN correo VARCHAR(255)", "ADD COLUMN empresa VARCHAR(255)", "ADD COLUMN fecha_registro DATE"]
    for c in cols_clientes:
        try: cursor.execute(f"ALTER TABLE Clientes {c}"); conn.commit()
        except Exception: pass
    try: cursor.execute("UPDATE Clientes SET fecha_registro = CURDATE() WHERE fecha_registro IS NULL"); conn.commit()
    except Exception: pass
    
    # 3. Inventario y ROI
    cols_inv = ["ADD COLUMN cantidad INT DEFAULT 1", "ADD COLUMN color VARCHAR(100)", "ADD COLUMN fecha_compra DATE", "ADD COLUMN factura VARCHAR(100)", "ADD COLUMN tienda_proveedor VARCHAR(255)", "ADD COLUMN nit_proveedor VARCHAR(100)", "ADD COLUMN celular_proveedor VARCHAR(100)"]
    for c in cols_inv:
        try: cursor.execute(f"ALTER TABLE Inventario {c}"); conn.commit()
        except Exception: pass
    
    # 4. Proveedores y Cadenas (Gastos Operativos)
    cols_gastos = ["ADD COLUMN estado_pago VARCHAR(50) DEFAULT 'Pagado'", "ADD COLUMN vendedor VARCHAR(255)", "ADD COLUMN id_credito INT", "ADD COLUMN tipo_gasto VARCHAR(255) DEFAULT 'Gasto Operativo'"]
    for c in cols_gastos:
        try: cursor.execute(f"ALTER TABLE Gastos_Operativos {c}"); conn.commit()
        except Exception: pass

    # 5. Créditos, Pagos e Inversiones (Escudo Fiscal)
    cols_creditos = ["ADD COLUMN precio_venta DECIMAL(15,2) DEFAULT 0", "ADD COLUMN abono_inicial DECIMAL(15,2) DEFAULT 0", "ADD COLUMN valor_comision DECIMAL(15,2) DEFAULT 0", "ADD COLUMN asesor_comision VARCHAR(255)", "ADD COLUMN estado_comision VARCHAR(255) DEFAULT 'No Aplica'", "ADD COLUMN fecha_pago_comision DATE"]
    for c in cols_creditos:
        try: cursor.execute(f"ALTER TABLE Creditos {c}"); conn.commit()
        except Exception: pass

    try: cursor.execute("ALTER TABLE Pagos ADD COLUMN id_cuenta INT, ADD COLUMN motivo_ingreso VARCHAR(255) DEFAULT 'Pago Cuotas'"); conn.commit()
    except Exception: pass
    try: cursor.execute("ALTER TABLE Deudas_Fondeo ADD COLUMN id_cuenta INT, ADD COLUMN motivo_ingreso VARCHAR(255) DEFAULT 'Incremento inversión'"); conn.commit()
    except Exception: pass

    try: cursor.execute("CREATE TABLE IF NOT EXISTS Vendedores (id_vendedor INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) UNIQUE)"); conn.commit()
    except Exception: pass
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Creditos_Items (id INT AUTO_INCREMENT PRIMARY KEY, id_credito INT, imei VARCHAR(100))"); conn.commit()
    except Exception: pass

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DaTo | Tecnología con Respaldo", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# ==========================================
# 🎨 UI CORPORATIVA Y LIMPIA
# ==========================================
# ==========================================
# 🎨 UI CORPORATIVA (ERP PREMIUM)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* FORZAR TEMA CLARO ABSOLUTO EN TODA LA APP */
        :root, [data-theme="dark"] { color-scheme: light !important; }
        .stApp, header, .stApp > header { background-color: #F8FAFC !important; background-image: none !important; }

        /* TIPOGRAFÍA Y COLOR DE TEXTO GLOBAL */
        p, span, div, label, li, td, th { font-family: 'Outfit', sans-serif; color: #1E293B !important; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif; color: #0052D4 !important; font-weight: 700 !important; letter-spacing: -0.5px; }

        /* ÍCONOS DEL SISTEMA */
        .material-symbols-rounded, .material-icons, i, [data-testid="collapsedControl"] * {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important; color: #0052D4 !important;
        }
        
        /* PESTAÑAS (TABS) - REEMPLAZAR ROJO POR AZUL CORPORATIVO */
        button[data-baseweb="tab"] { color: #64748B !important; background: transparent !important; border-bottom: 2px solid transparent !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #0052D4 !important; border-bottom: 2px solid #0052D4 !important; }
        div[data-baseweb="tab-highlight"] { background-color: #0052D4 !important; display: none !important; } /* Oculta la línea roja nativa */
        
        /* MULTISELECT (ADIÓS ETIQUETAS ROJAS) */
        span[data-baseweb="tag"] { background-color: #E0F2FE !important; color: #0369A1 !important; border: 1px solid #7DD3FC !important; border-radius: 6px !important; padding: 4px 12px !important; }
        span[data-baseweb="tag"] span { color: #0369A1 !important; font-weight: 600 !important; }
        span[data-baseweb="tag"] svg { fill: #0369A1 !important; }

        /* ELIMINAR BORDES ROJOS EN INPUTS Y LISTAS DESPLEGABLES */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { border: 1px solid #CBD5E1 !important; background-color: #FFFFFF !important; transition: 0.2s; border-radius: 8px !important; }
        div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div { border-color: #0052D4 !important; box-shadow: 0 0 0 2px rgba(0, 82, 212, 0.2) !important; }
        
        /* REPARACIÓN DE LAS LISTAS DESPLEGABLES NEGRAS (POPOVERS) */
        div[data-baseweb="popover"], ul[role="listbox"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important; }
        li[role="option"] { background-color: #FFFFFF !important; color: #1E293B !important; padding: 10px 15px !important; transition: 0.1s; }
        li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #F1F5F9 !important; color: #0052D4 !important; font-weight: 600 !important; }

        /* TOGGLES */
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div { background-color: #CBD5E1 !important; }
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div[aria-checked="true"] { background-color: #0052D4 !important; }

        /* BOTONES PREMIUM (Call to Action) */
        .stButton > button {
            background: linear-gradient(135deg, #0052D4 0%, #003366 100%) !important; color: #FFFFFF !important; border: none !important;
            border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s; width: 100% !important; box-shadow: 0 4px 10px rgba(0, 82, 212, 0.3) !important; padding: 0.5rem 1rem !important;
        }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0, 82, 212, 0.4) !important; }
        .stButton > button:active { transform: translateY(0); box-shadow: none !important; }
        
        [data-testid="stNumberInput"] button { background: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; color: #0052D4 !important; border-radius: 6px !important; box-shadow: none !important;}

        /* CAJAS Y TARJETAS (LOGIN Y FORMULARIOS) */
        div[data-testid="stForm"], .card-panel {
            background-color: #FFFFFF !important; border: 1px solid #F1F5F9 !important; border-radius: 16px !important; box-shadow: 0 8px 30px rgba(0,0,0,0.04) !important; padding: 25px !important;
        }

        /* MENÚ LATERAL MEJORADO */
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label div[data-baseweb="radio"], [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child, [data-testid="stSidebar"] [role="radiogroup"] label > span:first-child { display: none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label { background: #F8FAFC !important; border: 1px solid transparent !important; border-radius: 10px !important; padding: 12px 15px !important; margin: 6px 15px !important; cursor: pointer !important; transition: 0.2s; }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #E2E8F0 !important; transform: translateX(3px); }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] { background: #EFF6FF !important; border-left: 4px solid #0052D4 !important; transform: translateX(3px); box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] div[dir="auto"] { color: #0052D4 !important; font-weight: 700 !important; }
        
        /* EXPANDER CARDS (HOJAS DE VIDA CLIENTES) */
        [data-testid="stExpander"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important; margin-bottom: 10px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; }
        [data-testid="stExpander"] summary p { font-size: 1.1rem !important; font-weight: 600 !important; color: #0052D4 !important; }
    </style>
""", unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return None

def renderizar_logo(es_sidebar=False):
    b64_img = get_base64_image("logo2.png")
    if not b64_img: b64_img = get_base64_image("logo.png")
    width = "180px" if es_sidebar else "300px"
    img_html = f'<img src="data:image/png;base64,{b64_img}" style="max-width: {width}; height: auto; display: block; margin: 0 auto;">' if b64_img else f"<h1 style='color: #0052D4; font-weight: 800; text-align: center; margin: 0;'>⚡ DaTo</h1><p style='text-align: center; color: #64748B; margin: 0;'>Tecnología con respaldo</p>"
    st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; padding: 20px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);'><div>{img_html}</div></div>", unsafe_allow_html=True)

# ==========================================
# 🛡️ ALGORITMOS FINANCIEROS
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
    if val in ['Pagado', 'Pagada', 'Completado']: return 'background-color: #ECFDF5; color: #047857; font-weight: 600;'
    elif val in ['Activo', 'Pendiente']: return 'background-color: #EFF6FF; color: #1D4ED8; font-weight: 600;'
    elif val in ['Disponible']: return 'background-color: #F0FDF4; color: #059669; font-weight: 600;'
    elif val in ['Vendido']: return 'background-color: #F1F5F9; color: #475569; font-weight: 600;'
    return ''

def color_estado_cuota(val):
    if 'Pagada' in val: return 'background-color: #ECFDF5; color: #047857; font-weight: 600;'
    elif 'Parcial' in val: return 'background-color: #EFF6FF; color: #2563EB; font-weight: 600;'
    else: return 'color: #DC2626; font-weight: 500;'

def color_ganancia_real(val):
    if '-' in str(val): return 'color: #DC2626; font-weight: 600;'
    return 'color: #059669; font-weight: 600;'

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
                est, pagado_acum = 'Pagada', pagado_acum - esperado
                f_pago_mostrar = pagos_hist[idx]['fecha_pago'].strftime('%Y-%m-%d') if idx < len(pagos_hist) else '---'
            elif pagado_acum > 0: 
                est, pagado_acum = f'Abono Parcial ({fmt_cop(pagado_acum)})', 0
                f_pago_mostrar = pagos_hist[idx]['fecha_pago'].strftime('%Y-%m-%d') if idx < len(pagos_hist) else '---'
            else: 
                est, f_pago_mostrar = 'Pendiente', '---'
            plan.append({'Cuota': f"Número {c['numero_cuota']}", 'Vencimiento Límite': c['fecha_vencimiento'], 'Valor Exigido': fmt_cop(esperado), 'Estado Actual': est, 'Fecha de Pago': f_pago_mostrar})
    else:
        plazo, valor, f_base = int(cred['plazo_meses']), float(cred['valor_cuota'] or 0), cred['fecha_primera_cuota']
        for i in range(1, plazo + 1):
            if not f_base: break
            f_venc = sumar_meses_exactos(f_base, i - 1)
            esperado = valor
            if pagado_acum >= esperado: 
                est, pagado_acum = 'Pagada', pagado_acum - esperado
                f_pago_mostrar = pagos_hist[i-1]['fecha_pago'].strftime('%Y-%m-%d') if (i-1) < len(pagos_hist) else '---'
            elif pagado_acum > 0: 
                est, pagado_acum = f'Abono Parcial ({fmt_cop(pagado_acum)})', 0
                f_pago_mostrar = pagos_hist[i-1]['fecha_pago'].strftime('%Y-%m-%d') if (i-1) < len(pagos_hist) else '---'
            else: 
                est, f_pago_mostrar = 'Pendiente', '---'
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
CIUDADES_COLOMBIA = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bucaramanga", "Cúcuta", "Pereira", "Santa Marta", "Ibagué", "Pasto", "Manizales", "Neiva", "Villavicencio", "Armenia", "Valledupar", "Montería", "Sincelejo", "Popayán", "Tunja", "Riohacha", "Florencia", "Quibdó", "Arauca", "Yopal", "Leticia", "San Andrés", "Otra..."]

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
    #auto_fix_db(cursor, conn)
except Exception as e:
    st.error(f"🌐 Servidor de base de datos inalcanzable. Detalle: {e}")
    st.stop()

# Cargar Cuentas Bancarias Dinámicas
cursor.execute("SELECT id_cuenta, nombre_cuenta FROM Cuentas_Bancarias")
lista_cuentas = cursor.fetchall()
opc_cuentas = {c['nombre_cuenta']: c['id_cuenta'] for c in lista_cuentas}

# ==========================================
# LOGIN DUAL
# ==========================================
# ==========================================
# 🔐 LOGIN DUAL (UI REDISEÑADA)
# ==========================================
try:
    if 'logeado' not in st.session_state: st.session_state['logeado'] = False
    if 'id_usuario' not in st.session_state: st.session_state['id_usuario'] = None
    if 'nombre_usuario' not in st.session_state: st.session_state['nombre_usuario'] = None
    if 'rol' not in st.session_state: st.session_state['rol'] = None

    if not st.session_state['logeado']:
        # Centrado perfecto para pantallas anchas
        _, col_centro, _ = st.columns([1.5, 2.5, 1.5], gap="large")
        
        with col_centro:
            st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
            renderizar_logo(es_sidebar=False)
            st.markdown("<br>", unsafe_allow_html=True)
            
            tab_cliente, tab_admin = st.tabs(["👤 Portal de Clientes", "💼 Acceso Equipo DaTo"])

            with tab_cliente:
                with st.form("form_login_cliente"):
                    st.markdown("<h2 style='text-align: center; color: #0052D4; margin-bottom: 5px;'>Bienvenido a DaTo</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 25px;'>Consulta tu estado de cuenta y descargas de recibos.</p>", unsafe_allow_html=True)
                    cedula_cliente = st.text_input("Ingresa tu Número de Documento (C.C.)", placeholder="Ej: 1032501660")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Consultar Estado de Cuenta", width='stretch'):
                        cursor.execute("SELECT * FROM Clientes WHERE documento = %s", (cedula_cliente,))
                        cli_db = cursor.fetchone()
                        if cli_db:
                            st.session_state.update({'logeado': True, 'rol': 'Cliente', 'id_cliente': cli_db['id_cliente'], 'nombre_cliente': cli_db['nombre_completo']})
                            st.rerun()
                        else: st.error("No encontramos compras registradas con esta cédula en DaTo.")

            with tab_admin:
                with st.form("form_login"):
                    st.markdown("<h2 style='text-align: center; color: #0052D4; margin-bottom: 5px;'>Acceso Corporativo</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 25px;'>Ingrese sus credenciales administrativas.</p>", unsafe_allow_html=True)
                    usuario_input = st.text_input("Usuario de Sistema")
                    password_input = st.text_input("Contraseña de Acceso", type="password")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Iniciar Sesión", width='stretch'):
                        cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                        usuario_db = cursor.fetchone()
                        if usuario_db:
                            st.session_state.update({'logeado': True, 'id_usuario': usuario_db['id_usuario'], 'nombre_usuario': usuario_db['nombre_completo'], 'rol': usuario_db['rol']})
                            st.rerun()
                        else: st.error("Usuario o contraseña incorrectos. Verifica tus credenciales.")

    # ==========================================
    # 📱 VISTA EXCLUSIVA PARA EL CLIENTE
    # ==========================================
    elif st.session_state['rol'] == 'Cliente':
        st.markdown(f"<h1 style='text-align:center;'>👋 ¡Hola, {st.session_state['nombre_cliente'].split()[0]}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748B; font-size: 1.1rem;'>Este es el resumen de tus productos activos con nosotros.</p><br>", unsafe_allow_html=True)
        
        cursor.execute("SELECT c.id_credito, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, c.tasa_interes_mensual FROM Creditos c WHERE c.id_cliente = %s AND c.estado = 'Activo'", (st.session_state['id_cliente'],))
        creditos_cliente = cursor.fetchall()
        
        if not creditos_cliente:
            st.success("¡Felicidades! Actualmente estás a Paz y Salvo con DaTo.")
            st.markdown("""<div style="text-align:center;"><img src="https://media.giphy.com/media/3o7aD2saalEvTehEX2/giphy.gif" style="max-width:300px; border-radius:15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"></div>""", unsafe_allow_html=True)
        else:
            for cred in creditos_cliente:
                cursor.execute("SELECT i.marca, i.modelo FROM Creditos_Items ci JOIN Inventario i ON ci.imei = i.imei WHERE ci.id_credito = %s", (cred['id_credito'],))
                equipos = cursor.fetchall()
                if not equipos: 
                    cursor.execute("SELECT i.marca, i.modelo FROM Creditos c JOIN Inventario i ON c.imei = i.imei WHERE c.id_credito = %s", (cred['id_credito'],))
                    equipos = cursor.fetchall()
                nombres_equipos = " + ".join([f"{e['marca']} {e['modelo']}" for e in equipos])
                
                cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (cred['id_credito'],))
                cap_pag = cursor.fetchone()['cap'] or 0
                saldo_actual = float(cred['monto_financiado']) - float(cap_pag)
                pago_total = saldo_actual + (saldo_actual * float(cred['tasa_interes_mensual']))
                
                st.markdown(f"""
                <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 25px; margin-bottom: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                    <h3 style='text-align:center; color:#0052D4;'>📱 {nombres_equipos}</h3>
                    <div style='display:flex; justify-content:space-around; margin-top:20px; flex-wrap: wrap; gap: 20px;'>
                        <div style='text-align:center; background: #F8FAFC; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; min-width: 200px;'>
                            <p style='color:#64748B; margin-bottom:5px; font-weight: 600;'>Cuota Mensual</p>
                            <h2 style='color:#0052D4; margin:0;'>{fmt_cop(cred['valor_cuota'])}</h2>
                        </div>
                        <div style='text-align:center; background: #ECFDF5; padding: 20px; border-radius: 12px; min-width: 200px; border: 1px solid #A7F3D0;'>
                            <p style='color:#047857; margin-bottom:5px; font-weight: 600;'>Pago Total para Liquidar Hoy</p>
                            <h2 style='color:#10B981; margin:0;'>{fmt_cop(pago_total)}</h2>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🧾 Historial de tus pagos")
                cursor.execute("SELECT fecha_pago, monto_recibido FROM Pagos WHERE id_credito = %s ORDER BY fecha_pago DESC", (cred['id_credito'],))
                pagos = cursor.fetchall()
                if pagos:
                    df_p = pd.DataFrame(pagos)
                    df_p.columns = ['Fecha del Pago', 'Valor Abonado']
                    df_p['Valor Abonado'] = df_p['Valor Abonado'].apply(fmt_cop)
                    st.dataframe(df_p, width='stretch')
                else: st.info("Aún no tienes pagos registrados en este contrato.")

        if st.button("Cerrar Sesión", type="primary"):
            st.session_state['logeado'] = False; st.rerun()

    # ==========================================
    # 💼 VISTA DE ADMINISTRADOR
    # ==========================================
    else:
        es_admin = st.session_state['rol'] in ['Admin', 'Administrador']
        
        MODULOS_TOTALES = {
            "🔮 Cotizador y Simulación": "simulador",
            "📦 Gestión de Inventario": "inventario",
            "👥 Directorio de Clientes": "clientes",
            "📝 Registro de Ventas": "ventas",
            "💰 Caja y Recaudos": "pagos",
            "⏰ Cartera y Vencimientos": "vencimientos",
            "📱 Notificaciones a Clientes": "notificar",
            "📜 Historial y Anulaciones": "historial",
            "💸 Egresos y Proveedores": "egresos",
            "📈 Socios e Inversores": "flujo",
            "📊 Reportes (Radar DIAN)": "reportes",
            "⚙️ Configuración de Usuarios": "config_roles"
        }

        with st.sidebar:
            renderizar_logo(es_sidebar=True)
        
            st.sidebar.markdown(f"""
                <div style='padding: 15px; background: #F8FAFC; border-radius: 12px; border: 1px solid #CBD5E1; margin-bottom: 20px; text-align: center;'>
                    <b style='color:#1E293B; font-size: 15px;'>{st.session_state['nombre_usuario']}</b><br>
                    <span style='color:#0052D4; font-size: 12px; font-weight: 700; text-transform: uppercase;'>{str(st.session_state['rol'])}</span>
                </div>
            """, unsafe_allow_html=True)
            
            menu_map = {"🏠 Panel Principal": "inicio"} 
            if es_admin: menu_map.update(MODULOS_TOTALES)
            else:
                cursor.execute("SELECT m.nombre_interno FROM Modulos_Sistema m JOIN Permisos_Rol p ON m.id_modulo = p.id_modulo JOIN Roles r ON p.id_role = r.id_role WHERE r.nombre_rol = %s", (st.session_state['rol'],))
                for m in cursor.fetchall(): 
                    for k, v in MODULOS_TOTALES.items():
                        if v == m['nombre_interno']: menu_map[k] = m['nombre_interno']
            
            menu_seleccionado_texto = st.sidebar.radio("Navegación", list(menu_map.keys()), label_visibility="collapsed")
            menu_seleccionado = menu_map[menu_seleccionado_texto]
            
            st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
            if st.sidebar.button("Cerrar Sesión", width='stretch'): st.session_state['logeado'] = False; st.rerun()

        if menu_seleccionado == "inicio":
            st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                    <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 25px; margin-bottom: 0; color: #1E293B;'>HOLA, <span style='color: #0052D4;'>{st.session_state['nombre_usuario'].split(" ")[0].upper()}</span></h1>
                    <p style='color: #64748B; font-size: 1.1rem; font-weight: 400; margin-top: 10px;'>Es hora de poner a trabajar el ecosistema DaTo.</p>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "simulador":
            st.markdown("<h2>🔮 Cotizador y Simulación</h2>", unsafe_allow_html=True)
            tab_sim, tab_paz = st.tabs(["📊 Simular Cuotas", "🤝 Liquidación Paz y Salvo"])
            
            with tab_sim:
                st.markdown("<br>", unsafe_allow_html=True)
                modo_cliente = st.toggle("📸 Activar Vista Cliente (Oculta información sensible)")
                if 'tasa_simulador' not in st.session_state: st.session_state['tasa_simulador'] = 3.0
                    
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sim_precio = st.number_input("Valor del Producto ($)", min_value=0, step=10000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #0052D4; font-weight: 600; font-size: 13px; margin-top: -10px; margin-bottom: 15px;'>{fmt_cop(sim_precio)}</div>", unsafe_allow_html=True)
                    sim_abono = st.number_input("Abono Inicial ($)", min_value=0, step=10000, value=0)
                    st.markdown(f"<div style='text-align: right; color: #0052D4; font-weight: 600; font-size: 13px; margin-top: -10px;'>{fmt_cop(sim_abono)}</div>", unsafe_allow_html=True)
                with col_s2:
                    sim_plazo = st.number_input("Meses a Financiar", min_value=1, max_value=72, step=1, value=6)
                    if not modo_cliente:
                        idx_tasa = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0].index(st.session_state['tasa_simulador']) if st.session_state['tasa_simulador'] in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0] else 3
                        sim_tasa = st.selectbox("Tasa de Interés Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=idx_tasa)
                        st.session_state['tasa_simulador'] = sim_tasa
                    else: sim_tasa = st.session_state['tasa_simulador']
                    
                sim_capital = sim_precio - sim_abono
                if sim_capital > 0:
                    i_m = sim_tasa / 100.0
                    sim_cuota = sim_capital * (i_m * (1 + i_m)**sim_plazo) / (((1 + i_m)**sim_plazo) - 1) if sim_tasa > 0 else sim_capital / sim_plazo
                    st.success(f"🔹 **Proyección de Cuota Mensual:** {fmt_cop(int(round(sim_cuota)))}")
                elif sim_precio > 0: st.info("El abono cubre el total del equipo.")

            with tab_paz:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.documento, i.modelo, c.monto_financiado, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
                creditos_act = cursor.fetchall()
                if not creditos_act: st.info("No hay créditos activos pendientes.")
                else:
                    opc_paz = {f"{c['documento']} | {c['nombre_completo']} ({c['modelo']})": c for c in creditos_act}
                    sel_paz = st.selectbox("Seleccionar Cliente:", list(opc_paz.keys()), index=None, placeholder="Buscar cliente...")
                    
                    if sel_paz:
                        datos_paz = opc_paz[sel_paz]
                        cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (datos_paz['id_credito'],))
                        res = cursor.fetchone()
                        saldo_capital = float(datos_paz['monto_financiado']) - float(res['cap'] if res and res['cap'] else 0.0)
                        interes_mes = saldo_capital * float(datos_paz['tasa_interes_mensual'])
                        
                        st.markdown(f"""
                        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 20px; margin-top: 20px;">
                            <h3 style="color:#047857; margin:0; font-weight: 600;">VALOR TOTAL (PAZ Y SALVO HOY)</h3>
                            <h1 style="color:#10B981; font-size: 3.5rem; font-weight: 800; margin: 10px 0;">{fmt_cop(saldo_capital + interes_mes)}</h1>
                            <p style="color:#64748B; font-size: 14px; margin:0;">Saldo a Capital ({fmt_cop(saldo_capital)}) + Interés de este Mes ({fmt_cop(interes_mes)})</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.dataframe(generar_plan_pagos_real(datos_paz['id_credito'], cursor).style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "inventario":
            st.markdown("<h2>Gestión de Inventario 📦</h2>", unsafe_allow_html=True)
            tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Equipos Disponibles", "📥 Ingresar Nuevos Equipos", "📜 Historial de Ventas"])
            
            with tab_inv1:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT i.imei AS 'Serial/IMEI', 
                           i.tipo_ingreso AS 'Condición',
                           i.categoria AS 'Categoría', 
                           i.marca AS 'Marca', 
                           i.modelo AS 'Modelo', 
                           i.color AS 'Color', 
                           b.nombre_bolsa AS 'Fondeado por',
                           i.cantidad AS 'Unidades', 
                           i.costo_adquisicion AS 'Costo Unidad', 
                           i.precio_venta_contado AS 'Precio Sugerido' 
                    FROM Inventario i
                    LEFT JOIN Bolsas_Capital b ON i.id_bolsa = b.id_bolsa
                    WHERE i.estado = 'Disponible'
                """)
                df_inventario = pd.DataFrame(cursor.fetchall())
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📦 Productos Físicos Diferentes", f"{len(df_inventario)}")
                
                if not df_inventario.empty:
                    c2.metric("💰 Dinero Invertido en Stock", fmt_cop(sum([float(r['Costo Unidad']) * int(r['Unidades']) for _, r in df_inventario.iterrows()])))
                    c3.metric("💎 Proyección Venta Sugerida", fmt_cop(sum([float(r['Precio Sugerido'] or 0) * int(r['Unidades']) for _, r in df_inventario.iterrows()])))
                    
                    df_inventario['Costo Unidad'] = df_inventario['Costo Unidad'].apply(fmt_cop)
                    df_inventario['Precio Sugerido'] = df_inventario['Precio Sugerido'].apply(lambda x: fmt_cop(x) if x else 'N/A')
                    
                    # Colores automáticos según el estado del equipo
                    def color_condicion(val):
                        if val == 'Nuevo': return 'color: #059669; font-weight: 600;'
                        if val == 'Retoma': return 'color: #D97706; font-weight: 600;'
                        if val == 'Usado': return 'color: #2563EB; font-weight: 600;'
                        return ''
                        
                    st.dataframe(df_inventario.style.map(color_condicion, subset=['Condición']), width='stretch')
                else: 
                    st.markdown("""<div style="text-align:center;"><img src="https://media.giphy.com/media/3o7aD2saalEvTehEX2/giphy.gif" style="max-width:250px; border-radius:15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"><br><h3 style="color:#64748B;">La bodega está vacía.</h3></div>""", unsafe_allow_html=True)

            with tab_inv2:
                st.markdown("<br>", unsafe_allow_html=True)
                # Bolsas/Bolsillos representan el capital u origen de la inversión
                cursor.execute("SELECT id_bolsa, nombre_bolsa, saldo_actual FROM Bolsas_Capital")
                opc_bolsas = {f"Bolsillo de Inversión: {b['nombre_bolsa']} (Disponible: {fmt_cop(b['saldo_actual'])})": b for b in cursor.fetchall()}

                c1, c2 = st.columns(2)
                with c1: cat_sel = st.selectbox("Categoría", list(CATALOGO.keys()), index=None, placeholder="Seleccione Categoría...")
                
                if cat_sel:
                    with c2: marca_sel = st.selectbox("Marca", list(CATALOGO[cat_sel].keys()), index=None, placeholder="Seleccione Marca...")
                    if marca_sel:
                        c3, c4 = st.columns(2)
                        with c3:
                            marca_fin = st.text_input("Ingresar Marca Manual:") if marca_sel == "Otra Marca..." else marca_sel
                            mod = st.selectbox("Modelo", CATALOGO[cat_sel][marca_sel], index=None, placeholder="Seleccione Modelo...")
                            if mod: mod_fin = st.text_input("Ingresar Modelo Manual:") if mod in ["Otro...", "Escribir manual..."] else mod
                        with c4:
                            if mod:
                                opc_cap = CAPACIDADES_PC if "Cómputo" in cat_sel or "💻" in cat_sel else (CAPACIDADES_ELECTRO if "Electrónica" in cat_sel or "📺" in cat_sel else CAPACIDADES_MOVILES)
                                cap = st.selectbox("Capacidad", opc_cap, index=None, placeholder="Seleccione Capacidad...")
                                if cap: cap_fin = "" if cap == "No Aplica" else (st.text_input("Capacidad Manual:") if cap == "Escribir manual..." else cap)

                        if mod and cap:
                            with st.form("f_inv"):
                                st.markdown("#### Datos de la Compra")
                                l1, l2, l3, l4 = st.columns(4)
                                cantidad = l1.number_input("Cantidad a Ingresar", min_value=1, value=1)
                                color = l2.text_input("Color")
                                imei_in = l3.text_input("IMEI (Déjelo en blanco si es lote general)")
                                cond = l4.selectbox("Estado del equipo", ["Nuevo", "Usado", "Retoma"])
                                
                                st.markdown("#### Proveedor")
                                p1, p2, p3, p4 = st.columns(4)
                                proveedor = p1.text_input("Tienda / Proveedor")
                                nit = p2.text_input("NIT Proveedor")
                                cel_prov = p3.text_input("Celular Proveedor")
                                factura = p4.text_input("Factura de Compra")

                                c5, c6, c7 = st.columns(3)
                                with c5: bolsa = st.selectbox("¿Con la plata de quién se compró?", options=list(opc_bolsas.keys()), index=None)
                                with c6: costo = st.number_input("Costo de Compra (Por 1 Unidad)", min_value=0, step=10000, value=0)
                                with c7: precio_venta = st.number_input("Precio Sugerido Venta", min_value=0, step=10000, value=0)

                                if st.form_submit_button("Guardar en Inventario", width='stretch') and bolsa:
                                    dat_b = opc_bolsas[bolsa]
                                    costo_total = costo * cantidad
                                    if costo_total > float(dat_b['saldo_actual']): st.error("Ese bolsillo de inversión no tiene suficiente dinero para pagar esta mercancía.")
                                    elif not mod_fin: st.warning("El modelo es obligatorio.")
                                    else:
                                        for _ in range(cantidad):
                                            imei_final = imei_in if (cantidad == 1 and imei_in) else f"SYS-{str(uuid.uuid4())[:8].upper()}"
                                            cursor.execute("""
                                                INSERT INTO Inventario (imei, categoria, marca, modelo, tipo_ingreso, id_bolsa, costo_adquisicion, precio_venta_contado, estado, id_usuario_registro, cantidad, color, factura, tienda_proveedor, nit_proveedor, celular_proveedor, fecha_compra) 
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Disponible', %s, 1, %s, %s, %s, %s, %s, %s)
                                            """, (imei_final, cat_sel.split(" ")[1] if " " in cat_sel else cat_sel, marca_fin, f"{mod_fin} {cap_fin}".strip(), cond, dat_b['id_bolsa'], costo, precio_venta, st.session_state['id_usuario'], color, factura, proveedor, nit, cel_prov, datetime.date.today()))
                                        cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s WHERE id_bolsa = %s", (costo_total, dat_b['id_bolsa']))
                                        conn.commit(); st.toast('Equipos agregados con éxito.'); time.sleep(1.5); st.rerun()

            with tab_inv3:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT i.imei AS 'Serial/IMEI', CONCAT(i.marca, ' ', i.modelo) AS 'Equipo', i.costo_adquisicion AS 'Costo Real', IFNULL(cr.precio_venta, 0) AS 'Precio de Venta', i.estado AS 'Estado', IFNULL(c.nombre_completo, 'Bodega') AS 'Cliente'
                    FROM Inventario i LEFT JOIN Creditos_Items ci ON i.imei = ci.imei LEFT JOIN Creditos cr ON ci.id_credito = cr.id_credito LEFT JOIN Clientes c ON cr.id_cliente = c.id_cliente ORDER BY i.estado ASC
                """)
                df_hist = pd.DataFrame(cursor.fetchall())
                if not df_hist.empty:
                    df_hist['Costo Real'] = df_hist['Costo Real'].apply(fmt_cop)
                    df_hist['Precio de Venta'] = df_hist['Precio de Venta'].apply(lambda x: fmt_cop(x) if x > 0 else 'N/A')
                    st.dataframe(df_hist.style.map(color_estado, subset=['Estado']), width='stretch')
                else: st.info("Registro vacío.")

        elif menu_seleccionado == "clientes":
            st.markdown("<h2>Directorio de Clientes 👥</h2>", unsafe_allow_html=True)
            tab_ver, tab_nuevo, tab_editar = st.tabs(["📋 Ver Clientes (Hojas de Vida)", "➕ Nuevo Cliente", "✏️ Editar Perfil"])
            
            with tab_ver:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT * FROM Clientes ORDER BY fecha_registro DESC")
                clientes_db = cursor.fetchall()
                if not clientes_db:
                    st.info("No hay clientes registrados en el sistema.")
                else:
                    st.write("Haz clic en cualquier cliente para desplegar su historia financiera.")
                    for c in clientes_db:
                        # Calcular LTV y Créditos
                        cursor.execute("SELECT COUNT(id_credito) as activos FROM Creditos WHERE id_cliente = %s AND estado = 'Activo'", (c['id_cliente'],))
                        activos = cursor.fetchone()['activos']
                        cursor.execute("SELECT SUM(monto_recibido) as pagado FROM Pagos p JOIN Creditos cr ON p.id_credito = cr.id_credito WHERE cr.id_cliente = %s", (c['id_cliente'],))
                        res_p = cursor.fetchone()
                        ltv = float(res_p['pagado'] or 0)
                        
                        estado_ui = "🟢 Activo" if activos > 0 else "⚪ Sin créditos"
                        
                        with st.expander(f"{estado_ui} | 👤 {c['nombre_completo']} - C.C. {c['documento']}"):
                            st.markdown(f"""
                            <div style='display:flex; justify-content:space-between; margin-bottom:15px; flex-wrap:wrap; gap:10px;'>
                                <div style='background:#F1F5F9; padding:15px; border-radius:8px; flex:1; min-width:150px;'>
                                    <p style='color:#64748B; font-size:12px; margin:0;'>Fecha de Registro</p>
                                    <h4 style='margin:0; color:#1E293B;'>{c['fecha_registro']}</h4>
                                </div>
                                <div style='background:#F1F5F9; padding:15px; border-radius:8px; flex:1; min-width:150px;'>
                                    <p style='color:#64748B; font-size:12px; margin:0;'>Teléfono de Contacto</p>
                                    <h4 style='margin:0; color:#1E293B;'>{c['telefono'] if c['telefono'] else 'N/A'}</h4>
                                </div>
                                <div style='background:#E0F2FE; padding:15px; border-radius:8px; flex:1; border: 1px solid #BAE6FD; min-width:150px;'>
                                    <p style='color:#0369A1; font-size:12px; margin:0;'>Valor Histórico (LTV)</p>
                                    <h4 style='margin:0; color:#0284C7;'>{fmt_cop(ltv)}</h4>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("**📜 Historial de Pagos Recibidos**")
                            cursor.execute("SELECT p.fecha_pago AS 'Fecha', p.monto_recibido AS 'Valor Pagado', p.tipo_pago AS 'Concepto', cb.nombre_cuenta AS 'Cuenta Destino' FROM Pagos p JOIN Creditos cr ON p.id_credito = cr.id_credito LEFT JOIN Cuentas_Bancarias cb ON p.id_cuenta = cb.id_cuenta WHERE cr.id_cliente = %s ORDER BY p.fecha_pago DESC", (c['id_cliente'],))
                            hist_pagos = cursor.fetchall()
                            if hist_pagos:
                                df_hp = pd.DataFrame(hist_pagos)
                                df_hp['Valor Pagado'] = df_hp['Valor Pagado'].apply(fmt_cop)
                                st.dataframe(df_hp, width='stretch')
                            else:
                                st.write("El cliente no ha realizado pagos en el sistema.")

            with tab_nuevo:
                with st.form("f_cli"):
                    st.subheader("Crear Perfil de Cliente")
                    c1, c2, c3 = st.columns(3)
                    doc = c1.text_input("Número de Cédula / ID Consecutivo")
                    nom = c2.text_input("Nombre Completo / Temporal")
                    tel = c3.text_input("Número Celular")
                    
                    c4, c5, c6 = st.columns(3)
                    correo = c4.text_input("Correo Electrónico")
                    ciudad_sel = c5.selectbox("Ciudad", CIUDADES_COLOMBIA, index=0)
                    ciudad = c5.text_input("Especifique ciudad:") if ciudad_sel == "Otra..." else ciudad_sel
                    barrio = c6.text_input("Barrio")
                    
                    c7, c8 = st.columns(2)
                    direccion = c7.text_input("Dirección de Residencia")
                    empresa = c8.text_input("Empresa o Negocio donde labora")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("Guardar Nuevo Cliente", width='stretch'):
                        if doc and nom:
                            try:
                                cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, direccion, barrio, ciudad, correo, empresa, fecha_registro, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), %s)", 
                                            (doc, nom, tel, direccion, barrio, ciudad, correo, empresa, st.session_state['id_usuario']))
                                conn.commit(); st.toast("Cliente guardado exitosamente."); time.sleep(1); st.rerun()
                            except mysql.connector.Error: st.error("Ya existe un cliente con esta cédula.")
                        else: st.warning("La cédula y el nombre son obligatorios.")
            
            with tab_editar:
                if clientes_db:
                    opc_edit_cli = {f"{c['documento']} - {c['nombre_completo']}": c for c in clientes_db}
                    cli_a_editar = st.selectbox("Seleccione el cliente a actualizar:", list(opc_edit_cli.keys()), index=None)
                    
                    if cli_a_editar:
                        dat_c = opc_edit_cli[cli_a_editar]
                        with st.form("f_edit_cli"):
                            st.write(f"Actualizando datos del ID en sistema: **{dat_c['id_cliente']}**")
                            e_doc = st.text_input("Número de Cédula / Documento", value=dat_c['documento'])
                            e_nom = st.text_input("Nombre Completo", value=dat_c['nombre_completo'])
                            e_tel = st.text_input("Celular", value=dat_c['telefono'] if dat_c['telefono'] else "")
                            e_cor = st.text_input("Correo", value=dat_c['correo'] if dat_c['correo'] else "")
                            idx_c = CIUDADES_COLOMBIA.index(dat_c['ciudad']) if dat_c['ciudad'] in CIUDADES_COLOMBIA else len(CIUDADES_COLOMBIA)-1
                            e_ciu_sel = st.selectbox("Ciudad", CIUDADES_COLOMBIA, index=idx_c)
                            e_ciu = st.text_input("Especifique la ciudad", value=dat_c['ciudad']) if e_ciu_sel == "Otra..." else e_ciu_sel
                            e_bar = st.text_input("Barrio", value=dat_c['barrio'] if dat_c['barrio'] else "")
                            e_dir = st.text_input("Dirección", value=dat_c['direccion'] if dat_c['direccion'] else "")
                            e_emp = st.text_input("Trabajo / Empresa", value=dat_c['empresa'] if dat_c['empresa'] else "")
                            
                            if st.form_submit_button("Actualizar Datos en DB", width='stretch'):
                                try:
                                    cursor.execute("""
                                        UPDATE Clientes SET documento=%s, nombre_completo=%s, telefono=%s, correo=%s, ciudad=%s, barrio=%s, direccion=%s, empresa=%s WHERE id_cliente=%s
                                    """, (e_doc, e_nom, e_tel, e_cor, e_ciu, e_bar, e_dir, e_emp, dat_c['id_cliente']))
                                    conn.commit(); st.toast("Datos actualizados."); time.sleep(1); st.rerun()
                                except mysql.connector.Error: st.error("Error: Esa cédula ya está registrada a nombre de otro cliente.")

        elif menu_seleccionado == "ventas":
            st.markdown("<h2>Registro de Ventas 📝</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
            clientes = cursor.fetchall()
            cursor.execute("SELECT imei, categoria, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
            inventario = cursor.fetchall()
            cursor.execute("SELECT nombre FROM Vendedores")
            vendedores = [v['nombre'] for v in cursor.fetchall()]
            
            if not clientes: st.error("⚠️ **ALERTA:** No tienes ningún cliente registrado. Ve a 'Directorio de Clientes' y crea uno.")
            elif not inventario: st.error("⚠️ **ALERTA:** La bodega está vacía. Ingresa inventario para poder vender.")
            else:
                opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                opc_eq = {f"[{e['categoria']}] {e['marca']} {e['modelo']} (Cod: {e['imei']})": e['imei'] for e in inventario}
                
                tipo_v = st.selectbox("Tipo de Venta:", ["Crédito Financiado a Cuotas", "Plan Separé (Sin Interés)", "Venta de Contado"], index=None, placeholder="Seleccione modalidad...")
                st.divider()
                
                if tipo_v:
                    st.markdown("#### Selección de Cliente y Productos")
                    cliente_sel = st.selectbox("Seleccionar Cliente", list(opc_cli.keys()))
                    equipos_sel = st.multiselect("Selecciona uno o más equipos de la bodega:", list(opc_eq.keys()))
                    
                    if equipos_sel:
                        st.markdown("<div style='background: #E0F2FE; border-left: 4px solid #0052D4; padding: 15px; border-radius: 8px; margin-bottom: 20px;'><p style='color: #0052D4; font-weight: bold; margin-bottom: 5px;'>🛒 Equipos en esta factura:</p>", unsafe_allow_html=True)
                        for eq in equipos_sel: st.markdown(f"<span style='color: #0369A1;'>- ✅ {eq}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("#### Tiempos del Crédito", unsafe_allow_html=True)
                    c_f1, c_f2 = st.columns(2)
                    with c_f1: fecha_venta = st.date_input("Fecha de Venta", value=datetime.date.today())
                    with c_f2: f_cuota = st.date_input("Fecha de la Primera Cuota", value=sumar_meses_exactos(fecha_venta, 1))

                    c3, c4 = st.columns(2)
                    c_pers, c_fija = [], 0
                    p_final, ab_init, plazo, tasa, comis = 0, 0, 0, 0.0, 0
                    vendedor_existente, nuevo_vendedor = None, None
                    
                    if "Financiado" in tipo_v:
                        with c3:
                            p_final = st.number_input("Valor Total Factura ($)", min_value=0, value=0, step=10000)
                            ab_init = st.number_input("Abono Inicial Entregado ($)", min_value=0, value=0, step=10000)
                            plazo = st.number_input("Meses a Pagar", min_value=1, value=6)
                        with c4:
                            st.write("Datos del Asesor")
                            cx1, cx2 = st.columns([1,2])
                            with cx1: comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                            with cx2: 
                                vendedor_existente = st.selectbox("Vendedor", ["Seleccionar..."] + vendedores)
                                nuevo_vendedor = st.text_input("O crear nuevo:")
                            tasa = st.selectbox("Tasa de Interés Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                        
                        m_f = p_final - ab_init
                        if m_f > 0 and plazo > 0:
                            i_m = tasa / 100.0
                            c_fija = int(round(m_f * (i_m * (1 + i_m)**plazo) / (((1 + i_m)**plazo) - 1))) if tasa > 0 else int(round(m_f / plazo))
                            total_a_pagar = c_fija * plazo
                            total_interes = total_a_pagar - m_f
                            
                            st.markdown(f"""
                            <div style='background: #F0FDF4; border: 1px solid #10B981; border-radius: 12px; padding: 20px; margin-top: 20px;'>
                                <h4 style='color: #047857; margin-top:0;'>📊 Proyección y Ganancia del Crédito</h4>
                                <div style='display: flex; justify-content: space-between;'>
                                    <div><p style='margin: 0; color: #065F46;'><b>Cuota Mensual Exacta:</b></p><h2 style='color:#10B981; margin:0;'>{fmt_cop(c_fija)}</h2></div>
                                    <div><p style='margin: 0; color: #065F46;'><b>Interés Total a Ganar:</b></p><h2 style='color:#10B981; margin:0;'>{fmt_cop(total_interes)}</h2></div>
                                    <div><p style='margin: 0; color: #065F46;'><b>Valor Final del Negocio:</b></p><h2 style='color:#10B981; margin:0;'>{fmt_cop(total_a_pagar + ab_init)}</h2></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    elif "Separé" in tipo_v:
                        with c3:
                            p_final = st.number_input("Valor Total a Pagar ($)", min_value=0, value=0, step=10000)
                            ab_init = st.number_input("Abono Inicial (Para separar) ($)", min_value=0, value=0, step=10000)
                            plazo = st.number_input("Número de Cuotas", min_value=1, value=2)
                        with c4:
                            st.write("Datos del Asesor")
                            cx1, cx2 = st.columns([1,2])
                            with cx1: comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                            with cx2: 
                                vendedor_existente = st.selectbox("Vendedor", ["Seleccionar..."] + vendedores)
                                nuevo_vendedor = st.text_input("O crear nuevo:")
                        tasa, s_dif, s_cuotas = 0.0, p_final - ab_init, 0
                        st.markdown(f"<p style='color: #0052D4; font-weight: bold;'>Saldo pendiente a diferir: {fmt_cop(s_dif)}</p>", unsafe_allow_html=True)
                        for idx in range(plazo):
                            x1, x2 = st.columns(2)
                            with x1:
                                v_c = st.number_input(f"Valor Cuota {idx+1}", min_value=0, value=int(s_dif/plazo), step=10000, key=f"v_{idx}")
                                s_cuotas += v_c
                            with x2: f_c = st.date_input(f"Fecha Límite Cuota {idx+1}", value=sumar_meses_exactos(f_cuota, idx), key=f"f_{idx}")
                            c_pers.append((idx+1, v_c, f_c))
                    else:
                        p_final = st.number_input("Valor Total Pagado de Contado ($)", min_value=0, value=0, step=10000)
                        vendedor_existente = st.selectbox("Vendedor", ["Seleccionar..."] + vendedores)
                        nuevo_vendedor = st.text_input("O crear nuevo:")
                        comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                        ab_init, plazo, tasa = p_final, 0, 0.0

                    st.divider()
                    st.markdown("#### Origen de Fondos (Para Radar DIAN)")
                    c_acc1, c_acc2 = st.columns(2)
                    with c_acc1: 
                        cuenta_sel = st.selectbox("¿A dónde ingresó la plata del abono/contado?", list(opc_cuentas.keys()) + ["➕ Añadir nueva cuenta..."])
                    with c_acc2:
                        nueva_cuenta = ""
                        if cuenta_sel == "➕ Añadir nueva cuenta...":
                            nueva_cuenta = st.text_input("Nombre de la nueva cuenta (Ej: Bancolombia - Maria)")

                    if st.button("Registrar Venta en Sistema", type="primary", use_container_width=True):
                        if not equipos_sel: st.error("Debes seleccionar mínimo un equipo para vender.")
                        elif p_final <= 0: st.error("El valor de la factura debe ser mayor a cero.")
                        elif cuenta_sel == "➕ Añadir nueva cuenta..." and not nueva_cuenta: st.error("Escribe el nombre de la nueva cuenta bancaria.")
                        else:
                            vendedor_final = nuevo_vendedor if nuevo_vendedor else (vendedor_existente if vendedor_existente != "Seleccionar..." else None)
                            if comis > 0 and not vendedor_final: st.error("Asigna un vendedor para pagarle su comisión.")
                            elif "Separé" in tipo_v and s_cuotas != (p_final - ab_init): st.error("Las cuotas no suman el total de la deuda.")
                            else:
                                try:
                                    if nuevo_vendedor:
                                        try: cursor.execute("INSERT INTO Vendedores (nombre) VALUES (%s)", (nuevo_vendedor,))
                                        except: pass
                                    
                                    # Gestionar la creación dinámica de la cuenta bancaria
                                    if cuenta_sel == "➕ Añadir nueva cuenta...":
                                        cursor.execute("INSERT INTO Cuentas_Bancarias (nombre_cuenta) VALUES (%s)", (nueva_cuenta,))
                                        id_cuenta_final = cursor.lastrowid
                                    else:
                                        id_cuenta_final = opc_cuentas[cuenta_sel]
                                        
                                    m_f = p_final - ab_init if "Contado" not in tipo_v else 0
                                    e_f = 'Activo' if "Contado" not in tipo_v else 'Pagado'
                                    v_c_bd = c_fija if "Financiado" in tipo_v else (c_pers[0][1] if "Separé" in tipo_v else 0)
                                    
                                    primer_imei = opc_eq[equipos_sel[0]]
                                    cursor.execute("""
                                        INSERT INTO Creditos (id_cliente, imei, precio_venta, abono_inicial, monto_financiado, tasa_interes_mensual, plazo_meses, valor_cuota, estado, fecha_inicio, fecha_primera_cuota, valor_comision, asesor_comision, estado_comision, id_usuario_registro, id_cuenta) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (opc_cli[cliente_sel], primer_imei, p_final, ab_init, m_f, tasa/100.0, plazo, v_c_bd, e_f, fecha_venta.strftime('%Y-%m-%d'), f_cuota.strftime('%Y-%m-%d'), comis, vendedor_final, 'Pendiente' if comis > 0 else 'No Aplica', st.session_state['id_usuario'], id_cuenta_final))
                                    id_cr = cursor.lastrowid
                                    
                                    for eq in equipos_sel:
                                        imei_eq = opc_eq[eq]
                                        cursor.execute("INSERT INTO Creditos_Items (id_credito, imei) VALUES (%s, %s)", (id_cr, imei_eq))
                                        cursor.execute("UPDATE Inventario SET estado = 'Vendido' WHERE imei = %s", (imei_eq,))
                                    
                                    if "Separé" in tipo_v:
                                        for n_c, v_c, f_c in c_pers: cursor.execute("INSERT INTO Cuotas_Programadas (id_credito, numero_cuota, monto_esperado, fecha_vencimiento) VALUES (%s, %s, %s, %s)", (id_cr, n_c, v_c, f_c.strftime('%Y-%m-%d')))
                                    
                                    if ("Contado" not in tipo_v and ab_init > 0) or "Contado" in tipo_v: 
                                        dinero_entregado = ab_init if "Contado" not in tipo_v else p_final
                                        cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (dinero_entregado,))
                                        # Escudo Fiscal: Registrar este abono inicial en Pagos para el DIAN Radar
                                        motivo_in = 'Pago Contado' if "Contado" in tipo_v else 'Abono Inicial'
                                        cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro, id_cuenta, motivo_ingreso) VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s)", (id_cr, dinero_entregado, motivo_in, dinero_entregado, fecha_venta.strftime('%Y-%m-%d %H:%M:%S'), st.session_state['id_usuario'], id_cuenta_final, motivo_in))
                                        
                                    if comis > 0 and vendedor_final:
                                        cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, vendedor, id_credito, id_usuario_registro, tipo_gasto) VALUES (%s, %s, %s, 'Por Pagar', %s, %s, %s, 'Gasto Operativo')", (f"Comisión Venta - {vendedor_final} (Cliente: {cliente_sel.split(' - ')[1]})", comis, datetime.date.today(), vendedor_final, id_cr, st.session_state['id_usuario']))
                                        
                                    conn.commit()
                                    st.balloons()
                                    st.success("¡Venta y contrato guardados exitosamente!")
                                    time.sleep(2)
                                    st.rerun()
                                except mysql.connector.Error as err:
                                    st.error(f"❌ Error al guardar en base de datos. Por favor avisa a soporte con este código: {err}")

        elif menu_seleccionado == "pagos":
            st.markdown("<h2>Caja y Recaudos 💰</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.imei, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota, c.plazo_meses, i.marca, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay créditos pendientes por cobrar.")
            else:
                opc_c = {f"{c['nombre_completo']} (Credito #{c['id_credito']})": c for c in activos}
                sel_titular = st.selectbox("Buscar Cliente para recibir pago:", list(opc_c.keys()), index=None, placeholder="Escribe el nombre del cliente...")
                
                if sel_titular:
                    dat = opc_c[sel_titular]
                    
                    cursor.execute("SELECT p.id_pago, p.monto_recibido, p.fecha_pago, p.tipo_pago, p.capital_abonado, p.interes_cobrado, cb.nombre_cuenta FROM Pagos p LEFT JOIN Cuentas_Bancarias cb ON p.id_cuenta = cb.id_cuenta WHERE p.id_credito = %s ORDER BY p.fecha_pago DESC", (dat['id_credito'],))
                    hist = cursor.fetchall()
                    
                    cap_pagado = sum([float(p['capital_abonado']) for p in hist])
                    s_pend = float(dat['monto_financiado']) - cap_pagado
                    v_cuota_bd = int(dat['valor_cuota']) if dat['valor_cuota'] else 0
                    
                    interes_mes_paz = s_pend * float(dat['tasa_interes_mensual'])
                    paz_y_salvo_total = s_pend + interes_mes_paz
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Saldo Pendiente a Capital", fmt_cop(s_pend))
                    c2.metric("Cuota Mensual", fmt_cop(v_cuota_bd))
                    c3.metric("Último Pago", f"🗓️ {hist[0]['fecha_pago'].strftime('%Y-%m-%d')}" if hist else "Ninguno", fmt_cop(hist[0]['monto_recibido']) if hist else "$0")
                    c4.metric("Liquidación (Paz y Salvo)", fmt_cop(paz_y_salvo_total))
                    
                    st.markdown("<h3 style='color:#0052D4; margin-top:20px;'>📥 Recibir Dinero</h3>", unsafe_allow_html=True)
                    with st.form("f_pago"):
                        x1, x2 = st.columns(2)
                        with x1: monto = st.number_input("Dinero Recibido del Cliente ($)", value=v_cuota_bd, min_value=0, step=10000)
                        with x2: fecha_pago_efectiva = st.date_input("Fecha en que entregó el dinero", value=None)
                        
                        y1, y2 = st.columns(2)
                        with y1: tipo = st.selectbox("Comportamiento del Pago", ["Pago de Cuota Mensual", "Abono Extra (Reduce el valor de la cuota)", "Abono Extra (Reduce el tiempo del crédito)"], index=0)
                        with y2: cuenta_sel = st.selectbox("¿A qué cuenta te pagó?", list(opc_cuentas.keys()) + ["➕ Añadir nueva cuenta..."])
                        
                        nueva_cuenta = ""
                        if cuenta_sel == "➕ Añadir nueva cuenta...":
                            nueva_cuenta = st.text_input("Nombre de la nueva cuenta (Ej: Daviplata - Carlos)")

                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Registrar Pago", width='stretch'):
                            if monto <= 0: st.error("El monto debe ser mayor a cero.")
                            elif fecha_pago_efectiva is None: st.error("Seleccione la fecha de pago.")
                            elif cuenta_sel == "➕ Añadir nueva cuenta..." and not nueva_cuenta: st.error("Escribe el nombre de la cuenta.")
                            else:
                                if cuenta_sel == "➕ Añadir nueva cuenta...":
                                    cursor.execute("INSERT INTO Cuentas_Bancarias (nombre_cuenta) VALUES (%s)", (nueva_cuenta,))
                                    id_cuenta_final = cursor.lastrowid
                                else:
                                    id_cuenta_final = opc_cuentas[cuenta_sel]

                                interes = round(s_pend * float(dat['tasa_interes_mensual']), 2)
                                cap_abono = 0.0 if monto <= interes else monto - interes
                                
                                cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro, id_cuenta, motivo_ingreso) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (dat['id_credito'], monto, tipo, cap_abono, min(monto, interes), fecha_pago_efectiva.strftime('%Y-%m-%d %H:%M:%S'), st.session_state['id_usuario'], id_cuenta_final, 'Pago Cuotas'))
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (monto,))
                                
                                nuevo_saldo = s_pend - cap_abono
                                if nuevo_saldo <= 0: 
                                    cursor.execute("UPDATE Creditos SET estado = 'Pagado' WHERE id_credito = %s", (dat['id_credito'],))
                                    st.balloons()
                                else:
                                    if "Reduce el valor de la cuota" in tipo:
                                        cursor.execute("SELECT COUNT(*) as pagadas FROM Pagos WHERE id_credito = %s AND tipo_pago LIKE '%%Cuota%%'", (dat['id_credito'],))
                                        pagadas = int(cursor.fetchone()['pagadas'] or 0)
                                        meses_restantes = dat['plazo_meses'] - pagadas
                                        if meses_restantes <= 0: meses_restantes = 1
                                        i_m = float(dat['tasa_interes_mensual'])
                                        nueva_cuota = nuevo_saldo * (i_m * (1 + i_m)**meses_restantes) / (((1 + i_m)**meses_restantes) - 1) if i_m > 0 else nuevo_saldo / meses_restantes
                                        cursor.execute("UPDATE Creditos SET valor_cuota = %s WHERE id_credito = %s", (int(round(nueva_cuota)), dat['id_credito']))
                                
                                conn.commit(); st.toast("Dinero ingresado a la cuenta correcta.", icon='✅'); time.sleep(1.5); st.rerun()

                    st.markdown("<br>### 💸 Historial de este Crédito", unsafe_allow_html=True)
                    if hist:
                        df_trans = pd.DataFrame(hist)
                        df_trans.rename(columns={'fecha_pago': 'Fecha', 'tipo_pago': 'Motivo', 'monto_recibido': 'Dinero Entregado', 'capital_abonado': 'Abono a Capital', 'interes_cobrado': 'Cobro de Interés', 'nombre_cuenta': 'Destino'}, inplace=True)
                        for col in ['Dinero Entregado', 'Abono a Capital', 'Cobro de Interés']: df_trans[col] = df_trans[col].apply(fmt_cop)
                        st.dataframe(df_trans[['Fecha', 'Motivo', 'Destino', 'Dinero Entregado', 'Abono a Capital', 'Cobro de Interés']], width='stretch')
                    else:
                        st.info("Sin registros de pagos.")

                    st.markdown("<br>### 🧾 Plan de Pagos", unsafe_allow_html=True)
                    df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                    st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "vencimientos":
            st.markdown("<h2>Gestor de Cartera y Mora ⏰</h2>", unsafe_allow_html=True)
            cursor.execute("""
                SELECT cl.nombre_completo AS 'Cliente', cl.telefono AS 'Celular', c.valor_cuota AS 'Cuota Mensual', c.fecha_primera_cuota AS 'Día de Pago', 
                (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Saldo Capital',
                c.estado AS 'Estado', c.tasa_interes_mensual
                FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo' ORDER BY c.fecha_primera_cuota ASC
            """)
            df = pd.DataFrame(cursor.fetchall())
            if df.empty: st.info("No hay carteras activas.")
            else:
                df['Pago Total (Paz y Salvo)'] = df.apply(lambda r: float(r['Saldo Capital']) + (float(r['Saldo Capital']) * float(r['tasa_interes_mensual'])), axis=1)
                for c in ['Cuota Mensual', 'Saldo Capital', 'Pago Total (Paz y Salvo)']: df[c] = df[c].apply(fmt_cop)
                df = df.drop(columns=['tasa_interes_mensual'])
                st.dataframe(df.style.map(color_estado, subset=['Estado']), width='stretch')

        elif menu_seleccionado == "notificar":
            st.markdown("<h2>Estados de Cuenta para Clientes 📱</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.telefono, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, i.modelo, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay créditos activos para enviar notificaciones.")
            else:
                opc_n = {f"{c['nombre_completo']} (Equipo: {c['modelo']})": c for c in activos}
                sel_cli = st.selectbox("Seleccionar Cliente", list(opc_n.keys()), index=None)
                
                if sel_cli:
                    dat = opc_n[sel_cli]
                    cursor.execute("SELECT SUM(capital_abonado) as cap, MAX(monto_recibido) as last_val, MAX(fecha_pago) as last_date FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    res_pag = cursor.fetchone()
                    cap_pag = float(res_pag['cap']) if res_pag and res_pag['cap'] else 0
                    last_val = float(res_pag['last_val']) if res_pag and res_pag['last_val'] else 0
                    last_date = res_pag['last_date'] if res_pag and res_pag['last_date'] else None

                    s_act = float(dat['monto_financiado']) - cap_pag
                    paz_y_salvo = s_act + (s_act * float(dat['tasa_interes_mensual']))
                    
                    msg = f"¡Hola {dat['nombre_completo']}! Te saludamos de DaTo.\n\nEste es el estado de cuenta de tu crédito:\n💵 *Cuota Mensual:* {fmt_cop(dat['valor_cuota'])}\n📉 *Saldo Pendiente:* {fmt_cop(s_act)}\n💳 *Último Pago Recibido:* {fmt_cop(last_val) if last_val else '$0'} el {last_date.strftime('%Y-%m-%d') if last_date else 'N/A'}\n\n*💰 Si deseas pagar la totalidad hoy (Paz y Salvo): {fmt_cop(paz_y_salvo)}*\n\nRecuerda que tu fecha límite de pago es el día {str(dat['fecha_primera_cuota'].day)} de cada mes."
                    
                    c1, c2 = st.columns([1, 1])
                    with c1: st.text_area("Copia este mensaje y envíalo por WhatsApp", value=msg, height=350)
                    with c2:
                        st.markdown("<h4 style='color:#0052D4; margin-top:0;'>Estado del Crédito</h4>", unsafe_allow_html=True)
                        df_plan = generar_plan_pagos_real(dat['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "historial":
            st.markdown("<h2>Auditoría y Anulaciones 📜</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Necesitas ser Administrador."); st.stop()
            
            tab_v, tab_r = st.tabs(["📋 Todos los Contratos", "⚠️ Anular/Eliminar Errores"])
            
            with tab_v:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("""
                    SELECT c.id_credito, cl.nombre_completo AS 'Cliente', i.modelo AS 'Equipo', c.estado AS 'Estado', 
                           i.costo_adquisicion AS 'Costo Real', c.precio_venta AS 'Precio de Venta',
                           IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) AS 'Dinero Recaudado',
                           (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Deuda en Calle',
                           c.valor_comision AS 'Comisión Asesor',
                           (IFNULL((SELECT SUM(monto_recibido) FROM Pagos p WHERE p.id_credito = c.id_credito), 0) - i.costo_adquisicion - c.valor_comision) AS 'GANANCIA REAL'
                    FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.fecha_inicio DESC
                """)
                df_cart = pd.DataFrame(cursor.fetchall())
                if not df_cart.empty:
                    for col in ['Costo Real', 'Precio de Venta', 'Dinero Recaudado', 'Deuda en Calle', 'Comisión Asesor', 'GANANCIA REAL']: 
                        df_cart[col] = df_cart[col].apply(fmt_cop)
                    st.dataframe(df_cart.style.map(color_estado, subset=['Estado']).map(color_ganancia_real, subset=['GANANCIA REAL']), width='stretch')
                else: st.info("No hay contratos registrados.")

            with tab_r:
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("<h4 style='color:#0052D4;'>📥 Anular un Pago</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT p.id_pago, cl.nombre_completo, p.monto_recibido, p.fecha_pago, p.tipo_pago FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY p.id_pago DESC LIMIT 50")
                    pagos_db = cursor.fetchall()
                    if pagos_db:
                        opc_pagos = {f"[{p['fecha_pago'].strftime('%Y-%m-%d')}] {p['nombre_completo']} ({fmt_cop(p['monto_recibido'])})": p for p in pagos_db}
                        with st.form("f_anular_pago"):
                            pago_sel = st.selectbox("Seleccione el pago a borrar", list(opc_pagos.keys()), index=None)
                            if st.form_submit_button("Eliminar Pago", width='stretch') and pago_sel:
                                dat_p = opc_pagos[pago_sel]
                                cursor.execute("SELECT id_credito FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                id_c = cursor.fetchone()['id_credito']
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (dat_p['monto_recibido'],))
                                cursor.execute("DELETE FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                                cursor.execute("UPDATE Creditos SET estado = 'Activo' WHERE id_credito = %s", (id_c,))
                                conn.commit(); st.toast("Pago eliminado."); time.sleep(1.5); st.rerun()
                    else: st.info("No hay pagos.")

                with c2:
                    st.markdown("<h4 style='color:#0052D4;'>🚨 Anular Venta</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT c.id_credito, cl.nombre_completo, i.modelo, c.imei, c.abono_inicial FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei ORDER BY c.id_credito DESC")
                    creds_db = cursor.fetchall()
                    if creds_db:
                        opc_creds = {f"[Credito: {c['id_credito']}] {c['nombre_completo']} - {c['modelo']}": c for c in creds_db}
                        with st.form("f_anular_venta"):
                            cred_sel = st.selectbox("Seleccionar venta a borrar", list(opc_creds.keys()), index=None)
                            if st.form_submit_button("Borrar Venta y Recuperar Equipo", width='stretch') and cred_sel:
                                dat_c = opc_creds[cred_sel]
                                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                                cursor.execute("SELECT SUM(monto_recibido) as t FROM Pagos WHERE id_credito = %s", (dat_c['id_credito'],))
                                res_t = cursor.fetchone()
                                plata_a_restar = float(dat_c['abono_inicial']) + float(res_t['t'] if res_t and res_t['t'] else 0)
                                if plata_a_restar > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (plata_a_restar,))
                                
                                cursor.execute("SELECT imei FROM Creditos_Items WHERE id_credito = %s", (dat_c['id_credito'],))
                                for item in cursor.fetchall(): cursor.execute("UPDATE Inventario SET estado = 'Disponible' WHERE imei = %s", (item['imei'],))
                                cursor.execute("DELETE FROM Creditos_Items WHERE id_credito = %s", (dat_c['id_credito'],))
                                
                                cursor.execute("UPDATE Inventario SET estado = 'Disponible' WHERE imei = %s", (dat_c['imei'],))
                                cursor.execute("DELETE FROM Gastos_Operativos WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("DELETE FROM Cuotas_Programadas WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("DELETE FROM Pagos WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("DELETE FROM Creditos WHERE id_credito = %s", (dat_c['id_credito'],))
                                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                                conn.commit(); st.toast("Venta eliminada."); time.sleep(1.5); st.rerun()
                    else: st.info("No hay ventas.")
                    
                with c3:
                    st.markdown("<h4 style='color:#0052D4;'>📦 Eliminar de Bodega</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT imei, marca, modelo, costo_adquisicion, id_bolsa FROM Inventario WHERE estado = 'Disponible'")
                    inv_db = cursor.fetchall()
                    if inv_db:
                        opc_inv = {f"{i['marca']} {i['modelo']} ({i['imei']})": i for i in inv_db}
                        with st.form("f_anular_hardware"):
                            inv_sel = st.selectbox("Seleccione el equipo", list(opc_inv.keys()), index=None)
                            if st.form_submit_button("Eliminar y Devolver Dinero a Caja", width='stretch') and inv_sel:
                                dat_i = opc_inv[inv_sel]
                                if float(dat_i['costo_adquisicion']) > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s WHERE id_bolsa = %s", (dat_i['costo_adquisicion'], dat_i['id_bolsa']))
                                cursor.execute("DELETE FROM Inventario WHERE imei = %s", (dat_i['imei'],))
                                conn.commit(); st.toast("Equipo eliminado."); time.sleep(1.5); st.rerun()
                    else: st.info("Bodega vacía.")

        elif menu_seleccionado == "egresos":
            st.markdown("<h2>Egresos, Proveedores y Cadenas 💸</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("No tienes permisos para ver gastos."); st.stop()
            
            tab_com, tab_gas = st.tabs(["🤝 Pago de Comisiones a Vendedores", "🧾 Salidas de Caja (Proveedores y Gastos)"])
            with tab_com:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_gasto, descripcion, monto, vendedor, id_credito FROM Gastos_Operativos WHERE estado_pago = 'Por Pagar' AND descripcion LIKE '%Comisión%'")
                pends = cursor.fetchall()
                if pends:
                    df_p = pd.DataFrame(pends)
                    df_p['Valor a Pagar'] = df_p['monto'].apply(fmt_cop)
                    st.dataframe(df_p[['descripcion', 'vendedor', 'Valor a Pagar']], width='stretch')
                    with st.form("f_com"):
                        sel = st.selectbox("Seleccionar Comisión para Liquidar", list({f"{x['descripcion']} -> {fmt_cop(x['monto'])}": x['id_gasto'] for x in pends}.keys()), index=None)
                        if st.form_submit_button("Marcar como Pagada y Descontar de Caja Global", width='stretch') and sel:
                            id_g = {f"{x['descripcion']} -> {fmt_cop(x['monto'])}": x['id_gasto'] for x in pends}[sel]
                            cursor.execute("SELECT monto, id_credito FROM Gastos_Operativos WHERE id_gasto = %s", (id_g,))
                            g_data = cursor.fetchone()
                            val, id_credito = float(g_data['monto']), g_data['id_credito']
                            
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (val,))
                            cursor.execute("UPDATE Gastos_Operativos SET estado_pago = 'Pagado', fecha_gasto = %s WHERE id_gasto = %s", (datetime.date.today(), id_g))
                            if id_credito: cursor.execute("UPDATE Creditos SET estado_comision = 'Pagada' WHERE id_credito = %s", (id_credito,))
                            conn.commit(); st.toast("Comisión liquidada."); time.sleep(1.5); st.rerun()
                else: st.info("No hay comisiones pendientes de pago.")
                
            with tab_gas:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("f_g"):
                    tipo_g = st.selectbox("Categoría de la Salida de Dinero", ["Gasto Operativo (Luz, Arriendo, Papelería)", "Pago a Proveedor de Mercancía", "Aporte a Cadena / Fondo Fijo"])
                    desc = st.text_input("Detalle (Ej: Pago Arriendo Mes Agosto / Cadena Grupo 2)")
                    m_g = st.number_input("Valor Extraído de la Caja Global ($)", min_value=0, step=10000, value=0)
                    if st.form_submit_button("Registrar Salida", width='stretch'):
                        if desc and m_g > 0:
                            cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, id_usuario_registro, tipo_gasto) VALUES (%s, %s, %s, 'Pagado', %s, %s)", (desc, m_g, datetime.date.today(), st.session_state['id_usuario'], tipo_g))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (m_g,))
                            conn.commit(); st.toast("Salida de dinero registrada."); time.sleep(1); st.rerun()

        elif menu_seleccionado == "flujo":
            st.markdown("<h2>Socios e Inversores 📈</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Acceso denegado."); st.stop()
            
            tab_dash, tab_in, tab_out = st.tabs(["📊 Resumen de Deudas a Socios", "📥 Registrar Fondeo (Inyección)", "📤 Pagarle a Socio"])
            
            with tab_dash:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT prestamista AS 'Nombre del Socio', monto_prestado AS 'Plata Prestada a DaTo', monto_total_pagar AS 'Retorno Acordado', saldo_pendiente AS 'Deuda Actual', fecha_prestamo AS 'Fecha' FROM Deudas_Fondeo ORDER BY fecha_prestamo DESC")
                df_inversores = pd.DataFrame(cursor.fetchall())
                
                cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
                cap = float(cursor.fetchone()['cap'] or 0)
                deuda = df_inversores['Deuda Actual'].sum() if not df_inversores.empty else 0
                
                c1, c2 = st.columns(2)
                c1.metric("💵 Total Dinero Físico (Caja Global)", fmt_cop(cap))
                c2.metric("📉 Deuda Total con Socios", fmt_cop(deuda))
                
                if not df_inversores.empty:
                    for c in ['Plata Prestada a DaTo', 'Retorno Acordado', 'Deuda Actual']: df_inversores[c] = df_inversores[c].apply(fmt_cop)
                    st.dataframe(df_inversores, width='stretch')
                else: st.info("No hay dinero de socios registrado.")

            with tab_in:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("f_f_in"):
                    prov = st.text_input("Nombre del Socio / Inversor (Ej: Fondo Suárez)")
                    iny = st.number_input("Dinero Invertido (Entra a Caja Global) ($)", min_value=0, step=100000, value=0)
                    ret = st.number_input("Dinero Total a Devolver (Capital + Ganancia) ($)", min_value=0, step=100000, value=0)
                    
                    st.markdown("#### Radar DIAN (Origen de la transferencia)")
                    c1, c2 = st.columns(2)
                    with c1: cta_inv = st.selectbox("¿A qué cuenta bancaria te consignó?", list(opc_cuentas.keys()) + ["➕ Añadir nueva cuenta..."])
                    with c2: cta_nueva_inv = st.text_input("Si es nueva, escribe el nombre:")
                    
                    if st.form_submit_button("Guardar Inversión y Crear Bolsillo", width='stretch'):
                        if prov and iny > 0:
                            if cta_inv == "➕ Añadir nueva cuenta...":
                                cursor.execute("INSERT INTO Cuentas_Bancarias (nombre_cuenta) VALUES (%s)", (cta_nueva_inv,))
                                id_c_f = cursor.lastrowid
                            else: id_c_f = opc_cuentas[cta_inv]

                            # Crear la deuda
                            cursor.execute("INSERT INTO Deudas_Fondeo (prestamista, monto_prestado, monto_total_pagar, saldo_pendiente, fecha_prestamo, id_usuario_registro, id_cuenta, motivo_ingreso) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Incremento inversión')", (prov, iny, ret, ret, datetime.date.today(), st.session_state['id_usuario'], id_c_f))
                            # Crear el bolsillo virtual para luego comprar inventario
                            cursor.execute("INSERT INTO Bolsas_Capital (nombre_bolsa, saldo_actual, fecha_creacion) VALUES (%s, %s, CURDATE())", (prov, iny))
                            
                            conn.commit(); st.toast("Plata sumada a la caja global y bolsillo creado."); time.sleep(2); st.rerun()

            with tab_out:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_deuda, prestamista, saldo_pendiente FROM Deudas_Fondeo WHERE saldo_pendiente > 0")
                deudas = cursor.fetchall()
                if deudas:
                    opc_d = {f"{d['prestamista']} (Le debemos: {fmt_cop(d['saldo_pendiente'])})": d for d in deudas}
                    with st.form("f_d_out"):
                        d_sel = st.selectbox("Seleccionar Socio", list(opc_d.keys()), index=None)
                        ab = st.number_input("Dinero a entregar (Se resta de la Caja Global) ($)", min_value=0, step=100000, value=0)
                        if st.form_submit_button("Registrar Pago a Socio", width='stretch') and d_sel:
                            id_d = opc_d[d_sel]['id_deuda']
                            cursor.execute("INSERT INTO Pagos_Deuda (id_deuda, monto_pagado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s)", (id_d, ab, datetime.date.today(), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Deudas_Fondeo SET saldo_pendiente = saldo_pendiente - %s WHERE id_deuda = %s", (ab, id_d))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (ab,))
                            conn.commit(); st.toast("Plata entregada al socio."); time.sleep(1); st.rerun()
                else: st.info("No hay deudas con socios.")

        elif menu_seleccionado == "reportes":
            st.markdown("<h2>Reportes (Radar DIAN y ROI) 📊</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Módulo de gerencia."); st.stop()
            
            tab_bi, tab_dian, tab_roi, tab_libro = st.tabs(["🌐 Visión General", "🛡️ Radar Fiscal (DIAN)", "💎 ROI por Inversor", "📓 Libro Diario"])
            
            cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
            cap = float(cursor.fetchone()['cap'] or 0)
            cursor.execute("SELECT SUM(saldo_pendiente) as deu FROM Deudas_Fondeo")
            deuda = float(cursor.fetchone()['deu'] or 0)
            cursor.execute("SELECT SUM(monto_financiado) as mf FROM Creditos WHERE estado = 'Activo'")
            cartera_colocada = float(cursor.fetchone()['mf'] or 0)
            cursor.execute("SELECT SUM(capital_abonado) as ca FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito WHERE c.estado = 'Activo'")
            cartera_recaudada = float(cursor.fetchone()['ca'] or 0)
            
            cartera_neta_calle = cartera_colocada - cartera_recaudada
            patrimonio_neto = cap + cartera_neta_calle - deuda
            
            with tab_bi:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 30px; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); margin-bottom: 25px;">
                    <h3 style="color:#0052D4; margin:0; font-weight: 700;">VALOR TOTAL DE TU EMPRESA HOY</h3>
                    <h1 style="color:#1E293B; font-size: 4.5rem; font-weight: 800; margin: 10px 0;">{fmt_cop(patrimonio_neto)}</h1>
                    <p style="color:#64748B; font-size: 15px; margin:0;">Plata en Caja Global ({fmt_cop(cap)}) + Cartera en la calle ({fmt_cop(cartera_neta_calle)}) - Lo que debemos a Socios ({fmt_cop(deuda)})</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("💳 Cartera Pendiente en la calle", fmt_cop(cartera_neta_calle))
                recup_perc = (cartera_recaudada / cartera_colocada * 100) if cartera_colocada > 0 else 0
                c_m2.metric("✅ Tasa de Recuperación Total", f"{recup_perc:.1f}%")

            with tab_dian:
                st.markdown("<br><h4 style='color:#0052D4;'>🛡️ Radar DIAN y Topes Bancarios</h4>", unsafe_allow_html=True)
                st.write("Suma total de ingresos rastreados durante este año para vigilar los límites de declaración de renta. (El 'Efectivo' físico no suma a los bancos).")
                
                query_dian = """
                    SELECT cb.nombre_cuenta AS 'Cuenta / Destino Fiscal', SUM(t.monto) as 'Total Ingresado en el Año'
                    FROM (
                        SELECT id_cuenta, monto_recibido as monto FROM Pagos WHERE YEAR(fecha_pago) = YEAR(CURDATE())
                        UNION ALL
                        SELECT id_cuenta, monto_prestado as monto FROM Deudas_Fondeo WHERE YEAR(fecha_prestamo) = YEAR(CURDATE())
                    ) as t
                    JOIN Cuentas_Bancarias cb ON t.id_cuenta = cb.id_cuenta
                    GROUP BY cb.nombre_cuenta
                    ORDER BY 'Total Ingresado en el Año' DESC
                """
                cursor.execute(query_dian)
                df_dian = pd.DataFrame(cursor.fetchall())
                if not df_dian.empty:
                    df_dian['Total Ingresado en el Año'] = df_dian['Total Ingresado en el Año'].apply(float)
                    st.bar_chart(df_dian.set_index('Cuenta / Destino Fiscal'), color="#DC2626")
                    df_dian['Total Ingresado en el Año'] = df_dian['Total Ingresado en el Año'].apply(fmt_cop)
                    st.dataframe(df_dian, width='stretch')
                else: st.info("No hay ingresos bancarios rastreados este año.")

            with tab_roi:
                st.markdown("<br><h4 style='color:#0052D4;'>💎 Rentabilidad Exacta por Socio (ROI)</h4>", unsafe_allow_html=True)
                st.write("Cruza el costo de los equipos comprados con el bolsillo de cada inversor frente al valor al que fueron vendidos.")
                
                query_roi = """
                    SELECT b.nombre_bolsa AS 'Origen del Dinero (Socio)', 
                           SUM(i.costo_adquisicion) AS 'Costo Invertido', 
                           SUM(cr.precio_venta) AS 'Venta Bruta Generada',
                           (SUM(cr.precio_venta) - SUM(i.costo_adquisicion)) AS 'Ganancia Pura'
                    FROM Bolsas_Capital b 
                    JOIN Inventario i ON b.id_bolsa = i.id_bolsa 
                    JOIN Creditos_Items ci ON i.imei = ci.imei
                    JOIN Creditos cr ON ci.id_credito = cr.id_credito
                    GROUP BY b.id_bolsa
                """
                cursor.execute(query_roi)
                df_roi = pd.DataFrame(cursor.fetchall())
                if not df_roi.empty:
                    df_roi['ROI (%)'] = ((df_roi['Ganancia Pura'] / df_roi['Costo Invertido']) * 100).round(1).astype(str) + '%'
                    for c in ['Costo Invertido', 'Venta Bruta Generada', 'Ganancia Pura']: df_roi[c] = df_roi[c].apply(fmt_cop)
                    st.dataframe(df_roi, width='stretch')
                else: st.info("Aún no hay equipos marcados por bolsillo que hayan sido vendidos.")

            with tab_libro:
                st.markdown("<br><h4 style='color:#0052D4;'>📓 Histórico de Movimientos de Caja (Libro Diario)</h4>", unsafe_allow_html=True)
                st.write("Extracto cronológico de todas las entradas y salidas de dinero de tu Caja Global.")
                
                query_flujo = """
                    SELECT DATE(fecha_pago) AS Fecha, 'Ingreso' AS Tipo, motivo_ingreso AS Categoria, CONCAT('Crédito #', id_credito) AS Detalle, monto_recibido AS Ingreso, 0 AS Egreso FROM Pagos
                    UNION ALL
                    SELECT DATE(fecha_prestamo) AS Fecha, 'Ingreso' AS Tipo, motivo_ingreso AS Categoria, prestamista AS Detalle, monto_prestado AS Ingreso, 0 AS Egreso FROM Deudas_Fondeo
                    UNION ALL
                    SELECT DATE(fecha_compra) AS Fecha, 'Egreso' AS Tipo, 'Compra de Bodega' AS Categoria, CONCAT(cantidad, 'x ', marca, ' ', modelo) AS Detalle, 0 AS Ingreso, (costo_adquisicion * cantidad) AS Egreso FROM Inventario WHERE costo_adquisicion > 0
                    UNION ALL
                    SELECT DATE(fecha_gasto) AS Fecha, 'Egreso' AS Tipo, tipo_gasto AS Categoria, descripcion AS Detalle, 0 AS Ingreso, monto AS Egreso FROM Gastos_Operativos
                    UNION ALL
                    SELECT DATE(fecha_pago) AS Fecha, 'Egreso' AS Tipo, 'Retorno a Socio' AS Categoria, CONCAT('Pago Deuda #', id_deuda) AS Detalle, 0 AS Ingreso, monto_pagado AS Egreso FROM Pagos_Deuda
                    ORDER BY Fecha ASC
                """
                cursor.execute(query_flujo)
                flujo_db = cursor.fetchall()
                if flujo_db:
                    df_flujo = pd.DataFrame(flujo_db)
                    df_flujo['Saldo Acumulado'] = (df_flujo['Ingreso'] - df_flujo['Egreso']).cumsum()
                    for col in ['Ingreso', 'Egreso', 'Saldo Acumulado']: df_flujo[col] = df_flujo[col].apply(fmt_cop)
                    def color_tipo_movimiento(val): return 'color: #059669; font-weight: 600;' if val == 'Ingreso' else 'color: #DC2626; font-weight: 600;'
                    st.dataframe(df_flujo.style.map(color_tipo_movimiento, subset=['Tipo']), width='stretch')
                else: st.info("Aún no hay movimientos financieros registrados.")

        elif menu_seleccionado == "config_roles":
            st.markdown("<h2>Configuración de Usuarios ⚙️</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("No autorizado."); st.stop()
            
            tab_c1, tab_c2, tab_c3 = st.tabs(["👤 Crear Empleado", "🛡️ Dar Permisos", "➕ Crear Tipo de Rol"])
            cursor.execute("SELECT * FROM Roles")
            opc_r = [r['nombre_rol'] for r in cursor.fetchall()]
            
            with tab_c1:
                st.markdown("<br>", unsafe_allow_html=True)
                col_u1, col_u2, col_u3 = st.columns(3)
                with col_u1:
                    st.markdown("**✨ Crear Nuevo Empleado**")
                    with st.form("f_newUser"):
                        n_user = st.text_input("Usuario para entrar al sistema")
                        n_pass = st.text_input("Contraseña", type="password")
                        n_nombre = st.text_input("Nombre Real del Empleado")
                        n_rol = st.selectbox("Perfil / Cargo", opc_r)
                        if st.form_submit_button("Guardar Empleado", width='stretch'):
                            if n_user and n_pass and n_nombre:
                                try:
                                    cursor.execute("INSERT INTO Usuarios (username, password_hash, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_user, n_pass, n_nombre, n_rol))
                                    conn.commit(); st.toast("Empleado guardado."); time.sleep(1.5); st.rerun()
                                except mysql.connector.Error: st.error("El usuario ya existe.")
                with col_u2:
                    st.markdown("**🔄 Cambiar Cargo a Empleado**")
                    with st.form("f_change_rol"):
                        cursor.execute("SELECT username FROM Usuarios")
                        users_db = [u['username'] for u in cursor.fetchall()]
                        if users_db:
                            u_rol = st.selectbox("Seleccionar Empleado", users_db, index=None)
                            new_rol = st.selectbox("Nuevo Cargo", opc_r, index=None)
                            if st.form_submit_button("Actualizar Cargo", width='stretch') and u_rol and new_rol:
                                cursor.execute("UPDATE Usuarios SET rol = %s WHERE username = %s", (new_rol, u_rol))
                                conn.commit(); st.toast("Cargo cambiado."); time.sleep(1.5); st.rerun()
                with col_u3:
                    st.markdown("**🔑 Cambiar Contraseña**")
                    with st.form("f_reset"):
                        if users_db:
                            u_reset = st.selectbox("Seleccionar Empleado", users_db, index=None)
                            p_reset = st.text_input("Nueva Contraseña", type="password")
                            if st.form_submit_button("Actualizar Contraseña", width='stretch') and u_reset and p_reset:
                                cursor.execute("UPDATE Usuarios SET password_hash = %s WHERE username = %s", (p_reset, u_reset))
                                conn.commit(); st.toast("Contraseña actualizada."); time.sleep(1.5); st.rerun()

            with tab_c2:
                st.markdown("<br>", unsafe_allow_html=True)
                role_sel = st.selectbox("Seleccione el Cargo para ver a qué tiene acceso:", opc_r, index=None)
                if role_sel:
                    cursor.execute("SELECT * FROM Modulos_Sistema")
                    todos_modulos = cursor.fetchall()
                    cursor.execute("SELECT id_modulo FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                    activos_rol = [x['id_modulo'] for x in cursor.fetchall()]
                    
                    with st.form("form_permisos"):
                        check_resultados = {m['id_modulo']: st.checkbox(m['nombre_visible'], value=(m['id_modulo'] in activos_rol)) for m in todos_modulos}
                        if st.form_submit_button("Guardar Permisos", width='stretch'):
                            cursor.execute("DELETE FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                            cursor.execute("SELECT id_role FROM Roles WHERE nombre_rol = %s", (role_sel,))
                            id_r_actual = cursor.fetchone()['id_role']
                            for id_mod, marcado in check_resultados.items():
                                if marcado: cursor.execute("INSERT INTO Permisos_Rol (id_role, id_modulo) VALUES (%s, %s)", (id_r_actual, id_mod))
                            conn.commit(); st.toast("Permisos guardados."); time.sleep(1); st.rerun()

            with tab_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("form_nuevo_rol"):
                    nuevo_rol_nombre = st.text_input("Nombre del nuevo cargo:")
                    if st.form_submit_button("Crear Cargo", width='stretch'):
                        if nuevo_rol_nombre:
                            try:
                                cursor.execute("SELECT nombre_rol FROM Roles WHERE nombre_rol = %s", (nuevo_rol_nombre.strip(),))
                                if cursor.fetchone(): st.error("Ese cargo ya existe.")
                                else:
                                    cursor.execute("INSERT INTO Roles (nombre_rol) VALUES (%s)", (nuevo_rol_nombre.strip(),))
                                    conn.commit(); st.toast("Cargo creado."); time.sleep(1); st.rerun()
                            except Exception as e: st.error(f"Error: {e}")

finally:
    try:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn and conn.is_connected(): conn.close()
    except Exception: pass

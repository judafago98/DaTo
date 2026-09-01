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
    
    # Nuevos campos Clientes
    try: cursor.execute("ALTER TABLE Clientes ADD COLUMN direccion VARCHAR(255), ADD COLUMN barrio VARCHAR(255), ADD COLUMN ciudad VARCHAR(255), ADD COLUMN correo VARCHAR(255), ADD COLUMN empresa VARCHAR(255)"); conn.commit()
    except Exception: pass
    
    # Nuevos campos Inventario
    try: cursor.execute("ALTER TABLE Inventario ADD COLUMN cantidad INT DEFAULT 1, ADD COLUMN color VARCHAR(100), ADD COLUMN fecha_compra DATE, ADD COLUMN factura VARCHAR(100), ADD COLUMN tienda_proveedor VARCHAR(255), ADD COLUMN nit_proveedor VARCHAR(100), ADD COLUMN celular_proveedor VARCHAR(100)"); conn.commit()
    except Exception: pass
    
    # Adaptación de Gastos para Comisiones
    try: cursor.execute("ALTER TABLE Gastos_Operativos ADD COLUMN estado_pago VARCHAR(50) DEFAULT 'Pagado', ADD COLUMN vendedor VARCHAR(255), ADD COLUMN id_credito INT"); conn.commit()
    except Exception: pass

    # Tablas Adicionales
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Vendedores (id_vendedor INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) UNIQUE)"); conn.commit()
    except Exception: pass
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Creditos_Items (id INT AUTO_INCREMENT PRIMARY KEY, id_credito INT, imei VARCHAR(100))"); conn.commit()
    except Exception: pass

# --- Configuración visual de la app ---
st.set_page_config(page_title="DaTo Workspace", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# --- CINTURÓN DE SEGURIDAD PARA ASSETS VISUALES ---
def renderizar_logo(es_sidebar=False):
    alto = "90px" if es_sidebar else "160px"
    fuente = "2.2rem" if es_sidebar else "4rem"
    sub_fuente = "0.9rem" if es_sidebar else "1.3rem"
    st.markdown(f"""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: {alto}; background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04); margin-bottom: 20px;'>
        <h1 style='color: #0052D4; font-size: {fuente}; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin:0;'>⚡ DaTo</h1>
        <p style='color: #64748B; margin: 0; font-weight: 500; font-size: {sub_fuente};'>Tecnología con respaldo</p>
    </div>
    """, unsafe_allow_html=True)

# --- DISEÑO BLANCO CORPORATIVO FORZADO ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* FORZAR TEMA CLARO ABSOLUTO */
        :root { color-scheme: light !important; }
        
        .stApp { background-color: #F8FAFC !important; background-image: none !important; }

        /* Textos Generales a Negro/Gris Oscuro */
        html, body, [class*="css"], p, span, div, label, li, td, th { 
            font-family: 'Outfit', sans-serif !important; color: #1E293B !important; 
        }

        h1, h2, h3, h4, h5, h6 { color: #0052D4 !important; font-weight: 700 !important; }

        /* CONTENEDORES Y TARJETAS (Blancos) */
        div[data-testid="stForm"], .card-panel, [data-testid="stSidebar"] {
            background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
        }

        /* INPUTS Y SELECTS (Fondo blanco, texto oscuro) */
        input, textarea, select, 
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important; color: #0F172A !important; -webkit-text-fill-color: #0F172A !important;
        }
        
        input:focus, textarea:focus, div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {
            border-color: #00A2FF !important; box-shadow: 0 0 0 2px rgba(0, 162, 255, 0.2) !important; background-color: #FFFFFF !important;
        }

        /* BOTONES (+/- numéricos) */
        [data-testid="stNumberInput"] button {
            background-color: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; color: #0052D4 !important; border-radius: 6px !important; margin: 0 2px !important;
        }
        
        /* BOTONES MAESTROS */
        .stButton>button {
            background: #0088FF !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
            border: none !important; border-radius: 8px !important; font-weight: 600 !important; width: 100% !important; transition: all 0.2s;
        }
        .stButton>button:hover { background: #0052D4 !important; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0, 82, 212, 0.2) !important; }

        /* PESTAÑAS (TABS) - CERO ROJO */
        button[data-baseweb="tab"] { color: #64748B !important; background: transparent !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #0052D4 !important; border-bottom-color: #0052D4 !important; background: transparent !important; }
        div[data-baseweb="tab-highlight"] { display: none !important; }
        
        /* TOGGLES */
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div { background-color: #CBD5E1 !important; }
        [data-testid="stToggle"] [data-baseweb="checkbox"] > div[aria-checked="true"] { background-color: #00A2FF !important; }

        /* SIDEBAR MENÚ */
        [data-testid="stSidebar"] [role="radiogroup"] label div[data-baseweb="radio"],
        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child,
        [data-testid="stSidebar"] [role="radiogroup"] label > span:first-child { display: none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: #F1F5F9 !important; border: 1px solid transparent !important; border-radius: 8px !important;
            padding: 10px 15px !important; margin: 4px 10px !important; transition: all 0.2s ease !important; cursor: pointer !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: #E2E8F0 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
            background: #E0F2FE !important; border-left: 4px solid #00A2FF !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] div[dir="auto"] {
            color: #00A2FF !important; font-weight: 700 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛡️ ALGORITMOS DE FORMATO Y CONVERSIÓN Financiera
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
    st.error(f"🌐 Servidor de base de datos inalcanzable. Reintente en unos segundos. Detalle: {e}")
    st.stop()

# ==========================================
# SISTEMA DE CAPAS DE SEGURIDAD OPERATIVA (Y PORTAL CLIENTE)
# ==========================================
try:
    if 'logeado' not in st.session_state: st.session_state['logeado'] = False
    if 'id_usuario' not in st.session_state: st.session_state['id_usuario'] = None
    if 'nombre_usuario' not in st.session_state: st.session_state['nombre_usuario'] = None
    if 'rol' not in st.session_state: st.session_state['rol'] = None

    if not st.session_state['logeado']:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        col_espacio1, col_centro, col_espacio2 = st.columns([1, 2, 1], gap="large")
        
        with col_centro:
            renderizar_logo(es_sidebar=False)
            tab_admin, tab_cliente = st.tabs(["💼 Equipo DaTo", "👤 Autogestión Clientes"])

            with tab_admin:
                with st.form("form_login"):
                    st.markdown("<h3 style='color: #0052D4; margin-bottom: 5px;'>Acceso Corporativo</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #64748B; margin-bottom: 20px;'>Ingrese sus credenciales de empleado.</p>", unsafe_allow_html=True)
                    usuario_input = st.text_input("Usuario")
                    password_input = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("Ingresar al Sistema", width='stretch'):
                        cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                        usuario_db = cursor.fetchone()
                        if usuario_db:
                            st.session_state.update({'logeado': True, 'id_usuario': usuario_db['id_usuario'], 'nombre_usuario': usuario_db['nombre_completo'], 'rol': usuario_db['rol']})
                            st.rerun()
                        else: st.error("Usuario o contraseña incorrectos.")
            
            with tab_cliente:
                with st.form("form_login_cliente"):
                    st.markdown("<h3 style='color: #0052D4; margin-bottom: 5px;'>Bienvenido a DaTo</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #64748B; margin-bottom: 20px;'>Consulta tu estado de cuenta y recibos de pago.</p>", unsafe_allow_html=True)
                    cedula_cliente = st.text_input("Tu Número de Documento (C.C.)")
                    if st.form_submit_button("Ver mi Estado de Cuenta", width='stretch'):
                        cursor.execute("SELECT * FROM Clientes WHERE documento = %s", (cedula_cliente,))
                        cli_db = cursor.fetchone()
                        if cli_db:
                            st.session_state.update({'logeado': True, 'rol': 'Cliente', 'id_cliente': cli_db['id_cliente'], 'nombre_cliente': cli_db['nombre_completo']})
                            st.rerun()
                        else: st.error("No encontramos compras registradas con esta cédula.")

    # ==========================================
    # 📱 VISTA EXCLUSIVA PARA EL CLIENTE LOGUEADO
    # ==========================================
    elif st.session_state['rol'] == 'Cliente':
        st.markdown(f"<h1 style='text-align:center;'>👋 ¡Hola, {st.session_state['nombre_cliente'].split()[0]}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748B; font-size: 1.1rem;'>Este es el resumen de tus productos activos con nosotros.</p><br>", unsafe_allow_html=True)
        
        cursor.execute("SELECT c.id_credito, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, c.tasa_interes_mensual FROM Creditos c WHERE c.id_cliente = %s AND c.estado = 'Activo'", (st.session_state['id_cliente'],))
        creditos_cliente = cursor.fetchall()
        
        if not creditos_cliente:
            st.success("¡Felicidades! Actualmente estás a Paz y Salvo con DaTo.")
        else:
            for cred in creditos_cliente:
                # Buscar equipos multi-producto o modelo antiguo
                cursor.execute("SELECT i.marca, i.modelo FROM Creditos_Items ci JOIN Inventario i ON ci.imei = i.imei WHERE ci.id_credito = %s", (cred['id_credito'],))
                equipos = cursor.fetchall()
                if not equipos: 
                    cursor.execute("SELECT i.marca, i.modelo FROM Creditos c JOIN Inventario i ON c.imei = i.imei WHERE c.id_credito = %s", (cred['id_credito'],))
                    equipos = cursor.fetchall()
                
                nombres_equipos = " + ".join([f"{e['marca']} {e['modelo']}" for e in equipos])
                
                # Matemáticas simples
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
    # 💼 VISTA DE ADMINISTRADOR (TU CÓDIGO ORIGINAL)
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
            "💸 Egresos y Comisiones": "egresos",
            "📈 Socios e Inversores": "flujo",
            "📊 Reportes y Estadísticas": "reportes",
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
            if st.sidebar.button("Cerrar Sesión", width='stretch'):
                st.session_state['logeado'] = False; st.rerun()

        if menu_seleccionado == "inicio":
            st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                url_gif_divertido = "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif"
                st.markdown(f"""
                <div style="text-align: center; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                    <img src="{url_gif_divertido}" style="border-radius: 16px; width: 100%; max-width: 320px; border: 1px solid #E2E8F0;">
                    <h1 style='font-size: 2.8rem; font-weight: 800; margin-top: 25px; margin-bottom: 0; color: #1E293B;'>HOLA, <span style='color: #0052D4;'>{st.session_state['nombre_usuario'].split(" ")[0].upper()}</span></h1>
                    <p style='color: #64748B; font-size: 1.1rem; font-weight: 400; margin-top: 10px;'>Es hora de poner a trabajar el ecosistema DaTo.</p>
                </div>
                """, unsafe_allow_html=True)

        elif menu_seleccionado == "simulador":
            st.markdown("<h2 style='margin-bottom: 25px;'>🔮 Cotizador y Simulación</h2>", unsafe_allow_html=True)
            tab_sim, tab_paz = st.tabs(["📊 Simular Cuotas", "🤝 Liquidación Paz y Salvo"])
            
            with tab_sim:
                st.markdown("<br>", unsafe_allow_html=True)
                # AQUÍ ESTÁ EL TOGGLE QUE ME PEDISTE NO QUITAR
                modo_cliente = st.toggle("📸 Activar Vista Cliente (Oculta información sensible)")
                if 'tasa_simulador' not in st.session_state: st.session_state['tasa_simulador'] = 3.0
                    
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    # Inicia en ceros según tu petición
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
                    else:
                        sim_tasa = st.session_state['tasa_simulador']
                    
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
                        
                        df_plan = generar_plan_pagos_real(datos_paz['id_credito'], cursor)
                        st.dataframe(df_plan.style.map(color_estado_cuota, subset=['Estado Actual']), width='stretch')

        elif menu_seleccionado == "inventario":
            st.markdown("<h2>Gestión de Inventario 📦</h2>", unsafe_allow_html=True)
            tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Equipos Disponibles", "📥 Ingresar Nuevos Equipos", "📜 Historial de Ventas"])
            
            with tab_inv1:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT imei AS 'Serial/IMEI', categoria AS 'Tipo', marca AS 'Marca', modelo AS 'Modelo', color AS 'Color', cantidad AS 'Unidades', costo_adquisicion AS 'Costo Unidad' FROM Inventario WHERE estado = 'Disponible'")
                df_inventario = pd.DataFrame(cursor.fetchall())
                
                c1, c2 = st.columns(2)
                c1.metric("📦 Productos Físicos Diferentes", f"{len(df_inventario)}")
                if not df_inventario.empty:
                    c2.metric("💰 Dinero Invertido en Stock", fmt_cop(sum([float(r['Costo Unidad']) * int(r['Unidades']) for _, r in df_inventario.iterrows()])))
                    df_inventario['Costo Unidad'] = df_inventario['Costo Unidad'].apply(fmt_cop)
                    st.dataframe(df_inventario, width='stretch')
                else: st.info("No hay inventario disponible.")

            with tab_inv2:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_bolsa, nombre_bolsa, saldo_actual FROM Bolsas_Capital")
                opc_bolsas = {f"{b['nombre_bolsa']} (Dinero en caja: {fmt_cop(b['saldo_actual'])})": b for b in cursor.fetchall()}

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
                            # Nuevos campos de Lotes y Trazabilidad
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

                            c5, c6 = st.columns(2)
                            with c5:
                                bolsa = st.selectbox("¿De qué caja salió la plata?", options=list(opc_bolsas.keys()), index=None)
                            with c6:
                                if bolsa:
                                    costo = st.number_input("Costo de Compra (Por 1 Unidad)", min_value=0, step=10000, value=0)
                                    if st.button("Guardar en Inventario", width='stretch'):
                                        dat_b = opc_bolsas[bolsa]
                                        costo_total = costo * cantidad
                                        if costo_total > float(dat_b['saldo_actual']): st.error("No hay suficiente dinero en esa caja para pagar esta mercancía.")
                                        elif not mod_fin: st.warning("El modelo es obligatorio.")
                                        else:
                                            # Insertar ciclo por cantidad
                                            for _ in range(cantidad):
                                                imei_final = imei_in if (cantidad == 1 and imei_in) else f"SYS-{str(uuid.uuid4())[:8].upper()}"
                                                cursor.execute("""
                                                    INSERT INTO Inventario (imei, categoria, marca, modelo, tipo_ingreso, id_bolsa, costo_adquisicion, estado, id_usuario_registro, cantidad, color, factura, tienda_proveedor, nit_proveedor, celular_proveedor, fecha_compra) 
                                                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Disponible', %s, 1, %s, %s, %s, %s, %s, %s)
                                                """, (imei_final, cat_sel.split(" ")[1] if " " in cat_sel else cat_sel, marca_fin, f"{mod_fin} {cap_fin}".strip(), cond, dat_b['id_bolsa'], costo, st.session_state['id_usuario'], color, factura, proveedor, nit, cel_prov, datetime.date.today()))
                                            
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
            with st.form("f_cli"):
                st.subheader("Crear Perfil de Cliente")
                c1, c2, c3 = st.columns(3)
                doc = c1.text_input("Número de Cédula")
                nom = c2.text_input("Nombre Completo")
                tel = c3.text_input("Número Celular")
                
                c4, c5, c6 = st.columns(3)
                correo = c4.text_input("Correo Electrónico")
                ciudad = c5.text_input("Ciudad")
                barrio = c6.text_input("Barrio")
                
                c7, c8 = st.columns(2)
                direccion = c7.text_input("Dirección de Residencia")
                empresa = c8.text_input("Empresa o Negocio donde labora")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Guardar Cliente", width='stretch'):
                    if doc and nom:
                        try:
                            cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, direccion, barrio, ciudad, correo, empresa, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                           (doc, nom, tel, direccion, barrio, ciudad, correo, empresa, st.session_state['id_usuario']))
                            conn.commit(); st.toast("Cliente guardado exitosamente."); time.sleep(1); st.rerun()
                        except mysql.connector.Error: st.error("Ya existe un cliente con esta cédula.")
                    else: st.warning("La cédula y el nombre son obligatorios.")
            
            st.divider()
            cursor.execute("SELECT documento AS 'Cédula', nombre_completo AS 'Nombre', telefono AS 'Celular', ciudad AS 'Ciudad', empresa AS 'Trabajo' FROM Clientes")
            df_clientes = pd.DataFrame(cursor.fetchall())
            if not df_clientes.empty: st.dataframe(df_clientes, width='stretch')

        elif menu_seleccionado == "ventas":
            st.markdown("<h2>Registro de Ventas 📝</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
            clientes = cursor.fetchall()
            cursor.execute("SELECT imei, categoria, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
            inventario = cursor.fetchall()
            cursor.execute("SELECT nombre FROM Vendedores")
            vendedores = [v['nombre'] for v in cursor.fetchall()]
            
            # Avisos separados para que sea más claro
            if not clientes: st.warning("⚠️ No hay clientes creados. Ve a la pestaña 'Directorio de Clientes' para crear uno primero.")
            if not inventario: st.warning("⚠️ No hay equipos disponibles en bodega. Ingresa stock primero.")
            
            if clientes and inventario:
                opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                opc_eq = {f"[{e['categoria']}] {e['marca']} {e['modelo']} (Cod: {e['imei']})": e['imei'] for e in inventario}
                
                tipo_v = st.selectbox("Tipo de Venta:", ["Crédito Financiado a Cuotas", "Plan Separé (Sin Interés)", "Venta de Contado"], index=None, placeholder="Seleccione modalidad...")
                st.divider()
                
                if tipo_v:
                    with st.form("f_venta"):
                        cliente_sel = st.selectbox("Seleccionar Cliente", list(opc_cli.keys()))
                        
                        # MULTIPRODUCTO
                        st.markdown("#### Productos a llevar el cliente")
                        equipos_sel = st.multiselect("Selecciona uno o más equipos de la bodega:", list(opc_eq.keys()))
                        
                        st.markdown("#### Tiempos del Crédito")
                        c_f1, c_f2 = st.columns(2)
                        with c_f1: fecha_venta = st.date_input("Fecha de Venta", value=datetime.date.today())
                        with c_f2: f_cuota = st.date_input("Fecha de la Primera Cuota", value=sumar_meses_exactos(fecha_venta, 1))

                        c3, c4 = st.columns(2)
                        c_pers, c_fija = [], 0
                        
                        if "Financiado" in tipo_v:
                            with c3:
                                p_final = st.number_input("Valor Total Factura ($)", min_value=1, value=0, step=10000)
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
                                st.info(f"🔹 **Cuota Mensual Exacta:** {fmt_cop(c_fija)}")
                        
                        elif "Separé" in tipo_v:
                            with c3:
                                p_final = st.number_input("Valor Total a Pagar ($)", min_value=1, value=0, step=10000)
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
                            st.write(f"Saldo pendiente a diferir: {fmt_cop(s_dif)}")
                            for idx in range(plazo):
                                x1, x2 = st.columns(2)
                                with x1:
                                    v_c = st.number_input(f"Valor Cuota {idx+1}", min_value=0, value=int(s_dif/plazo), step=10000, key=f"v_{idx}")
                                    s_cuotas += v_c
                                with x2: 
                                    f_c = st.date_input(f"Fecha Límite Cuota {idx+1}", value=sumar_meses_exactos(f_cuota, idx), key=f"f_{idx}")
                                c_pers.append((idx+1, v_c, f_c))
                        else:
                            p_final = st.number_input("Valor Total Pagado de Contado ($)", min_value=1, value=0, step=10000)
                            vendedor_existente = st.selectbox("Vendedor", ["Seleccionar..."] + vendedores)
                            nuevo_vendedor = st.text_input("O crear nuevo:")
                            comis = st.number_input("Comisión Asesor ($)", min_value=0, step=10000, value=0)
                            ab_init, plazo, tasa = p_final, 0, 0.0

                        st.divider()
                        if st.form_submit_button("Registrar Venta en Sistema", width='stretch'):
                            if not equipos_sel: st.error("Debes seleccionar mínimo un equipo para vender.")
                            elif p_final <= 0: st.error("El valor del equipo debe ser mayor a cero.")
                            else:
                                vendedor_final = nuevo_vendedor if nuevo_vendedor else (vendedor_existente if vendedor_existente != "Seleccionar..." else None)
                                if comis > 0 and not vendedor_final: st.error("Asigna un vendedor para pagarle su comisión.")
                                elif "Separé" in tipo_v and s_cuotas != (p_final - ab_init): st.error("Las cuotas no suman el total de la deuda.")
                                else:
                                    if nuevo_vendedor:
                                        try: cursor.execute("INSERT INTO Vendedores (nombre) VALUES (%s)", (nuevo_vendedor,))
                                        except: pass
                                        
                                    m_f = p_final - ab_init if "Contado" not in tipo_v else 0
                                    e_f = 'Activo' if "Contado" not in tipo_v else 'Pagado'
                                    v_c_bd = c_fija if "Financiado" in tipo_v else (c_pers[0][1] if "Separé" in tipo_v else 0)
                                    
                                    primer_imei = opc_eq[equipos_sel[0]]
                                    cursor.execute("""INSERT INTO Creditos (id_cliente, imei, precio_venta, abono_inicial, monto_financiado, tasa_interes_mensual, plazo_meses, valor_cuota, estado, fecha_inicio, fecha_primera_cuota, valor_comision, asesor_comision, estado_comision, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (opc_cli[cliente_sel], primer_imei, p_final, ab_init, m_f, tasa/100.0, plazo, v_c_bd, e_f, fecha_venta.strftime('%Y-%m-%d'), f_cuota.strftime('%Y-%m-%d'), comis, vendedor_final, 'Por Pagar' if comis > 0 else 'No Aplica', st.session_state['id_usuario']))
                                    id_cr = cursor.lastrowid
                                    
                                    # MULTIPRODUCTO GUARDADO:
                                    for eq in equipos_sel:
                                        imei_eq = opc_eq[eq]
                                        cursor.execute("INSERT INTO Creditos_Items (id_credito, imei) VALUES (%s, %s)", (id_cr, imei_eq))
                                        cursor.execute("UPDATE Inventario SET estado = 'Vendido' WHERE imei = %s", (imei_eq,))
                                    
                                    if "Separé" in tipo_v:
                                        for n_c, v_c, f_c in c_pers: cursor.execute("INSERT INTO Cuotas_Programadas (id_credito, numero_cuota, monto_esperado, fecha_vencimiento) VALUES (%s, %s, %s, %s)", (id_cr, n_c, v_c, f_c.strftime('%Y-%m-%d')))
                                    
                                    if ("Contado" not in tipo_v and ab_init > 0) or "Contado" in tipo_v: 
                                        cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (ab_init if "Contado" not in tipo_v else p_final,))
                                        
                                    if comis > 0 and vendedor_final:
                                        cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, vendedor, id_credito, id_usuario_registro) VALUES (%s, %s, %s, 'Por Pagar', %s, %s, %s)", (f"Comisión Venta - {vendedor_final} (Cliente: {cliente_sel.split(' - ')[1]})", comis, datetime.date.today(), vendedor_final, id_cr, st.session_state['id_usuario']))
                                        
                                    conn.commit(); st.toast("Venta y contrato guardados exitosamente."); time.sleep(1.5); st.rerun()

        elif menu_seleccionado == "pagos":
            st.markdown("<h2>Caja y Recaudos 💰</h2>", unsafe_allow_html=True)
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.imei, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota, c.plazo_meses, i.marca, i.modelo FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay créditos pendientes por cobrar.")
            else:
                opc_c = {f"{c['nombre_completo']} (Equipo: {c['marca']} {c['modelo']})": c for c in activos}
                sel_titular = st.selectbox("Buscar Cliente para recibir pago:", list(opc_c.keys()), index=None, placeholder="Escribe el nombre del cliente...")
                
                if sel_titular:
                    dat = opc_c[sel_titular]
                    
                    cursor.execute("SELECT id_pago, monto_recibido, fecha_pago, tipo_pago, capital_abonado, interes_cobrado FROM Pagos WHERE id_credito = %s ORDER BY fecha_pago DESC", (dat['id_credito'],))
                    hist = cursor.fetchall()
                    
                    cap_pagado = sum([float(p['capital_abonado']) for p in hist])
                    s_pend = float(dat['monto_financiado']) - cap_pagado
                    v_cuota_bd = int(dat['valor_cuota']) if dat['valor_cuota'] else 0
                    
                    # CÁLCULO PAZ Y SALVO
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
                        with x1: 
                            monto = st.number_input("Dinero Recibido del Cliente ($)", value=v_cuota_bd, min_value=0, step=10000)
                        with x2: fecha_pago_efectiva = st.date_input("Fecha en que entregó el dinero", value=None)
                        
                        tipo = st.selectbox("Tipo de Pago", ["Pago de Cuota Mensual", "Abono Extra (Reduce el valor de la cuota)", "Abono Extra (Reduce el tiempo del crédito)"], index=0)
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Registrar Pago", width='stretch'):
                            if monto <= 0: st.error("El monto debe ser mayor a cero.")
                            elif fecha_pago_efectiva is None: st.error("Seleccione la fecha de pago.")
                            else:
                                interes = round(s_pend * float(dat['tasa_interes_mensual']), 2)
                                cap_abono = 0.0 if monto <= interes else monto - interes
                                
                                cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s)", (dat['id_credito'], monto, tipo, cap_abono, min(monto, interes), fecha_pago_efectiva.strftime('%Y-%m-%d %H:%M:%S'), st.session_state['id_usuario']))
                                cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (monto,))
                                
                                nuevo_saldo = s_pend - cap_abono
                                if nuevo_saldo <= 0: 
                                    cursor.execute("UPDATE Creditos SET estado = 'Pagado' WHERE id_credito = %s", (dat['id_credito'],))
                                    st.balloons()
                                else:
                                    if "Reduce el valor de la cuota" in tipo:
                                        cursor.execute("SELECT COUNT(*) as pagadas FROM Pagos WHERE id_credito = %s AND tipo_pago LIKE '%%Cuota%%'", (dat['id_credito'],))
                                        pag_res = cursor.fetchone()
                                        pagadas = int(pag_res['pagadas']) if pag_res and pag_res['pagadas'] else 0
                                        meses_restantes = dat['plazo_meses'] - pagadas
                                        if meses_restantes <= 0: meses_restantes = 1
                                        i_m = float(dat['tasa_interes_mensual'])
                                        nueva_cuota = nuevo_saldo * (i_m * (1 + i_m)**meses_restantes) / (((1 + i_m)**meses_restantes) - 1) if i_m > 0 else nuevo_saldo / meses_restantes
                                        cursor.execute("UPDATE Creditos SET valor_cuota = %s WHERE id_credito = %s", (int(round(nueva_cuota)), dat['id_credito']))
                                
                                conn.commit(); st.toast("Dinero ingresado a la caja.", icon='✅'); time.sleep(1.5); st.rerun()

                    st.markdown("<br>### 💸 Historial de este Crédito", unsafe_allow_html=True)
                    if hist:
                        df_trans = pd.DataFrame(hist)
                        df_trans.rename(columns={'fecha_pago': 'Fecha', 'tipo_pago': 'Motivo', 'monto_recibido': 'Dinero Entregado', 'capital_abonado': 'Abono a Capital', 'interes_cobrado': 'Cobro de Interés'}, inplace=True)
                        for col in ['Dinero Entregado', 'Abono a Capital', 'Cobro de Interés']: df_trans[col] = df_trans[col].apply(fmt_cop)
                        st.dataframe(df_trans[['Fecha', 'Motivo', 'Dinero Entregado', 'Abono a Capital', 'Cobro de Interés']], width='stretch')
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
                    st.markdown("<h4 style='color:#0052D4;'>📥 Anular un Pago Recibido</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT p.id_pago, cl.nombre_completo, p.monto_recibido, p.fecha_pago, p.tipo_pago FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY p.id_pago DESC LIMIT 50")
                    pagos_db = cursor.fetchall()
                    if pagos_db:
                        opc_pagos = {f"[{p['fecha_pago'].strftime('%Y-%m-%d')}] {p['nombre_completo']} ({fmt_cop(p['monto_recibido'])}) - {p['tipo_pago']}": p for p in pagos_db}
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
                    else: st.info("No hay pagos recientes.")

                with c2:
                    st.markdown("<h4 style='color:#0052D4;'>🚨 Anular Venta Completa</h4>", unsafe_allow_html=True)
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
                                
                                # Multi-product revert
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
                    else: st.info("No hay ventas para anular.")
                    
                with c3:
                    st.markdown("<h4 style='color:#0052D4;'>📦 Eliminar Equipo de Bodega</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT imei, marca, modelo, costo_adquisicion, id_bolsa FROM Inventario WHERE estado = 'Disponible'")
                    inv_db = cursor.fetchall()
                    if inv_db:
                        opc_inv = {f"{i['marca']} {i['modelo']} ({i['imei']})": i for i in inv_db}
                        with st.form("f_anular_hardware"):
                            inv_sel = st.selectbox("Seleccione el equipo a borrar", list(opc_inv.keys()), index=None)
                            if st.form_submit_button("Eliminar y Devolver Dinero a Caja", width='stretch') and inv_sel:
                                dat_i = opc_inv[inv_sel]
                                if float(dat_i['costo_adquisicion']) > 0: cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s WHERE id_bolsa = %s", (dat_i['costo_adquisicion'], dat_i['id_bolsa']))
                                cursor.execute("DELETE FROM Inventario WHERE imei = %s", (dat_i['imei'],))
                                conn.commit(); st.toast("Equipo eliminado."); time.sleep(1.5); st.rerun()
                    else: st.info("No hay equipos en bodega.")

        elif menu_seleccionado == "egresos":
            st.markdown("<h2>Egresos y Gastos 💸</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("No tienes permisos para ver gastos."); st.stop()
            
            tab_com, tab_gas = st.tabs(["🤝 Pago de Comisiones a Vendedores", "🧾 Registrar Gasto Operativo"])
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
                        if st.form_submit_button("Marcar como Pagada y Descontar de Caja", width='stretch') and sel:
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
                    desc = st.text_input("Motivo del Gasto (Ej: Arriendo, Luz, Papelería)")
                    m_g = st.number_input("Valor Pagado ($)", min_value=0, step=10000, value=0)
                    if st.form_submit_button("Registrar Gasto", width='stretch'):
                        if desc and m_g > 0:
                            cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, id_usuario_registro) VALUES (%s, %s, %s, 'Pagado', %s)", (desc, m_g, datetime.date.today(), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (m_g,))
                            conn.commit(); st.toast("Gasto guardado."); time.sleep(1); st.rerun()

        elif menu_seleccionado == "flujo":
            st.markdown("<h2>Socios e Inversores 📈</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Acceso denegado."); st.stop()
            
            tab_dash, tab_in, tab_out = st.tabs(["📊 Resumen de Deudas a Socios", "📥 Registrar Dinero de Socio", "📤 Pagarle a Socio"])
            
            with tab_dash:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT prestamista AS 'Nombre del Socio', monto_prestado AS 'Plata Prestada a DaTo', monto_total_pagar AS 'Retorno Acordado', saldo_pendiente AS 'Deuda Actual', fecha_prestamo AS 'Fecha' FROM Deudas_Fondeo ORDER BY fecha_prestamo DESC")
                df_inversores = pd.DataFrame(cursor.fetchall())
                
                cursor.execute("SELECT SUM(saldo_actual) as cap FROM Bolsas_Capital")
                cap = float(cursor.fetchone()['cap'] or 0)
                deuda = df_inversores['Deuda Actual'].sum() if not df_inversores.empty else 0
                
                c1, c2 = st.columns(2)
                c1.metric("💵 Total Dinero en Cajas", fmt_cop(cap))
                c2.metric("📉 Dinero a devolver a Socios", fmt_cop(deuda))
                
                if not df_inversores.empty:
                    for c in ['Plata Prestada a DaTo', 'Retorno Acordado', 'Deuda Actual']: df_inversores[c] = df_inversores[c].apply(fmt_cop)
                    st.dataframe(df_inversores, width='stretch')
                else: st.info("No hay dinero de socios registrado.")

            with tab_in:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("f_f_in"):
                    prov = st.text_input("Nombre del Socio / Inversor")
                    iny = st.number_input("Dinero Invertido (Entra a Caja) ($)", min_value=0, step=100000, value=0)
                    ret = st.number_input("Dinero Total a Devolver (Capital + Ganancia) ($)", min_value=0, step=100000, value=0)
                    if st.form_submit_button("Guardar Inversión", width='stretch'):
                        if prov and iny > 0:
                            cursor.execute("INSERT INTO Deudas_Fondeo (prestamista, monto_prestado, monto_total_pagar, saldo_pendiente, fecha_prestamo, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s)", (prov, iny, ret, ret, datetime.date.today(), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual + %s ORDER BY id_bolsa ASC LIMIT 1", (iny,))
                            conn.commit(); st.toast("Plata sumada a la caja."); time.sleep(1); st.rerun()

            with tab_out:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT id_deuda, prestamista, saldo_pendiente FROM Deudas_Fondeo WHERE saldo_pendiente > 0")
                deudas = cursor.fetchall()
                if deudas:
                    opc_d = {f"{d['prestamista']} (Le debemos: {fmt_cop(d['saldo_pendiente'])})": d for d in deudas}
                    with st.form("f_d_out"):
                        d_sel = st.selectbox("Seleccionar Socio", list(opc_d.keys()), index=None)
                        ab = st.number_input("Dinero a entregar (Se resta de la Caja) ($)", min_value=0, step=100000, value=0)
                        if st.form_submit_button("Registrar Pago a Socio", width='stretch') and d_sel:
                            id_d = opc_d[d_sel]['id_deuda']
                            cursor.execute("INSERT INTO Pagos_Deuda (id_deuda, monto_pagado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s)", (id_d, ab, datetime.date.today(), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Deudas_Fondeo SET saldo_pendiente = saldo_pendiente - %s WHERE id_deuda = %s", (ab, id_d))
                            cursor.execute("UPDATE Bolsas_Capital SET saldo_actual = saldo_actual - %s ORDER BY id_bolsa ASC LIMIT 1", (ab,))
                            conn.commit(); st.toast("Plata entregada al socio."); time.sleep(1); st.rerun()
                else: st.info("No hay deudas con socios.")

        elif menu_seleccionado == "reportes":
            st.markdown("<h2>Reportes y Estadísticas 📊</h2>", unsafe_allow_html=True)
            if not es_admin: st.error("Módulo de gerencia."); st.stop()
            
            tab_bi, tab_graf, tab_riesgo, tab_eficiencia = st.tabs(["🌐 Resumen Financiero", "📈 Ingresos", "⚖️ Estado de Cartera", "💸 Rentabilidad"])
            
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

            cursor.execute("SELECT SUM(cr.precio_venta - i.costo_adquisicion) as gan_equipos FROM Creditos cr JOIN Inventario i ON cr.imei = i.imei")
            ganancia_por_venta = float(cursor.fetchone()['gan_equipos'] or 0)
            cursor.execute("SELECT SUM(interes_cobrado) as interes FROM Pagos")
            ganancia_por_interes = float(cursor.fetchone()['interes'] or 0)
            cursor.execute("SELECT SUM(monto) as gastos FROM Gastos_Operativos")
            gastos_totales = float(cursor.fetchone()['gastos'] or 0)

            cursor.execute("SELECT SUM(monto_recibido) as t_rec FROM Pagos")
            total_recaudo_hist = float(cursor.fetchone()['t_rec'] or 0)
            cursor.execute("SELECT SUM(i.costo_adquisicion) as t_costo FROM Creditos c JOIN Inventario i ON c.imei = i.imei")
            total_costo_equipos = float(cursor.fetchone()['t_costo'] or 0)
            
            ganancia_neta_100 = total_recaudo_hist - total_costo_equipos - gastos_totales
            
            with tab_bi:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 30px; text-align: center; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); margin-bottom: 25px;">
                    <h3 style="color:#0052D4; margin:0; font-weight: 700;">VALOR TOTAL DE TU NEGOCIO HOY</h3>
                    <h1 style="color:#1E293B; font-size: 4.5rem; font-weight: 800; margin: 10px 0;">{fmt_cop(patrimonio_neto)}</h1>
                    <p style="color:#64748B; font-size: 15px; margin:0;">Plata en Cajas ({fmt_cop(cap)}) + Plata que deben los clientes ({fmt_cop(cartera_neta_calle)}) - Lo que debemos a Socios ({fmt_cop(deuda)})</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("✅ Ganancia Real Neta Histórica", fmt_cop(ganancia_neta_100))
                c_m2.metric("💳 Plata en la calle prestando", fmt_cop(cartera_neta_calle))

            with tab_graf:
                st.markdown("<br>", unsafe_allow_html=True)
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("<h4 style='color:#0052D4;'>📅 Dinero Cobrado por Mes</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT DATE_FORMAT(fecha_pago, '%Y-%m') as mes, SUM(monto_recibido) as total FROM Pagos GROUP BY mes ORDER BY mes ASC")
                    recaudos_mes = cursor.fetchall()
                    if recaudos_mes:
                        df_chart_rec = pd.DataFrame(recaudos_mes).set_index('mes')
                        st.bar_chart(df_chart_rec, color="#00A2FF")
                    else: st.info("Sin datos.")
                with col_g2:
                    st.markdown("<h4 style='color:#0052D4;'>📈 Ventas Totales por Mes</h4>", unsafe_allow_html=True)
                    cursor.execute("SELECT DATE_FORMAT(fecha_inicio, '%Y-%m') as mes, SUM(precio_venta) as total FROM Creditos GROUP BY mes ORDER BY mes ASC")
                    ventas_mes = cursor.fetchall()
                    if ventas_mes:
                        df_chart_ven = pd.DataFrame(ventas_mes).set_index('mes')
                        st.area_chart(df_chart_ven, color="#0052D4")
                    else: st.info("Sin datos.")

            with tab_riesgo:
                st.markdown("<br>", unsafe_allow_html=True)
                cursor.execute("SELECT estado, COUNT(*) as cantidad FROM Creditos GROUP BY estado")
                estados_credito = cursor.fetchall()
                c_r1, c_r2 = st.columns([1.5, 1])
                with c_r1:
                    recup_perc = (cartera_recaudada / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Tasa de Recuperación Total:** {recup_perc:.1f}%")
                    st.progress(min(int(recup_perc), 100))
                    mora_perc = ((cartera_colocada - cartera_recaudada) / cartera_colocada * 100) if cartera_colocada > 0 else 0
                    st.write(f"**Por cobrar en la calle:** {mora_perc:.1f}%")
                    st.progress(min(int(mora_perc), 100))
                with c_r2:
                    if estados_credito:
                        df_est = pd.DataFrame(estados_credito)
                        df_est.columns = ['Estado del Crédito', 'Cantidad']
                        st.bar_chart(df_est.set_index('Estado del Crédito'), color="#00A2FF")

            with tab_eficiencia:
                st.markdown("<br>", unsafe_allow_html=True)
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown("<h4 style='color:#0052D4;'>💎 ¿De dónde sale la ganancia?</h4>", unsafe_allow_html=True)
                    df_ingresos = pd.DataFrame([{"Origen": "Venta de Equipos", "Valor": ganancia_por_venta}, {"Origen": "Cobro de Intereses", "Valor": ganancia_por_interes}])
                    st.bar_chart(df_ingresos.set_index("Origen"), color="#10B981")
                with col_e2:
                    st.markdown("<h4 style='color:#0052D4;'>💸 ¿En qué se va la plata?</h4>", unsafe_allow_html=True)
                    df_egresos = pd.DataFrame([{"Gasto": "Costos y Comisiones Operativas", "Valor": gastos_totales}])
                    st.bar_chart(df_egresos.set_index("Gasto"), color="#DC2626")

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
                        n_nombre = st.text_input("Nombre Completo")
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

# === SEGURO ANTI-FUGAS DE MEMORIA ===
try:
    if 'cursor' in locals() and cursor: cursor.close()
    if 'conn' in locals() and conn and conn.is_connected(): conn.close()
except Exception:
    pass

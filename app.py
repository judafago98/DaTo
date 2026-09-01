import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
import datetime
import time
import uuid
import calendar
import os

# ==========================================
# 🛠️ AUTO-MIGRACIÓN DE BASE DE DATOS
# ==========================================
def auto_fix_db(cursor, conn):
    try: cursor.execute("ALTER TABLE Pagos MODIFY COLUMN tipo_pago VARCHAR(255)"); conn.commit()
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

    # Tablas para Vendedores y Multiproducto
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Vendedores (id_vendedor INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) UNIQUE)"); conn.commit()
    except Exception: pass
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Creditos_Items (id INT AUTO_INCREMENT PRIMARY KEY, id_credito INT, imei VARCHAR(100))"); conn.commit()
    except Exception: pass

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DaTo | Tecnología con Respaldo", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# ==========================================
# 🎨 UI CORPORATIVA (TEMA CLARO, CERO ROJOS, LOGO OFICIAL)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #1E293B !important; }
        .stApp { background-color: #F8FAFC !important; background-image: none !important; }

        /* Pestañas (Tabs) Azules */
        div[data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #E2E8F0 !important; }
        div[data-baseweb="tab"] { color: #64748B !important; font-weight: 600 !important; padding-bottom: 10px !important; }
        div[data-baseweb="tab"][aria-selected="true"] { color: #00A2FF !important; border-bottom: 3px solid #00A2FF !important; }
        div[data-baseweb="tab-highlight"] { background-color: transparent !important; }
        
        /* Tarjetas Blancas */
        div[data-testid="stForm"], .card-panel {
            background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important; padding: 24px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }

        /* Inputs Limpios */
        div[data-testid="stTextInput"] div[data-baseweb="input"], 
        div[data-testid="stNumberInput"] div[data-baseweb="input"], 
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] {
            border-radius: 8px !important; border: 1px solid #CBD5E1 !important; background-color: #FFFFFF !important; color: #1E293B !important;
        }
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within, 
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"]:focus-within {
            border-color: #00A2FF !important; box-shadow: 0 0 0 2px rgba(0, 162, 255, 0.2) !important;
        }

        /* Botones Azules */
        .stButton>button {
            background: #00A2FF !important; color: #FFFFFF !important; border: none !important;
            border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease; width: 100% !important;
        }
        .stButton>button:hover { background: #0088FF !important; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0, 162, 255, 0.3) !important; }

        /* Sidebar Limpio */
        [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: #F1F5F9 !important; border-radius: 8px !important; padding: 10px 15px !important; margin: 4px 10px !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
            background: #E0F2FE !important; border-left: 4px solid #00A2FF !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] div[dir="auto"] {
            color: #00A2FF !important; font-weight: 700 !important;
        }
        
        h1, h2, h3 { color: #003366 !important; font-weight: 800 !important; }
        h4, h5 { color: #1E293B !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

def renderizar_logo(es_sidebar=False):
    padding = "15px" if es_sidebar else "30px 20px"
    st.markdown(f"""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; padding: {padding}; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);'>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <svg width="45" height="45" viewBox="0 0 100 100">
                    <polygon points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5" fill="none" stroke="#003366" stroke-width="8" stroke-linejoin="round"/>
                    <polygon points="50,15 85,32.5 85,67.5 50,85 15,67.5 15,32.5" fill="none" stroke="#00A2FF" stroke-width="3" stroke-linejoin="round"/>
                    <path d="M55,25 L35,55 L48,55 L42,80 L65,45 L52,45 Z" fill="#00A2FF"/>
                </svg>
                <h1 style='color: #00A2FF; font-size: 2.5rem; font-weight: 800; margin:0; letter-spacing: -1px;'>DaTo</h1>
            </div>
            <p style='text-align: center; color: #00A2FF; margin-top: 5px; margin-bottom: 0; font-weight: 500; font-size: 0.9rem;'>Tecnología con respaldo</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🛡️ FUNCIONES Y CÁLCULOS FINANCIEROS
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
            plan.append({'Cuota': f"Número {c['numero_cuota']}", 'Fecha Límite': c['fecha_vencimiento'], 'Valor': fmt_cop(esperado), 'Estado': est, 'Fecha de Pago Real': f_pago_mostrar})
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
            plan.append({'Cuota': f"Mes {i}", 'Fecha Límite': f_venc.strftime('%Y-%m-%d'), 'Valor': fmt_cop(esperado), 'Estado': est, 'Fecha de Pago Real': f_pago_mostrar})
    return pd.DataFrame(plan)

# ==========================================
# 🌐 CONEXIÓN BLINDADA POR POOL
# ==========================================
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
    st.error(f"🌐 No se pudo conectar a la base de datos. Detalle: {e}"); st.stop()

# ==========================================
# 🔐 SISTEMA DE LOGIN DUAL (ADMIN VS CLIENTE)
# ==========================================
if 'logeado' not in st.session_state: st.session_state['logeado'] = False
if 'id_usuario' not in st.session_state: st.session_state['id_usuario'] = None
if 'nombre_usuario' not in st.session_state: st.session_state['nombre_usuario'] = None
if 'rol' not in st.session_state: st.session_state['rol'] = None

if not st.session_state['logeado']:
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        renderizar_logo(es_sidebar=False)
        tab_admin, tab_cliente = st.tabs(["💼 Equipo DaTo", "👤 Portal Clientes"])
        
        with tab_admin:
            with st.form("form_login"):
                st.markdown("### Acceso Corporativo")
                usuario_input = st.text_input("Usuario")
                password_input = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar", width='stretch'):
                    cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                    usuario_db = cursor.fetchone()
                    if usuario_db:
                        st.session_state.update({'logeado': True, 'id_usuario': usuario_db['id_usuario'], 'nombre_usuario': usuario_db['nombre_completo'], 'rol': usuario_db['rol']})
                        st.rerun()
                    else: st.error("Usuario o contraseña incorrectos.")
                    
        with tab_cliente:
            with st.form("form_login_cliente"):
                st.markdown("### Bienvenido a tu Autogestión")
                st.write("Consulta el estado de tus productos ingresando tu documento.")
                cedula_cliente = st.text_input("Número de Documento (C.C.)")
                if st.form_submit_button("Consultar mi cuenta", width='stretch'):
                    cursor.execute("SELECT * FROM Clientes WHERE documento = %s", (cedula_cliente,))
                    cli_db = cursor.fetchone()
                    if cli_db:
                        st.session_state.update({'logeado': True, 'rol': 'Cliente', 'id_cliente': cli_db['id_cliente'], 'nombre_cliente': cli_db['nombre_completo']})
                        st.rerun()
                    else: st.error("No encontramos información asociada a esta cédula.")

else:
    # ==========================================
    # 📱 PORTAL VISIÓN CLIENTE
    # ==========================================
    if st.session_state['rol'] == 'Cliente':
        st.markdown(f"<h1 style='text-align:center;'>👋 ¡Hola, {st.session_state['nombre_cliente'].split()[0]}!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748B; font-size: 1.1rem;'>Este es el estado actual de tus productos con DaTo.</p><br>", unsafe_allow_html=True)
        
        cursor.execute("""
            SELECT c.id_credito, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, c.tasa_interes_mensual, c.estado 
            FROM Creditos c WHERE c.id_cliente = %s AND c.estado = 'Activo'
        """, (st.session_state['id_cliente'],))
        creditos_cliente = cursor.fetchall()
        
        if not creditos_cliente:
            st.markdown("""
            <div style="background: #ECFDF5; border: 1px solid #34D399; border-radius: 12px; padding: 30px; text-align: center;">
                <h2 style="color: #059669; margin: 0;">¡Estás al día! 🎉</h2>
                <p style="color: #047857; margin-top: 10px; font-size: 1.1rem;">No tienes saldos pendientes. ¿Listo para estrenar equipo?</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for cred in creditos_cliente:
                # Buscar equipos asociados (Multiproducto o Antiguo)
                cursor.execute("SELECT i.marca, i.modelo FROM Creditos_Items ci JOIN Inventario i ON ci.imei = i.imei WHERE ci.id_credito = %s", (cred['id_credito'],))
                equipos = cursor.fetchall()
                if not equipos: 
                    cursor.execute("SELECT i.marca, i.modelo FROM Creditos c JOIN Inventario i ON c.imei = i.imei WHERE c.id_credito = %s", (cred['id_credito'],))
                    equipos = cursor.fetchall()
                
                nombres_equipos = " + ".join([f"{e['marca']} {e['modelo']}" for e in equipos])
                
                # Cálculos
                cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (cred['id_credito'],))
                cap_pag = cursor.fetchone()['cap'] or 0
                saldo_actual = float(cred['monto_financiado']) - float(cap_pag)
                pago_total = saldo_actual + (saldo_actual * float(cred['tasa_interes_mensual']))
                
                st.markdown(f"""
                <div class='card-panel' style='margin-bottom:30px; border-top: 5px solid #00A2FF !important;'>
                    <h3 style='text-align:center; color:#003366;'>📱 {nombres_equipos}</h3>
                    <div style='display:flex; justify-content:space-around; margin-top:30px; flex-wrap: wrap; gap: 20px;'>
                        <div style='text-align:center; background: #F8FAFC; padding: 20px; border-radius: 12px; min-width: 200px;'>
                            <p style='color:#64748B; margin-bottom:5px; font-weight: 600;'>Cuota Mensual</p>
                            <h2 style='color:#00A2FF; margin:0;'>{fmt_cop(cred['valor_cuota'])}</h2>
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
                else:
                    st.info("Aún no tienes pagos registrados en este contrato.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Cerrar Sesión", type="primary"):
            st.session_state['logeado'] = False; st.rerun()

    # ==========================================
    # 💼 PORTAL ADMINISTRATIVO (EQUIPO DATO)
    # ==========================================
    else:
        es_admin = st.session_state['rol'] in ['Admin', 'Administrador']
        
        MODULOS_TOTALES = {
            "🔮 Cotizador y Simulación": "simulador",
            "📦 Bodega e Inventario": "inventario",
            "👥 Directorio de Clientes": "clientes",
            "📝 Registro de Ventas": "ventas",
            "💰 Caja y Pagos": "pagos",
            "⏰ Cartera y Vencimientos": "vencimientos",
            "📱 Mensajes y Estados de Cuenta": "notificar",
            "📜 Historial y Anulaciones": "historial",
            "💸 Egresos y Comisiones": "egresos",
            "📈 Socios y Fondeo": "flujo",
            "📊 Reportes y Estadísticas": "reportes",
            "⚙️ Configuración de Accesos": "config_roles"
        }

        with st.sidebar:
            renderizar_logo(es_sidebar=True)
            st.markdown(f"<div style='text-align:center; color:#64748B;'>Usuario: <b>{st.session_state['nombre_usuario']}</b><br>Nivel: {str(st.session_state['rol'])}</div><br>", unsafe_allow_html=True)
            
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

        # ------------------------------------------
        # 🏠 PANEL PRINCIPAL
        # ------------------------------------------
        if menu_seleccionado == "inicio":
            st.markdown("## Resumen del Negocio")
            cursor.execute("SELECT SUM(monto_recibido) as t FROM Pagos WHERE DATE(fecha_pago) = CURDATE()")
            ingresos_hoy = cursor.fetchone()['t'] or 0
            
            cursor.execute("SELECT SUM(monto_financiado) as mf FROM Creditos WHERE estado = 'Activo'")
            cartera_colocada = cursor.fetchone()['mf'] or 0
            
            cursor.execute("SELECT SUM(capital_abonado) as ca FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito WHERE c.estado = 'Activo'")
            cartera_recaudada = cursor.fetchone()['ca'] or 0
            
            cartera_calle = cartera_colocada - cartera_recaudada
            
            cursor.execute("SELECT SUM(cantidad) as c FROM Inventario WHERE estado = 'Disponible'")
            unidades_bodega = cursor.fetchone()['c'] or 0
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Recaudo Hoy</h5><h2 style='color:#10B981;'>{fmt_cop(ingresos_hoy)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Capital en la Calle</h5><h2 style='color:#00A2FF;'>{fmt_cop(cartera_calle)}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Equipos en Bodega</h5><h2 style='color:#64748B;'>{unidades_bodega} Unds.</h2></div>", unsafe_allow_html=True)

        # ------------------------------------------
        # 🔮 COTIZADOR Y SIMULACIÓN
        # ------------------------------------------
        elif menu_seleccionado == "simulador":
            st.markdown("## Cotizador Rápido")
            tab_sim, tab_paz = st.tabs(["🧮 Simular Cuotas", "🤝 Consultar Paz y Salvo"])
            
            with tab_sim:
                st.write("Calcula cuotas para clientes rápidamente. Los valores inician en cero.")
                c1, c2 = st.columns(2)
                sim_precio = c1.number_input("Valor del Equipo ($)", min_value=0, value=0, step=10000)
                sim_abono = c2.number_input("Abono Inicial ($)", min_value=0, value=0, step=10000)
                sim_plazo = c1.number_input("Meses a Financiar", min_value=1, max_value=72, value=6)
                sim_tasa = c2.selectbox("Tasa de Interés Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                
                if sim_precio > 0:
                    sim_capital = sim_precio - sim_abono
                    i_m = sim_tasa / 100.0
                    sim_cuota = sim_capital * (i_m * (1 + i_m)**sim_plazo) / (((1 + i_m)**sim_plazo) - 1) if sim_tasa > 0 else sim_capital / sim_plazo
                    st.success(f"🔹 **Cuota Mensual Estimada:** {fmt_cop(int(round(sim_cuota)))}")
            
            with tab_paz:
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.documento, i.modelo, c.monto_financiado, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente JOIN Inventario i ON c.imei = i.imei WHERE c.estado = 'Activo'")
                creditos_act = cursor.fetchall()
                if not creditos_act: st.info("No hay clientes con saldos activos.")
                else:
                    opc_paz = {f"{c['documento']} | {c['nombre_completo']} ({c['modelo']})": c for c in creditos_act}
                    sel_paz = st.selectbox("Buscar cliente:", list(opc_paz.keys()), index=None)
                    if sel_paz:
                        datos_paz = opc_paz[sel_paz]
                        cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (datos_paz['id_credito'],))
                        res = cursor.fetchone()
                        saldo_capital = float(datos_paz['monto_financiado']) - float(res['cap'] if res and res['cap'] else 0.0)
                        interes_mes = saldo_capital * float(datos_paz['tasa_interes_mensual'])
                        
                        st.markdown(f"""
                        <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 12px; padding: 25px; text-align: center;">
                            <h3 style="color:#047857; margin:0;">PAGO TOTAL PARA LIQUIDAR HOY</h3>
                            <h1 style="color:#10B981; font-size: 3.5rem; margin: 10px 0;">{fmt_cop(saldo_capital + interes_mes)}</h1>
                            <p style="color:#64748B; margin:0;">Saldo a Capital ({fmt_cop(saldo_capital)}) + Interés del Mes ({fmt_cop(interes_mes)})</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.dataframe(generar_plan_pagos_real(datos_paz['id_credito'], cursor), width='stretch')

        # ------------------------------------------
        # 📦 BODEGA E INVENTARIO
        # ------------------------------------------
        elif menu_seleccionado == "inventario":
            st.markdown("## Gestión de Bodega e Inventario")
            tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Equipos Disponibles", "📥 Ingresar Mercancía", "📜 Historial de Salidas"])
            
            with tab_inv1:
                cursor.execute("SELECT marca AS Marca, modelo AS Modelo, SUM(cantidad) AS Unidades, costo_adquisicion AS Costo_Unitario FROM Inventario WHERE estado = 'Disponible' GROUP BY marca, modelo, costo_adquisicion")
                df_inventario = pd.DataFrame(cursor.fetchall())
                if not df_inventario.empty:
                    df_inventario['Costo_Unitario'] = df_inventario['Costo_Unitario'].apply(fmt_cop)
                    st.dataframe(df_inventario, width='stretch')
                else: st.info("Bodega vacía.")

            with tab_inv2:
                # Catálogo Dinámico (Aprende de la base de datos)
                cursor.execute("SELECT DISTINCT marca FROM Inventario WHERE marca IS NOT NULL")
                marcas_existentes = [m['marca'] for m in cursor.fetchall()]
                
                with st.form("ingreso_inventario"):
                    st.info("💡 Si recibiste un lote, escribe el total en 'Cantidad' en lugar de ingresarlos uno por uno.")
                    c1, c2, c3 = st.columns(3)
                    marca_sel = c1.selectbox("Marca", marcas_existentes + ["Agregar Nueva Marca..."])
                    marca_final = c1.text_input("Escribe la nueva marca:") if marca_sel == "Agregar Nueva Marca..." else marca_sel
                    
                    modelos_existentes = []
                    if marca_sel != "Agregar Nueva Marca...":
                        cursor.execute("SELECT DISTINCT modelo FROM Inventario WHERE marca = %s", (marca_sel,))
                        modelos_existentes = [m['modelo'] for m in cursor.fetchall()]
                    
                    modelo_sel = c2.selectbox("Modelo / Capacidad", modelos_existentes + ["Agregar Nuevo Modelo..."])
                    modelo_final = c2.text_input("Escribe el nuevo modelo:") if modelo_sel == "Agregar Nuevo Modelo..." else modelo_sel
                    
                    color = c3.text_input("Color")
                    
                    c4, c5, c6 = st.columns(3)
                    imei = c4.text_input("IMEI / Serial (Opcional si es lote genérico)")
                    cantidad = c5.number_input("Cantidad de Unidades", min_value=1, value=1)
                    costo = c6.number_input("Costo de Compra (Por Unidad)", min_value=0, value=0, step=10000)
                    
                    st.markdown("#### Datos de Facturación (Opcional)")
                    p1, p2, p3, p4 = st.columns(4)
                    fecha_compra = p1.date_input("Fecha de Compra")
                    proveedor = p2.text_input("Tienda/Proveedor")
                    nit = p3.text_input("NIT Proveedor")
                    factura = p4.text_input("N° Factura")
                    
                    if st.form_submit_button("Guardar en Bodega", width='stretch'):
                        if not marca_final or not modelo_final: st.error("Marca y Modelo son obligatorios.")
                        else:
                            for i in range(cantidad):
                                imei_guardar = imei if (cantidad == 1 and imei) else f"SYS-{str(uuid.uuid4())[:8].upper()}"
                                cursor.execute("""
                                    INSERT INTO Inventario (imei, categoria, marca, modelo, costo_adquisicion, estado, cantidad, color, factura, tienda_proveedor, nit_proveedor, fecha_compra, id_usuario_registro) 
                                    VALUES (%s, 'General', %s, %s, %s, 'Disponible', 1, %s, %s, %s, %s, %s, %s)
                                """, (imei_guardar, marca_final, modelo_final, costo, color, factura, proveedor, nit, fecha_compra, st.session_state['id_usuario']))
                            conn.commit(); st.success(f"¡{cantidad} unidad(es) ingresada(s)!"); time.sleep(1.5); st.rerun()

            with tab_inv3:
                cursor.execute("""
                    SELECT i.imei AS 'Serial/IMEI', CONCAT(i.marca, ' ', i.modelo) AS 'Equipo', i.costo_adquisicion AS 'Costo Real', IFNULL(cr.precio_venta, 0) AS 'Precio Venta', i.estado AS 'Estado', IFNULL(c.nombre_completo, 'En Bodega') AS 'Cliente Final'
                    FROM Inventario i LEFT JOIN Creditos_Items ci ON i.imei = ci.imei LEFT JOIN Creditos cr ON ci.id_credito = cr.id_credito LEFT JOIN Clientes c ON cr.id_cliente = c.id_cliente 
                    ORDER BY i.estado ASC
                """)
                df_hist = pd.DataFrame(cursor.fetchall())
                if not df_hist.empty:
                    df_hist['Costo Real'] = df_hist['Costo Real'].apply(fmt_cop)
                    df_hist['Precio Venta'] = df_hist['Precio Venta'].apply(lambda x: fmt_cop(x) if x > 0 else 'N/A')
                    st.dataframe(df_hist, width='stretch')
                else: st.info("Sin registros.")

        # ------------------------------------------
        # 👥 DIRECTORIO DE CLIENTES
        # ------------------------------------------
        elif menu_seleccionado == "clientes":
            st.markdown("## Base de Datos de Clientes")
            with st.form("f_cli"):
                st.subheader("Crear o Actualizar Cliente")
                c1, c2, c3 = st.columns(3)
                doc = c1.text_input("Cédula / Documento")
                nom = c2.text_input("Nombre Completo")
                tel = c3.text_input("Celular")
                
                c4, c5, c6 = st.columns(3)
                correo = c4.text_input("Correo Electrónico")
                ciudad = c5.text_input("Ciudad")
                barrio = c6.text_input("Barrio")
                
                c7, c8 = st.columns(2)
                direccion = c7.text_input("Dirección de Residencia")
                empresa = c8.text_input("Trabajo / Empresa")
                
                if st.form_submit_button("Guardar Cliente", width='stretch'):
                    if doc and nom:
                        try:
                            cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, direccion, barrio, ciudad, correo, empresa, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                           (doc, nom, tel, direccion, barrio, ciudad, correo, empresa, st.session_state['id_usuario']))
                            conn.commit(); st.toast("Cliente guardado."); time.sleep(1); st.rerun()
                        except mysql.connector.Error: st.error("Esta cédula ya está registrada.")
                    else: st.warning("Cédula y Nombre son obligatorios.")
            
            st.divider()
            cursor.execute("SELECT documento AS Cédula, nombre_completo AS Nombre, telefono AS Celular, ciudad AS Ciudad, empresa AS Empresa FROM Clientes")
            df_clientes = pd.DataFrame(cursor.fetchall())
            if not df_clientes.empty: st.dataframe(df_clientes, width='stretch')

        # ------------------------------------------
        # 📝 REGISTRO DE VENTAS (Multiproducto)
        # ------------------------------------------
        elif menu_seleccionado == "ventas":
            st.markdown("## Registro de Ventas")
            cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
            clientes = cursor.fetchall()
            cursor.execute("SELECT imei, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
            inventario = cursor.fetchall()
            cursor.execute("SELECT nombre FROM Vendedores")
            vendedores = [v['nombre'] for v in cursor.fetchall()]
            
            if not clientes or not inventario: st.warning("Necesitas clientes registrados y equipos en bodega.")
            else:
                opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                opc_eq = {f"{e['marca']} {e['modelo']} (Cod: {e['imei']})": e['imei'] for e in inventario}
                
                tipo_v = st.selectbox("Modalidad de Venta:", ["Crédito a Cuotas", "Plan Separé", "Pago de Contado"], index=None)
                
                if tipo_v:
                    with st.form("f_venta"):
                        cliente_sel = st.selectbox("Seleccionar Cliente", list(opc_cli.keys()))
                        equipos_sel = st.multiselect("Seleccionar Equipo(s) - Soporta múltiples para una sola factura", list(opc_eq.keys()))
                        
                        v1, v2 = st.columns(2)
                        if "Contado" not in tipo_v:
                            precio_total = v1.number_input("Valor Total Factura", min_value=1, value=0, step=10000)
                            ab_init = v2.number_input("Abono Inicial", min_value=0, value=0, step=10000)
                            plazo = v1.number_input("Meses a Financiar", min_value=1, value=6)
                            tasa = v2.selectbox("Tasa Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                        else:
                            precio_total = v1.number_input("Valor Pagado de Contado", min_value=1, value=0, step=10000)
                            ab_init, plazo, tasa = precio_total, 0, 0.0
                            
                        st.markdown("#### Comisiones")
                        cx1, cx2 = st.columns(2)
                        vendedor_existente = cx1.selectbox("Vendedor / Asesor", ["Seleccionar..."] + vendedores)
                        nuevo_vendedor = cx2.text_input("O crear nuevo Vendedor:")
                        comis = cx1.number_input("Comisión a Pagar por la Venta", min_value=0, step=10000, value=0)
                        
                        if st.form_submit_button("Guardar Venta", width='stretch'):
                            if not equipos_sel: st.error("Debes seleccionar al menos un producto.")
                            elif precio_total <= 0: st.error("El valor debe ser mayor a cero.")
                            else:
                                vendedor_final = nuevo_vendedor if nuevo_vendedor else (vendedor_existente if vendedor_existente != "Seleccionar..." else None)
                                if nuevo_vendedor:
                                    try: cursor.execute("INSERT INTO Vendedores (nombre) VALUES (%s)", (nuevo_vendedor,))
                                    except: pass
                                
                                m_f = precio_total - ab_init if "Contado" not in tipo_v else 0
                                e_f = 'Activo' if "Contado" not in tipo_v else 'Pagado'
                                
                                i_m = tasa / 100.0
                                cuota_fija = 0
                                if "Financiado" in tipo_v or "Crédito" in tipo_v:
                                    cuota_fija = int(round(m_f * (i_m * (1 + i_m)**plazo) / (((1 + i_m)**plazo) - 1))) if tasa > 0 else int(round(m_f / plazo))
                                
                                # Credito Maestro
                                primer_imei = opc_eq[equipos_sel[0]]
                                cursor.execute("""INSERT INTO Creditos (id_cliente, imei, precio_venta, abono_inicial, monto_financiado, tasa_interes_mensual, plazo_meses, valor_cuota, estado, fecha_inicio, fecha_primera_cuota, valor_comision, asesor_comision, estado_comision, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (opc_cli[cliente_sel], primer_imei, precio_total, ab_init, m_f, tasa/100.0, plazo, cuota_fija, e_f, datetime.date.today(), sumar_meses_exactos(datetime.date.today(), 1), comis, vendedor_final, 'Por Pagar' if comis > 0 else 'No Aplica', st.session_state['id_usuario']))
                                id_cr = cursor.lastrowid
                                
                                # Detalles Multi-Producto
                                for eq in equipos_sel:
                                    imei_eq = opc_eq[eq]
                                    cursor.execute("INSERT INTO Creditos_Items (id_credito, imei) VALUES (%s, %s)", (id_cr, imei_eq))
                                    cursor.execute("UPDATE Inventario SET estado = 'Vendido' WHERE imei = %s", (imei_eq,))
                                
                                # Comisiones
                                if comis > 0 and vendedor_final:
                                    cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, vendedor, id_credito, id_usuario_registro) VALUES (%s, %s, %s, 'Por Pagar', %s, %s, %s)", (f"Comisión Venta - {vendedor_final} (Cred #{id_cr})", comis, datetime.date.today(), vendedor_final, id_cr, st.session_state['id_usuario']))
                                
                                conn.commit(); st.success("Venta completada."); time.sleep(1.5); st.rerun()

        # ------------------------------------------
        # 💰 CAJA Y PAGOS
        # ------------------------------------------
        elif menu_seleccionado == "pagos":
            st.markdown("## Caja y Recepción de Pagos")
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay créditos pendientes de cobro.")
            else:
                opc_c = {f"{c['nombre_completo']} (Credito #{c['id_credito']})": c for c in activos}
                sel_titular = st.selectbox("Buscar cliente a cobrar:", list(opc_c.keys()), index=None)
                
                if sel_titular:
                    dat = opc_c[sel_titular]
                    
                    cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    cap_pagado = float(cursor.fetchone()['cap'] or 0)
                    saldo_pendiente = float(dat['monto_financiado']) - cap_pagado
                    interes_mes = saldo_pendiente * float(dat['tasa_interes_mensual'])
                    paz_salvo = saldo_pendiente + interes_mes
                    
                    st.markdown(f"""
                        <div style='display:flex; justify-content: space-around; background: #F8FAFC; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 25px;'>
                            <div style='text-align:center;'>
                                <p style='margin:0; color:#64748B;'>Cuota Mensual</p>
                                <h2 style='margin:0; color:#00A2FF;'>{fmt_cop(dat['valor_cuota'])}</h2>
                            </div>
                            <div style='text-align:center; border-left: 1px solid #CBD5E1; padding-left: 20px;'>
                                <p style='margin:0; color:#64748B;'>Saldo Pendiente</p>
                                <h2 style='margin:0; color:#64748B;'>{fmt_cop(saldo_pendiente)}</h2>
                            </div>
                            <div style='text-align:center; border-left: 1px solid #CBD5E1; padding-left: 20px; background: #ECFDF5; padding: 15px; border-radius: 8px;'>
                                <p style='margin:0; font-weight: bold; color:#047857;'>Pago Total (Paz y Salvo)</p>
                                <h2 style='margin:0; color:#10B981;'>{fmt_cop(paz_salvo)}</h2>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form("f_pago"):
                        monto = st.number_input("Dinero Recibido", value=int(dat['valor_cuota']), step=10000)
                        tipo = st.selectbox("Tipo de Abono", ["Cuota Normal", "Abono Extra (Reduce Cuota)", "Abono Extra (Reduce Plazo)"])
                        if st.form_submit_button("Registrar Pago", width='stretch'):
                            if monto <= 0: st.error("Monto inválido.")
                            else:
                                cap_abono = 0.0 if monto <= interes_mes else monto - interes_mes
                                cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                               (dat['id_credito'], monto, tipo, cap_abono, min(monto, interes_mes), datetime.datetime.now(), st.session_state['id_usuario']))
                                
                                si_nuevo = saldo_pendiente - cap_abono
                                if si_nuevo <= 0: 
                                    cursor.execute("UPDATE Creditos SET estado = 'Pagado' WHERE id_credito = %s", (dat['id_credito'],))
                                elif "Reduce Cuota" in tipo:
                                    cursor.execute("SELECT COUNT(*) as p FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                                    pagadas = cursor.fetchone()['p']
                                    meses_restantes = max(1, int(dat['plazo_meses']) - int(pagadas))
                                    i_m = float(dat['tasa_interes_mensual'])
                                    nueva_c = si_nuevo * (i_m * (1 + i_m)**meses_restantes) / (((1 + i_m)**meses_restantes) - 1) if i_m > 0 else si_nuevo / meses_restantes
                                    cursor.execute("UPDATE Creditos SET valor_cuota = %s WHERE id_credito = %s", (int(round(nueva_c)), dat['id_credito']))
                                
                                conn.commit(); st.success("Pago procesado."); time.sleep(1.5); st.rerun()

        # ------------------------------------------
        # ⏰ CARTERA Y VENCIMIENTOS
        # ------------------------------------------
        elif menu_seleccionado == "vencimientos":
            st.markdown("## Análisis de Cartera y Mora")
            cursor.execute("""
                SELECT cl.nombre_completo AS 'Cliente', cl.telefono AS 'Celular', c.valor_cuota AS 'Cuota', c.fecha_primera_cuota AS 'Fecha de Corte', 
                (c.monto_financiado - IFNULL((SELECT SUM(capital_abonado) FROM Pagos p WHERE p.id_credito = c.id_credito), 0)) AS 'Saldo Pendiente',
                c.tasa_interes_mensual
                FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo' ORDER BY c.fecha_primera_cuota ASC
            """)
            df = pd.DataFrame(cursor.fetchall())
            if df.empty: st.info("No hay carteras activas.")
            else:
                df['Paz y Salvo (Aprox)'] = df.apply(lambda r: float(r['Saldo Pendiente']) + (float(r['Saldo Pendiente']) * float(r['tasa_interes_mensual'])), axis=1)
                for c in ['Cuota', 'Saldo Pendiente', 'Paz y Salvo (Aprox)']: df[c] = df[c].apply(fmt_cop)
                df = df.drop(columns=['tasa_interes_mensual'])
                st.dataframe(df, width='stretch')

        # ------------------------------------------
        # 📱 MENSAJES Y ESTADOS DE CUENTA (WHATSAPP)
        # ------------------------------------------
        elif menu_seleccionado == "notificar":
            st.markdown("## Plantillas de WhatsApp")
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, cl.telefono, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, c.tasa_interes_mensual FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("Sin clientes activos para notificar.")
            else:
                opc_n = {f"{c['nombre_completo']}": c for c in activos}
                sel_cli = st.selectbox("Seleccionar Cliente para armar mensaje:", list(opc_n.keys()), index=None)
                
                if sel_cli:
                    dat = opc_n[sel_cli]
                    cursor.execute("SELECT SUM(capital_abonado) as cap, MAX(monto_recibido) as last_val, MAX(fecha_pago) as last_date FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    res_pag = cursor.fetchone()
                    cap_pag = float(res_pag['cap']) if res_pag and res_pag['cap'] else 0
                    last_val = float(res_pag['last_val']) if res_pag and res_pag['last_val'] else 0
                    last_date = res_pag['last_date']
                    
                    s_act = float(dat['monto_financiado']) - cap_pag
                    paz_y_salvo = s_act + (s_act * float(dat['tasa_interes_mensual']))
                    
                    msg = f"¡Hola {dat['nombre_completo']}! 👋 Te saludamos de DaTo.\n\nEste es el estado actual de tu cuenta:\n💵 *Cuota Mensual:* {fmt_cop(dat['valor_cuota'])}\n📉 *Saldo a Capital:* {fmt_cop(s_act)}\n💳 *Último pago recibido:* {fmt_cop(last_val) if last_val else '$0'} el {last_date.strftime('%Y-%m-%d') if last_date else 'N/A'}\n\n*💰 Si deseas pagar la totalidad hoy (Paz y Salvo): {fmt_cop(paz_y_salvo)}*\n\n¡Gracias por confiar en Tecnología con Respaldo!"
                    st.text_area("Texto listo para copiar y enviar a WhatsApp:", value=msg, height=250)

        # ------------------------------------------
        # 📜 HISTORIAL Y ANULACIONES
        # ------------------------------------------
        elif menu_seleccionado == "historial":
            st.markdown("## Auditoría y Correcciones")
            if not es_admin: st.error("Acceso denegado."); st.stop()
            
            tab_p, tab_v = st.tabs(["⚠️ Anular Pago", "🚨 Anular Venta Completa"])
            
            with tab_p:
                st.write("Si registraste un pago por error, elimínalo aquí.")
                cursor.execute("SELECT p.id_pago, cl.nombre_completo, p.monto_recibido, p.fecha_pago FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY p.id_pago DESC LIMIT 50")
                pagos_db = cursor.fetchall()
                if pagos_db:
                    opc_pagos = {f"[{p['fecha_pago'].strftime('%Y-%m-%d')}] {p['nombre_completo']} -> {fmt_cop(p['monto_recibido'])}": p for p in pagos_db}
                    with st.form("f_anular_pago"):
                        pago_sel = st.selectbox("Seleccionar Pago a Eliminar", list(opc_pagos.keys()))
                        if st.form_submit_button("Borrar Pago Permanentemente"):
                            dat_p = opc_pagos[pago_sel]
                            cursor.execute("SELECT id_credito FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                            id_c = cursor.fetchone()['id_credito']
                            cursor.execute("DELETE FROM Pagos WHERE id_pago = %s", (dat_p['id_pago'],))
                            cursor.execute("UPDATE Creditos SET estado = 'Activo' WHERE id_credito = %s", (id_c,))
                            conn.commit(); st.toast("Pago eliminado."); time.sleep(1); st.rerun()
                else: st.info("No hay pagos para anular.")

            with tab_v:
                st.write("Esto borrará la venta, los pagos asociados, devolverá los equipos a bodega y anulará las comisiones.")
                cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.abono_inicial FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente ORDER BY c.id_credito DESC")
                creds_db = cursor.fetchall()
                if creds_db:
                    opc_creds = {f"Venta #{c['id_credito']} - {c['nombre_completo']}": c for c in creds_db}
                    with st.form("f_anular_venta"):
                        cred_sel = st.selectbox("Seleccionar Venta a Anular", list(opc_creds.keys()))
                        if st.form_submit_button("Anular Venta y Restaurar Inventario"):
                            dat_c = opc_creds[cred_sel]
                            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                            # Devolver items a bodega
                            cursor.execute("SELECT imei FROM Creditos_Items WHERE id_credito = %s", (dat_c['id_credito'],))
                            for item in cursor.fetchall(): cursor.execute("UPDATE Inventario SET estado = 'Disponible' WHERE imei = %s", (item['imei'],))
                            # Borrar gastos/comisiones de este crédito
                            cursor.execute("DELETE FROM Gastos_Operativos WHERE id_credito = %s", (dat_c['id_credito'],))
                            # Borrar todo lo demás
                            cursor.execute("DELETE FROM Creditos_Items WHERE id_credito = %s", (dat_c['id_credito'],))
                            cursor.execute("DELETE FROM Cuotas_Programadas WHERE id_credito = %s", (dat_c['id_credito'],))
                            cursor.execute("DELETE FROM Pagos WHERE id_credito = %s", (dat_c['id_credito'],))
                            cursor.execute("DELETE FROM Creditos WHERE id_credito = %s", (dat_c['id_credito'],))
                            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            conn.commit(); st.toast("Venta anulada. Equipos devueltos a bodega."); time.sleep(1.5); st.rerun()

        # ------------------------------------------
        # 💸 EGRESOS Y COMISIONES
        # ------------------------------------------
        elif menu_seleccionado == "egresos":
            st.markdown("## Gastos y Comisiones")
            if not es_admin: st.error("Módulo restringido."); st.stop()
            
            tab_com, tab_gas = st.tabs(["🤝 Comisiones de Vendedores", "🧾 Registrar Gasto (Luz, Arriendo...)"])
            with tab_com:
                st.write("Comisiones pendientes generadas por ventas.")
                cursor.execute("SELECT id_gasto, descripcion, monto, vendedor FROM Gastos_Operativos WHERE estado_pago = 'Por Pagar'")
                comisiones = cursor.fetchall()
                if comisiones:
                    df_p = pd.DataFrame(comisiones)
                    df_p['Monto a Pagar'] = df_p['monto'].apply(fmt_cop)
                    st.dataframe(df_p[['descripcion', 'vendedor', 'Monto a Pagar']], width='stretch')
                    with st.form("f_com"):
                        sel = st.selectbox("Seleccionar para Pagar", list({f"{x['descripcion']} -> {fmt_cop(x['monto'])}": x['id_gasto'] for x in comisiones}.keys()))
                        if st.form_submit_button("Marcar como Pagada", width='stretch'):
                            id_g = {f"{x['descripcion']} -> {fmt_cop(x['monto'])}": x['id_gasto'] for x in comisiones}[sel]
                            cursor.execute("UPDATE Gastos_Operativos SET estado_pago = 'Pagado' WHERE id_gasto = %s", (id_g,))
                            conn.commit(); st.toast("Comisión pagada."); time.sleep(1); st.rerun()
                else: st.info("No debes comisiones en este momento.")
                
            with tab_gas:
                with st.form("f_g"):
                    desc = st.text_input("Concepto del Gasto")
                    m_g = st.number_input("Valor Pagado ($)", min_value=0, step=10000)
                    if st.form_submit_button("Guardar Gasto", width='stretch'):
                        if desc and m_g > 0:
                            cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, id_usuario_registro) VALUES (%s, %s, %s, 'Pagado', %s)", (desc, m_g, datetime.date.today(), st.session_state['id_usuario']))
                            conn.commit(); st.toast("Gasto registrado."); time.sleep(1); st.rerun()

        # ------------------------------------------
        # 📈 SOCIOS Y FONDEO
        # ------------------------------------------
        elif menu_seleccionado == "flujo":
            st.markdown("## Capitales de Socios")
            if not es_admin: st.error("Acceso denegado."); st.stop()
            tab_dash, tab_in, tab_out = st.tabs(["📊 Resumen Fondeo", "📥 Registrar Inversión", "📤 Pagar a Socio"])
            
            with tab_dash:
                cursor.execute("SELECT prestamista AS 'Socio/Inversor', monto_prestado AS 'Dinero Invertido', monto_total_pagar AS 'Retorno Acordado', saldo_pendiente AS 'Deuda Actual' FROM Deudas_Fondeo")
                df_inversores = pd.DataFrame(cursor.fetchall())
                if not df_inversores.empty:
                    for c in ['Dinero Invertido', 'Retorno Acordado', 'Deuda Actual']: df_inversores[c] = df_inversores[c].apply(fmt_cop)
                    st.dataframe(df_inversores, width='stretch')
                else: st.info("No hay dinero de socios registrado.")

            with tab_in:
                with st.form("f_f_in"):
                    prov = st.text_input("Nombre del Socio")
                    iny = st.number_input("Dinero que entrega a DaTo", min_value=0, step=100000)
                    ret = st.number_input("Dinero total que debemos devolverle (Capital + Ganancia)", min_value=0, step=100000)
                    if st.form_submit_button("Guardar Inversión"):
                        if prov and iny > 0:
                            cursor.execute("INSERT INTO Deudas_Fondeo (prestamista, monto_prestado, monto_total_pagar, saldo_pendiente, fecha_prestamo, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s)", (prov, iny, ret, ret, datetime.date.today(), st.session_state['id_usuario']))
                            conn.commit(); st.toast("Capital registrado."); time.sleep(1); st.rerun()

            with tab_out:
                cursor.execute("SELECT id_deuda, prestamista, saldo_pendiente FROM Deudas_Fondeo WHERE saldo_pendiente > 0")
                deudas = cursor.fetchall()
                if deudas:
                    opc_d = {f"{d['prestamista']} (Le debemos: {fmt_cop(d['saldo_pendiente'])})": d for d in deudas}
                    with st.form("f_d_out"):
                        d_sel = st.selectbox("Seleccionar Socio a Pagar", list(opc_d.keys()))
                        ab = st.number_input("Dinero a entregar hoy", min_value=0, step=10000)
                        if st.form_submit_button("Registrar Pago al Socio"):
                            id_d = opc_d[d_sel]['id_deuda']
                            cursor.execute("INSERT INTO Pagos_Deuda (id_deuda, monto_pagado, fecha_pago, id_usuario_registro) VALUES (%s, %s, %s, %s)", (id_d, ab, datetime.date.today(), st.session_state['id_usuario']))
                            cursor.execute("UPDATE Deudas_Fondeo SET saldo_pendiente = saldo_pendiente - %s WHERE id_deuda = %s", (ab, id_d))
                            conn.commit(); st.toast("Pago al socio registrado."); time.sleep(1); st.rerun()

        # ------------------------------------------
        # 📊 REPORTES Y ESTADÍSTICAS (BI)
        # ------------------------------------------
        elif menu_seleccionado == "reportes":
            st.markdown("## Métricas y Rentabilidad")
            if not es_admin: st.error("Módulo restringido."); st.stop()
            
            # Rentabilidad Base (Ingresos Totales vs Costos Equipos vs Gastos)
            cursor.execute("SELECT SUM(monto_recibido) as t_rec FROM Pagos")
            total_recaudo = float(cursor.fetchone()['t_rec'] or 0)
            
            cursor.execute("SELECT SUM(i.costo_adquisicion) as t_costo FROM Creditos_Items ci JOIN Inventario i ON ci.imei = i.imei")
            total_costo = float(cursor.fetchone()['t_costo'] or 0)
            
            cursor.execute("SELECT SUM(monto) as gastos FROM Gastos_Operativos")
            total_gastos = float(cursor.fetchone()['gastos'] or 0)
            
            ganancia_neta = total_recaudo - total_costo - total_gastos
            
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 30px; text-align: center;">
                <h3 style="color:#00A2FF; margin:0;">UTILIDAD NETA ESTIMADA DEL NEGOCIO</h3>
                <h1 style="color:#1E293B; font-size: 3.5rem; margin: 10px 0;">{fmt_cop(ganancia_neta)}</h1>
                <p style="color:#64748B;">Total cobrado a clientes - Costo de compra de los equipos vendidos - Gastos/Comisiones.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Ingresos Mes a Mes")
                cursor.execute("SELECT DATE_FORMAT(fecha_pago, '%Y-%m') as mes, SUM(monto_recibido) as total FROM Pagos GROUP BY mes ORDER BY mes ASC")
                rec_mes = cursor.fetchall()
                if rec_mes:
                    df_r = pd.DataFrame(rec_mes).set_index('mes')
                    st.bar_chart(df_r, color="#00A2FF")
            with c2:
                st.markdown("#### Gastos vs Costos")
                df_eg = pd.DataFrame([{"Tipo": "Costo Equipos", "Valor": total_costo}, {"Tipo": "Gastos / Comisiones", "Valor": total_gastos}])
                df_eg.set_index("Tipo", inplace=True)
                st.bar_chart(df_eg, color="#64748B")

        # ------------------------------------------
        # ⚙️ CONFIGURACIÓN DE ACCESOS
        # ------------------------------------------
        elif menu_seleccionado == "config_roles":
            st.markdown("## Usuarios y Permisos")
            if not es_admin: st.error("Rechazado."); st.stop()
            
            cursor.execute("SELECT * FROM Roles")
            opc_r = [r['nombre_rol'] for r in cursor.fetchall()]
            
            tab_u, tab_p = st.tabs(["👤 Crear Usuario", "🛡️ Control de Vistas"])
            with tab_u:
                with st.form("f_newUser"):
                    n_user = st.text_input("Usuario de Acceso")
                    n_pass = st.text_input("Contraseña", type="password")
                    n_nombre = st.text_input("Nombre Real del Empleado")
                    n_rol = st.selectbox("Perfil / Jerarquía", opc_r)
                    if st.form_submit_button("Crear Empleado"):
                        if n_user and n_pass and n_nombre:
                            try:
                                cursor.execute("INSERT INTO Usuarios (username, password_hash, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_user, n_pass, n_nombre, n_rol))
                                conn.commit(); st.toast("Empleado creado."); time.sleep(1); st.rerun()
                            except: st.error("El usuario ya existe.")
            with tab_p:
                st.write("Controla a qué menú tiene acceso cada tipo de empleado.")
                role_sel = st.selectbox("Seleccione Perfil:", opc_r)
                if role_sel:
                    cursor.execute("SELECT * FROM Modulos_Sistema")
                    todos_modulos = cursor.fetchall()
                    cursor.execute("SELECT id_modulo FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                    activos_rol = [x['id_modulo'] for x in cursor.fetchall()]
                    
                    with st.form("form_permisos"):
                        check_res = {m['id_modulo']: st.checkbox(m['nombre_visible'], value=(m['id_modulo'] in activos_rol)) for m in todos_modulos}
                        if st.form_submit_button("Guardar Permisos"):
                            cursor.execute("DELETE FROM Permisos_Rol WHERE id_role = (SELECT id_role FROM Roles WHERE nombre_rol = %s)", (role_sel,))
                            cursor.execute("SELECT id_role FROM Roles WHERE nombre_rol = %s", (role_sel,))
                            id_r_actual = cursor.fetchone()['id_role']
                            for id_mod, marcado in check_res.items():
                                if marcado: cursor.execute("INSERT INTO Permisos_Rol (id_role, id_modulo) VALUES (%s, %s)", (id_r_actual, id_mod))
                            conn.commit(); st.toast("Permisos actualizados."); time.sleep(1); st.rerun()

# ==========================================
# 🛑 CIERRE SEGURO DE BASE DE DATOS
# ==========================================
try:
    if 'cursor' in locals() and cursor: cursor.close()
    if 'conn' in locals() and conn and conn.is_connected(): conn.close()
except Exception:
    pass

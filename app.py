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
# 🛠️ AUTO-MIGRACIÓN DE BASE DE DATOS (Nuevas Columnas)
# ==========================================
def auto_fix_db(cursor, conn):
    # Nuevos campos Clientes
    try: cursor.execute("ALTER TABLE Clientes ADD COLUMN direccion VARCHAR(255), ADD COLUMN barrio VARCHAR(255), ADD COLUMN ciudad VARCHAR(255), ADD COLUMN correo VARCHAR(255), ADD COLUMN empresa VARCHAR(255)"); conn.commit()
    except Exception: pass
    
    # Nuevos campos Inventario
    try: cursor.execute("ALTER TABLE Inventario ADD COLUMN cantidad INT DEFAULT 1, ADD COLUMN color VARCHAR(100), ADD COLUMN fecha_compra DATE, ADD COLUMN factura VARCHAR(100), ADD COLUMN tienda_proveedor VARCHAR(255), ADD COLUMN nit_proveedor VARCHAR(100), ADD COLUMN celular_proveedor VARCHAR(100)"); conn.commit()
    except Exception: pass
    
    # Adaptación de Gastos para Comisiones
    try: cursor.execute("ALTER TABLE Gastos_Operativos ADD COLUMN estado_pago VARCHAR(50) DEFAULT 'Pagado', ADD COLUMN vendedor VARCHAR(255), ADD COLUMN id_credito INT"); conn.commit()
    except Exception: pass

    # Tabla de Vendedores
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Vendedores (id_vendedor INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(255) UNIQUE)"); conn.commit()
    except Exception: pass
    
    # Soporte Multiproducto
    try: cursor.execute("CREATE TABLE IF NOT EXISTS Creditos_Items (id INT AUTO_INCREMENT PRIMARY KEY, id_credito INT, imei VARCHAR(100))"); conn.commit()
    except Exception: pass

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DaTo | Tecnología con Respaldo", layout="wide", initial_sidebar_state="expanded", page_icon="⚡")

# ==========================================
# 🎨 UI CORPORATIVA (TEMA CLARO + CIRCUITOS + LOGOS)
# ==========================================
# SVG de circuitos y logos tech integrado en el fondo (muy sutil)
fondo_circuitos = """data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10 10h10v10H10zM30 10h10v10H30zM50 10h10v10H50zM70 10h10v10H70zM90 10h10v10H90z' fill='%230052D4' fill-opacity='0.03' fill-rule='evenodd'/%3E%3Cpath d='M50 50c-5.5 0-10-4.5-10-10s4.5-10 10-10 10 4.5 10 10-4.5 10-10 10zM20 80c-5.5 0-10-4.5-10-10s4.5-10 10-10 10 4.5 10 10-4.5 10-10 10z' fill='%230052D4' fill-opacity='0.02'/%3E%3C/svg%3E"""

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        :root {{
            --primary: #0052D4;
            --secondary: #4364F7;
            --accent: #6FB1FC;
            --bg: #F4F7F9;
            --card-bg: #FFFFFF;
            --text-dark: #1E293B;
            --text-muted: #64748B;
        }}
        
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; color: var(--text-dark) !important; }}
        
        .stApp {{
            background-color: var(--bg) !important;
            background-image: url("{fondo_circuitos}") !important;
            background-size: 150px;
        }}

        /* Tarjetas y Contenedores */
        div[data-testid="stForm"], .card-panel {{
            background: var(--card-bg) !important;
            border: 1px solid rgba(0, 82, 212, 0.1) !important;
            border-radius: 12px !important;
            padding: 24px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        }}

        /* Inputs y Selects */
        div[data-testid="stTextInput"] div[data-baseweb="input"], 
        div[data-testid="stNumberInput"] div[data-baseweb="input"], 
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] {{
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            color: var(--text-dark) !important;
            transition: all 0.2s;
        }}
        
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within, 
        div[data-testid="stSelectbox"] > div > div[data-baseweb="select"]:focus-within {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(0, 82, 212, 0.2) !important;
        }}

        /* Botones Comerciales */
        .stButton>button {{
            background: var(--primary) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.5rem !important;
            box-shadow: 0 2px 4px rgba(0, 82, 212, 0.2) !important;
        }}
        .stButton>button:hover {{ background: var(--secondary) !important; transform: translateY(-1px); }}

        /* Sidebar Limpio */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }}
        
        /* Títulos */
        h1, h2, h3 {{ color: var(--primary) !important; font-weight: 700 !important; }}
        h4, h5 {{ color: var(--text-dark) !important; font-weight: 600 !important; }}
    </style>
""", unsafe_allow_html=True)

def renderizar_logo():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; padding: 20px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
            <h1 style='color: #0052D4; font-size: 2.5rem; font-weight: 800; margin:0;'>⚡ DaTo</h1>
        </div>
        <p style='text-align: center; color: #64748B; margin-top: -15px; margin-bottom: 30px; font-weight: 500;'>Tecnología con Respaldo</p>
    """, unsafe_allow_html=True)

# ==========================================
# 🛠️ FUNCIONES DE FORMATO Y CÁLCULO
# ==========================================
def fmt_cop(val):
    try: val_int = int(float(val))
    except (ValueError, TypeError): return "$0"
    return f"${val_int:,.0f}".replace(",", ".")

def sumar_meses_exactos(fecha_base, meses_a_sumar):
    mes = fecha_base.month - 1 + meses_a_sumar
    año = fecha_base.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha_base.day, calendar.monthrange(año, mes)[1])
    return datetime.date(año, mes, dia)

# ==========================================
# 🌐 CONEXIÓN A LA BASE DE DATOS
# ==========================================
@st.cache_resource
def get_connection_pool():
    return pooling.MySQLConnectionPool(
        pool_name="dato_pool", pool_size=10, pool_reset_session=True,
        host="gateway01.us-east-1.prod.aws.tidbcloud.com", port=4000,
        user="2xRKoKTDAr4tRLF.root", password="7KGQVtKygobgy311",
        database="sistema_creditos", ssl_verify_cert=False, autocommit=True
    )

try:
    pool = get_connection_pool()
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    auto_fix_db(cursor, conn)
except Exception as e:
    st.error(f"Error conectando al servidor: {e}"); st.stop()

# ==========================================
# 🔐 SISTEMA DE LOGIN DUAL (ADMIN VS CLIENTE)
# ==========================================
if 'logeado' not in st.session_state: st.session_state['logeado'] = False
if 'rol' not in st.session_state: st.session_state['rol'] = None

if not st.session_state['logeado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        renderizar_logo()
        
        tab_admin, tab_cliente = st.tabs(["🔒 Ingreso Administrativo", "👤 Soy Cliente"])
        
        with tab_admin:
            with st.form("form_login"):
                st.markdown("### Acceso al Sistema")
                usuario_input = st.text_input("Usuario")
                password_input = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar", width='stretch'):
                    cursor.execute("SELECT id_usuario, nombre_completo, rol FROM Usuarios WHERE username = %s AND password_hash = %s", (usuario_input, password_input))
                    usuario_db = cursor.fetchone()
                    if usuario_db:
                        st.session_state.update({'logeado': True, 'id_usuario': usuario_db['id_usuario'], 'nombre_usuario': usuario_db['nombre_completo'], 'rol': usuario_db['rol']})
                        st.rerun()
                    else: st.error("Datos incorrectos.")
                    
        with tab_cliente:
            with st.form("form_login_cliente"):
                st.markdown("### Portal de Autogestión")
                st.write("Consulta el estado de tu cuenta ingresando tu número de cédula.")
                cedula_cliente = st.text_input("Número de Documento (C.C.)")
                if st.form_submit_button("Consultar Estado de Cuenta", width='stretch'):
                    cursor.execute("SELECT * FROM Clientes WHERE documento = %s", (cedula_cliente,))
                    cli_db = cursor.fetchone()
                    if cli_db:
                        st.session_state.update({'logeado': True, 'rol': 'Cliente', 'id_cliente': cli_db['id_cliente'], 'nombre_cliente': cli_db['nombre_completo']})
                        st.rerun()
                    else: st.error("No encontramos productos asociados a este documento.")

else:
    # ==========================================
    # 📱 PORTAL VISIÓN CLIENTE
    # ==========================================
    if st.session_state['rol'] == 'Cliente':
        st.markdown(f"<h1 style='text-align:center;'>👋 Hola, {st.session_state['nombre_cliente']}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748B;'>Bienvenido a tu portal de cliente DaTo. Aquí tienes el resumen de tu cuenta.</p>", unsafe_allow_html=True)
        
        cursor.execute("""
            SELECT c.id_credito, c.monto_financiado, c.valor_cuota, c.fecha_primera_cuota, c.tasa_interes_mensual, c.estado 
            FROM Creditos c WHERE c.id_cliente = %s AND c.estado = 'Activo'
        """, (st.session_state['id_cliente'],))
        creditos_cliente = cursor.fetchall()
        
        if not creditos_cliente:
            st.success("¡Felicidades! Actualmente no tienes deudas pendientes con nosotros. Estás a Paz y Salvo.")
        else:
            for cred in creditos_cliente:
                # Buscar equipos asociados
                cursor.execute("SELECT i.marca, i.modelo FROM Creditos_Items ci JOIN Inventario i ON ci.imei = i.imei WHERE ci.id_credito = %s", (cred['id_credito'],))
                equipos = cursor.fetchall()
                if not equipos: # Fallback al modelo viejo
                    cursor.execute("SELECT i.marca, i.modelo FROM Creditos c JOIN Inventario i ON c.imei = i.imei WHERE c.id_credito = %s", (cred['id_credito'],))
                    equipos = cursor.fetchall()
                
                nombres_equipos = " + ".join([f"{e['marca']} {e['modelo']}" for e in equipos])
                
                # Cálculos
                cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (cred['id_credito'],))
                cap_pag = cursor.fetchone()['cap'] or 0
                saldo_actual = float(cred['monto_financiado']) - float(cap_pag)
                pago_total = saldo_actual + (saldo_actual * float(cred['tasa_interes_mensual']))
                
                st.markdown(f"""
                <div class='card-panel' style='margin-bottom:20px; text-align:center; border-top: 5px solid #0052D4 !important;'>
                    <h4>Dispositivos Adquiridos: {nombres_equipos}</h4>
                    <div style='display:flex; justify-content:space-around; margin-top:20px;'>
                        <div>
                            <p style='color:#64748B; margin-bottom:5px;'>Valor de Cuota Mensual</p>
                            <h2 style='color:#0052D4; margin:0;'>{fmt_cop(cred['valor_cuota'])}</h2>
                        </div>
                        <div>
                            <p style='color:#64748B; margin-bottom:5px;'>Pago Total (Paz y Salvo Hoy)</p>
                            <h2 style='color:#10B981; margin:0;'>{fmt_cop(pago_total)}</h2>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Historial de Pagos del Cliente
                st.markdown("### 🧾 Tus últimos pagos")
                cursor.execute("SELECT fecha_pago, monto_recibido FROM Pagos WHERE id_credito = %s ORDER BY fecha_pago DESC", (cred['id_credito'],))
                pagos = cursor.fetchall()
                if pagos:
                    df_p = pd.DataFrame(pagos)
                    df_p.columns = ['Fecha del Pago', 'Valor Abonado']
                    df_p['Valor Abonado'] = df_p['Valor Abonado'].apply(fmt_cop)
                    st.table(df_p)
                else:
                    st.info("Aún no tienes pagos registrados para esta obligación.")

        if st.button("Cerrar Sesión"):
            st.session_state['logeado'] = False; st.rerun()

    # ==========================================
    # 💼 PORTAL ADMINISTRATIVO / COMERCIAL
    # ==========================================
    else:
        with st.sidebar:
            st.markdown(f"**Usuario:** {st.session_state['nombre_usuario']}<br>**Rol:** {st.session_state['rol']}", unsafe_allow_html=True)
            st.divider()
            
            menu = st.radio("Menú Principal", [
                "📊 Panel General", 
                "🛒 Ventas y Contratos",
                "💰 Caja y Pagos", 
                "👥 Clientes", 
                "📦 Inventario",
                "💸 Control de Gastos y Comisiones"
            ])
            
            st.divider()
            if st.button("Cerrar Sesión", width='stretch'): st.session_state['logeado'] = False; st.rerun()

        # ------------------------------------------
        # MÓDULO: CLIENTES
        # ------------------------------------------
        if menu == "👥 Clientes":
            st.markdown("## Directorio de Clientes")
            with st.form("nuevo_cliente"):
                st.subheader("Registrar Nuevo Cliente")
                c1, c2, c3 = st.columns(3)
                doc = c1.text_input("Cédula / Documento")
                nom = c2.text_input("Nombre Completo")
                tel = c3.text_input("Teléfono / Celular")
                
                c4, c5, c6 = st.columns(3)
                correo = c4.text_input("Correo Electrónico")
                ciudad = c5.text_input("Ciudad")
                barrio = c6.text_input("Barrio")
                
                c7, c8 = st.columns(2)
                direccion = c7.text_input("Dirección de Residencia")
                empresa = c8.text_input("Empresa o Negocio donde trabaja")
                
                if st.form_submit_button("Guardar Cliente", width='stretch'):
                    if doc and nom:
                        try:
                            cursor.execute("INSERT INTO Clientes (documento, nombre_completo, telefono, direccion, barrio, ciudad, correo, empresa, id_usuario_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                           (doc, nom, tel, direccion, barrio, ciudad, correo, empresa, st.session_state['id_usuario']))
                            conn.commit(); st.success("Cliente guardado correctamente."); time.sleep(1); st.rerun()
                        except mysql.connector.Error: st.error("Esta cédula ya está registrada.")
                    else: st.warning("La cédula y el nombre son obligatorios.")
            
            cursor.execute("SELECT documento AS Cédula, nombre_completo AS Nombre, telefono AS Celular, ciudad AS Ciudad FROM Clientes")
            df_cli = pd.DataFrame(cursor.fetchall())
            if not df_cli.empty: st.dataframe(df_cli, width='stretch')

        # ------------------------------------------
        # MÓDULO: INVENTARIO Y CATÁLOGO DINÁMICO
        # ------------------------------------------
        elif menu == "📦 Inventario":
            st.markdown("## Bodega e Inventario")
            
            # Obtener Catálogo Dinámico (Aprende de lo que ya está en DB)
            cursor.execute("SELECT DISTINCT marca FROM Inventario WHERE marca IS NOT NULL")
            marcas_existentes = [m['marca'] for m in cursor.fetchall()]
            
            with st.form("ingreso_inventario"):
                st.subheader("Ingresar Productos")
                st.info("💡 Puedes ingresar varios equipos del mismo modelo usando el campo 'Cantidad'.")
                
                c1, c2, c3 = st.columns(3)
                marca_sel = c1.selectbox("Marca", marcas_existentes + ["Agregar Nueva Marca..."])
                if marca_sel == "Agregar Nueva Marca...": marca_final = c1.text_input("Escribe la nueva marca:")
                else: marca_final = marca_sel
                
                # Modelos dinámicos por marca
                modelos_existentes = []
                if marca_sel != "Agregar Nueva Marca...":
                    cursor.execute("SELECT DISTINCT modelo FROM Inventario WHERE marca = %s", (marca_sel,))
                    modelos_existentes = [m['modelo'] for m in cursor.fetchall()]
                
                modelo_sel = c2.selectbox("Modelo / Capacidad", modelos_existentes + ["Agregar Nuevo Modelo..."])
                if modelo_sel == "Agregar Nuevo Modelo...": modelo_final = c2.text_input("Escribe el nuevo modelo:")
                else: modelo_final = modelo_sel
                
                color = c3.text_input("Color")
                
                c4, c5, c6 = st.columns(3)
                imei = c4.text_input("IMEI / Serial (Opcional si es lote genérico)")
                cantidad = c5.number_input("Cantidad a Ingresar", min_value=1, value=1)
                costo = c6.number_input("Costo de Compra (Unitario)", min_value=0, value=0, step=10000)
                
                st.markdown("#### Datos del Proveedor (Opcional)")
                p1, p2, p3, p4 = st.columns(4)
                proveedor = p1.text_input("Nombre Tienda/Proveedor")
                nit = p2.text_input("NIT Proveedor")
                cel_prov = p3.text_input("Celular Proveedor")
                factura = p4.text_input("N° Factura de Compra")
                
                if st.form_submit_button("Guardar en Inventario", width='stretch'):
                    if not marca_final or not modelo_final: st.error("Marca y Modelo son obligatorios.")
                    else:
                        for i in range(cantidad):
                            imei_guardar = imei if cantidad == 1 and imei else f"SYS-{str(uuid.uuid4())[:8].upper()}"
                            cursor.execute("""
                                INSERT INTO Inventario (imei, categoria, marca, modelo, costo_adquisicion, estado, cantidad, color, factura, tienda_proveedor, nit_proveedor, celular_proveedor, fecha_compra, id_usuario_registro) 
                                VALUES (%s, 'General', %s, %s, %s, 'Disponible', 1, %s, %s, %s, %s, %s, %s, %s)
                            """, (imei_guardar, marca_final, modelo_final, costo, color, factura, proveedor, nit, cel_prov, datetime.date.today(), st.session_state['id_usuario']))
                        conn.commit(); st.success(f"{cantidad} producto(s) agregado(s)."); time.sleep(1); st.rerun()

            # Ver Inventario
            cursor.execute("SELECT marca AS Marca, modelo AS Modelo, COUNT(*) AS Disponibles, costo_adquisicion AS Costo FROM Inventario WHERE estado = 'Disponible' GROUP BY marca, modelo, costo_adquisicion")
            df_inv = pd.DataFrame(cursor.fetchall())
            if not df_inv.empty: 
                df_inv['Costo'] = df_inv['Costo'].apply(fmt_cop)
                st.dataframe(df_inv, width='stretch')

        # ------------------------------------------
        # MÓDULO: VENTAS Y COTIZADOR (Multiproducto & Comisiones)
        # ------------------------------------------
        elif menu == "🛒 Ventas y Contratos":
            tab_coti, tab_venta = st.tabs(["🧮 Simulador / Cotizador", "🤝 Registrar Nueva Venta"])
            
            with tab_coti:
                st.markdown("### Cotizador Rápido")
                st.write("Los valores inician en cero para cotizar libremente.")
                c1, c2 = st.columns(2)
                sim_precio = c1.number_input("Valor Total del Producto", value=0, step=10000)
                sim_abono = c2.number_input("Abono Inicial del Cliente", value=0, step=10000)
                sim_meses = c1.number_input("Plazo (Meses)", min_value=1, value=1)
                sim_tasa = c2.selectbox("Tasa de Interés (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=0)
                
                if sim_precio > 0:
                    capital = sim_precio - sim_abono
                    i_m = sim_tasa / 100.0
                    cuota = capital * (i_m * (1 + i_m)**sim_meses) / (((1 + i_m)**sim_meses) - 1) if sim_tasa > 0 else capital / sim_meses
                    st.success(f"💰 **Cuota Mensual Estimada:** {fmt_cop(cuota)}")
            
            with tab_venta:
                st.markdown("### Registrar Contrato Comercial")
                
                # Cargar Clientes, Inventario y Vendedores
                cursor.execute("SELECT id_cliente, documento, nombre_completo FROM Clientes")
                clientes = cursor.fetchall()
                cursor.execute("SELECT imei, marca, modelo FROM Inventario WHERE estado = 'Disponible'")
                inventario = cursor.fetchall()
                cursor.execute("SELECT nombre FROM Vendedores")
                vendedores = [v['nombre'] for v in cursor.fetchall()]
                
                if not clientes or not inventario: st.warning("Debes tener clientes y productos en bodega para vender.")
                else:
                    opc_cli = {f"{c['documento']} - {c['nombre_completo']}": c['id_cliente'] for c in clientes}
                    opc_eq = {f"{e['marca']} {e['modelo']} (Cod: {e['imei']})": e['imei'] for e in inventario}
                    
                    with st.form("f_venta"):
                        cliente_sel = st.selectbox("Seleccionar Cliente", list(opc_cli.keys()))
                        
                        st.markdown("#### Productos a Facturar")
                        equipos_sel = st.multiselect("Seleccionar Equipo(s) - Soporta múltiples", list(opc_eq.keys()))
                        
                        st.markdown("#### Condiciones Financieras")
                        v1, v2 = st.columns(2)
                        precio_total = v1.number_input("Valor Comercial Total", value=0, step=10000)
                        abono_ini = v2.number_input("Abono Inicial Entregado", value=0, step=10000)
                        plazo = v1.number_input("Meses a Financiar", min_value=1, value=6)
                        tasa = v2.selectbox("Tasa de Interés Mensual (%)", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], index=3)
                        
                        st.markdown("#### Gestión Comercial (Comisiones)")
                        c_vend1, c_vend2, c_vend3 = st.columns(3)
                        vendedor_existente = c_vend1.selectbox("Vendedor / Asesor", ["Seleccionar..."] + vendedores)
                        nuevo_vendedor = c_vend2.text_input("O crear nuevo Vendedor:")
                        comision = c_vend3.number_input("Comisión a Pagar por esta Venta", value=0, step=10000)
                        
                        if st.form_submit_button("Guardar Venta", width='stretch'):
                            if not equipos_sel: st.error("Debes seleccionar al menos un producto.")
                            else:
                                vendedor_final = nuevo_vendedor if nuevo_vendedor else (vendedor_existente if vendedor_existente != "Seleccionar..." else None)
                                
                                # Si hay un nuevo vendedor, lo guardamos en catálogo
                                if nuevo_vendedor:
                                    try: cursor.execute("INSERT INTO Vendedores (nombre) VALUES (%s)", (nuevo_vendedor,))
                                    except: pass
                                
                                m_f = precio_total - abono_ini
                                i_m = tasa / 100.0
                                cuota_fija = int(round(m_f * (i_m * (1 + i_m)**plazo) / (((1 + i_m)**plazo) - 1))) if tasa > 0 else int(round(m_f / plazo))
                                
                                # Crear Crédito Maestro (usamos el primer IMEI en la tabla original por compatibilidad, y los demás en Detalles)
                                primer_imei = opc_eq[equipos_sel[0]]
                                cursor.execute("""
                                    INSERT INTO Creditos (id_cliente, imei, precio_venta, abono_inicial, monto_financiado, tasa_interes_mensual, plazo_meses, valor_cuota, estado, fecha_inicio, fecha_primera_cuota, valor_comision, asesor_comision, estado_comision, id_usuario_registro) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo', %s, %s, %s, %s, %s, %s)
                                """, (opc_cli[cliente_sel], primer_imei, precio_total, abono_ini, m_f, i_m, plazo, cuota_fija, datetime.date.today(), sumar_meses_exactos(datetime.date.today(), 1), comision, vendedor_final, 'Por Pagar' if comision > 0 else 'No Aplica', st.session_state['id_usuario']))
                                
                                id_credito = cursor.lastrowid
                                
                                # Registrar Multi-Productos y descontar stock
                                for eq in equipos_sel:
                                    imei_eq = opc_eq[eq]
                                    cursor.execute("INSERT INTO Creditos_Items (id_credito, imei) VALUES (%s, %s)", (id_credito, imei_eq))
                                    cursor.execute("UPDATE Inventario SET estado = 'Vendido' WHERE imei = %s", (imei_eq,))
                                
                                # Si hay comisión, enviar a Gastos como "Por Pagar"
                                if comision > 0 and vendedor_final:
                                    concepto = f"Comisión por Venta - {vendedor_final} (Cred #{id_credito})"
                                    cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, vendedor, id_credito, id_usuario_registro) VALUES (%s, %s, %s, 'Por Pagar', %s, %s, %s)",
                                                   (concepto, comision, datetime.date.today(), vendedor_final, id_credito, st.session_state['id_usuario']))
                                
                                conn.commit(); st.success("Venta guardada y equipos despachados."); time.sleep(1.5); st.rerun()

        # ------------------------------------------
        # MÓDULO: CAJA Y PAGOS
        # ------------------------------------------
        elif menu == "💰 Caja y Pagos":
            st.markdown("## Recepción de Pagos")
            cursor.execute("SELECT c.id_credito, cl.nombre_completo, c.monto_financiado, c.tasa_interes_mensual, c.valor_cuota FROM Creditos c JOIN Clientes cl ON c.id_cliente = cl.id_cliente WHERE c.estado = 'Activo'")
            activos = cursor.fetchall()
            
            if not activos: st.info("No hay créditos activos pendientes de cobro.")
            else:
                opc_cobro = {f"{c['nombre_completo']} (ID: {c['id_credito']})": c for c in activos}
                cliente_pago = st.selectbox("Buscar Cliente", list(opc_cobro.keys()))
                
                if cliente_pago:
                    dat = opc_cobro[cliente_pago]
                    
                    # Cálculos Financieros
                    cursor.execute("SELECT SUM(capital_abonado) as cap FROM Pagos WHERE id_credito = %s", (dat['id_credito'],))
                    cap_pagado = float(cursor.fetchone()['cap'] or 0)
                    saldo_pendiente = float(dat['monto_financiado']) - cap_pagado
                    interes_mes = saldo_pendiente * float(dat['tasa_interes_mensual'])
                    pago_total_paz_salvo = saldo_pendiente + interes_mes
                    
                    # VISUALIZACIÓN CLARA DE PAGOS
                    st.markdown(f"""
                        <div style='display:flex; justify-content: space-between; background: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 20px;'>
                            <div style='text-align:center;'>
                                <p style='margin:0; color:#64748B;'>Cuota Mensual</p>
                                <h2 style='margin:0; color:#0052D4;'>{fmt_cop(dat['valor_cuota'])}</h2>
                            </div>
                            <div style='text-align:center; border-left: 2px solid #E2E8F0; padding-left: 20px;'>
                                <p style='margin:0; color:#64748B;'>Saldo a Capital</p>
                                <h2 style='margin:0; color:#64748B;'>{fmt_cop(saldo_pendiente)}</h2>
                            </div>
                            <div style='text-align:center; border-left: 2px solid #E2E8F0; padding-left: 20px;'>
                                <p style='margin:0; font-weight: bold; color:#1E293B;'>Pago Total (Paz y Salvo)</p>
                                <h2 style='margin:0; color:#10B981;'>{fmt_cop(pago_total_paz_salvo)}</h2>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form("f_pago"):
                        monto = st.number_input("Valor Entregado por el Cliente", value=int(dat['valor_cuota']), step=10000)
                        if st.form_submit_button("Registrar Pago", width='stretch'):
                            if monto <= 0: st.error("Ingresa un valor válido.")
                            else:
                                cap_abono = 0.0 if monto <= interes_mes else monto - interes_mes
                                cursor.execute("INSERT INTO Pagos (id_credito, monto_recibido, tipo_pago, capital_abonado, interes_cobrado, fecha_pago, id_usuario_registro) VALUES (%s, %s, 'Cuota / Abono', %s, %s, %s, %s)", 
                                               (dat['id_credito'], monto, cap_abono, min(monto, interes_mes), datetime.datetime.now(), st.session_state['id_usuario']))
                                
                                if saldo_pendiente - cap_abono <= 0:
                                    cursor.execute("UPDATE Creditos SET estado = 'Pagado' WHERE id_credito = %s", (dat['id_credito'],))
                                    st.balloons()
                                
                                conn.commit(); st.success("Pago aplicado correctamente."); time.sleep(1.5); st.rerun()

        # ------------------------------------------
        # MÓDULO: GASTOS Y COMISIONES
        # ------------------------------------------
        elif menu == "💸 Control de Gastos y Comisiones":
            st.markdown("## Egresos y Liquidación de Asesores")
            
            tab_com, tab_gas = st.tabs(["🤝 Comisiones por Pagar", "🧾 Registrar Gasto General"])
            
            with tab_com:
                st.write("Listado de comisiones generadas por ventas recientes.")
                cursor.execute("SELECT id_gasto, descripcion, monto, vendedor FROM Gastos_Operativos WHERE estado_pago = 'Por Pagar' AND descripcion LIKE '%Comisión%'")
                comisiones = cursor.fetchall()
                
                if comisiones:
                    df_c = pd.DataFrame(comisiones)
                    df_c['Monto'] = df_c['monto'].apply(fmt_cop)
                    st.table(df_c[['descripcion', 'vendedor', 'Monto']])
                    
                    opc_pago = {f"{c['descripcion']} -> {fmt_cop(c['monto'])}": c['id_gasto'] for c in comisiones}
                    com_sel = st.selectbox("Seleccionar Comisión para Liquidar (Pagar)", list(opc_pago.keys()))
                    if st.button("Marcar como Pagada", type="primary"):
                        cursor.execute("UPDATE Gastos_Operativos SET estado_pago = 'Pagado' WHERE id_gasto = %s", (opc_pago[com_sel],))
                        # Si quieres descontar esto de Bolsas_Capital, agregas el UPDATE respectivo aquí.
                        conn.commit(); st.success("Comisión pagada al asesor."); time.sleep(1); st.rerun()
                else:
                    st.info("No tienes comisiones pendientes por pagar.")
            
            with tab_gas:
                with st.form("f_gasto"):
                    desc = st.text_input("Concepto del Gasto (Ej. Arriendo, Publicidad, Servicios)")
                    valor_gasto = st.number_input("Valor", min_value=0, step=10000)
                    if st.form_submit_button("Registrar Gasto", width='stretch'):
                        if desc and valor_gasto > 0:
                            cursor.execute("INSERT INTO Gastos_Operativos (descripcion, monto, fecha_gasto, estado_pago, id_usuario_registro) VALUES (%s, %s, %s, 'Pagado', %s)", 
                                           (desc, valor_gasto, datetime.date.today(), st.session_state['id_usuario']))
                            conn.commit(); st.success("Gasto registrado."); time.sleep(1); st.rerun()

        # ------------------------------------------
        # MÓDULO: PANEL GENERAL (Dashboards)
        # ------------------------------------------
        elif menu == "📊 Panel General":
            st.markdown("## Resumen del Negocio")
            
            # Cálculos rápidos
            cursor.execute("SELECT SUM(monto_recibido) as t FROM Pagos WHERE DATE(fecha_pago) = CURDATE()")
            ingresos_hoy = cursor.fetchone()['t'] or 0
            
            cursor.execute("SELECT SUM(monto_financiado) as mf FROM Creditos WHERE estado = 'Activo'")
            cartera_colocada = cursor.fetchone()['mf'] or 0
            
            cursor.execute("SELECT SUM(capital_abonado) as ca FROM Pagos p JOIN Creditos c ON p.id_credito = c.id_credito WHERE c.estado = 'Activo'")
            cartera_recaudada = cursor.fetchone()['ca'] or 0
            
            cartera_calle = cartera_colocada - cartera_recaudada
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Recaudo Hoy</h5><h2 style='color:#10B981;'>{fmt_cop(ingresos_hoy)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Capital en la Calle</h5><h2 style='color:#0052D4;'>{fmt_cop(cartera_calle)}</h2></div>", unsafe_allow_html=True)
            
            cursor.execute("SELECT COUNT(*) as c FROM Inventario WHERE estado = 'Disponible'")
            c3.markdown(f"<div class='card-panel' style='text-align:center;'><h5>Equipos en Bodega</h5><h2 style='color:#64748B;'>{cursor.fetchone()['c']} Unds.</h2></div>", unsafe_allow_html=True)
finally:
    try:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn and conn.is_connected(): conn.close()
    except Exception: 
    pass


    

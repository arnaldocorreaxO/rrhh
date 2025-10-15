import IfxPy
from config.utils import print_err, print_info

# 🔧 Configuración por sede
CONFIGURACION = {
    'CEN': {
        'HOST': '10.130.10.250',
        'SERVER': 'ol_informix1170',
        'SERVICE': '22767',
        'DB': 'pl4sjasu'
    },
    'VTA': {
        'HOST': '192.100.100.8',
        'SERVER': 'ol_informix1170',
        'SERVICE': '22767',
        'DB': 'pl4sjpvi'
    },
    'VMI': {
        'HOST': '192.168.100.7',
        'SERVER': 'ol_informix1170',
        'SERVICE': '22767',
        'DB': 'pl4sjvalle'
    }
}

# 🔐 Credenciales comunes
IFX_USER = 'informix'
IFX_PASS = 'cnumtc'

# 🧩 Obtener parámetros de conexión
def get_config(sede='CEN'):
    conf = CONFIGURACION.get(sede, CONFIGURACION['CEN'])
    print_info(f'Conectando a sede {sede}')
    print_info(f'Parámetros: {conf}')
    return conf['SERVER'], conf['DB'], conf['HOST'], conf['SERVICE'], IFX_USER, IFX_PASS

# 🔌 Conexión
def connect(sede='CEN'):
    server, db, host, service, user, pwd = get_config(sede)
    conn_str = f"SERVER={server};DATABASE={db};HOST={host};SERVICE={service};UID={user};PWD={pwd};"
    try:
        conn = IfxPy.connect(conn_str, "", "")
        IfxPy.autocommit(conn, False)
        print_info(f'Conexión OK a {sede}')
        return conn
    except Exception as e:
        print_err(f'Error de conexión a {sede}: {e}')
        raise

# 📄 Ejecutar SQL
def execute(conn, sql, params=None):
    try:
        if not isinstance(sql, str):
            raise ValueError("La instrucción SQL debe ser una cadena de texto")

        if params:
            stmt = IfxPy.prepare(conn, sql)
            IfxPy.execute(stmt, params)
        else:
            stmt = IfxPy.prepare(conn, sql)
            IfxPy.execute(stmt)
        return stmt
    except Exception as e:
        print_err(f"Error al ejecutar SQL: {e}")
        raise

# 📄 Ejecutar Procedimiento SQL
# Usar fetch_both para obtener resultados
def execute_sp(conn, sql, params=None):
    try:
        if not isinstance(sql, str):
            raise ValueError("La instrucción SQL debe ser una cadena de texto")

        if params:
            stmt = IfxPy.prepare(conn, sql)
            IfxPy.execute(stmt, params)
            data = IfxPy.fetch_both(stmt,params)
        else:
            stmt = IfxPy.prepare(conn, sql)
            IfxPy.execute(stmt)
            data = IfxPy.fetch_both(stmt)
        return data
    except Exception as e:
        print_err(f"Error al ejecutar SQL: {e}")
        raise



# ✅ Commit
def commit(conn):
    try:
        if IfxPy.commit(conn):
            print_info('Commit OK')
            return True
        else:
            IfxPy.rollback(conn)
            print_err('Commit fallido, rollback ejecutado')
            return False
    except Exception as e:
        print_err(f'Error en commit: {e}')
        raise

# ❌ Cerrar conexión
def close(stmt, conn):
    try:
        IfxPy.free_result(stmt)
        IfxPy.free_stmt(stmt)
        IfxPy.close(conn)
        print_info('Conexión cerrada y recursos liberados')
    except Exception as e:
        print_err(f'Error al cerrar conexión: {e}')

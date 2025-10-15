import pyodbc
import datetime

from config.utils import print_err, print_info


class SqlConnection:
    def __init__(self, cnn_string):
        self.cnn_string = cnn_string
        self.connection = pyodbc.connect(self.cnn_string, autocommit=False)
        self.cursor = self.connection.cursor()
        self.results = None

    def close_cnn(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def command_execute(self, sql_command, commit=False):
        self.cursor.execute(sql_command)
        if commit:
            self.connection.commit()
        return self.cursor

    def getresults(self):
        return self.results

    def query_execute(self, sql_command):
        try:
            self.cursor.execute(sql_command)
            self.results = self.cursor.fetchall()
            return self.results
        except Exception as e:
            self.results = e
            return self.results

# '''CONFIGURACION DE CONEXION'''
# def config(cod,*args):
#     if cod == 'VMI':
#         #PARAMETROS DE CONEXION SQLSERVER VALLEMI

#         MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
#         MSSQL_SERVER = '192.168.100.48'
#         MSSQL_DB = 'db_inc'
#         MSSQL_USER='intranet'
#         MSSQL_PASS='tic2019*'
#         #MSSQL_USER='sa'
#         #MSSQL_PASS='AreaTic22*'

#         conStr = MSSQL_DRIVER,\
#         MSSQL_SERVER,\
#         MSSQL_DB,\
#         MSSQL_USER,\
#         MSSQL_PASS

#         print_info('PARAMETROS DE CONEXION A BASE DE DATOS')
#         print(conStr)
#         return conStr     
#     if cod=='VTA':
#         #PARAMETROS DE CONEXION SQLSERVER VALLEMI

#         MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
#         MSSQL_SERVER = '10.130.11.20'
#         MSSQL_DB = 'db_inc'
#         MSSQL_USER='intranet'
#         MSSQL_PASS='tic2019*'
#         #MSSQL_USER='sa'
#         #MSSQL_PASS='AreaTic22*'

#         conStr = MSSQL_DRIVER,\
#                 MSSQL_SERVER,\
#                 MSSQL_DB,\
#                 MSSQL_USER,\
#                 MSSQL_PASS

#         print_info('PARAMETROS DE CONEXION A BASE DE DATOS')
#         print(conStr)
#         return conStr   
    
def config(*args):
    """Configuración de conexión a la base de datos según el código de sucursal."""
    
    if not args:
        print("Error: No se proporcionó el código de sucursal.")
        return None

    cod = args[0]  # Obtener el código de sucursal del primer argumento

    # Parámetros de conexión comunes
    MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'

    # Diccionario para almacenar los parámetros de conexión según el código
    connection_params = {
        'VMI': {
            'server': '192.168.100.48',
            'db': 'db_inc',
            'user': 'intranet',  # Reemplaza con el nombre de usuario real para VMI
            'password': 'tic2019*'  # Reemplaza con la contraseña real para VMI
        },
    'VTA': {
            'server': '10.130.11.20',
            'db': 'db_inc',
            'user': 'intranet',  # Reemplaza con el nombre de usuario real para VTA
            'password': 'tic2019*'  # Reemplaza con la contraseña real para VTA
        }
    }

    # Verificar si el código está en el diccionario
    if cod in connection_params:
        params = connection_params[cod]
        conStr = (
            MSSQL_DRIVER,
            params['server'],
            params['db'],
            params['user'],
            params['password']
        )

        print_info('PARAMETROS DE CONEXION A BASE DE DATOS')
        print(conStr)
        return conStr

    # Si el código no es válido, se puede manejar el error aquí
    print(f"Error: Código de sucursal '{cod}' no reconocido.")
    return None


'''OBTENEMOS TIPO DE MARCACION E/S SEGUN TURNO Y HORARIO'''
'''ESTO LO HACE DEL LADO DEL MSSQL '''
def getTipoMarcacion(*args):
    pass
    # tipo  = 'E'     #Entrada por defecto
    # try:
    #     conn  = args[0]
    #     cod   = args[1] #Legajo del Personal
    #     fecha = args[2] #Fecha de marcacion del dia
    #     hora  = args[3] #Hora de marcacion del dia
        

    #     # HORARIO DEL PERSONAL
    #     sql = '''SELECT hora_tipo, vige_hora_lega    
    #             FROM ashor
    #             WHERE lega = '{0}'
    #             AND vige_hora_lega =
    #             (SELECT MAX(vige_hora_lega)
    #             FROM ashor
    #             WHERE lega='{0}'
    #             AND vige_hora_lega <= '{1}');'''.format(cod,fecha)
    #     #print(sql)
    #     stmt = query(conn,sql)
    #     data = IfxPy.fetch_both(stmt)

    #     #RELACION TURNO HORARIO DEL PERSONAL
    #     hora_tipo = data['hora_tipo']
    #     sql = '''SELECT vige_hora_tipo, 
    #                     domi as dom, lune as lun, mart as mar, 
    #                     mier as mie, juev as jue, vier as vie, saba as sab
    #             FROM asrtg
    #             WHERE hora_tipo = '{0}'
    #             AND vige_hora_tipo = (SELECT MAX(vige_hora_tipo)
    #                                   FROM asrtg
    #                                   WHERE hora_tipo = '{0}'
    #                                   AND vige_hora_tipo <= '{1}');'''.format(hora_tipo,fecha)
    #     # print(sql)
    #     stmt = query(conn,sql)
    #     data = IfxPy.fetch_assoc(stmt)
    #     # print(data)

    #     #HORARIO DEL PERSONAL SEGUN TURNO DEL DIA 
    #     dia_actual = datetime.datetime.strptime(fecha,'%d-%m-%Y').weekday()
    #     #Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
    #     # print(dia_actual)
        
    #     turno = []    
    #     turno.append(data['lun'])
    #     turno.append(data['mar'])
    #     turno.append(data['mie'])
    #     turno.append(data['jue'])
    #     turno.append(data['vie'])
    #     turno.append(data['sab'])
    #     turno.append(data['dom'])

    #     turno = turno[dia_actual]
        
    #     sql = '''SELECT hora_ent1, hora_sal1, tras from astur where turn = '{0}';'''.format(turno)

    #     # print(sql)
    #     stmt = query(conn,sql)
    #     data = IfxPy.fetch_assoc(stmt)
    #     # print(data)

    #     horario_entrada = data['hora_ent1']
    #     horario_salida = data['hora_sal1']
    #     turno_noche = data['tras']

    #     # Convertir hora entrada/salida a segundos (este es la hora que marcó entrada o salida)
    #     hora_segundos = int(hora[:2])*3600 + int(hora[3:])*60

    #     # Convertir horario entrada segundos (este es el horario entrada/salida segun turno)
    #     horario_ent_segundos = int(horario_entrada[:2])*3600 + int(horario_entrada[3:])*60
    #     horario_sal_segundos = int(horario_salida[:2]) *3600 + int(horario_salida[3:])*60

    #     #Si la diferencia entre la hora de marcacion y el horario de entrada supera 3 horas ya se considera Entrada E
    #     if abs(horario_ent_segundos - hora_segundos) >= 10800:
    #         tipo = 'S'

    # except Exception as e:
    #     print(e)
    #     tipo = 'E' #Retornamos tipo E en caso de errores 
    # return tipo

'''INSERTA MARCACIONES EN TABLA AUXILIAR'''    
def insert_marcaciones(*args):
    from core.asistencia.models import Marcacion,MarcacionDetalle
    try:
        ''''
        args: marcacion_id,fecha_desde,fecha_hasta
        '''
        data={}
        marcacion_id = args[0] #Marcacion Cabecera
        fecha_desde  = args[1] #Fecha Inicial desde registro marcaciones detalle
        fecha_hasta  = args[2] #Fecha Final.. hasta registro marcaciones detalle
        # marcacion_list = [5,3,2,9,10,8,12,13,11,14,15,16,20,21,22]
        
        '''MARCACION CABECERA'''
        marcacion = Marcacion.objects.filter(id=marcacion_id).first()    
        
        
        #CONECTAR CON MSSQL  
        print_info('INTENTANDO CONECTAR')
        conn = SqlConnection(cnn_string="DRIVER={%s};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s;" %(config(marcacion.sucursal.cod)))
        # conn = connect()
        # cursor = conn.cursor()
        table = 'astmp'       
        
        print_info('PREPARANDO SQL INSERCION DE DATOS')

        #ELIMINAR MOVIMIENTOS AUXILIARES
        sql = f"DELETE FROM {table};"
        # query(cursor,sql)
        cursor = conn.command_execute(sql, commit=False)

        #RESTABLECER VALOR INICIAL DEL ID DE LA TABLA
        sql+= f"DBCC CHECKIDENT([{table}], RESEED, 0);"
        # query(cursor,sql)
        cursor = conn.command_execute(sql, commit=False)

        qs = MarcacionDetalle.objects\
                             .filter(marcacion = marcacion_id,fecha__range=(fecha_desde,fecha_hasta))\
                             .order_by('cod','fecha','hora')
        # print(qs.query)
        i=0;t=0
        sql+= f"INSERT INTO {table} (legajo,fecha,hora,EntSal) VALUES"
        for row in qs:
            i+=1
            row.fecha = row.fecha.strftime('%Y-%m-%d')
            row.hora  = row.hora.strftime('%H:%M')   
            sql+=f"('{row.cod}', '{row.fecha}', '{row.hora}','{row.tipo}'),"
            if i == 1000:
                #INSERTA EN TABLA TEMPORAL PARA MARCACIONES ANTES DE LLAMAR AL PROCEDIMIENTO
                t+=i
                print_info('INSERTANDO DATOS POR FAVOR ESPERE')
                sql = sql[:-1]+";"
                # print(sql) #Consume mucho recurso
                cursor = conn.command_execute(sql, commit=False)
                sql+= f"INSERT INTO {table} (legajo,fecha,hora,EntSal) VALUES"
                i=0
        t+=i
        sql = sql[:-1]+";"       
        #INSERTA EN TABLA TEMPORAL PARA MARCACIONES ANTES DE LLAMAR AL PROCEDIMIENTO
        print_info('INSERTANDO DATOS POR FAVOR ESPERE')
        # print(sql) #Consume mucho recurso
        cursor = conn.command_execute(sql, commit=False)        
        #COMMIT TRANS
        conn.commit()

        fecha_desde = datetime.datetime.strptime(fecha_desde,'%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_hasta = datetime.datetime.strptime(fecha_hasta,'%Y-%m-%d').strftime('%d/%m/%Y')
        parameters=(fecha_desde,fecha_hasta,'CM','A') #tupla
        print(parameters)
        # sql = f"EXECUTE FUNCTION informix.sp_cmt_asis_env_xo('{fecha_desde}', '{fecha_hasta}', 'CM', 'A');"
        print_info('EJECUTANDO PROCEDIMIENTO POR FAVOR ESPERE')
        #sql = "EXECUTE FUNCTION informix.sp_cmt_asis_inc('{0}', '{1}', '{2}', '{3}');".format(*parameters)
        sql = "EXEC sp_act_asis_inc"
        print(sql)        
        # cursor = conn.cursor()
        # cursor.execute(sp)
        cursor = conn.command_execute(sql)
        row = cursor.fetchone()
        print(row[0])       
        
        # En la posicion 1 retorna valor 0 si el preocedimiento sp_cmt_asis_env se ejecutó correctamente
        if row[0] == 'OK':
            msg = row[1] #Recibe el mensaje del procedimiento en la columna 2
            data['info'] = msg
            print_info(msg)

        conn.commit()
        # rtn = commit(conn)        
        # if not rtn: 
        #     data['error']='COMMIT PROCEDIMIENTO HA FALLADO'
        #     print_err(data)

        # # CONTAMOS REGISTROS DE LA TABLA 
        # sql = f"SELECT COUNT('1') AS RC FROM {table}"
        # stmt = query(conn, sql)
        # # ddata = IfxPy.fetch_both(stmt) #dictionary data
        # ddata = IfxPy.fetch_assoc(stmt) #dictionary data
        # rc = ddata['rc'] #ROWCOUNT
        
        # # CONTAMOS REGISTROS DE LA TABLA XINERR es donde el procedimiento de informix
        # # guarda los registros de errores si hubo
        # sql = f"SELECT COUNT('1') AS RC FROM XINERR"
        # stmt = query(conn, sql)
        # # ddata = IfxPy.fetch_both(stmt) #dictionary data
        # ddata = IfxPy.fetch_assoc(stmt) #dictionary data
        # rce = ddata['rc'] #ROWCOUNT

        # PROCESADO
        marcacion.procesado = True
        marcacion.save()

        data['info']+="\n<br>\n{}\t".format(str(marcacion.sucursal.denom_corta))
        data['info']+="\n<br>\nTOTAL REGISTROS INSERTADOS\t: {}".format(t) 
        # data['info']+="\n<br>\nTOTAL REGISTROS SELECCIONADOS\t:{}".format(rc)
        # data['info']+="\n<br>\nTOTAL REGISTROS CON ERRORES\t:{}".format(rce)
        data['info']+="\n"
        print_info(data['info'])
        # close(conn)

    except pyodbc.OperationalError as e:
        print('No se puede establecer la conexión: ' + str(e))

    except ValueError as e:
        print(str(e))

    except Exception as e:
        print(e)
        data['error'] = e

    finally:
        # attempt to close the connection
        try:
            conn.close_cnn()
        except:
            pass
    return data

import IfxPy
import datetime

from config.utils import print_err, print_info

# from bs.models import *
'''CONFIGURACION DE CONEXION'''
def config(*args):
    #CENTRAL
    IFX_CEN_HOST = '10.130.10.250'
    IFX_CEN_SERVER = 'ol_informix1170'
    IFX_CEN_SERVICE = '22767'
    IFX_CEN_DB = 'pl4sjasu'
    # IFX_CEN_DB = 'pl4prueba'
    #VILLETA
    IFX_VTA_HOST = IFX_CEN_HOST #'192.100.100.8'
    IFX_VTA_SERVER = IFX_CEN_SERVER #'ol_platino'
    IFX_VTA_SERVICE = IFX_CEN_SERVICE #'1530'
    IFX_VTA_DB = 'pl4sjpvi'
    #VALLEMI
    IFX_VMI_HOST = '192.168.100.7'
    IFX_VMI_SERVER = 'ol_informix1171'
    IFX_VMI_SERVICE = '22767'
    IFX_VMI_DB = 'pl4sjvalle'

    #COMUN
    IFX_USER = 'informix'
    IFX_PASS ='cnumtc'

    '''DEFAULT CENTRAL'''
    IFX_HOST = IFX_CEN_HOST
    IFX_SERVER = IFX_CEN_SERVER
    IFX_SERVICE = IFX_CEN_SERVICE
    IFX_DB = IFX_CEN_DB

    sede = args[0]
    if sede=='VTA':
        IFX_HOST = IFX_VTA_HOST
        IFX_SERVER = IFX_VTA_SERVER
        IFX_SERVICE = IFX_VTA_SERVICE
        IFX_DB = IFX_VTA_DB
    elif sede=='VMI':
        IFX_HOST = IFX_VMI_HOST
        IFX_SERVER = IFX_VMI_SERVER
        IFX_SERVICE = IFX_VMI_SERVICE
        IFX_DB = IFX_VMI_DB

    conStr = IFX_SERVER,\
             IFX_DB,\
             IFX_HOST,\
             IFX_SERVICE,\
             IFX_USER,\
             IFX_PASS 
    print_info('PARAMETROS DE CONEXION A BASE DE DATOS')
    print(conStr)
    return conStr    

'''CONEXION A LA BASE DE DATOS'''
def connect(*args):
    # print(args)
    ConStr = "SERVER=%s;DATABASE=%s;HOST=%s;SERVICE=%s;UID=%s;PWD=%s;" %(config(args[0]))
    conn=None
    try:
        # netstat -a | findstr  9088
        conn = IfxPy.connect( ConStr, "", "")
        IfxPy.autocommit(conn,False)
        print_info('CONEXION REALIZADA OK')
    except Exception as e:
        print ('ERROR: Falló la conexion')
        print ( e )
        quit()
    return conn

'''QUERY SQL'''
def query(*args):
    try:    
        conn = args[0]
        sql  = args[1]
        stmt = IfxPy.exec_immediate(conn, sql)
        return stmt
    except Exception as e:
        print('FALLÓ LA INSTRUCCION SQL')
        print(e)
        quit()
    

'''COMMIT TRANS'''
def commit(*args):
    conn = args[0]
    try:
        # netstat -a | findstr  9088
        rtn = IfxPy.commit(conn)
        print_info('COMMIT OK')
        if not rtn:
            IfxPy.rollback(conn)
            print_info('ROLLBACK KO')
        return rtn
    except Exception as e:
        print('FALLO LA INSTRUCCION COMMIT')
        print(e)
        quit()

'''CLOSE CONEXION'''
def close(*args):
    stmt = args[0]
    conn  = args[1]
    # LIBERAR MEMORIA
    IfxPy.free_result(stmt)
    IfxPy.free_stmt (stmt)
    IfxPy.close(conn)
    print_info('CONEXION LIBERADA')

'''OBTENEMOS TIPO DE MARCACION E/S SEGUN TURNO Y HORARIO'''
def getTipoMarcacion(*args):
    tipo  = 'E'     #Entrada por defecto
    try:
        conn  = args[0]
        cod   = args[1] #Legajo del Personal
        fecha = args[2] #Fecha de marcacion del dia
        hora  = args[3] #Hora de marcacion del dia
        

        # HORARIO DEL PERSONAL
        sql = '''SELECT hora_tipo, vige_hora_lega    
                FROM ashor
                WHERE lega = '{0}'
                AND vige_hora_lega =
                (SELECT MAX(vige_hora_lega)
                FROM ashor
                WHERE lega='{0}'
                AND vige_hora_lega <= '{1}');'''.format(cod,fecha)
        #print(sql)
        stmt = query(conn,sql)
        data = IfxPy.fetch_both(stmt)

        #RELACION TURNO HORARIO DEL PERSONAL
        hora_tipo = data['hora_tipo']
        sql = '''SELECT vige_hora_tipo, 
                        domi as dom, lune as lun, mart as mar, 
                        mier as mie, juev as jue, vier as vie, saba as sab
                FROM asrtg
                WHERE hora_tipo = '{0}'
                AND vige_hora_tipo = (SELECT MAX(vige_hora_tipo)
                                      FROM asrtg
                                      WHERE hora_tipo = '{0}'
                                      AND vige_hora_tipo <= '{1}');'''.format(hora_tipo,fecha)
        # print(sql)
        stmt = query(conn,sql)
        data = IfxPy.fetch_assoc(stmt)
        # print(data)

        #HORARIO DEL PERSONAL SEGUN TURNO DEL DIA 
        dia_actual = datetime.datetime.strptime(fecha,'%d-%m-%Y').weekday()
        #Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
        # print(dia_actual)
        
        turno = []    
        turno.append(data['lun'])
        turno.append(data['mar'])
        turno.append(data['mie'])
        turno.append(data['jue'])
        turno.append(data['vie'])
        turno.append(data['sab'])
        turno.append(data['dom'])

        turno = turno[dia_actual]
        
        sql = '''SELECT hora_ent1, hora_sal1, tras from astur where turn = '{0}';'''.format(turno)

        # print(sql)
        stmt = query(conn,sql)
        data = IfxPy.fetch_assoc(stmt)
        # print(data)

        horario_entrada = data['hora_ent1']
        horario_salida = data['hora_sal1']
        turno_noche = data['tras']

        # Convertir hora entrada/salida a segundos (este es la hora que marcó entrada o salida)
        hora_segundos = int(hora[:2])*3600 + int(hora[3:])*60

        # Convertir horario entrada segundos (este es el horario entrada/salida segun turno)
        horario_ent_segundos = int(horario_entrada[:2])*3600 + int(horario_entrada[3:])*60
        horario_sal_segundos = int(horario_salida[:2]) *3600 + int(horario_salida[3:])*60

        #Si la diferencia entre la hora de marcacion y el horario de entrada supera 3 horas ya se considera Entrada E
        if abs(horario_ent_segundos - hora_segundos) >= 10800:
            tipo = 'S'

    except Exception as e:
        print(e)
        tipo = 'E' #Retornamos tipo E en caso de errores 
    return tipo

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
        
        
        #CONECTAR CON INFORMIX SEGUN SEDE
        # sede = marcacion.sede
        sede = marcacion.sucursal.cod
        conn = connect(sede)
        table = 'xcmtas'       
        
        print_info('PREPARANDO SQL INSERCION DE DATOS')

        SetupSqlSet=[]
        # qs = MarcacionDetalle.objects\
        #                             .filter(cod='0668',marcacion__in=(marcacion_list),fecha__range=(fecha_desde,fecha_hasta))\
        #                             .order_by('cod','fecha','hora')
        qs = MarcacionDetalle.objects\
                             .filter(marcacion = marcacion_id,fecha__range=(fecha_desde,fecha_hasta))\
                             .order_by('cod','fecha','hora')
        # print(qs.query)
         #ELIMINAR MOVIMIENTOS AUXILIARES
        sql = f"DELETE FROM {table};"
        query(conn,sql)

        #INSERTA EN TABLA TEMPORAL PARA MARCACIONES ANTES DE LLAMAR AL PROCEDIMIENTO
        
        i = 0;t=0;sql = ''
        for row in qs:
            i+=1            
            row.fecha = row.fecha.strftime('%d-%m-%Y')
            row.hora  = row.hora.strftime('%H:%M')
            # Acá obtenemos si es Entrada o Salida 
            # Si Sede es Villeta tomamos el tipo de marcacion detalle (indicaron 1 = E, 3 = S)
            if sede =='VTA':
                tipo = row.tipo
            else:
                tipo = getTipoMarcacion(conn,row.cod,row.fecha,row.hora)

            # SetupSqlSet.append(f"INSERT INTO {table} VALUES( 0, '{row.cod}', '{row.fecha}', '{row.hora}','{tipo}','');")
            sql+=f"INSERT INTO {table} VALUES( 0, '{row.cod}', '{row.fecha}', '{row.hora}','{tipo}','');"
            # -460 Statement length exceeds maximum.
            # in most cases up to 65,535 characters
            # 65535 / 68 = 963,75
            # 68 caracteres tiene la instruccion INSERT SQL 
            if i == 950:
                # print (sql)
                t+=i
                print_info('INSERTANDO DATOS POR FAVOR ESPERE')
                query(conn,sql)
                i = 0;sql = ''
        
        t+=i
        print_info('INSERTANDO DATOS POR FAVOR ESPERE')
        query(conn,sql)
        
        # i = 0
        # for sql in SetupSqlSet:
        #     i += 1
        #     print (sql)
        #     query(conn,sql)
        
        #COMMIT TRANS
        commit(conn)

        fecha_desde = datetime.datetime.strptime(fecha_desde,'%Y-%m-%d').strftime('%d/%m/%Y')
        fecha_hasta = datetime.datetime.strptime(fecha_hasta,'%Y-%m-%d').strftime('%d/%m/%Y')
        parameters=(fecha_desde,fecha_hasta,'CM','A') #tupla
        print(parameters)
        # sql = f"EXECUTE FUNCTION informix.sp_cmt_asis_env_xo('{fecha_desde}', '{fecha_hasta}', 'CM', 'A');"
        print_info('EJECUTANDO PROCEDIMIENTO POR FAVOR ESPERE')
        sql = "EXECUTE FUNCTION informix.sp_cmt_asis_inc('{0}', '{1}', '{2}', '{3}');".format(*parameters)
        print(sql)        
        stmt = query(conn,sql)
        ddata = IfxPy.fetch_both(stmt) #dictionary data Acá recien se ejecuta la instruccion SQL 
        
        # En la posicion 1 retorna valor 0 si el preocedimiento sp_cmt_asis_env se ejecutó correctamente
        if ddata[1] == 0:
            msg = 'PROCEDIMIENTO FINALIZADO CON EXITO'
            data['info'] = msg
            print_info(msg)

        rtn = commit(conn)        
        if not rtn: 
            data['error']='COMMIT PROCEDIMIENTO HA FALLADO'
            print_err(data)

        # CONTAMOS REGISTROS DE LA TABLA 
        sql = f"SELECT COUNT('1') AS RC FROM {table}"
        stmt = query(conn, sql)
        # ddata = IfxPy.fetch_both(stmt) #dictionary data
        ddata = IfxPy.fetch_assoc(stmt) #dictionary data
        rc = ddata['rc'] #ROWCOUNT
        
        # CONTAMOS REGISTROS DE LA TABLA XINERR es donde el procedimiento de informix
        # guarda los registros de errores si hubo
        sql = f"SELECT COUNT('1') AS RC FROM XINERR"
        stmt = query(conn, sql)
        # ddata = IfxPy.fetch_both(stmt) #dictionary data
        ddata = IfxPy.fetch_assoc(stmt) #dictionary data
        rce = ddata['rc'] #ROWCOUNT

        # PROCESADO
        marcacion.procesado = True
        marcacion.save()

        data['info']+="\n<br>\n{}\t".format(str(marcacion.sede))
        data['info']+="\n<br>\nTOTAL REGISTROS INSERTADOS\t:{}".format(t) 
        data['info']+="\n<br>\nTOTAL REGISTROS SELECCIONADOS\t:{}".format(rc)
        data['info']+="\n<br>\nTOTAL REGISTROS CON ERRORES\t:{}".format(rce)
        data['info']+="\n"
        print_info(data['info'])
        close(stmt,conn)

    except Exception as e:
        print(e)
        data['error'] = e
    return data
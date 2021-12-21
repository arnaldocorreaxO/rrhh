from config import settings
#Obtenemos los valores de la connection por default
from django.db import connection

JASPER_PGSQL = {
        'driver'    : 'postgres',
        'username'  : connection.settings_dict['USER'],
        'password'  : connection.settings_dict['PASSWORD'],
        'host'      : connection.settings_dict['HOST'],
        'database'  : connection.settings_dict['NAME'],
        'schema'    : 'public',
        'port'      : connection.settings_dict['PORT'],
        'jdbc_driver':'org.postgresql.Driver',
        'jdbc_dir'  : settings.PGSQL_JDBC_DIR
}
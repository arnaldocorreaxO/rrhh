from config.utils import *
from config.utils import print_err, print_info
from core.base.models import ModeloBase, Sucursal
from django.core.files import File
from django.db import models, transaction
from django.forms.models import model_to_dict


class Reloj(ModeloBase):	
	sede = models.CharField(max_length=3,choices=choiceSede(),default='CEN')
	sucursal = models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	denominacion = models.CharField(max_length=100,unique=True)
	ip = models.CharField(max_length=15)
	puerto = models.CharField(max_length=4)
	
	def toJSON(self):
		item = model_to_dict(self)		
		return item
	
	def __str__(self):
		return f"{self.denominacion} - {self.ip}"
	
	def testConexion(self):
		import socket
		try:
			host = self.ip
			port = int(self.puerto)
			data = {}
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(2)
			# connect to remote host			
			s.connect((host, port))
			s.close()
			data['info'] = {'Msg' : f"HANDPUNCH {host} - {port} DISPONIBLE"}
			# Podemos agregar dos diccionarios en Python y almacenar su combinación 
			# en un tercer diccionario usando el operador de desempaquetado de diccionario **. 
			# Este método no cambia los pares clave-valor del diccionario original.
			# Este operador trabaja desde Python 3.5.
			data['info'] = {**data['info'],**self.getInfo()}
			print(data)	
		except:
			data['error'] = f"ERROR al intentar conectar con HandPunch {host} - {port}"
		return data
		
	def getInfo(self):
		import csv
		import datetime
		import os
		try:
			data={}
			
			nombreArchivo = self.ip + '_' + 'reader_info.csv'
			rutaExe = os.path.join(settings.BASE_DIR,'core','asistencia','handpunch','traeinfo.exe')		
			print_info('OBTENIENDO INFORMACIONES')
			os.system(rutaExe + ' ' + self.ip + ' ' + nombreArchivo)		
			rutaArchivo = os.path.join(settings.BASE_DIR,'registros', nombreArchivo)
			# rutaArchivo = os.path.join(settings.BASE_DIR,'registros', '10.67.1.21_23_11_2021_10_05_52.csv')
			# rutaArchivo ='C:\\Users\\marcacion\\rrhh\\registros\\192.100.100.70_22_12_2021_14_47_45.csv'
			print(rutaArchivo)
			if rutaArchivo:
				with open(rutaArchivo, 'rU') as infile:
				# read the file as a dictionary for each row ({header : value})
					reader = csv.DictReader(infile)
					data = {}
					nRows = 0 #Nro. de Filas 
					for row in reader:
						nRows += 1
						for header, value in row.items():
							try:
								data[header].append(value)
							except KeyError:
								data[header] = [value]
						# extract the variables you want
				if nRows > 0:
					print(data)
					# data['info'] = f'DESCARGA DE DATOS REALIZADA CON ÉXITO\n<br>\n<br> Total Registros: {nRows}'
						
				else:
					msg = "NO SE ENCONTRARON INFORMACIONES DEL DISPOSITIVO"
					print(msg)
					data['error'] = msg
			else:
				print("NO SE HA ENCONTRADO EL ARCHIVO CSV DE INFORMACIONES")
				msg = "NO SE ENCONTRARON INFORMACIONES EN EL DISPOSITIVO"
				data['error'] = msg
		except Exception as e:
			print(e)
			data['error'] = e
		return data

	def getMarcaciones(self):
		import csv
		import datetime
		import os
		try:
			data={}
			fechaHoraActual = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
			nombreArchivo = self.ip + '_' + fechaHoraActual + '.csv'
			nombreArchivo = 'R004.csv'
			#rutaExe = os.path.join(settings.BASE_DIR,'core','asistencia','handpunch','traedatos.exe')		
			print_info('OBTENIENDO MARCACIONES XOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
			#os.system(rutaExe + ' ' + self.ip + ' ' + nombreArchivo)		
			rutaArchivo = os.path.join(settings.BASE_DIR,'registros', nombreArchivo)
			# rutaArchivo = os.path.join(settings.BASE_DIR,'registros', '10.67.1.23_11_04_2022_13_54_06.csv')
			# rutaArchivo ='C:\\Users\\marcacion\\rrhh\\registros\\192.168.100.9_25_04_2022_06_27_34.csv'
			print(rutaArchivo)
			if rutaArchivo:
				with open(rutaArchivo, 'rU') as infile:
				# read the file as a dictionary for each row ({header : value})
					reader = csv.DictReader(infile)
					data = {}
					nRows = 0 #Nro. de Filas 
					for row in reader:
						nRows += 1
						for header, value in row.items():
							try:
								data[header].append(value)
							except KeyError:
								data[header] = [value]
						# extract the variables you want
				if nRows > 0:
					with transaction.atomic():
						'''MARCACION CABECERA'''
						print_info('GENERANDO MARCACION CABECERA')
						marcacion = Marcacion.objects.filter(sede=self.sede,procesado=False).first()
						if not marcacion:
							marcacion = Marcacion()
							marcacion.sede = self.sede
							marcacion.sucursal = self.sucursal
							marcacion.fecha = datetime.datetime.today().strftime('%Y-%m-%d')
							marcacion.hora  = datetime.datetime.now().strftime('%H:%M:%S')	
							marcacion.save()	
							print(marcacion.id,marcacion)
						
						'''MARCACION ARCHIVO'''
						# marcacion_archivo = MarcacionArchivo()
						# marcacion_archivo.marcacion = marcacion
						# marcacion_archivo.reloj = self
						# marcacion_archivo.archivo.save(nombreArchivo, File(open(rutaArchivo, 'rb')), save=False)
						# marcacion_archivo.save()				

						'''MARCACIONES DETALLE'''
						print_info('GENERANDO MARCACION DETALLE')							
						#data es un diccionario con clave (key) valor (value) y valor como lista 
						#{'id':[2973,2973,2973,2973,6118,6118,6118],
						#{'Date':[1-11-21,1-11-21,...],
						#{'time':[8:41,8;42...],				
						codigos = data['id'] 			#Lista de Legajos 
						fechas = data['Date']			#Lista de Fechas de Marcaciones
						tipo_marcaciones=data['taCode'] #Lista de Tipo de Marcaciones Entrada/Salida 1=E 3=S
						horas = data['time']			#Lista de Horas de Marcaciones						
							
						for i in range(0, len(codigos)):
							marcacion_detalle = MarcacionDetalle()
							marcacion_detalle.marcacion = marcacion
							marcacion_detalle.reloj = self
							marcacion_detalle.cod = codigos[i][-4:]
							# print(fechas[i])
							if fechas[i]:
								marcacion_detalle.fecha = datetime.datetime.strptime(fechas[i],'%d-%m-%y')
							# print(horas[i])
							if horas[i]:
								marcacion_detalle.hora = datetime.datetime.strptime(horas[i],'%H:%M')
							
							marcacion_detalle.tipo='E'
							if tipo_marcaciones[i]=='3':
								marcacion_detalle.tipo ='S'

							marcacion_detalle.save()
							print(marcacion_detalle)	
					
					# Llamar en otro procedimiento
					# rtn = dbifx.insert_marcaciones(marcacion.id,'2021-01-01','2021-12-31') 
					data['info'] = f'DESCARGA DE DATOS REALIZADA CON ÉXITO\n<br>{marcacion}\n<br> Total Registros: {nRows}'
						
				else:
					msg = "NO SE ENCONTRARON DATOS EN EL DISPOSITIVO"
					print(msg)
					data['error'] = msg
			else:
				print("NO SE HA ENCONTRADO EL ARCHIVO CSV")
				msg = "NO SE ENCONTRARON DATOS EN EL DISPOSITIVO"
				data['error'] = msg
		except Exception as e:
			print(e)
			data['error'] = e
		return data

	class Meta:
		ordering = ['sede',]
		# db_table = 'as_reloj'
		verbose_name = 'Reloj'
		verbose_name_plural = 'Relojes'

class Marcacion(ModeloBase):	
	sede = models.CharField(max_length=3,choices=choiceSede(),default='CEN')
	sucursal = models.ForeignKey(Sucursal,on_delete=models.PROTECT)
	fecha= models.DateField()
	hora = models.TimeField()	
	procesado = models.BooleanField(default=False)
	
	def toJSON(self):
		item = model_to_dict(self)
		sede = dict(choiceSede())
		item['sede'] = sede[self.sede] if self.sede else None
		item['cod_sucursal'] = self.sucursal.cod if self.sucursal.cod else None
		item['suc_denom_corta'] = self.sucursal.denom_corta if self.sucursal.denom_corta else None
		item['sucursal'] = str(self.sucursal) if self.sucursal else None
		item['fecha'] = self.fecha.strftime('%d/%m/%Y') if self.fecha else None
		item['hora'] = self.hora.strftime('%H:%M:%S') if self.hora else None
		item['fec_insercion'] = self.fec_insercion.strftime('%d/%m/%Y %H:%M:%S') if self.fec_insercion else None
		item['fec_modificacion'] = self.fec_modificacion.strftime('%d/%m/%Y %H:%M:%S') if self.fec_modificacion else None
		return item	
		
	def __str__(self):
		return f"{self.id} - {self.fecha} - {str(self.hora)}"

	class Meta:
		ordering = ['-id',]
		# db_table = 'as_marcacion'
		verbose_name = 'Marcacion'
		verbose_name_plural = 'Marcaciones'

class MarcacionDetalle(ModeloBase):	
	marcacion = models.ForeignKey(Marcacion,on_delete=models.PROTECT,null=True)
	cod = models.CharField(max_length=4)#Legajo
	fecha = models.DateField()
	hora = models.TimeField()
	tipo = models.CharField(max_length=1,choices=choiceTipoMarcacion(),default='E')
	reloj = models.ForeignKey(Reloj,on_delete=models.PROTECT,default=1)
	
	def toJSON(self):
		item = model_to_dict(self)
		item['fecha'] = self.fecha.strftime('%d/%m/%Y') if self.fecha else None
		item['hora'] = self.hora.strftime('%H:%M:%S') if self.hora else None
		item['marcacion'] = str(self.marcacion) if self.marcacion else None
		item['reloj'] = str(self.reloj) if self.reloj else None
		return item
	
	def __str__(self):
		return f"{self.cod} - {str(self.fecha)} - {str(self.hora)} - {str(self.reloj)}"

	class Meta:
	# ordering = ['1',]
		# db_table = 'as_marcacion_detalle'
		verbose_name = 'Marcacion Detalle'
		verbose_name_plural = 'Marcaciones Detalle'


class MarcacionArchivo(ModeloBase):	
	marcacion = models.ForeignKey(Marcacion,on_delete=models.PROTECT,null=True)
	reloj = models.ForeignKey(Reloj,on_delete=models.PROTECT,default=1)
	archivo = models.FileField(upload_to='backup/marcaciones/%Y/%m/%d',null=True,blank=True)
	
	def toJSON(self):
		item = model_to_dict(self)
		item['marcacion'] = str(self.marcacion) if self.marcacion else None
		item['reloj'] = str(self.reloj) if self.reloj else None
		item['archivo'] = self.get_archive()
		item['fec_insercion'] = self.fec_insercion.strftime('%d/%m/%Y %H:%M:%S') if self.fec_insercion else None
		item['fec_modificacion'] = self.fec_modificacion.strftime('%d/%m/%Y %H:%M:%S') if self.fec_modificacion else None
		return item
	
	def get_archive(self):
		if self.archivo:
			return '{0}{1}'.format(settings.MEDIA_URL, self.archivo)
		return ''
		
	def __str__(self):
		return self.marcacion

	class Meta:
	# ordering = ['1',]
		# db_table = 'as_marcacion'
		verbose_name = 'Archivo Marcacion'
		verbose_name_plural = 'Archivo Marcaciones'
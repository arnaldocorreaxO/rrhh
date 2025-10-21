import IfxPy
import json
import math
from django.shortcuts import render
from config import dbinformix as dbifx
from config import dbsqlserver as dbmssql
from config import dbsqlserver as dbmssql_villeta
from config.utils import print_info
from core.asistencia.forms import MarcacionForm
from core.asistencia.models import Marcacion, MarcacionArchivo
from core.security.mixins import PermissionMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

# Adicionales para la importación y procesamiento de marcaciones desde SQL Server e Informix
from config.dbsqlserver import SqlConnection, config
from config.dbinformix_new import connect, execute, commit, close, execute_sp
from datetime import datetime



class MarcacionListView(PermissionMixin, ListView):
	model = Marcacion
	template_name = 'asistencia/marcacion/list.html'
	# permission_required = 'asistencia.view_marcacion'
	permission_required = 'view_marcacion'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.suc_usuario = self.request.user.sucursal.id 
		return super().dispatch(request, *args, **kwargs)
	
	def get_fecha_inicial(self):
		import datetime
		"""Devuelve la fecha inicial como el primer día del año anterior y la fecha final actual."""
		fec_fin = datetime.datetime.today().strftime("%Y-%m-%d")
		fec_ini = f"{int(fec_fin[:4]) - 1}-01-01"  # Inclusive el año anterior
		return fec_ini, fec_fin

	def load_data(self,tipo,marcacion_id, sucursal_cod):
		"""Carga los datos de marcaciones según la sucursal."""
		fec_ini, fec_fin = self.get_fecha_inicial()
		if tipo == 'INFORMIX':
			if sucursal_cod == 'VMI':
				return dbmssql.insert_marcaciones(marcacion_id,fec_ini,fec_fin) #Vallemi
			else:
				return dbifx.insert_marcaciones(marcacion_id,fec_ini,fec_fin) 	#Central y Villeta
			
		elif tipo=='MSSQL_VILLETA':
			return dbmssql.insert_marcaciones(marcacion_id,fec_ini,fec_fin)		#Villeta 
	
	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST.get('action')
		marcacion_id = request.POST.get('marcacion_id')
		tipo = request.POST.get('tipo')
		try:
			if action in ['load_data']:
				marcacion = Marcacion.objects.filter(id=marcacion_id).first()
				print_info(str(marcacion))

			if action == 'load_data':
				data = self.load_data(tipo,marcacion.id, marcacion.sucursal.cod)

			elif action == 'search_archivos':
				data = []
				for det in MarcacionArchivo.objects.filter(marcacion_id=request.POST['id']):
					data.append(det.toJSON())								
			elif action =='search':
				data=[]					
				_start = request.POST['start']
				_length = request.POST['length']
				_search = request.POST['search[value]']
								
				# _order = ['barrio','manzana','nro_casa'] debe enviarse ya el orden desde el datatable para default
				_order = []
				# print(request.POST)
				#range(start, stop, step)
				for i in range(9): 
					_column_order = f'order[{i}][column]'
					
					if _column_order in request.POST:					
						_column_number = request.POST[_column_order]								
						_order.append(request.POST[f'columns[{_column_number}][data]'].split(".")[0])
					else:
						#Orden por defecto
						_order =['procesado','-fecha']
					if f'order[{i}][dir]' in request.POST:
						_dir = request.POST[f'order[{i}][dir]']
						if (_dir=='desc'):
							_order[i] = f"-{_order[i]}"
	
				
				_where = "'' = %s"
				# _where = "nro_pedido = 1000"
				if len(_search):
					if _search.isnumeric():
						_where = " asistencia_marcacion.id = %s"
					else:
						_search = "%" + _search.replace(' ', '%') + "%"
						_where = " upper(fecha||' '|| hora ) LIKE upper(%s)"
						# _where = " upper(fecha||' '|| hora||' '||asistencia_reloj.denominacion||' '||asistencia_reloj.ip ) LIKE upper(%s)"
				
				if not self.request.user.is_superuser:	
					qs = Marcacion.objects.filter(sucursal=self.suc_usuario)
				else:
					qs = Marcacion.objects.all()
										

				qs = qs.extra(where=[_where], params=[_search])\
					   .order_by(*_order)
				# #Pedidos del Año
				# if len(start_date) and len(end_date):			
				# 	start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
				# 	qs = qs.filter(fecha__range=(start_date,end_date))
								   
				total = qs.count()
				# print(qs.query)
				
				if _start and _length:
					start = int(_start)
					length = int(_length)
					page = math.ceil(start / length) + 1
					per_page = length

				if _length == '-1':
					qs = qs[start:]
				else:
					qs = qs[start:start + length]

				position = start + 1
				for i in qs:
					item = i.toJSON()
					item['position'] = position
					data.append(item)
					position += 1
				# print(data)
				data = {'data': data,
						'page': page,  # [opcional]
						'per_page': per_page,  # [opcional]
						'recordsTotal': total,
						'recordsFiltered': total, }
			else:
				data['error'] = 'No ha ingresado una opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['create_url'] = reverse_lazy('marcacion_create')
		context['title'] = 'Listado de Marcaciones '
		if not self.request.user.is_superuser:
			context['object_list'] = Marcacion.objects.filter(sucursal=self.suc_usuario)
		return context


class MarcacionCreateView(PermissionMixin, CreateView):
	model = Marcacion
	template_name = 'asistencia/marcacion/create.html'
	form_class = MarcacionForm
	success_url = reverse_lazy('marcacion_list')
	# permission_required = 'asistencia.add_marcacion'
	permission_required = 'add_marcacion'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()            
			if type == 'denominacion':                
				if Marcacion.objects.filter(denominacion__iexact=obj):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST['action']
		try:
			if action == 'add':
				data = self.get_form().save()
			elif action == 'validate_data':
				return self.validate_data()
			else:
				data['error'] = 'No ha seleccionado ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context['list_url'] = self.success_url
		context['title'] = 'Nuevo registro Marcaciones '
		context['action'] = 'add'
		return context


class MarcacionUpdateView(PermissionMixin, UpdateView):
	model = Marcacion
	template_name = 'asistencia/marcacion/create.html'
	form_class = MarcacionForm
	success_url = reverse_lazy('marcacion_list')
	# permission_required = 'asistencia.change_marcacion'
	permission_required = 'change_marcacion'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()
			id = self.get_object().id
			if type == 'denominacion':
				if Marcacion.objects.filter(denominacion__iexact=obj).exclude(id=id):
					data['valid'] = False
		except:
			pass
		return JsonResponse(data)

	def post(self, request, *args, **kwargs):
		data = {}
		action = request.POST['action']
		try:
			if action == 'edit':
				data = self.get_form().save()
			elif action == 'validate_data':
				return self.validate_data()
			else:
				data['error'] = 'No ha seleccionado ninguna opción'
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data()
		context['list_url'] = self.success_url
		context['title'] = 'Edición de Marcaciones '
		context['action'] = 'edit'
		return context


class MarcacionDeleteView(PermissionMixin, DeleteView):
	model = Marcacion
	template_name = 'asistencia/marcacion/delete.html'
	success_url = reverse_lazy('marcacion_list')
	# permission_required = 'asistencia.delete_marcacion'
	permission_required = 'delete_marcacion'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		data = {}
		try:
			self.get_object().delete()
		except Exception as e:
			data['error'] = str(e)
		return HttpResponse(json.dumps(data), content_type='application/json')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Notificación de eliminación'
		context['list_url'] = self.success_url
		return context



def obtener_filtro_tarjeta(sede):
	return {
		"CEN": "('CE','CO')",
		"VTA": "('VI')",
		"VMI": "('VA')"
	}.get(sede)

def importar_desde_sqlserver(sede, f_desde, f_hasta):
	tabla_origen = "xcmtas_tr"
	filtro = obtener_filtro_tarjeta(sede)
	if not filtro:
		yield f"❌ Sede desconocida: {sede}\n"
		return

	try:
		conn_sql = SqlConnection(cnn_string="DRIVER={%s};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s;" % (
			config(sede)
		))
		yield f"🔗 Conectado a SQL Server {sede}\n"

		sql = f"""
			SET DATEFORMAT DMY;
			SELECT noid, nume_tarj, 
			CONVERT(VARCHAR(10), ddma_emis, 103) AS ddma_emis, hora
			FROM {tabla_origen}
			WHERE proces = 'F'
			  AND nume_tarj IS NOT NULL
			  AND SUBSTRING(nume_tarj, 1, 2) IN {filtro}
			  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
		"""
		# cursor = conn_sql.cursor()
		cursor = conn_sql.command_execute(sql)
		rows = cursor.fetchall()
		yield f"📥 Registros obtenidos desde SQL Server: {len(rows)}\n"

		conn_inf = connect(sede)
		for idx,row in enumerate(rows, start=1):
			noid, nume_tarj, ddma_emis, hora = row
			# entr_sali = "E"  # o usar fn_tipo_marcacion
			sql_insert = f"""
				INSERT INTO {tabla_origen} (noid, nume_tarj, ddma_emis, hora, entr_sali,proces)
				VALUES ('{noid}', '{nume_tarj}', '{ddma_emis}', '{hora}', fn_tipo_marcacion(SUBSTR('{nume_tarj}', 3, 4), '{ddma_emis}', '{hora}'),'F')
			"""
			yield f"📥Insertando registro {idx} de {len(rows)} desde SQL Server\n"
			execute(conn_inf, sql_insert)
		commit(conn_inf)
		yield f"✅ Insertados {len(rows)} registros en Informix {sede}\n"

		# Actualizar estado en SQL Server
		conn_sql.command_execute(f"""
			UPDATE {tabla_origen}
			SET proces = 'V'
			WHERE proces = 'F'
			  AND nume_tarj IS NOT NULL
			  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
		""",commit=True)
		
		yield f"✔ Estado actualizado a 'V'\n"
		
	except Exception as e:
		yield f"❌ Error en importación desde SQL Server: {e}\n"

def ejecutar_procesamiento(sede, f_desde, f_hasta):
	tabla_temporal = "xcmtas"
	tabla_origen = "xcmtas_tr"
	procedimiento = "informix.sp_cmt_asis_inc"
	filtro = obtener_filtro_tarjeta(sede)

	if not filtro:
		yield f"❌ Sede desconocida: {sede}\n"
		return

	try:
		conn = connect(sede)
		yield f"🔌 Conexión exitosa a {sede}\n"
	except Exception as e:
		yield f"❌ Error al conectar con {sede}: {e}\n"
		return

	try:
		execute(conn, f"DELETE FROM {tabla_temporal};")
		yield f"📥 Delete masivo en tabla {tabla_temporal}\n"

		sql_insert = f"""
			INSERT INTO {tabla_temporal} (noid, nume_tarj, ddma_emis, hora, entr_sali)
			SELECT DISTINCT noid, SUBSTR(nume_tarj, 3, 4), ddma_emis, hora,
				   fn_tipo_marcacion(SUBSTR(nume_tarj, 3, 4), ddma_emis, hora)
			FROM {tabla_origen}
			WHERE proces = 'F'
			  AND nume_tarj IS NOT NULL
			  AND SUBSTR(nume_tarj, 1, 2) IN {filtro}
			  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
		"""
		execute(conn, sql_insert)
		# commit(conn)
		yield f"📥 Insert masivo realizado entre {f_desde} y {f_hasta}\n"

		execute(conn, f"""
			UPDATE {tabla_origen}
			SET proces = 'V'
			WHERE proces = 'F'
			  AND nume_tarj IS NOT NULL
			  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
		""")
		# commit(conn)
		yield f"✔ Estado actualizado a 'V'\n"

		execute_sp(conn, f"EXECUTE FUNCTION {procedimiento}('{f_desde}', '{f_hasta}', 'CM', 'A')")
		commit(conn)
		yield f"🚀 Procedimiento ejecutado: {procedimiento}\n"

		stmt = execute(conn, f"SELECT COUNT(*) AS rc FROM {tabla_temporal}")
		rc = int(IfxPy.fetch_assoc(stmt)['rc'])
		yield f"📊 Total registros seleccionados: {rc}\n"

		stmt = execute(conn, "SELECT COUNT(*) AS rc FROM XINERR")
		rce = int(IfxPy.fetch_assoc(stmt)['rc'])
		yield f"⚠️ Total registros con errores: {rce}\n"

	except Exception as e:
		yield f"❌ Error durante procesamiento: {e}\n"
	finally:
		try:
			close(None, conn)
		except Exception as e:
			yield f"⚠️ Error al cerrar conexión: {e}\n"

def verificar_marcaciones_por_sede(sede, f_desde, f_hasta):
	filtro = obtener_filtro_tarjeta(sede)
	if not filtro:
		yield f"❌ Sede desconocida: {sede}\n"
		return

	try:
		conn = connect(sede)
		sql = f"""
			SELECT COUNT(*) AS rc
			FROM xcmtas_tr
			WHERE proces = 'F'
			  AND nume_tarj IS NOT NULL
			  AND SUBSTR(nume_tarj, 1, 2) IN {filtro}
			  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
		"""
		stmt = execute(conn, sql)
		rc = int(IfxPy.fetch_assoc(stmt)['rc'])

		if rc > 0:
			yield f"✅ Hay {rc} marcaciones nuevas para procesar en {sede}\n"
		else:
			yield f"ℹ️ No hay marcaciones nuevas en {sede}\n"
	except Exception as e:
		yield f"❌ Error al verificar: {e}\n"
	finally:
		try:
			close(None, conn)
		except Exception as e:
			yield f"⚠️ Error al cerrar conexión: {e}\n"

from django.http import StreamingHttpResponse
from django.shortcuts import render
#from marcaciones_utils import ejecutar_procesamiento, verificar_marcaciones_por_sede, importar_desde_sqlserver
from datetime import datetime

def procesar_marcaciones_view(request):
	return render(request, 'asistencia/marcacion/procesar_marcaciones.html')

def procesar_marcaciones_stream(request):
	def event_stream():
		sede = request.POST.get("sede")
		fecha_desde = request.POST.get("fecha_desde")
		fecha_hasta = request.POST.get("fecha_hasta")

		if not sede or not fecha_desde or not fecha_hasta:
			yield "❌ Faltan datos\n"
			return

		try:
			f_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").strftime('%d/%m/%Y')
			f_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").strftime('%d/%m/%Y')
			yield f"📅 Procesando desde {f_desde} hasta {f_hasta}\n"
		except Exception as e:
			yield f"❌ Error en fechas: {e}\n"
			return
		
		
		if sede in("VTA","VMI"):
			for line in importar_desde_sqlserver(sede, f_desde, f_hasta):
				yield line

		for line in ejecutar_procesamiento(sede, f_desde, f_hasta):
			yield line

	return StreamingHttpResponse(event_stream(), content_type='text/plain')

def verificar_marcaciones(request):
	def event_stream():
		sede = request.POST.get("sede")
		fecha_desde = request.POST.get("fecha_desde")
		fecha_hasta = request.POST.get("fecha_hasta")

		if not sede or not fecha_desde or not fecha_hasta:
			yield "❌ Faltan datos\n"
			return

		try:
			f_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").strftime('%d/%m/%Y')
			f_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").strftime('%d/%m/%Y')
			yield f"📅 Verificando desde {f_desde} hasta {f_hasta}\n"
		except Exception as e:
			yield f"❌ Error en fechas: {e}\n"
			return

	   # 🔄 Importar desde SQL Server si es VTA
		if sede in("VTA","VMI"):
			for line in importar_desde_sqlserver(sede, f_desde, f_hasta):
				yield line

		# 🔍 Verificar en Informix
		for line in verificar_marcaciones_por_sede(sede, f_desde, f_hasta):
			yield line

	return StreamingHttpResponse(event_stream(), content_type='text/plain')

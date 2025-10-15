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

from django.http import StreamingHttpResponse
from config.dbinformix_new import connect, execute, commit, execute_sp
import time

def procesar_marcaciones_view(request):
	return render(request, 'asistencia/marcacion/procesar_marcaciones.html')


from django.http import StreamingHttpResponse
from config.dbinformix_new import connect, execute, commit, close
from datetime import datetime

def procesar_marcaciones_stream(request):
	def event_stream():
		tabla_temporal = "xcmtas"
		procedimiento = "informix.sp_cmt_asis_inc"

		fecha_desde = request.POST.get("fecha_desde")
		fecha_hasta = request.POST.get("fecha_hasta")

		if not fecha_desde or not fecha_hasta:
			yield "❌ Faltan fechas de filtro\n"
			return

		try:
			
			f_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").strftime('%d/%m/%Y')
			f_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").strftime('%d/%m/%Y')
			yield f"📅 Filtrando desde {f_desde} hasta {f_hasta}\n"
		except Exception as e:
			yield f"❌ Error en formato de fechas: {e}\n"
			return

		try:
			cen_conn = connect("CEN")
		except Exception as e:
			yield f"❌ Error al conectar con CENTRAL: {e}\n"
			return
		
		# 🔄 Delete masivo en tabla temporal
		try:
			sql_delete_central = f"""
				DELETE FROM {tabla_temporal};
			"""
			execute(cen_conn, sql_delete_central)			
			yield f"📥 Delete masivo en tabla {tabla_temporal}\n"
		except Exception as e:
			yield f"❌ Error en delete masivo tabla {tabla_temporal} CENTRAL: {e}\n"
			return
		
		# 🔄 Insert masivo con filtro de fechas
		try:
			sql_insert_central = f"""
				INSERT INTO {tabla_temporal} (noid, nume_tarj, ddma_emis, hora, entr_sali)
				SELECT DISTINCT noid, SUBSTR(nume_tarj, 3, 4), ddma_emis, hora, fn_tipo_marcacion(SUBSTR(nume_tarj, 3, 4),ddma_emis, hora) AS entr_sali
				FROM xcmtas_tr
				WHERE proces = 'F'
				  AND nume_tarj IS NOT NULL
				  AND SUBSTR(nume_tarj, 1, 2) IN ('CE','CO')
				  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
			"""
			execute(cen_conn, sql_insert_central)
			commit(cen_conn)			
			yield f"📥 Insert masivo realizado entre {f_desde} y {f_hasta}\n"
		except Exception as e:
			yield f"❌ Error en insert masivo CENTRAL: {e}\n"
			return

		# ✅ Actualizar estado
		try:
			execute(cen_conn, f"""
				UPDATE xcmtas_tr
				SET proces = 'V'
				WHERE proces = 'F'
				  AND nume_tarj IS NOT NULL
				  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
			""")
			commit(cen_conn)
			yield f"✔ Estado actualizado a 'V' entre {f_desde} y {f_hasta}\n"
		except Exception as e:
			yield f"❌ Error al actualizar estado en CENTRAL: {e}\n"
			return

		# 🚀 Ejecutar procedimiento
		try:
			execute_sp(cen_conn, f"""EXECUTE FUNCTION informix.sp_cmt_asis_inc('{f_desde}', '{f_hasta}','CM','A')""")
			commit(cen_conn)
			yield f"🚀 Ejecutado con éxito {procedimiento} en CENTRAL\n"
		except Exception as e:
			yield f"❌ Error al ejecutar {procedimiento} en CENTRAL: {e}\n"
			return
		# 📊 Conteo de registros procesados y errores
		
		try:
			# Total seleccionados en tabla temporal
			sql_rc = f"SELECT COUNT(*) AS rc FROM {tabla_temporal}"
			stmt = execute(cen_conn, sql_rc)
			ddata = IfxPy.fetch_assoc(stmt)
			rc = ddata['rc']
			yield f"📊 Total registros seleccionados en {tabla_temporal}: {rc}\n"

			# Total con errores en XINERR
			sql_rce = "SELECT COUNT(*) AS rc FROM XINERR"
			stmt = execute(cen_conn, sql_rce)
			ddata = IfxPy.fetch_assoc(stmt)
			rce = ddata['rc']
			yield f"⚠️ Total registros con errores en XINERR: {rce}\n"

		except Exception as e:
			yield f"❌ Error al contar registros: {e}\n"


		# 🔒 Cierre
		try:
			close(None, cen_conn)
		except Exception as e:
			yield f"⚠️ Error al cerrar conexión CENTRAL: {e}\n"

	return StreamingHttpResponse(event_stream(), content_type='text/plain')


# ✅ Verificar si hay marcaciones nuevas sin procesar
def verificar_marcaciones(request):
    def event_stream():
        tabla_origen = "xcmtas_tr"

        fecha_desde = request.POST.get("fecha_desde")
        fecha_hasta = request.POST.get("fecha_hasta")

        if not fecha_desde or not fecha_hasta:
            yield "❌ Faltan fechas de filtro\n"
            return

        try:
            f_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").strftime('%d/%m/%Y')
            f_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").strftime('%d/%m/%Y')
            yield f"📅 Verificando marcaciones entre {f_desde} y {f_hasta}\n"
        except Exception as e:
            yield f"❌ Error en formato de fechas: {e}\n"
            return

        try:
            cen_conn = connect("CEN")
        except Exception as e:
            yield f"❌ Error al conectar con CENTRAL: {e}\n"
            return

        try:
            sql_verificar = f"""
                SELECT COUNT(*) AS rc
                FROM {tabla_origen}
                WHERE proces = 'F'
                  AND nume_tarj IS NOT NULL
                  AND SUBSTR(nume_tarj, 1, 2) IN ('CE','CO')
                  AND ddma_emis BETWEEN '{f_desde}' AND '{f_hasta}'
            """
            stmt = execute(cen_conn, sql_verificar)
            data = IfxPy.fetch_assoc(stmt)
            rc = int(data['rc'])

            if rc > 0:
                yield f"✅ Hay {rc} marcacione(s) nuevas para procesar\n"
            else:
                yield f"ℹ️ No hay marcaciones nuevas en el rango seleccionado\n"

        except Exception as e:
            yield f"❌ Error al verificar marcaciones: {e}\n"
        finally:
            try:
                close(None, cen_conn)
            except Exception as e:
                yield f"⚠️ Error al cerrar conexión CENTRAL: {e}\n"

    return StreamingHttpResponse(event_stream(), content_type='text/plain')

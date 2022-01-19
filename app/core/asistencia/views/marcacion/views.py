
import json
import math

from config import dbinformix as dbifx
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
		return super().dispatch(request, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		data = {}
		# print(request.POST)
		action = request.POST['action']
		marcacion_id = request.POST['marcacion_id'] if 'marcacion_id' in request.POST else None
		try:
			if action == 'load_data':
				import datetime
				marcacion = Marcacion.objects.filter(id=marcacion_id).first()                
				print_info(str(marcacion))
				# Llamar en otro procedimiento
				fec_fin = datetime.datetime.today().strftime("%Y-%m-%d")
				fec_ini = f"{int(fec_fin[:4]) - 1 }-01-01"		#Inclusive el año anterior, cuando se hace la carga los primeros dias de enero 						
				data = dbifx.insert_marcaciones(marcacion.id,fec_ini,fec_fin) 
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
					# print('Column Order:',_column_order)
					if _column_order in request.POST:					
						_column_number = request.POST[_column_order]								
						_order.append(request.POST[f'columns[{_column_number}][data]'].split(".")[0])
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

				qs = Marcacion.objects\
                                    .filter()\
                                    .extra(where=[_where], params=[_search])\
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

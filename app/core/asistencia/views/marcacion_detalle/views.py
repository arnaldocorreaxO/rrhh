import json
import math

from django.views.generic.edit import FormView

from core.asistencia.forms import MarcacionDetalleForm, SearchForm
from core.asistencia.models import MarcacionDetalle
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from core.security.mixins import PermissionMixin

class MarcacionDetalleListView(PermissionMixin, FormView):
	# model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/list.html'
	# permission_required = 'asistencia.view_marcaciondetalle'
	permission_required = 'view_marcaciondetalle'
	form_class = SearchForm

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		data = {}
		# print(request.POST)
		action = request.POST['action']

		try:
			if action =='search':
				data=[]
				term = request.POST['term']		
				start_date = request.POST['start_date']
				end_date = request.POST['end_date']
					
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
				
				if len(term):
					_search = term
				
				_where = "'' = %s"				
				if len(_search):
					if _search.isnumeric():
						_where = " asistencia_marcaciondetalle.cod = %s"
					elif len(_search)==9:
						cod_desde = _search[:4]
						cod_hasta = _search[5:]
						_search=''
						_where += f" AND asistencia_marcaciondetalle.cod BETWEEN '{cod_desde}' AND '{cod_hasta}'"
					# else:
					# 	_search = "%" + _search.replace(' ', '%') + "%"
					# 	_where = " upper(cod ||' '|| fecha ||' '|| hora ) LIKE upper(%s)"
						# _where = " upper(fecha||' '|| hora||' '||asistencia_reloj.denominacion||' '||asistencia_reloj.ip ) LIKE upper(%s)"
				print(_where)
				qs = MarcacionDetalle.objects\
							  			.filter()\
										.extra(where=[_where], params=[_search])\
										.order_by(*_order)

				#Filtrar por Fechas
				if len(start_date) and len(end_date):			
					qs = qs.filter(fecha__range=(start_date,end_date))
								   
				total = qs.count()
				# print(qs.query)
				
				if _start and _length:
					start = int(_start)
					length = int(_length)
					page = math.ceil(start / length) + 1
					per_page = length
				
				if _length== '-1':
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
		context['create_url'] = reverse_lazy('marcacion_detalle_create')
		context['title'] = 'Listado de Detalle de Marcaciones '
		return context


class MarcacionDetalleCreateView(PermissionMixin, CreateView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/create.html'
	form_class = MarcacionDetalleForm
	success_url = reverse_lazy('marcacion_detalle_list')
	# permission_required = 'asistencia.add_marcaciondetalle'
	permission_required = 'add_marcaciondetalle'

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def validate_data(self):
		data = {'valid': True}
		try:
			type = self.request.POST['type']
			obj = self.request.POST['obj'].strip()            
			if type == 'denominacion':                
				if MarcacionDetalle.objects.filter(denominacion__iexact=obj):
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
		context['title'] = 'Nuevo registro Detalle de Marcaciones '
		context['action'] = 'add'
		return context


class MarcacionDetalleUpdateView(PermissionMixin, UpdateView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/create.html'
	form_class = MarcacionDetalleForm
	success_url = reverse_lazy('marcacion_detalle_list')
	# permission_required = 'asistencia.change_marcaciondetalle'
	permission_required = 'change_marcaciondetalle'

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
				if MarcacionDetalle.objects.filter(denominacion__iexact=obj).exclude(id=id):
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
		context['title'] = 'Edición de Detalle de Marcaciones '
		context['action'] = 'edit'
		return context


class MarcacionDetalleDeleteView(PermissionMixin, DeleteView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/delete.html'
	success_url = reverse_lazy('marcacion_detalle_list')
	# permission_required = 'asistencia.delete_marcaciondetalle'
	permission_required = 'delete_marcaciondetalle'

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

import json
import math

from core.asistencia.forms import MarcacionDetalleForm
from core.asistencia.models import MarcacionDetalle
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


class MarcacionDetalleListView(PermissionRequiredMixin, ListView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/list.html'
	permission_required = 'cm.view_marcacion_detalle'

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
						_where = " asistencia_marcaciondetalle.id = %s"
					else:
						_search = "%" + _search.replace(' ', '%') + "%"
						_where = " upper(cod ||' '|| fecha ||' '|| hora ) LIKE upper(%s)"
						# _where = " upper(fecha||' '|| hora||' '||asistencia_reloj.denominacion||' '||asistencia_reloj.ip ) LIKE upper(%s)"

				qs = MarcacionDetalle.objects\
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


class MarcacionDetalleCreateView(PermissionRequiredMixin, CreateView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/create.html'
	form_class = MarcacionDetalleForm
	success_url = reverse_lazy('marcacion_detalle_list')
	permission_required = 'cm.add_marcacion_detalle'

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


class MarcacionDetalleUpdateView(PermissionRequiredMixin, UpdateView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/create.html'
	form_class = MarcacionDetalleForm
	success_url = reverse_lazy('marcacion_detalle_list')
	permission_required = 'cm.change_marcacion_detalle'

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


class MarcacionDetalleDeleteView(PermissionRequiredMixin, DeleteView):
	model = MarcacionDetalle
	template_name = 'asistencia/marcacion_detalle/delete.html'
	success_url = reverse_lazy('marcacion_detalle_list')
	permission_required = 'cm.delete_marcacion_detalle'

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

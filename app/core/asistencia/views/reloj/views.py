import json

from config.utils import print_info
from core.asistencia.forms import Reloj, RelojForm
from core.base.models import Sucursal
from core.reports.forms import ReportForm
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from core.security.mixins import PermissionMixin

class RelojListView(PermissionMixin, ListView):
    model = Reloj
    template_name = 'asistencia/reloj/list.html'
    # permission_required = 'asistencia.view_reloj'
    permission_required = 'view_reloj'
    form_class = ReportForm
 
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.suc_usuario = self.request.user.sucursal.id 
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        data = {}
        print(request.POST)
        action = request.POST['action']
        id_reloj = request.POST['id_reloj']
        try:
            if action == 'test_conexion':
                reloj = Reloj.objects.get(id=id_reloj)
                data = reloj.testConexion()
                print_info(str(reloj))
            elif action == 'download_data':
                reloj = Reloj.objects.filter(id=id_reloj).first()
                data = reloj.getMarcaciones()
                print_info(str(reloj))
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):         
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('reloj_create')
        context['title'] = 'Listado de Relojes Marcadores'
        if not self.request.user.is_superuser:
            context['object_list'] = Reloj.objects.filter(sucursal=self.suc_usuario)
        return context


class RelojCreateView(PermissionMixin, CreateView):
    model = Reloj
    template_name = 'asistencia/reloj/create.html'
    form_class = RelojForm
    success_url = reverse_lazy('reloj_list')
    # permission_required = 'asistencia.add_reloj'
    permission_required = 'add_reloj'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:            
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()            
            if type == 'denominacion':                
                if Reloj.objects.filter(denominacion__iexact=obj):
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
        context['title'] = 'Nuevo registro de Reloj Marcador'
        context['action'] = 'add'        
        return context


class RelojUpdateView(PermissionMixin, UpdateView):
    model = Reloj
    template_name = 'asistencia/reloj/create.html'
    form_class = RelojForm
    success_url = reverse_lazy('reloj_list')
    # permission_required = 'asistencia.change_reloj'
    permission_required = 'change_reloj'

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
                if Reloj.objects.filter(name__iexact=obj).exclude(id=id):
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
        context['title'] = 'Edición de un elector'
        context['action'] = 'edit'
        return context


class RelojDeleteView(PermissionMixin, DeleteView):
    model = Reloj
    template_name = 'asistencia/reloj/delete.html'
    success_url = reverse_lazy('reloj_list')
    # permission_required = 'asistencia.delete_reloj'
    permission_required = 'delete_reloj'

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

import locale
import datetime
from django.db.models.aggregates import Count

from django.db.models.fields import FloatField
from django.db.models.query_utils import Q

# from core.bascula.models import Categoria, Cliente, Movimiento, Producto
from core.base.models import Empresa
from core.security.models import Dashboard
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import TemplateView
from core.user.models import User

locale.setlocale(locale.LC_TIME, '')


class DashboardView(LoginRequiredMixin, TemplateView):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        dashboard = Dashboard.objects.filter()
        if dashboard.exists():
            if dashboard[0].layout == 1:
                return 'vtcpanel.html'
        return 'hztpanel.html'

    # def get(self, request, *args, **kwargs):
    #     request.user.set_group_session()
    #     return super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     data = {}
    #     try:
    #         action = request.POST['action']
    #         if action == 'get_graph_1':
    #             info = []
    #             hoy = datetime.datetime.now()
    #             for i in Movimiento.objects.values('producto__denominacion') \
    #                     .filter(fecha=hoy, peso_neto__gt=0)\
    #                     .exclude(anulado=True)\
    #                     .annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField())) \
    #                     .order_by('-tot_recepcion'):
    #                 info.append([i['producto__denominacion'],
    #                              i['tot_recepcion']/1000])

    #             data = {
    #                 'name': 'Stock de Productos',
    #                 'type': 'pie',
    #                 'colorByPoint': True,
    #                 'data': info,
    #             }
    #         elif action == 'get_graph_2':
    #             data = []
    #             categorias=[]
    #             val_tot_recepcion_series=[]
    #             val_tot_recepcion_series_data=[]
    #             val_ctd_recepcion_series=[]
    #             val_ctd_recepcion_series_data=[]

    #             now = datetime.datetime.now()

    #             movimientos = Movimiento.objects\
    #                         .values('producto__denominacion', 'cliente__denominacion') \
    #                         .filter(fecha=now, peso_neto__gt=0)\
    #                         .exclude(anulado=True)\
    #                         .annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
    #                                   ctd_recepcion=Count(True)) \
    #                         .order_by('-tot_recepcion')
    #             for i in movimientos:

    #                 # CATEGORIAS DENOMINACION DE LOS PRODUCTOS + CLIENTES
    #                 categorias.append(i['producto__denominacion'] + ' - ' + i['cliente__denominacion'])
    #                  # SERIES           
    #                 val_tot_recepcion_series_data.append(i['tot_recepcion']/1000)          
    #                 val_ctd_recepcion_series_data.append(i['ctd_recepcion'])
                
    #             val_tot_recepcion_series = {
    #                 'name': 'Toneladas',
    #                 'data': val_tot_recepcion_series_data,
    #                 'dataLabels': {
    #                                         'enabled': 'true',
    #                                         'format': "<b>{point.y:.2f}",
    #                                         'style': {
    #                                             'fontSize': "20 + 'px'"
    #                                         }
    #                                     }
    #             }
    #             val_ctd_recepcion_series = {
    #                 'name': 'Viajes',
    #                 'data': val_ctd_recepcion_series_data,
    #                 'dataLabels': {
    #                                         'enabled': 'true',
    #                                         'format': "<b>{point.y:.0f}",
    #                                         'style': {
    #                                             'fontSize': "20 + 'px'"
    #                                         }
    #                                     }
    #             }
    #             data = {
    #             'categories': categorias,
    #             'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
    #             }
    #             # print(data)

    #         elif action == 'get_graph_3':
    #             data = []
    #             categorias=[]
    #             val_tot_recepcion_series=[]
    #             val_tot_recepcion_series_data=[]
    #             val_ctd_recepcion_series=[]
    #             val_ctd_recepcion_series_data=[]
               
    #             month = datetime.datetime.now().month
    #             year = datetime.datetime.now().year
    #             movimientos = Movimiento.objects\
    #                         .values('fecha') \
    #                         .filter(producto=2, fecha__month=month, fecha__year=year,peso_neto__gt=0)\
    #                         .exclude(cliente=1)\
    #                         .exclude(anulado=True)\
    #                         .annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
    #                                   ctd_recepcion=Count(True)) \
    #                         .order_by('fecha')
    #             #.exclude(anulado=True)\ Este debe ir solo no combinar con otros campos la razon es que 
    #             # no genera de forma correcta el query 
    #             # NOT (anulado=True and otro_campo=1) 
    #             # esto es igual a (False and True) = False
    #             # print(movimientos.query)
    #             for mov in movimientos:
    #                 # CATEGORIAS Dias 1 al 31
    #                 categorias.append(mov['fecha'].strftime('%d'))
    #                 # SERIES           
    #                 val_tot_recepcion_series_data.append(mov['tot_recepcion']/1000)          
    #                 val_ctd_recepcion_series_data.append(mov['ctd_recepcion'])
                   
    #             val_tot_recepcion_series = {
    #                 'name': 'Toneladas',
    #                 'data': val_tot_recepcion_series_data,
    #                 'color':'#f9975d',
    #                 'dataLabels': {
    #                                         'enabled': 'true',
    #                                         'format': "<b>{point.y:.2f}",
    #                                         'style': {
    #                                             'fontSize': "20 + 'px'"
    #                                         }
    #                                     }
    #             }
    #             val_ctd_recepcion_series = {
    #                 'name': 'Viajes',
    #                 'data': val_ctd_recepcion_series_data,
    #                  'color':'#090910',
    #                 'dataLabels': {
    #                                         'enabled': 'true',
    #                                         'format': "<b>{point.y:.0f}",
    #                                         'style': {
    #                                             'fontSize': "20 + 'px'"
    #                                         }
    #                                     }
    #             }
    #             data = {
    #             'categories': categorias,
    #             'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
    #             }
    #             # print(data)
    #             # data['series'] = data
    #             # print(data)
    #         elif action == 'get_graph_4':
    #             data = []
    #             categorias=[]
    #             val_tot_recepcion_series=[]
    #             val_tot_recepcion_series_data=[]
    #             val_ctd_recepcion_series=[]
    #             val_ctd_recepcion_series_data=[]
    #             year = datetime.datetime.now().year
    #             movimientos = Movimiento.objects\
    #                         .values('fecha__month') \
    #                         .filter(producto=2, fecha__year=year, peso_neto__gt=0)\
    #                         .exclude(cliente=1)\
    #                         .exclude(anulado=True)\
    #                         .annotate(tot_recepcion=Sum('peso_neto', output_field=FloatField()),
    #                                   ctd_recepcion=Count(True)) \
    #                         .order_by('fecha__month')
    #             for mov in movimientos:
    #                 # CATEGORIAS MESES
    #                 #Utilizamos una fecha cualquiera para retornar solo el mes ;)
    #                 mes = datetime.date(1900, mov['fecha__month'], 1).strftime('%B').capitalize()
    #                 categorias.append(mes)
    #                 # SERIES           
    #                 val_tot_recepcion_series_data.append(mov['tot_recepcion']/1000)          
    #                 val_ctd_recepcion_series_data.append(mov['ctd_recepcion'])
                
    #             val_tot_recepcion_series = {
    #                 'name': 'Toneladas',
    #                 'data': val_tot_recepcion_series_data,
    #                 'color':'#a9ff96',
    #                 'dataLabels': {
    #                                         'enabled': 'true',
    #                                         'format': "<b>{point.y:.2f}",                          
    #                                         'style': {
    #                                             'fontSize': '14px'
    #                                         }
    #                                     }
    #             }
    #             val_ctd_recepcion_series = {
    #                 'name': 'Viajes',
    #                 'data': val_ctd_recepcion_series_data,
    #                 'color':'#090910',
    #                 'dataLabels': {
    #                                         'enabled': 'true',                                            
    #                                         'format': "<b>{point.y:.0f}",
    #                                         'style': {
    #                                             'fontSize': '14px'
    #                                         }
    #                                     }
    #             }
    #             data = {
    #             'categories': categorias,
    #             'series': [val_tot_recepcion_series,val_ctd_recepcion_series]
    #             }

    #             # print(data)

    #         elif action == 'get_graph_5':
    #             now = datetime.datetime.now()
    #             dataset = Movimiento.objects \
    #                                 .values('producto__denominacion', 'cliente__denominacion') \
    #                                 .filter(fecha=now)\
    #                                 .exclude(anulado=True)\
    #                                 .annotate(vehiculo_entrada_count=Count('id'),
    #                                           vehiculo_salida_count=Count('id', filter=Q(peso_neto__gt=0)),
    #                                           vehiculo_pendiente_count=Count('id', filter=Q(peso_neto=0))) \
    #                                 .order_by('producto__denominacion')
    #             # print(dataset)

    #             categorias = list()
    #             vehiculo_entrada_series_data = list()
    #             vehiculo_salida_series_data = list()
    #             vehiculo_pendiente_series_data = list()

    #             for entry in dataset:
    #                 categorias.append(
    #                     '%s - %s' % (entry['producto__denominacion'], entry['cliente__denominacion']))
    #                 vehiculo_entrada_series_data.append(
    #                     entry['vehiculo_entrada_count'])
    #                 vehiculo_salida_series_data.append(
    #                     entry['vehiculo_salida_count'])
    #                 vehiculo_pendiente_series_data.append(
    #                     entry['vehiculo_pendiente_count'])

    #             vehiculo_entrada_series = {
    #                 'name': 'Entraron',
    #                 'data': vehiculo_entrada_series_data,
    #                 # 'color': 'green'
    #             }

    #             vehiculo_salida_series = {
    #                 'name': 'Salieron',
    #                 'data': vehiculo_salida_series_data,
    #                 # 'color': 'red'
    #             }

    #             vehiculo_pendiente_series = {
    #                 'name': 'Pendientes',
    #                 'data': vehiculo_pendiente_series_data,
    #                 # 'color': 'red'
    #             }

    #             data = {
    #                 'xAxis': {'categories': categorias},
    #                 'series': [vehiculo_entrada_series, vehiculo_salida_series, vehiculo_pendiente_series]
    #             }

    #             # print(data)
    #         else:
    #             data['error'] = 'Ha ocurrido un error'
    #     except Exception as e:
    #         data['error'] = str(e)
    #     return JsonResponse(data, safe=False)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = 'Panel de administración'
    #     context['fecha_actual'] = datetime.datetime.today().strftime("%d/%m/%Y")
    #     context['fecha_hora_actual'] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
    #     context['mes_actual'] = datetime.datetime.today().strftime("%B").capitalize()
    #     context['anho_actual'] = datetime.datetime.today().strftime("%Y")
    #     context['empresa'] = Empresa.objects.first()
    #     context['clientes'] = Cliente.objects.all().count()
    #     context['categorias'] = Categoria.objects.filter().count()
    #     context['productos'] = Producto.objects.all().count()
    #     context['movimientos'] = Movimiento.objects.filter().order_by('-id')[0:10]
    #     context['usuario'] = User.objects.filter(id=self.request.user.id).first()
    #     return context


@requires_csrf_token
def error_404(request, exception):
    return render(request, '404.html', {})


@requires_csrf_token
def error_500(request, exception):
    return render(request, '500.html', {})

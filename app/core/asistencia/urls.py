from django.urls import path
from core.asistencia.views.marcacion_archivo.views import MarcacionArchivoListView
from core.asistencia.views.reloj.views import *
from core.asistencia.views.marcacion.views import *
from core.asistencia.views.marcacion_detalle.views import *


urlpatterns = [
    # Reloj
    path('reloj', RelojListView.as_view(), name='reloj_list'),
    path('reloj/add/', RelojCreateView.as_view(), name='reloj_create'),
    path('reloj/update/<int:pk>/', RelojUpdateView.as_view(), name='reloj_update'),
    path('reloj/delete/<int:pk>/', RelojDeleteView.as_view(), name='reloj_delete'),
    # Marcacion
    path('marcacion', MarcacionListView.as_view(), name='marcacion_list'),
    path('marcacion/add/', MarcacionCreateView.as_view(), name='marcacion_create'),
    path('marcacion/update/<int:pk>/', MarcacionUpdateView.as_view(), name='marcacion_update'),
    path('marcacion/delete/<int:pk>/', MarcacionDeleteView.as_view(), name='marcacion_delete'),
    # Marcacion Archivo
    path('marcacion_archivo', MarcacionArchivoListView.as_view(), name='marcacion_archivo_list'),
    # path('marcacion/add/', MarcacionCreateView.as_view(), name='marcacion_create'),
    # path('marcacion/update/<int:pk>/', MarcacionUpdateView.as_view(), name='marcacion_update'),
    # path('marcacion/delete/<int:pk>/', MarcacionDeleteView.as_view(), name='marcacion_delete'),
    # Marcacion Detalle
    path('marcacion_detalle', MarcacionDetalleListView.as_view(), name='marcacion_detalle_list'),
    path('marcacion_detalle/add/', MarcacionDetalleCreateView.as_view(), name='marcacion_detalle_create'),
    path('marcacion_detalle/update/<int:pk>/', MarcacionDetalleUpdateView.as_view(), name='marcacion_detalle_update'),
    path('marcacion_detalle/delete/<int:pk>/', MarcacionDetalleDeleteView.as_view(), name='marcacion_detalle_delete'),
    
   ]
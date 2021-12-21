from django.contrib import admin
from core.base.admin import ModeloAdminBase
from core.asistencia.models import Reloj
from core.asistencia.models import Marcacion
from core.asistencia.models import MarcacionDetalle

# Register your models here.
class MarcacionAdmin(ModeloAdminBase):
    list_display = ('id','fecha','hora')
    search_fields = ('fecha',)
admin.site.register(Reloj, ModeloAdminBase)
admin.site.register(Marcacion, MarcacionAdmin)
admin.site.register(MarcacionDetalle, ModeloAdminBase)
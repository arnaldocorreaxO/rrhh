
from django.http import HttpResponse
from django.template.loader import get_template
from io import StringIO as StringIO
from weasyprint import HTML, CSS
from django.conf import settings

from datetime import datetime, timedelta

def print_info(*args):
	txt = args[0] 	# Texto
	rel = '-'*15	# Relleno
	print(f'{rel} {txt.center(70)} {rel}')

def print_err(*args):
	txt = args[0]	#Texto
	rel = '#'*15	#Relleno
	print(f'{rel} {txt.center(70)} {rel}')

def calculate_age(born):
	from datetime import date
	today = date.today()
	#((today.month, today.day) < (born.month, born.day)) That can be done much simpler
	# considering that int(True) is 1 and int(False) is 0:
	return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


#datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
#vAnhoActual = datetime.now().year
vFechaActual = datetime.today().strftime('%d/%m/%Y')


def choiceAnho():
	import datetime
	vAnhoActual = datetime.datetime.now().year
	CHOICE = [(str(x), str(x)) for x in range(vAnhoActual, vAnhoActual - 10, -1)]
	return CHOICE


def choiceMes():
	CHOICE = [
			('1', "Enero"),
		 			('2', "Febrero"),
		 			('3', "Marzo"),
		 			('4', "Abril"),
		 			('5', "Mayo"),
		 			('6', "Junio"),
		 			('7', "Julio"),
		 			('8', "Agosto"),
		 			('9', "Setiembre"),
		 			('10', "Octubre"),
		 			('11', "Noviembre"),
		 			('12', "Diciembre"),
		]
	return CHOICE


def fechaInicial():
  	import datetime
  	from datetime import timedelta
  	return ((datetime.datetime.now() - timedelta(days=datetime.datetime.now().day - 1)).strftime('%d/%m/%Y'))


def fechaActual():
  	import datetime
  	return (datetime.datetime.now().strftime('%d/%m/%Y'))


def pMesActual():
	import datetime
	return (datetime.datetime.now().month)


def choiceTipoEmpleado():
	CHOICE = [
			('PER', 'PERMANENTE'),
			('CON', 'CONTRATADO'),
			('COM', 'COMISIONADO'),
	]
	return CHOICE


def choiceSede():
	CHOICE = [
			('CEN', 'CENTRAL'),
			('VTA', 'VILLETA'),
			('VMI', 'VALLEMI'),
	]
	return CHOICE


def choiceEstado():
	CHOICE = [
			('A', 'ACTIVO'),
			('I', 'INACTIVO'),
	]
	return CHOICE

def choiceTipoMarcacion():
	CHOICE = [
			('E', 'ENTRADA'),
			('S', 'SALIDA'),
	]
	return CHOICE


def choiceGenero():
	CHOICE = [
			('M', 'Masculino'),
			('F', 'Femenino'),
		]
	return CHOICE


def choiceEstadoCivil():
	CHOICE = [
			('SO', 'Soltero/a'),
			('CA', 'Casado/a'),
			('VI', 'Viudo/a'),
			('DI', 'Divorciado/a'),
			('SE', 'Separado/a'),
			('DE', 'Desconocido/a'),
		]
	return CHOICE


def choiceTipoRecibo():
	CHOICE = [
			('NOR', 'SALARIO'),
			('AGU', 'AGUINALDO'),
			#('100','SUBSIDIO (100) - GRATIFICACION'),
			#('300','SUBSIDIO (300) - GRATIFICACION'),
		]
	return CHOICE


def pdf_generation(template_src, context_dict):
	template = get_template(template_src)
	context = context_dict
	html_template = template.render(context)
	pdf_file = HTML(string=html_template).write_pdf(
		stylesheets=[CSS(settings.STATICFILES_DIRS[0] + '/css/sb-admin.css'), CSS(settings.STATICFILES_DIRS[0] + '/css/sb-admin.css')])
	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="recibo.pdf"'
	return response

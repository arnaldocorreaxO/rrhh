/*
===================================================================
Author: xO
C:\Users\arnaldo\proyectos\electoral\.env\Lib\site-packages\django\
contrib\admin\templates\admin\change_form.html
Se utiliza para modificar el comportamiento de todos los SELECT en 
el Administrador de Django
En ese path se referencia a este js para Select2 Anidado de Barrios 
y Manzanas
====================================================================
*/
$(function () {
    
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });


    // FILTRAR PRODUCTOS POR CLIENTE SELECCIONADO
 
    var select_cliente = $('select[name="cliente"]');
    var select_producto = $('select[name="producto"]');
    var select_vehiculo = $('select[name="vehiculo"]');
    var token = $('input[name="csrfmiddlewaretoken"]');
    // alert(token.val())

        select_cliente.on('change', function () {
            var id_cliente = $(this).val(); //ID CLIENTE        
            var options = '<option value="">--------------</option>';
            if (id_cliente === '') {
                select_producto.html(options);
                return false;
            }
            $.ajax({
                headers: { "X-CSRFToken": token.val() },
                // url: window.location.pathname,
                url: '/bascula/movimiento/add/',
                type: 'POST',
                data: {
                    'action': 'search_producto_id',
                    'id': id_cliente,
                },
                dataType: 'json',
            }).done(function (data) {
                if (!data.hasOwnProperty('error')) {
                    select_producto.html('').select2({
                        theme: "bootstrap4",
                        language: 'es',
                        data: data
                    });
                    return false;
                }
                message_error(data.error);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ': ' + errorThrown);
            }).always(function (data) {
                //select_producto.html(options);
            });



            var id_vehiculo = $('#id_vehiculo').val(); //ID VEHICULO
            $.ajax({
                headers: { "X-CSRFToken": token.val() },
                // url: window.location.pathname,
                url: '/bascula/movimiento/add/',
                type: 'POST',
                data: {
                    'action': 'search_peso_tara_interno',
                    'id': id_vehiculo
                },
                dataType: 'json',
            }).done(function (data) {
                if (!data.hasOwnProperty('error')) {
                    // SOLO INTERNO 
                    if (id_cliente == 1) {
                        $('#id_peso_entrada').val(parseInt(data['peso']));
                    };
                    return false;
                }
                $('#id_vehiculo').val('').change();
                $('#id_cliente').val('').change();
                message_error(data.error);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ': ' + errorThrown);
            }).always(function (data) {
                //select_producto.html(options);
            });

        });

        select_vehiculo.on('change', function () {
            select_cliente.change();
        });
   
});
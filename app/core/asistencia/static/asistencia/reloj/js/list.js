$(function(){
    
    $('.btnTestConexion').on('click', function (e) {
        e.preventDefault(); 
        var id_reloj = $(this).attr('value');
        testConexion(id_reloj); 
        return false; 

    });

    $('.btnDownloadData').on('click', function (e) {
        e.preventDefault(); 
        var id_reloj = $(this).attr('value');
        downloadData(id_reloj); 
        return false; 

    });

});

function testConexion(id_reloj){   
    

    var parameters = {
        'action': 'test_conexion',
        'id_reloj': id_reloj,
    };

    submit_with_ajax('Notificación',
            '¿Estas seguro de realizar la siguiente acción?',
            window.location.pathname,
            parameters,           
            function (data) {
                if (!data.hasOwnProperty('error')) {
                    message_success(data.info)
                    return false;
                };
            });
 
};

function downloadData(id_reloj) {
    /*Descarga los datos de marcacion del Reloj*/
    var parameters = {
        'action': 'download_data',
        'id_reloj': id_reloj,
    };
    submit_with_ajax_loading('Notificación',
        '¿Estas seguro desea descargar los datos del Reloj?',
        window.location.pathname,
        parameters,
        function (data) {
            if (!data.hasOwnProperty('error')) {
                message_success(data.info)
                return false;
            };
        });
};


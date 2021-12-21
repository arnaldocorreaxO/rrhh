var date_current;
var input_daterange;
var tblData;
var columns = [];
function init() {


    tblData = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
        // deferRender: true,
        // processing: true,
        // serverSide: true,
    });

    $.each(tblData.settings()[0].aoColumns, function (key, value) {
        columns.push(value.sWidthOrig);
    });

    $('#data tbody tr').each(function (idx) {
        $(this).children("td:eq(0)").html(idx + 1);
        console.log(idx+1);
    });
};

function getData(all) {
    var parameters = {
        'action': 'search',
        // 'marcacion_id': '0',
        // 'start_date': input_daterange.data('daterangepicker').startDate.format('YYYY-MM-DD'),
        // 'end_date': input_daterange.data('daterangepicker').endDate.format('YYYY-MM-DD'),
    };

    if (all) {
        parameters['start_date'] = '';
        parameters['end_date'] = '';
    }

    tblData = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        paging: true,
        ordering: true,
        searching: true,
        // stateSave: true,      Salva la seleccion de longitud de pagina lengthMenu  
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "Todos"]],
        pagingType: "full_numbers",
        pageLength: 10,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            // dataSrc: ""
        },
        columns: [
            { data: "id" },
            { data: "marcacion" },
            { data: "reloj" },
            { data: "cod" },
            { data: "fecha" },
            { data: "hora" },
            { data: "tipo" },
            { data: "id" },
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    var buttons = '';
                    buttons += '<a href="/asistencia/marcacion/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
                    buttons += '<a href="/asistencia/marcacion/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash"></i></a> ';
                    return buttons;
                }
            },
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
}

$(function () {

    date_current = new moment().format("YYYY-MM-DD");
    input_daterange = $('input[name="date_range"]');

    input_daterange
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            getData(false);
        });
    
    init();
    getData(false);

    $('.btnSearchAll').on('click', function () {
        input_daterange.val('');
        getData(true);
    });

    $('#data tbody')
    .on('click', 'a[rel="load"]', function (e) {
        e.preventDefault(); 
        var tr = tblData.cell($(this).closest('td, li')).index();
        var data = tblData.row(tr.row).data();
        loadData(data.id)
        return false; 
    });

});


function loadData(id){   
    

    var parameters = {
        'action': 'load_data',
        'marcacion_id': id,
    };

    submit_with_ajax('Notificación',
            '¿Estas seguro desea cargar los datos de la Marcación?',
            window.location.pathname,
            parameters,           
            function (data) {
                if (!data.hasOwnProperty('error')) {
                    message_success(data.info)
                    return false;
                };
            });
 
};
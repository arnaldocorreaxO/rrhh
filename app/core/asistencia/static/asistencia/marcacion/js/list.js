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
        order: [[0, 'desc'],],
        columns: [
            { data: "id" },
            { data: "suc_denom_corta" },
            { data: "fecha" },
            { data: "hora" },
            { data: "fec_insercion" },
            { data: "fec_modificacion" },
            // { data: "archivo" },
            { data: "id" },
        ],
        columnDefs: [           
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    // var buttons = '';
                    // btnClass = "btn btn-secondary btn-flat disabled_load_data"
                    // if (!row.procesado) {
                    //     btnClass = "btn btn-primary btn-flat"  
                    // };  
                    // if (row.suc_denom_corta.includes("CIP")) {
                    //     buttons += '<a href="#" rel="load2" class="btn btn-primary  btn-flat" value="' + row.id + '"data-toggle="tooltip" title="Insertar Datos MSSQL Villeta"><i class="fas fa-cloud-upload-alt"></i></a> ';
                    // }else {
                    //     buttons += '<a href="#" rel="#" class="' + btnClass + '" value="#" data-toggle="tooltip" title="#"><i class="fas fa-cloud-upload-alt"></i></a> ';
                    // }                 
                    // buttons += '<a href="#" rel="load1" class="' + btnClass + '" value="' + row.id + '"data-toggle="tooltip" title="Insertar Datos Informix"><i class="fas fa-upload"></i></a> ';                                                          
                    // buttons += '<a class="btn btn-primary  btn-flat" data-toggle="tooltip" title="Detalles" rel="detail"><i class="fas fa-folder-open"></i></a> ';
                    // buttons += '<a href="/asistencia/marcacion/update/' + row.id + '/" class="btn btn-warning btn-flat" data-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a> ';
                    // buttons += '<a href="/asistencia/marcacion/delete/' + row.id + '/" class="btn btn-danger btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash"></i></a> ';
                    // return buttons;
                    function createButton(href, className, title, iconClass, rel, value) {
                        return `<a href="${href}" rel="${rel}" class="${className}" value="${value}" data-toggle="tooltip" title="${title}">
                                    <i class="${iconClass}"></i>
                                </a> `;
                    }
                    
                    // function generateButtons(row) {
                        let buttons = '';
                        let btnClass = row.procesado ? "btn btn-secondary btn-flat disabled_load_data" : "btn btn-primary btn-flat";
                    
                        if (row.suc_denom_corta.includes("CIP")) {
                            buttons += createButton("#", "btn btn-info btn-flat", "Insertar Datos MSSQL Villeta", "fas fa-cloud-upload-alt", "load2", row.id);
                        } else {
                            buttons += createButton("#", btnClass, "#", "fas fa-cloud-upload-alt", "#", "#");
                        }
                    
                        buttons += createButton("#", btnClass, "Insertar Datos Informix", "fas fa-upload", "load1", row.id);
                        buttons += createButton("#", "btn btn-primary btn-flat", "Detalles", "fas fa-folder-open", "detail", "");
                        buttons += createButton(`/asistencia/marcacion/update/${row.id}/`, "btn btn-warning btn-flat", "Editar", "fas fa-edit", "", "");
                        buttons += createButton(`/asistencia/marcacion/delete/${row.id}/`, "btn btn-danger btn-flat", "Eliminar", "fas fa-trash", "", "");
                    
                        return buttons;
                    // }
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

    // Cargar datos de marcacion Informix Central, Informix Villeta y MSSQL Vallemi (Vallemi no utiliza Informix)
    $('#data tbody')
    .on('click', 'a[rel="load1"]', function (e) {
        e.preventDefault(); 
        var tr = tblData.cell($(this).closest('td, li')).index();
        var data = tblData.row(tr.row).data();
        loadData(data.id)
        return false; 
    });

    // Cargar datos de marcacion MSSQL Villeta (Villeta utiliza Informix que se carga en el loadData anterior)
    $('#data tbody')
    .on('click', 'a[rel="load2"]', function (e) {
        e.preventDefault(); 
        var tr = tblData.cell($(this).closest('td, li')).index();
        var data = tblData.row(tr.row).data();
        loadDataMSSQLVilleta(data.id)
        return false; 
    });


    $('#data tbody').on('click', 'a[rel="detail"]', function () {
        $('.tooltip').remove();
        var tr = tblData.cell($(this).closest('td, li')).index(),
            row = tblData.row(tr.row).data();
        $('#tblArchivo').DataTable({
            // responsive: true,
            // autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search_archivos',
                    'id': row.id
                },
                dataSrc: ""
            },
            scrollX: true,
            scrollCollapse: true,
            columns: [
                {data: "id"},
                {data: "marcacion"},
                {data: "reloj"},
                {data: "fec_insercion"},                
                {data: "fec_modificacion"},                
                {data: "archivo"},                
            ],
            columnDefs: [
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        var buttons = '<span class="badge badge-secondary">Sin archivo</span>';
                        if (!$.isEmptyObject(row.archivo)) {
                            buttons = '<a href="' + row.archivo + '" target="_blank" class="btn btn-secondary btn-xs btn-flat" data-toggle="tooltip" title="Descargar Respaldo"><i class="fas fa-database"></i></a>';
                        }
                        return buttons;
                    }
                },
            ]
        });
        $('#myModalDetails').modal('show');
    });


});


function loadData(id) {
    /*Inserta los datos de marcacion en Informix*/
    var parameters = {
        'action': 'load_data',
        'marcacion_id': id,
    };
    submit_with_ajax_loading('Notificación',
        '¿Estas seguro desea cargar los datos de la Marcación?',
        window.location.pathname,
        parameters,
        function (data) {
            if (!data.hasOwnProperty('error')) {
                message_success(data.info)
                tblData.draw('page');
                return false;
            };
        });
};

function loadDataMSSQLVilleta(id) {
    /*Inserta los datos de marcacion en Informix*/
    var parameters = {
        'action': 'load_data_to_mssql_villeta',
        'marcacion_id': id,
    };
    submit_with_ajax_loading('Notificación',
        '¿Estas seguro desea cargar los datos de la Marcación?',
        window.location.pathname,
        parameters,
        function (data) {
            if (!data.hasOwnProperty('error')) {
                message_success(data.info)
                tblData.draw('page');
                return false;
            };
        });
};

function get_graph_1(args) {

    var graph_1 = Highcharts.chart('graph_1', {
        chart: {
            type: 'pie',
            options3d: {
                enabled: true,
                alpha: 45,
                beta: 0
            }
        },
        exporting: {
            enabled: false
        },
        title: {
            text: ''
        },
        subtitle: {
            text: args[0] + '<br> Actualizado: '+ args[1]
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        tooltip: {
            pointFormat: 'Stock: <b>{point.y:.2f} TON</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                depth: 35,
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
    });


    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'get_graph_1'
        },
        dataType: 'json',
    }).done(function (request) {
        if (!request.hasOwnProperty('error')) {
            graph_1.addSeries(request);
            return false;
        }
        message_error(request.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {

    });
}
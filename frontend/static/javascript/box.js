window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};
var default_data = {
    datasets: []
};
var config = {
    type: 'line',
    data: JSON.parse(JSON.stringify(default_data)),
    options: {
        responsive: true,
        hoverMode: 'index',
        stacked: false,
        title: {
            display: true,
            text: 'Box in Japan'
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            x: {
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'DateTime'
                }
            },
            xAxes: [{
                type: 'time',
                time: {
                    displayFormats: {
                        'millisecond': 'MMM DD',
                        'second': 'MMM DD',
                        'minute': 'h:mm a',
                        'hour': 'hA',
                        'day': 'MMM D',
                    },
                    "unit": "hour"
                }
            }],
            yAxes: [
                {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    id: 'sale',
                },
                {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    id: 'rate',
                    ticks: {
                        suggestedMax: 1.00,
                        suggestedMin: 0.00
                    }
                },
            ],/*
            sale: {
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Sale'
                },
                position: 'left',
            },
            rate: {
                type: 'linear',
                display: true,
                position: 'right',
                gridLines: {
                    drawOnChartArea: false,
                }
            }*/
        }
    }
};

function show_modal() {
    $("#loading_modal").modal("show");
}

function close_modal() {
    setTimeout(function () {
        $('#loading_modal').modal('hide')
    }, 500)
}

var colorNames = Object.keys(window.chartColors);
var exists_time = [];
var movie_data = {};

function update_chart(names, day_offset = 0) {
    show_modal();
    const d = new Date();
    let date = d.getUTCDate(), month = d.getUTCMonth(), year = d.getUTCFullYear(),
        utc_day_start = Date.UTC(year, month, date, 0, 0, 0, 0);

    var japan_day_start = moment(new Date(utc_day_start - 9 * 3600 * 1000));
    japan_day_start.add(day_offset, 'days');
    var japan_day_end = moment(new Date(utc_day_start - 9 * 3600 * 1000));
    japan_day_end.add(day_offset + 1, 'days');
    let datetime_format = 'YYYY/MM/DD HH:mm:ssZZ';
    $.post('/api/japan_box', {
            start: japan_day_start.format(datetime_format),
            end: japan_day_end.format(datetime_format),
            name: names
        },
        function (resp) {
            var color_count = 0;
            var new_datasets = {};
            resp.names.forEach(function (item, _index) {
                let new_color = window.chartColors[colorNames[color_count % colorNames.length]];
                if (movie_data[item] === undefined) {
                    movie_data[item] = [];
                }
                if (movie_data[item + 'rate'] === undefined) {
                    movie_data[item + 'rate'] = [];
                }
                new_datasets[item] = {
                    label: item,
                    backgroundColor: new_color,
                    borderColor: new_color,
                    data: movie_data[item],
                    fill: false,
                    lineTension: 0,
                    yAxisID: 'sale'
                };
                color_count++;
                new_color = window.chartColors[colorNames[color_count % colorNames.length]];
                new_datasets[item + 'rate'] = {
                    label: item + ' Rate',
                    backgroundColor: new_color,
                    borderColor: new_color,
                    data: movie_data[item + 'rate'],
                    fill: false,
                    //lineTension: 0,
                    yAxisID: 'rate',
                };
                color_count++;
            });
            var box = resp.data[0];
            new_exists_time = [];
            for (var key in box) {
                if (exists_time.indexOf(key) === -1) {
                    new_exists_time.push(key);
                    box[key].forEach(function (movie) {
                        movie_data[movie.name].push({x: moment(key), y: movie.sale});
                        movie_data[movie.name + 'rate'].push({x: moment(key), y: movie.rate});
                    });
                }
            }
            exists_time = exists_time.concat(new_exists_time);
            for (var key in new_datasets) {
                let found = false;
                for (var d in config.data.datasets) {
                    if (config.data.datasets[d].label === key) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    config.data.datasets.push(new_datasets[key]);
                }
            }
            console.log(config.data.datasets);
            close_modal();
            window.chart.update();
        })
        .fail(function (resp) {
            close_modal();
            setTimeout(function () {
                show_toast('Error', resp.responseText, 'red')
            }, 2000);
        })
}

function update_chart_wrapper() {
    update_chart(["アナと雪の女王２"]);//, "スター・ウォーズ スカイウ"]);
}

window.onload = function () {
    const ctx = document.getElementById('canvas').getContext('2d');
    window.chart = new Chart(ctx, config);
    update_chart_wrapper();
    document.getElementById('refresh').addEventListener('click', update_chart_wrapper);
};

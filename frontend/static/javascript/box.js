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

var yAxes_with_right = [
    {
        type: 'linear',
        display: true,
        position: 'left',
        id: 'sale',
        ticks: {
            suggestedMin: 0.00
        }
    },
    {
        type: 'linear',
        display: true,
        position: 'right',
        id: 'rate',
        ticks: {
            suggestedMin: 0.00
        }
    },
];

var yAxes_without_right = [
    {
        type: 'linear',
        display: true,
        position: 'left',
        id: 'sale',
        ticks: {
            suggestedMin: 0.00
        }
    }
];

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
            yAxes: [],
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

let expected_movie_name = [
    "アナと雪の女王２",
    "スター・ウォーズ"
];

let day_offset = 0;

let display_rate = true;

function onclick_checkbox_display_rate() {
    if ($("#display_rate").is(':checked')) {
        display_rate = true;
        window.chart.config.data = JSON.parse(JSON.stringify(default_data));
        update_chart(expected_movie_name, day_offset);
    } else {
        display_rate = false;
        window.chart.config.data = JSON.parse(JSON.stringify(default_data));
        update_chart(expected_movie_name, day_offset);
    }
}

var colorNames = Object.keys(window.chartColors);
var exists_time = [];
var movie_data = {};

function set_today() {
    change_day_offset(-day_offset);
}

function fix_next_day_button() {
    if (day_offset >= 0) {
        $("#next_day").attr("disabled", true);
    } else {
        $("#next_day").attr("disabled", false);
    }
}

function change_day_offset(new_day_offset) {
    day_offset += new_day_offset;
    fix_next_day_button();
    window.chart.config.data = JSON.parse(JSON.stringify(default_data));
    window.chart.update();
    movie_data = {};
    exists_time = [];
    update_chart(expected_movie_name, day_offset);
}

function get_datetime(day_offset) {
    const d = new Date();
    let date = d.getUTCDate(), month = d.getUTCMonth(), year = d.getUTCFullYear(),
        utc_day_start = Date.UTC(year, month, date, 0, 0, 0, 0);

    var japan_day_start = moment(new Date(utc_day_start - 9 * 3600 * 1000));
    japan_day_start.add(day_offset, 'days');
    var japan_day_end = moment(new Date(utc_day_start - 9 * 3600 * 1000));
    japan_day_end.add(day_offset + 1, 'days');
    return [japan_day_start, japan_day_end];
}

function update_chart(names, day_offset = 0) {
    show_modal();
    const [japan_day_start, japan_day_end] = get_datetime(day_offset);

    let datetime_format = 'YYYY/MM/DD HH:mm:ssZZ';
    $.get('/api/japan_box', {
            start: japan_day_start.format(datetime_format),
            end: japan_day_end.format(datetime_format),
            name: names
        },
        function (resp) {
            var color_count = 0;
            var new_datasets = {};
            if (display_rate) {
                config.options.scales.yAxes = yAxes_with_right;
            } else {
                config.options.scales.yAxes = yAxes_without_right;
            }
            resp.names.forEach(function (item, _index) {
                let new_color = window.chartColors[colorNames[color_count % colorNames.length]];
                if (movie_data[item] === undefined) {
                    movie_data[item] = [];
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
                if (display_rate) {
                    new_color = window.chartColors[colorNames[color_count % colorNames.length]];
                    if (movie_data[item + ' Rate'] === undefined) {
                        movie_data[item + ' Rate'] = [];
                    }
                    new_datasets[item + ' Rate'] = {
                        label: item + ' Rate',
                        backgroundColor: new_color,
                        borderColor: new_color,
                        data: movie_data[item + ' Rate'],
                        fill: false,
                        //lineTension: 0,
                        borderDash: [5, 5],
                        yAxisID: 'rate',
                    };
                }
                color_count++;
            });
            var box = resp.data;
            new_exists_time = [];
            for (var key in box) {
                if (exists_time.indexOf(key) === -1) {
                    new_exists_time.push(key);
                    box[key].forEach(function (movie) {
                        movie_data[movie.name].push({x: moment(key), y: movie.sale});
                        if (display_rate)
                            movie_data[movie.name + ' Rate'].push({x: moment(key), y: movie.rate});
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
            $("#datetime_range_start").text(japan_day_start.format(datetime_format));
            $("#datetime_range_end").text(japan_day_end.format(datetime_format));
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
    update_chart(expected_movie_name, day_offset);
}

window.onload = function () {
    const ctx = document.getElementById('canvas').getContext('2d');
    window.chart = new Chart(ctx, config);
    fix_next_day_button();
    update_chart_wrapper();
    document.getElementById('refresh').addEventListener('click', update_chart_wrapper);
};

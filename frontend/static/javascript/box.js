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
}
var config = {
    type: 'line',
    data: JSON.parse(JSON.stringify(default_data)),
    options: {
        responsive: true,
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
            y: {
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Sale'
                }
            }
        }
    }
};
var colorNames = Object.keys(window.chartColors);
var exists_time = [];
var movie_data = {};
var update_chart = function (names) {
    document.getElementById('refresh').innerText = "Loading";
    axios.post("/api/japan_box", 
        Qs.stringify({
            name: names 
        }))
        .then(function (resp) {
            var color_count = 0;
            var new_datasets = {};
            names.forEach(function (item, _index) {
                var new_color = window.chartColors[colorNames[color_count % colorNames.length]];
                if (movie_data[item] === undefined) {
                    movie_data[item] = []
                }
                new_datasets[item] = {
                    label: item,
                    backgroundColor: new_color,
                    borderColor: new_color,
                    data: movie_data[item],
                    fill: false,
                    lineTension: 0,
                };
                color_count++;
            })
            var box = resp.data.data[0];
            new_exists_time = []
            for (var key in box) {
                if (exists_time.indexOf(key) == -1) {
                    new_exists_time.push(key);
                    //console.log(movie.name);
                    box[key].forEach(movie => movie_data[movie.name].push({ x: moment(key), y: movie.sale }));
                }
            }
            exists_time = exists_time.concat(new_exists_time);
            for (var key in new_datasets) {
                var found = false;
                for (var d in config.data.datasets) {
                    if (config.data.datasets[d].label == key) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    config.data.datasets.push(new_datasets[key]);
                }
            }

            window.chart.update();
            document.getElementById('refresh').innerText = "Refresh";
        })
};
var update_chart_wrapper = function () {
    update_chart(["アナと雪の女王２", "スター・ウォーズ スカイウォ…"]);
}
window.onload = function () {
    var ctx = document.getElementById('canvas').getContext('2d');
    window.chart = new Chart(ctx, config);
    update_chart_wrapper();
    document.getElementById('refresh').addEventListener('click', update_chart_wrapper);
};

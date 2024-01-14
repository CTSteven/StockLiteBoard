
var stockChart = null;
var epsChart = null;
var priceCompareSlider = null;
var default_ticker = 'GOOG';
var discount_slide_start = null;

$(function () {


    $('[data-toggle="tooltip"]').tooltip();

    $("#select-discount").slider({
        tooltip: 'always'
    });

    $("#select-margin").slider({
        tooltip: 'always'
    });

    $('#select-discount').on('slideStop', function (e) {
        var ticker;
        ticker = $('#select-stock').val();
        if ($('#select-discount-value').text() == e.value)
            return false;
        $('#select-discount-value').text(e.value);
        updateInvestmentSuggestion(ticker);
        $('#PV').fadeOut(500).fadeIn(500);
        $('#margin-price').fadeOut(500).fadeIn(500);

    });

    $('#select-margin').on('slideStop', function (e) {
        var ticker;
        ticker = $('#select-stock').val();
        if ($('#select-margin-value').text() == e.value)
            return false;
        $('#select-margin-value').text(e.value);
        var present_value = parseFloat($('#PV').text());
        var margin_rate = parseFloat(e.value);
        var price_margin = present_value * margin_rate;
        var latest_price = parseFloat($('#latest-price').text());
        $('#price-margin').html('&#x00B1; ' + price_margin.toFixed(2));
        $('#price-margin').fadeOut(500).fadeIn(500);
        updatePriceCompareSlider(present_value, margin_rate, latest_price)

    });


    $('#select-stock').change(function () {
        var ticker;
        ticker = $(this).val();
        updateSelectedStock(ticker);
    });

});

$(document).ready(function() {
    updateSelectedStock('GOOG');
});

function updateSelectedStock(ticker) {
        Promise.all([
            updateStockPriceHistory(ticker),
            updateFinancialReport(ticker),
            updateInvestmentSuggestion(ticker)
        ]).then(([historyResult, reportResult, suggestionResult]) => {
           
        }).catch(error => {
            console.log(error);
            alert(error);
        });
}


function updateStockPriceHistory(ticker) {
    var url = '/pages/stockPriceHistory?ticker=' + ticker;
    showDataLoading();

    $.ajax({
        type: "GET",
        url: url,
        success: function (data) {
            ohlc = [],
                volume = [],
                dataLength = data.length,
                i = 0;
            for (i; i < dataLength; i += 1) {
                ohlc.push([
                    data[i][0], // the date
                    data[i][1], // open
                    data[i][2], // high
                    data[i][3], // low
                    data[i][4] // close
                ]);
                volume.push([
                    data[i][0], // the date
                    data[i][5] // the volume
                ]);
            }
            /*
            stockChart.setTitle( {
                text: ticker+', Stock Price'
            });*/
            stockChart.series[0].update({
                data: ohlc,
                name: ticker + ' Stock Price'
            }, false);
            stockChart.series[4].update({
                data: volume,
                name: ticker + ' Volume '
            }, false);
            stockChart.redraw();
            yahooFinancial_url =
                '<a target="YahooFinancial" class="text-success ml-3" style="font-size:1rem; text-decoration:underline" href="https://finance.yahoo.com/quote/' +
                ticker + '/">Yahoo Financial</a>';
            $('#stock-chart-title').html(ticker + ', ' + gettext('Stock Price History') + ' ' + yahooFinancial_url);
            $('#stock-chart-title').fadeOut(500).fadeIn(500);
            hideDataLoading();
        },
        error: function (xhr, status, error) {
            processAjaxErrorMessage(xhr, status, error);
            hideDataLoading();
            // console.log("ajax call went wrong:" + request.responseText);
            // alert("Error message :" + request.responseText);
        }
    });

    priceCompareSlider = $("#price-compare-slider > .js-range-slider").ionRangeSlider({
        type: "double",
        min: 1000,
        max: 2000,
        from: 1300,
        to: 1700,
        grid: true,
        grid_snap: false,
        from_fixed: true,  // fix position of FROM handle
        to_fixed: true,     // fix position of TO handle
        to_shadow: false,
        prettify_separator: ",",
        grid_num: 6,
        onStart: function (data) {
            var html = '';
            var left = priceConvertToPercent(0, 1000, 2000);
            html += '<span id="latest-price-mark" style="left:' + left + '%">' + 0 + '<br>Latest Price</span>';
            data.slider.append(html);
        }
    });
};

function priceConvertToPercent(num, min, max) {
    return (num - min) / (max - min) * 100;
}

function updatePriceCompareSlider(present_value, margin_rate, latest_price) {
    var margin_low = present_value * (1 - margin_rate);
    var margin_heigh = present_value * (1 + margin_rate);
    var half_range = 0;
    if (margin_low < 0) {
        margin_low = 0;
    }
    if (latest_price < margin_low) {
        half_range = (present_value - latest_price) * 1.25;
    }
    else if (latest_price > margin_heigh) {
        half_range = (latest_price - present_value) * 1.25;
    }
    else {
        half_range = (margin_heigh - present_value) * 1.25;
    }
    var min = present_value - half_range;
    var max = present_value + half_range;
    var left = priceConvertToPercent(latest_price, min, max);
    min = min.toFixed(0);
    max = max.toFixed(0);
    if (min < 0) min = 0;
    margin_low = margin_low.toFixed(0);
    margin_heigh = margin_heigh.toFixed(0);
    latest_price = latest_price.toFixed(0);
    priceCompareSlider.data('ionRangeSlider').update({
        min: min,
        max: max,
        from: margin_low,
        to: margin_heigh,
        onUpdate: function (data) {
            var html = '';
            var left = priceConvertToPercent(latest_price, min, max);
            html += '<span id="latest-price-mark" style="left:' + left + '%">' + latest_price + '<br>' + gettext('Latest Price') + '</span>';
            data.slider.append(html);
        }
    });
    $('#expected-price-range').fadeOut(500).fadeIn(500);
}


function updateInvestmentSuggestion(ticker) {
    var discount;
    var margin;
    discount = $('#select-discount').val();
    margin = $('#select-margin-value').text();
    post_data = JSON.stringify({
        'ticker': ticker,
        'discount': parseFloat(discount) / 100.0,
        'margin': parseFloat(margin)
    })
    $.ajax({
        type: "POST",
        url: "/pages/investmentSuggestion",
        dataType: 'json',
        data: post_data,
        success: function (data) {
            obj = data[0];
            price_margin = parseFloat(obj.PV) * parseFloat(margin);
            price_margin = price_margin.toFixed(2);
            $('#annual-growth-rate').text(obj.annualgrowthrate);
            $('#last-eps').text(obj.lasteps);
            $('#future-eps').text(obj.futureeps);
            $('#pe-ratio').text(obj.peratio);
            $('#FV').text(obj.FV);
            $('#PV').text(obj.PV);
            $('#price-margin').html('&#x00B1; ' + price_margin);
            $('#latest-price').text(obj.lastprice);
            //$('#suggestion').text(obj.suggestion);
            $('#investment-suggestion-title').text(ticker + ', ' + gettext('Predicting Future Value'));
            $('#investment-suggestion-title').fadeOut(500).fadeIn(500);
            updatePriceCompareSlider(parseFloat(obj.PV), parseFloat(margin), parseFloat(obj.lastprice));
        },
        error: function (xhr, status, error) {
            processAjaxErrorMessage(xhr, status, error);
            // console.log("ajax call went wrong:" + request.responseText);
            // alert("Error message :" + request.responseText);
        }
    })
}

function updateFinancialReport(ticker) {
    post_data = JSON.stringify({
        'ticker': ticker
    })
    $.ajax({
        type: "POST",
        url: "/pages/financialReport",
        dataType: 'json',
        data: post_data,
        success: function (data) {
            // update financial report
            tbody = $('#financial-report-table > tbody');
            tbody.empty();
            row_list = "";
            financial_report = JSON.parse(data.financial_report);
            $.each(financial_report, function (idx, obj) {
                row = "<tr><td>" +
                    obj.year + "</td><td>" +
                    obj.eps + "</td><td>" +
                    obj.epsgrowth + "</td><td>" +
                    obj.netincome + "</td><td>" +
                    obj.shareholderequity + "</td><td>" +
                    obj.roa + "</td><td>" +
                    obj.longtermdebt + "</td><td>" +
                    obj.interestexpense + "</td><td>" +
                    obj.ebitda + "</td><td>" +
                    obj.roe + "</td><td>" +
                    obj.interestcoverageratio + "</td></tr>";
                row_list = row_list + row;
            });
            tbody.append(row_list);
            marketWatch_url =
                '<a target="MarketWatch" class="text-success ml-3" style="font-size:1rem; text-decoration:underline" href="https://www.marketwatch.com/investing/stock/' +
                ticker + '/financials">MarketWatch</a>';
            $('#financial-info-title').html(ticker + ', ' + gettext('Financial Information') + marketWatch_url);
            $('#financial-info-title').fadeOut(500).fadeIn(500);
            // update financial warning list
            tbody = $('#financial-warning-list-table > tbody');
            tbody.empty();
            row_list = "";
            financial_warning_list = data.financial_warning_list;
            $.each(financial_warning_list, function (idx, value) {
                row = "<tr><td>" + value + "</td></tr>";
                row_list = row_list + row;
            });
            tbody.append(row_list);
            $('#financial-warning-list-title').text(ticker + ', ' + gettext('Financial Warning List'));
            $('#financial-warning-list-title').fadeOut(500).fadeIn(500);
            // update EPS chart
            years = [];
            eps_list = [];
            stock_price_list = [];
            stock_lmh_list = [];
            yearly_stock_price = JSON.parse(data.yearly_stock_price);
            var financial_number_rex = /\((.*)\)/;
            $.each(financial_report, function (idx, obj) {
                years.push(obj.year);

                eps = parseFloat(obj.eps.replace(financial_number_rex, '-$1').replace(",", ""));
                eps_list.push(eps);
                find_stock_price = false;
                $.each(yearly_stock_price, function (idx, stock) {
                    if (stock.year == obj.year) {
                        stock_price_list.push(stock.close);
                        stock_lmh_list.push([stock.low, stock.mean, stock.high])
                        find_stock_price = true;
                        return false;
                    }

                });
                if (!find_stock_price) {
                    stock_price_list.push('');
                    stock_lmh_list.push([]);
                }
            });
            //console.log(yearly_stock_price);
            epsChart.setTitle({
                text: ticker + ', ' + gettext('EPS & Stock mean price')
            });
            epsChart.xAxis[0].update({
                categories: years
            }, false);
            epsChart.series[0].update({
                data: eps_list,
                //name: ticker + ' EPS of Recent Years'
            }, false);
            epsChart.series[1].update({
                data: stock_price_list,
                //name: ticker + ' EPS of Recent Years'
            }, false);
            epsChart.series[2].update({
                data: stock_lmh_list,
                //name: ticker + ' EPS of Recent Years'
            }, false);
            epsChart.redraw();
        },
        error: function (xhr, status, error) {
            processAjaxErrorMessage(xhr, status, error);
            //console.log("ajax call went wrong:" + request.responseText);
            //alert("Error message :" + request.responseText);
        }
    })
}

function showDataLoading() {
    $('#data-loading').css('visibility', 'visible');
}

function hideDataLoading() {
    $('#data-loading').css('visibility', 'hidden');
}

// Define custom series type for displaying low/med/high values using boxplot as a base
Highcharts.seriesType('lowmedhigh', 'boxplot', {
    keys: ['low', 'median', 'high'],
    tooltip: {
        pointFormat: '<span style="color:{point.color}">\u25CF</span> {series.name}: ' +
            'Low <b>{point.low}</b> - Median <b>{point.median}</b> - High <b>{point.high}</b><br/>'
    }
}, {
    // Change point shape to a line with three crossing lines for low/median/high
    // Stroke width is hardcoded to 1 for simplicity
    drawPoints: function () {
        var series = this;
        Highcharts.each(this.points, function (point) {
            var graphic = point.graphic,
                verb = graphic ? 'animate' : 'attr',
                shapeArgs = point.shapeArgs,
                width = shapeArgs.width,
                left = Math.floor(shapeArgs.x) + 0.5,
                right = left + width,
                crispX = left + Math.round(width / 2) + 0.5,
                highPlot = Math.floor(point.highPlot) + 0.5,
                medianPlot = Math.floor(point.medianPlot) + 0.5,
                lowPlot = Math.floor(point.lowPlot) + 0.5 - (point.low === 0 ? 1 : 0); // Sneakily draw low marker even if 0

            if (point.isNull) {
                return;
            }

            if (!graphic) {
                point.graphic = graphic = series.chart.renderer.path('point').add(series.group);
            }

            graphic.attr({
                stroke: point.color || series.color,
                "stroke-width": 1
            });

            graphic[verb]({
                d: [
                    'M', left, highPlot,
                    'H', right,
                    'M', left, medianPlot,
                    'H', right,
                    'M', left, lowPlot,
                    'H', right,
                    'M', crispX, highPlot,
                    'V', lowPlot
                ]
            });
        });
    }
});

stockChart = Highcharts.stockChart('stock-chart-container', {
    yAxis: [{
        labels: {
            align: 'left'
        },
        height: '60%',
        resize: {
            enabled: true
        }
    }, {
        top: '60%',
        height: '10%',
        labels: {
            align: 'right',
            x: -3
        },
        offset: 0,
        title: {
            text: 'VOLUME'
        }
    }, {
        top: '70%',
        height: '17%',
        labels: {
            align: 'right',
            x: -3
        },
        offset: 0,
        title: {
            text: 'MACD'
        }
    }, {
        top: '87%',
        height: '13%',
        labels: {
            align: 'right',
            x: -3
        },
        offset: 0,
        title: {
            text: 'RSI'
        },
        plotLines: [{
            value: 70,
            color: 'lightgray',
            width: 1
        }, {
            value: 30,
            color: 'lightgray',
            width: 1
        }],
    }
    ],
    plotOptions: {
        candlestick: {
            color: '#6ba887',
            lineColor: '#6ba887',
            upLineColor: '#db5f5f',
            upColor: '#db5f5f'
        }

    },
    rangeSelector: {
        selected: 4, buttonTheme: { // styles for the buttons
            fill: 'none',
            stroke: 'none',
            'stroke-width': 0,
            r: 8,
            style: {
                color: '#039',
                fontWeight: 'bold'
            },
            states: {
                hover: {
                },
                select: {
                    fill: '#039',
                    style: {
                        color: 'white'
                    }
                }
                // disabled: { ... }
            }
        },
    },
    series: [{
        type: 'candlestick', // ohlc
        id: 'stock-data',
    }, {
        type: 'sma',
        linkedTo: 'stock-data',
        color: '#dd6666',
        params: {
            period: 5
        },
        marker: {
            enabled: false
        }
    }, {
        type: 'sma',
        linkedTo: 'stock-data',
        params: {
            period: 20
        },
        marker: {
            enabled: false
        }
    }, {
        type: 'sma',
        linkedTo: 'stock-data',
        color: 'orange',
        params: {
            period: 60
        },
        marker: {
            enabled: false
        }
    }, {
        type: 'column',
        id: 'aapl-volume',
        name: 'AAPL Volume',
        color: '#38c',
        yAxis: 1
    },
    {
        type: 'macd',
        yAxis: 2,
        color: 'orange',
        linkedTo: 'stock-data'
    },
    {
        type: 'rsi',
        yAxis: 3,
        linkedTo: 'stock-data',
        marker: {
            enabledThreshold: 5
        }
    }
    ],
    responsive: {
        rules: [{
            condition: {
                maxWidth: 800
            },
            chartOptions: {
                rangeSelector: {
                    inputEnabled: false
                }
            }
        }]
    }
});

epsChart = Highcharts.chart('eps-chart-container', {
    chart: {
        type: 'line'
    },
    title: {
        text: 'EPS',
        style: {
            fontWeight: '500'
        }
    },
    subtitle: {
        text: ''
    },
    xAxis: {
        categories: [],
        crosshair: true
    },
    yAxis: [{
        title: {
            text: 'EPS'
        }
    },
    {
        title: {
            text: 'Stock close price'
        },
        opposite: true
    }],
    stockTools: {
        gui: {
            enabled: false // disable the built-in toolbar
        }
    },
    tooltip: {
        enabled: true,
        shared: true
    },
    legend: {
        layout: 'vertical',
        align: 'left',
        x: 60,
        verticalAlign: 'top',
        y: 0,
        floating: true,
        backgroundColor:
            Highcharts.defaultOptions.legend.backgroundColor || // theme
            'rgba(255,255,255,0.25)'
    },
    plotOptions: {
        line: {
            dataLabels: {
                enabled: true
            },
            enableMouseTracking: true
        },

    },
    series: [{
        name: 'EPS',
        yAxis: 0,
        data: []
    }, {
        name: 'Stock close price',
        yAxis: 1,
        data: [],
        color: 'orange'
    }, {
        name: 'Stock L-M-H',
        type: 'lowmedhigh',
        yAxis: 1,
        data: [],
        color: 'orange',
        pointWidth: 14,
        showInLegend: false
    }]
});

Highcharts.setOptions({
    lang: {
        thousandsSep: ','
    }
});




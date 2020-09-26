
var stockChart = null;

//stockPriceHistory(request,ticker,start_date,end_date=dt.now()) 
//https://demo-live-data.highcharts.com/aapl-ohlcv.json
Highcharts.getJSON('/pages/stockPriceHistory?ticker=GOOG', function (data) {

    // split the data set into ohlc and volume
    var ohlc = [],
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

    stockChart= Highcharts.stockChart('stock-chart-container', {
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
        series: [{
            type: 'candlestick', // ohlc
            id: 'stock-data',
            name: 'GOOG Stock Price',
            data: ohlc
        }, {
            type: 'sma',
            linkedTo: 'stock-data',
            color:'#dd6666',
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
            color:'orange',
            params: {
                period: 60
            },
            marker: {
                enabled: false
            }
        },{
            type: 'column',
            id: 'aapl-volume',
            name: 'AAPL Volume',
            data: volume,
            color: '#38c',
            yAxis: 1
        },
        {
            type: 'macd',
            yAxis: 2,
            color:'orange',
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
});
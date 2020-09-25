/*
function addPopupEvents(chart) {
    var closePopupButtons = document.getElementsByClassName('highcharts-close-popup');
    // Close popup button:
    Highcharts.addEvent(
        closePopupButtons[0],
        'click',
        function () {
            this.parentNode.style.display = 'none';
        }
    );

    Highcharts.addEvent(
        closePopupButtons[1],
        'click',
        function () {
            this.parentNode.style.display = 'none';
        }
    );

    // Add an indicator from popup
    Highcharts.addEvent(
        document.querySelectorAll('.highcharts-popup-indicators button')[0],
        'click',
        function () {
            var typeSelect = document.querySelectorAll(
                    '.highcharts-popup-indicators select'
                )[0],
                type = typeSelect.options[typeSelect.selectedIndex].value,
                period = document.querySelectorAll(
                    '.highcharts-popup-indicators input'
                )[0].value || 14;

            chart.addSeries({
                linkedTo: 'aapl-ohlc',
                type: type,
                params: {
                    period: parseInt(period, 10)
                }
            });

            chart.stockToolbar.indicatorsPopupContainer.style.display = 'none';
        }
    );

    // Update an annotaiton from popup
    Highcharts.addEvent(
        document.querySelectorAll('.highcharts-popup-annotations button')[0],
        'click',
        function () {
            var strokeWidth = parseInt(
                    document.querySelectorAll(
                        '.highcharts-popup-annotations input[name="stroke-width"]'
                    )[0].value,
                    10
                ),
                strokeColor = document.querySelectorAll(
                    '.highcharts-popup-annotations input[name="stroke"]'
                )[0].value;

            // Stock/advanced annotations have common options under typeOptions
            if (chart.currentAnnotation.options.typeOptions) {
                chart.currentAnnotation.update({
                    typeOptions: {
                        lineColor: strokeColor,
                        lineWidth: strokeWidth,
                        line: {
                            strokeWidth: strokeWidth,
                            stroke: strokeColor
                        },
                        background: {
                            strokeWidth: strokeWidth,
                            stroke: strokeColor
                        },
                        innerBackground: {
                            strokeWidth: strokeWidth,
                            stroke: strokeColor
                        },
                        outerBackground: {
                            strokeWidth: strokeWidth,
                            stroke: strokeColor
                        },
                        connector: {
                            strokeWidth: strokeWidth,
                            stroke: strokeColor
                        }
                    }
                });
            } else {
                // Basic annotations:
                chart.currentAnnotation.update({
                    shapes: [{
                        'stroke-width': strokeWidth,
                        stroke: strokeColor
                    }],
                    labels: [{
                        borderWidth: strokeWidth,
                        borderColor: strokeColor
                    }]
                });
            }
            chart.stockToolbar.annotationsPopupContainer.style.display = 'none';
        }
    );
}
*/
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
        /*
        chart: {
            events: {
                load: function () {
                    addPopupEvents(this);
                }
            }
        },*/
        /* stock tools will overlap with title
        title:{
            text: 'GOOG, Stock Price',
            align: 'left',
            style:{
                "fontSize":"1.75rem",
                "fontWeight":500
            }
        },
        */
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
        /*
        navigationBindings: {
            events: {
                selectButton: function (event) {
                    var newClassName = event.button.className + ' highcharts-active',
                        topButton = event.button.parentNode.parentNode;

                    if (topButton.classList.contains('right')) {
                        newClassName += ' right';
                    }

                    // If this is a button with sub buttons,
                    // change main icon to the current one:
                    if (!topButton.classList.contains('highcharts-menu-wrapper')) {
                        topButton.className = newClassName;
                    }

                    // Store info about active button:
                    this.chart.activeButton = event.button;
                },
                deselectButton: function (event) {
                    event.button.parentNode.parentNode.classList.remove('highcharts-active');

                    // Remove info about active button:
                    this.chart.activeButton = null;
                },
                showPopup: function (event) {

                    if (!this.indicatorsPopupContainer) {
                        this.indicatorsPopupContainer = document
                            .getElementsByClassName('highcharts-popup-indicators')[0];
                    }

                    if (!this.annotationsPopupContainer) {
                        this.annotationsPopupContainer = document
                            .getElementsByClassName('highcharts-popup-annotations')[0];
                    }

                    if (event.formType === 'indicators') {
                        this.indicatorsPopupContainer.style.display = 'block';
                    } else if (event.formType === 'annotation-toolbar') {
                        // If user is still adding an annotation, don't show popup:
                        if (!this.chart.activeButton) {
                            this.chart.currentAnnotation = event.annotation;
                            this.annotationsPopupContainer.style.display = 'block';
                        }
                    }

                },
                closePopup: function () {
                    this.indicatorsPopupContainer.style.display = 'none';
                    this.annotationsPopupContainer.style.display = 'none';
                }
            }
        },
        */
        /*
        stockTools: {
            gui: {
                enabled: true
            }
        },*/
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
function getData(){
	var url = window.location.href;
	var arr = url.split("/");
	var code = arr[arr.length-2]
	 
	 $.ajax({
	     type: 'POST',
	     url: "/api/trends/product" ,
	     data: "code="+code,
	     success: function(data){
	    	 syncDesc(data, '#sync-product')
	     }
	 })
	 
//	 $.ajax({
//	     type: 'POST',
//	     url: "/api/trends/job" ,
//	     data: "id="+id,
//	     success: function(data){
//	    	 syncDesc(data, '#sync-job')
//	     }
//	 })
	 
}




function syncDesc(activity, divId){
	 $(divId).bind('mousemove touchmove', function (e) {
	        var chart,
	            point,
	            i;

	        for (i = 0; i < Highcharts.charts.length; i++) {
	            chart = Highcharts.charts[i];
	            e = chart.pointer.normalize(e); // Find coordinates within the chart
	            point = chart.series[0].searchPoint(e, true); // Get the hovered point

	            if (point) {
	                point.onMouseOver(); // Show the hover marker
	                chart.tooltip.refresh(point); // Show the tooltip
	                chart.xAxis[0].drawCrosshair(e, point); // Show the crosshair
	            }
	        }
	    });
	    /**
	     * Override the reset function, we don't need to hide the tooltips and crosshairs.
	     */
	    Highcharts.Pointer.prototype.reset = function () {};

	    /**
	     * Synchronize zooming through the setExtremes event handler.
	     */
	    function syncExtremes(e) {
	        var thisChart = this.chart;

	        Highcharts.each(Highcharts.charts, function (chart) {
	            if (chart !== thisChart) {
	                if (chart.xAxis[0].setExtremes) { // It is null while updating
	                    chart.xAxis[0].setExtremes(e.min, e.max);
	                }
	            }
	        });
	    }

      $.each(activity.datasets, function (i, dataset) {

            // Add X values
            dataset.data = Highcharts.map(dataset.data, function (val, i) {
                return [activity.xData[i], val];
            });
            
            
            var reversed = false;
            
            if(dataset.name.indexOf("Alexa") > 0){
            	reversed = true;
            }
            
            	

            $('<div class="chart">')
                .appendTo(divId)
                .highcharts({
                    chart: {
                        marginLeft: 40, // Keep all charts left aligned
                        spacingTop: 20,
                        spacingBottom: 20
                        // zoomType: 'x',
                        // pinchType: null // Disable zoom on touch devices
                    },
                    title: {
                        text: dataset.name,
                        align: 'left',
                        margin: 20,
                        x: 40,
                        y: 5
                    },
                    credits: {
                        enabled: false
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle',
                        borderWidth: 0
                    },
                    xAxis: {
                        crosshair: true,
                        events: {
                            setExtremes: syncExtremes
                        },
                        categories: activity.xData
                    },
                    yAxis: {
                        title: {
                            text: ''
                        },
                        offset: -10,
                        reversed: reversed,
                        min:0,
                    },
                    tooltip: {
                        positioner: function () {
                            return {
                                x: this.chart.chartWidth - this.label.width, // right aligned
                                y: -1 // align to title
                            };
                        },
                        borderWidth: 0,
                        backgroundColor: 'none',
                        pointFormat: '{point.y}',
                        headerFormat: '',
                        shadow: false,
                        style: {
                            fontSize: '18px'
                        },
                        valueDecimals: dataset.valueDecimals
                    },
                    series: [{
                        data: dataset.data,
                        name: '-',
                        type: dataset.type,
                        color: Highcharts.getOptions().colors[i],
                        fillOpacity: 0.3,
                        tooltip: {
                            valueSuffix: ' ' + dataset.unit
                        }
                    }]
                });
        });
}





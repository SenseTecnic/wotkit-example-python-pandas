/*API Object to encapsulate REST calls this application's API*/
function API (){
    var API_URL = "api"

    /**
    * An Ajax call to the "correlation" endpoint of this application's API
    * @param	sensora		First sensor to compare
    * @param	sensorb 	Second sensor to compare
    * @param	callBack 	Callback function that will be called when the
    * 				request is successful
    **/
    this.getCorrelation = function (sensora, sensorb, callBack) {
        $.ajax({
              type:"GET",
              url:API_URL+'/correlation?'+
                          'a='  + encodeURIComponent(sensora)+
                          '&b=' + encodeURIComponent(sensorb)+
                          '&hours='+timespan, //TODO: attach to slider
              success: function(data){
                  callBack(data);
              }
        });
    }
 
    /**
    * An Ajax call to the "search" endpoint of this application's API
    * @param	searchText	Text to search
    * @param	callBack 	Callback function that will be called when the
    * 				request is successful
    **/
    this.searchSensors = function(searchText, callBack) {
        $.ajax({
            type:"GET",
            url:API_URL+'/search?text='+encodeURIComponent(searchText),
            success: function(data){callBack(data)}
        });
    }

}

/**
* Update an HTML list with sensors and bind click events to the 'updateCharts' function
* @param	sensorList	An array of sensors as returned by the WoTKit API: 
* 				[{"id":1, "name":"sensor", "fields": [..], ..}, ..]
**/

function updateSensorList(sensorList) {
    $('#sensor-list').empty();
    for (var i=0; i<sensorList.length; i++){
        var listItem = "<a href='#' class='list-group-item' id='"+
                                sensorList[i].id+"'>"+sensorList[i].longName+"</a>"
        $('#sensor-list').append(listItem);
        $('#'+sensorList[i].id).click(function(){ //bind click events to update charts
            var sensorLongName = $(this).html();
            var sensorId = $(this).attr('id');
            var sensorpanel = $(".modal-body .input-group #sensor").val();
            $('.placeholder#'+sensorpanel+ ' h4').html(sensorLongName);
            var id = $('.placeholder#'+sensorpanel+ ' .chart-object canvas').attr('id', sensorId);
            updateCharts();
            $('#searchModal').modal('hide');            
        });
    }
}

/**
* When a sensor is selected update all charts in the dashboard.
**/

function updateCharts(){

    var myAPI = new API();
    var canvasA = $('.placeholder#sensora .chart-object canvas');
    var canvasB = $('.placeholder#sensorb .chart-object canvas');
    var canvasComp = $('.placeholder#sensorcomparison .chart-object canvas');

    myAPI.getCorrelation(canvasA.attr('id'), canvasB.attr('id'), function(data){
          var dataLabels = data['labels'];         
          drawLineChart(canvasA, dataLabels, data['a']);
          drawLineChart(canvasB, dataLabels, data['b']);
          drawLineChart(canvasComp, dataLabels, data['comparison']);
    });
}

 
/**
* Draw a ChartJS line chart using sensor data
* @param	canvas		A DOM element to use for drawing the chart
* @param	dataLabels	An array of labels ["Label 1", "Label 2", "Label 3"]
* @param	dataDatasets	A dictionary of datasets {'a':{'average':[1,2,..], ..}	
**/

function drawLineChart (canvas, dataLabels, dataDatasets) {

    /* Build the data array according to specification
    *  http://www.chartjs.org/docs/#line-chart
    */
    var lineChartData = {
        labels : dataLabels,
        datasets: []
    }

    for ( var k in dataDatasets ){
        if (dataDatasets.hasOwnProperty(k)) {
            lineChartData.datasets.push(
                {
                    label: String(k),
                    fillColor : "rgba(220,220,220,0.2)",
                    strokeColor : "rgba(220,220,220,1)",
                    pointColor : getRandomColor(),
                    pointStrokeColor : "#fff",
                    pointHighlightFill : "#fff",
                    pointHighlightStroke : "rgba(220,220,220,1)",
                    data : dataDatasets[k]
                }
            );
        }

    }

    var ctx = canvas[0].getContext("2d");
    var name = canvas.data('sensorpanel');
    if (window['chart'+name] ) window['chart'+name].destroy(); //Destroy previous 
    window['chart'+name] = new Chart(ctx).Line(lineChartData, {
        responsive: true, 
        maintainAspectRatio: false,
        multiTooltipTemplate: "<%= datasetLabel %>: <%= value %>"
    });
}

/*Utility functions */

/**
* Get a random HTML color.
* @return		A string in the form #123456
**/

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}


/**
* A function to animate the '#loader-bar' element as a loading bar;
* these are not the droids you're looking for.
**/

function loaderAnimation () {
    $('.loader-bar').animate({
                              width:"100%"
                             }, 500, function() { 
                                 $(this).css({"width":"0%"});
                             } );
}

var timespan = 6; //TODO: remove this global variable: 

window.onload = function(){

    /*Our API object*/
    var myAPI = new API();

    /*JQuery AJAX Listners*/
    $('#search-form').submit(function(){
        var searchText = $(this).find('input:text').val();
        searchSensors(searchText, updateSensorList);       
        $(this).find('input:text').val("") //update as cleaned
    });

    $(".btn-sensor").click(function(){
        var sensor = $(this).data('sensorpanel');
        $(".modal-body .input-group #sensor").val( sensor );
    });

    $("#modal-search-btn").click(function(){
        var searchText = $('#modal-search-text').val();
        myAPI.searchSensors(searchText, updateSensorList);
    });

    /*Attach a nice loader animation to all AJAX requests.*/
    $( document ).ajaxStart(function() {
        loaderAnimation ();
    });

    $(".timespan").click(function(){
        timespan = this.id;
        updateCharts();
    });

    updateCharts();

};





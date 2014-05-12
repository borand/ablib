var debug_websocket = false;
var debug_js = true;
var debug_all = true;
var plot_height = 700;
var chart;
var plot;
var power = -5;
var constl_plot_1;
var constl_plot_2;

var data_surf; 
var surface_plot;
var tooltipStrings = new Array();
var numRows = 64;
var numCols = 64;
var constl;
// UTILITY FUNCTIONS
//
//

google.load("visualization", "1");

function reset_constl(constl){
	for (var i = 0; i < numRows; i++) {
		for (var j = 0; j < numCols; j++) {
			constl[i][j] = 0;
		}
	}
	return constl;
}

function add_to_constl(constl, constl2){
	for (var i = 0; i < numRows; i++) {
		for (var j = 0; j < numCols; j++) {
			constl[i][j] += constl2[i][j];
		}
	}
	return constl;
}

function draw_surface_plot(cnst) {
		
	var idx = 0;	
	for (var i = 0; i < numRows; i++) {
		for (var j = 0; j < numCols; j++) {
			var value = cnst[i][j];
			data_surf.setValue(i, j, data_surf.getValue(i, j) + value / 100);
			tooltipStrings[idx] = "I:" + i + ", Q:" + j + " = " + value;
			idx++;
		}
	}	

	// Don't fill polygons in IE. It's too slow.
	var fillPly = true;

	// Define a colour gradient.
	var colour1 = {
		red : 0,
		green : 0,
		blue : 255
	};
	var colour2 = {
		red : 0,
		green : 255,
		blue : 255
	};
	var colour3 = {
		red : 0,
		green : 255,
		blue : 0
	};
	var colour4 = {
		red : 255,
		green : 255,
		blue : 0
	};
	var colour5 = {
		red : 255,
		green : 0,
		blue : 0
	};
	var colours = [colour1, colour2, colour3, colour4, colour5];

	// Axis labels.
	var xAxisHeader = "I";
	var yAxisHeader = "Q";
	var zAxisHeader = "Z";

	var options = {
		xPos : 50,
		yPos : 50,
		width : 600,
		height : 600,
		colourGradient : colours,
		fillPolygons : fillPly,
		xTitle : xAxisHeader,
		yTitle : yAxisHeader,
		zTitle : zAxisHeader,
		restrictXRotation : true
	};
	//tooltips: tooltipStrings,

	surface_plot.draw(data_surf, options);
}



function dbg(message) {
	console.log(message);
	show_server_msg(message);
}

function show_server_msg(message) {
	if (debug_all)
	{	
		$("#debug_console").html( $("#debug_console").text() + message + '\n');					
	    var psconsole = $('#debug_console');
	    psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	}
}

function set_object_value(id, val){
	var datarole = $("#"+id).attr('data-role');
	dbg('id:' + id + " data-role: " + datarole + "  val: " + val);
	switch(datarole){
		case 'slider':
			dbg('case: slider');
			$('#' + id).val(val).slider("refresh");
			break;
		case 'flipswitch':			
			dbg('about to flip the switch value to:' + val + ' currently set to: ' + $('#' + id).val());
			$('#' + id).val(val).flipswitch("refresh");
			break;
		case 'text':
			$('#' + id).text(val);
			break
		default:
			dbg('case: default');
			$('#' + id).val(val)[datarole]("refresh");
	}
	
}

///////////////////////////////////////////////////////////////////////
// HIGHCHARTS
//
//

function draw_chart(render_to) {
	
	Highcharts.setOptions({
		global : {
			useUTC : false
		}
	});
	
	// Create the chart
	chart = new Highcharts.StockChart({
		chart : {
			renderTo : render_to,
			height : plot_height,			
		},
		
		rangeSelector: {
			buttons: [{
				count: 1,
				type: 'minute',
				text: '1M'
			}, {
				count: 5,
				type: 'minute',
				text: '5M'
			}, {
				type: 'all',
				text: 'All'
			}],
			inputEnabled: false,
			selected: 0
		},		
		title : {
			text : 'BER 1sec'
		},
		
		exporting: {
			enabled: false
		},
		
		legend : {
			enabled: true
		},
		
		yAxis : {
			title : {
				text : 'BER'
			},
			max : 0.034,
			min : 0.005,
		},
		
		series : [{
			name : 'Flex 3',
			color: '#00FF00',
			step: true,
			data : (function() {
				// generate an array of random data
				var data = [], time = (new Date()).getTime(), i;

				for( i = -99; i <= 0; i++) {
					data.push([
						time + i * 1000,
						0.0
					]);
				}
				return data;
			})()
		},
		{
			name : 'NL Compensated',
			color: '#FF00FF',
			step: true,
			data : (function() {
				// generate an array of random data
				var data = [], time = (new Date()).getTime(), i;

				for( i = -200; i <= 0; i++) {
					data.push([
						time + i * 1000,
						0.0
					]);
				}
				return data;
			})()
		}]
	});
	return chart;
}

function draw_constl_plot(render_to) {
	plot2 = new Highcharts.Chart({
		chart : {
			renderTo : render_to,
			defaultSeriesType : 'scatter',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : ''
		},
		subtitle : {
			text : ''
		},
		xAxis : {
			title : {
				enabled : true,
				text : 'I'
			},
			//startOnTick : true,
			//endOnTick : true,
			showLastLabel : true,
			min : -250,
			max : 250,
		},
		yAxis : {
			title : {
				text : 'Q'
			},
			min : -250,
			max : 250,			
		},		
		plotOptions : {
			scatter : {
				marker : {
					radius : 4,					
				},
			}
		},
		series : [{
			name : 'X-POL',
			color : 'rgba(255, 0, 0, .5)',
			//data : [[75, 75],[75, 150], [150, 75],[150, 150]],
			data : [[0,0]],
		},{
			name : 'Y-POL',
			color : 'rgba(0, 0, 255, .5)',
			//data : [[75, 75],[75, 150], [150, 75],[150, 150]],
			data : [[0,0]],

		}]
	});
	return plot2;
}

function draw_plot(render_to) {
	plot = new Highcharts.Chart({
		chart : {
			renderTo : render_to,
			defaultSeriesType : 'spline',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : '10 Span TrueWave Classic Link'
		},
				
		xAxis : {
			title : {
				//enabled : true,
				text : 'Launch Power [dBm]'
			},
			startOnTick : true,
			endOnTick : true,
			//showLastLabel : true
		},
		yAxis : {
			title : {
				text : 'OSNR [dB]'
			},
			min : 20,
			max : 34,			
		},		
		series : [{
			name : 'OSNR',
			color : 'rgba(223, 83, 83, .5)',
			data : [[-7.3, 22.6],[-5.9, 24.5],[-4.7, 25.8],[-3.6, 26.9],[-2.6, 27.8],[-1.6, 28.6],[-0.6, 29.5],[0.4, 30.3],[1.4, 31.0],[2.4, 31.7],[3.4, 32.3],[4.3, 32.9],[5.4, 33.4]],

		},{
			name : 'Current Launch Power',			
			// data : [[power, 0],[power, 6]]
			data : [[power, 22],[power, 34]]
		}]
	});
	return plot;
}

function add_measurement(value){
	var t = (new Date()).getTime();
	for (i=0;i<value.length;i++){
		series = chart.series[i];
		series.addPoint([t, value[i]], true, true);	
	}
}

function update_const_plot(plot_id, data) {	
	dbg('update_const_plot(' + plot_id + ")");
	switch(plot_id) {
		case 'constl_plot_1': {
			dbg('   case: constl_plot_1');
			constl_plot_1.series[0].update({ data : data});			
			break;
		}
		case 'constl_plot_2': {
			constl_plot_2.series[0].update({ data : data});
			break;
		}
		default:
		break
		
	}
}

function parse_message(message_text){
	var temp;
}
///////////////////////////////////////////////////////////////////////
// WEBSOCKETS FUNCTIONS
//
//
function open_websocket(hostname, hostport, hosturl) {

	dbg('Attempting to open web socket');
	function show_message(message) {
		show_server_msg(message);		
	}

	var websocket_address = "ws://" + hostname + ":" + hostport + "/" + hosturl;
	var ws = new WebSocket(websocket_address);
	
	ws.onopen = function() {
		dbg('web socket open');
		$('#live').text('CONNECTED');
		$("#live").css("background-color",'#B2BB1E');
	};

	ws.onmessage = function(event) {
		//dbg('incomming message');
		var JsonData;
		try {
			JsonData = JSON.parse(event.data);			
			if (JsonData.hasOwnProperty('id')) {
				//console.log(JsonData.id);
				switch(JsonData.id)
				{	
					case 'chart':{
						add_measurement(JsonData.val);
						break;
					}
					case 'const':{						
						//update_const_plot(JsonData.val.id, JsonData.val.data);						
						draw_surface_plot(JsonData.val.data);
						break;
					}
					case 'launch_power':{
						power = JsonData.val;
						plot.series[1].update({ data : [[power, 22],[power, 34]]});
						break;
					}					
					case 'accum':{	
						pdate_const_plot(JsonData.val.id, JsonData.val.data);						
						break;
					}
					default:{	
						set_object_value(JsonData.id,JsonData.val);
					}
				}
				
			}
			else if(JsonData.hasOwnProperty('data')){
				add_measurement(JsonData.data);
			}
			else{
				add_measurement(JsonData);
			}

		} catch(e) {
			dbg('JSON.parse error: "' + e + '". JsonData = ' + JsonData);			
		}
		//show_server_msg(event.data);
	};
	ws.onclose = function() {
		dbg('closing websockets');
		$('#live').text('OFFLINE');
		$("#live").css("background-color",'#C71C2C');
	};
}

function connect_to_websocket_host(){
	var hostname = $('#hostname').val();
	var hostport = $('#hostport').val();
	var hosturl  = $('#hosturl').val();
	dbg('Pressed button: button_connect: [host, port] ' + hostname +':' + hostport + '/'+ hosturl);
	open_websocket(hostname, hostport, hosturl);
}
///////////////////////////////////////////////////////////////////////
// MAIN GUI - jQUERY
//
//
$(document).ready(function() {	
	
	$("#underline").append("<img id='underline' src='static/line.jpg'/>");
	//$("#page_header").css("background-color",'#C71C2C');
	dbg('Document ready');

	debug_websocket = $('#debug_websocket').prop("checked");
	debug_js        = $('#debug_js').prop("checked");
	debug_all       = $('#debug_all').prop("checked");
	
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );	
	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);
	$("#live").css("background-color",'#C71C2C');
	
	$('#button_power_up').hide();
	$('#button_power_down').hide();
	
	data_surf    = new google.visualization.DataTable();
	

	for (var i = 0; i < numCols; i++) {
		data_surf.addColumn('number', 'col' + i);
	}
	data_surf.addRows(numRows);
	
	surface_plot = new greg.ross.visualisation.SurfacePlot(document.getElementById('constl_plot_2'));
	
	//$("#button_power_up").button("disable");
	//$( "#button_power_down" ).button("option", "disabled",true);
	

	chart         = draw_chart('chart');
	plot          = draw_plot('power_plot');
	constl_plot_1 = draw_constl_plot('constl_plot_1');
	//constl_plot_2 = draw_constl_plot('constl_plot_2');
	var cnst = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0],[0,0,0,11,9,12,8,3,1,0,0,0,0,0,0,0,0,0,0,0,0,2,10,12,8,7,2,0,0,0,0,0,0,0,0,0,0,0,0,1,13,5,9,5,5,0,0,0,0,0,0,0,0,0,0,0,0,2,7,11,9,4,1,0],[0,0,3,21,42,63,31,18,3,0,0,0,0,0,0,0,0,0,0,0,4,9,37,51,53,10,2,0,0,0,0,0,0,0,0,0,0,0,4,10,24,66,55,17,8,1,0,0,0,0,0,0,0,0,0,0,0,3,31,63,73,30,9,0],[0,0,7,52,148,174,117,41,3,2,0,0,0,0,0,0,0,0,0,0,5,41,110,179,153,62,13,1,0,0,0,0,0,0,0,0,0,0,4,21,97,152,176,46,25,0,0,0,0,0,0,0,0,0,0,0,2,14,62,159,170,91,33,0],[1,0,8,78,181,235,166,49,6,0,0,0,0,0,0,0,0,0,0,0,9,50,123,235,209,65,10,0,0,0,0,0,0,0,0,0,0,0,1,34,113,255,201,100,18,4,0,0,0,0,0,0,0,0,0,0,0,20,88,210,220,132,30,5],[0,1,4,46,118,131,105,28,8,0,0,0,0,0,0,0,0,0,0,1,7,26,108,156,121,53,7,0,0,0,0,0,0,0,0,0,0,0,3,27,79,142,154,54,13,1,1,0,0,0,0,0,0,0,0,0,0,12,52,127,164,85,20,3],[0,0,3,14,37,49,39,8,1,0,0,0,0,0,0,0,0,0,0,1,4,4,30,43,33,15,3,0,0,0,0,0,0,0,0,0,0,0,0,4,32,43,50,12,3,0,0,0,0,0,0,0,0,0,0,0,0,3,14,49,44,27,6,2],[0,0,1,2,3,9,5,1,0,0,0,0,0,0,0,0,0,0,1,0,0,2,4,12,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,6,5,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,6,6,7,4,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],[0,0,0,3,3,4,3,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,5,8,6,0,1,0,0,0,0,0,0,0,0,0,0,0,1,2,2,5,4,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,4,5,0,0],[0,0,3,11,28,49,26,6,0,0,0,0,0,0,0,0,0,0,0,0,0,7,29,45,31,12,2,1,0,0,0,0,0,0,0,0,0,0,2,3,29,59,46,19,5,2,0,0,0,0,0,0,0,0,0,0,0,4,14,41,51,22,2,1],[0,0,10,41,128,168,93,42,4,0,0,0,0,0,0,0,0,0,0,1,7,28,105,160,116,37,14,0,0,0,0,0,0,0,0,0,0,0,1,22,70,133,126,70,10,1,0,0,0,0,0,0,0,0,0,0,2,9,71,126,151,73,12,0],[0,0,10,57,157,232,132,66,10,1,0,0,0,0,0,0,0,0,0,1,7,53,137,226,196,67,14,1,0,0,0,0,0,0,0,0,0,0,3,30,126,218,212,95,22,3,0,0,0,0,0,0,0,0,0,0,3,23,96,215,228,141,32,1],[0,2,9,59,153,176,113,52,3,2,0,0,0,0,0,0,0,0,0,1,3,37,114,193,147,57,10,1,0,0,0,0,0,0,0,0,0,0,5,20,105,145,167,83,17,1,1,0,0,0,0,0,0,0,0,0,0,15,72,149,152,88,23,2],[0,1,5,24,55,74,45,14,1,0,0,0,0,0,0,0,0,0,0,0,6,17,47,63,38,14,4,0,0,0,0,0,0,0,0,0,0,0,2,6,33,71,56,34,5,1,0,0,0,0,0,0,0,0,0,0,0,7,31,62,73,32,15,2],[0,0,2,1,10,12,5,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,7,15,10,2,1,0,0,0,0,0,0,0,0,0,0,0,0,1,4,13,10,6,0,0,0,0,0,0,0,0,0,0,0,0,1,0,7,13,14,10,3,0],[0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,1,2,2,3,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,5,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,2,1,3,1,1,0,0],[0,0,1,17,23,23,22,4,0,0,0,0,0,0,0,0,0,0,0,0,1,10,14,30,24,9,4,1,0,0,0,0,0,0,0,0,0,0,1,5,13,26,28,7,2,1,0,0,0,0,0,0,0,0,0,0,0,2,15,34,34,20,6,1],[0,1,6,33,84,133,83,23,4,0,0,0,0,0,0,0,0,0,0,0,3,18,72,116,95,42,4,1,0,0,0,0,0,0,0,0,0,0,1,15,61,129,90,65,12,2,0,0,0,0,0,0,0,0,0,0,1,6,45,113,108,57,22,4],[0,2,15,62,188,210,158,40,5,0,0,0,0,0,0,0,0,0,0,1,5,43,127,254,186,71,17,1,0,0,0,0,0,0,0,0,0,0,4,33,105,221,204,101,17,2,0,0,0,0,0,0,0,0,0,0,2,17,67,217,227,115,29,3],[0,1,14,56,160,196,149,45,6,0,0,0,0,0,0,0,0,0,0,0,8,37,107,193,153,70,15,0,0,0,0,0,0,0,0,0,0,0,5,26,99,216,161,73,20,3,0,0,0,0,0,0,0,0,0,0,1,15,82,188,209,123,26,6],[0,0,3,32,69,92,53,23,2,1,0,0,0,0,0,0,0,0,0,0,3,14,61,82,76,33,9,0,0,0,0,0,0,0,0,0,0,0,2,8,45,93,95,35,7,1,0,0,0,0,0,0,0,0,0,0,1,5,31,63,71,57,11,3],[0,0,2,4,15,25,12,2,0,0,0,0,0,0,0,0,0,0,0,0,0,4,24,29,24,5,1,0,0,0,0,0,0,0,0,0,0,0,0,4,9,11,22,9,1,0,0,0,0,0,0,0,0,0,0,0,0,2,10,22,18,8,3,0],[0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,1,0,0,0],[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],[0,0,0,0,2,3,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1,5,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0],[0,0,1,9,17,15,6,2,0,0,0,0,0,0,0,0,0,0,0,0,1,6,17,19,14,4,0,0,0,0,0,0,0,0,0,0,0,0,0,1,9,24,18,6,1,0,0,0,0,0,0,0,0,0,0,0,0,2,5,18,25,15,3,1],[0,0,3,24,52,109,69,22,3,0,0,0,0,0,0,0,0,0,0,2,3,15,77,111,77,26,2,1,0,0,0,0,0,0,0,0,0,0,1,13,28,71,89,44,7,0,1,0,0,0,0,0,0,0,0,0,1,8,39,73,87,36,12,4],[0,0,11,54,160,219,129,32,9,0,0,0,0,0,0,0,0,0,0,0,5,39,129,193,152,64,14,0,0,0,0,0,0,0,0,0,0,0,4,23,107,190,190,84,15,2,0,0,0,0,0,0,0,0,0,0,1,10,81,158,206,99,30,5],[0,0,19,58,165,246,149,41,7,0,0,0,0,0,0,0,0,0,0,1,14,40,133,212,174,98,9,1,1,0,0,0,0,0,0,0,0,1,2,33,118,228,214,92,11,2,0,0,0,0,0,0,0,0,0,0,1,21,96,195,203,128,29,4],[0,3,5,28,84,122,95,31,1,0,0,0,0,0,0,0,0,0,0,0,3,22,69,122,87,36,5,1,0,0,0,0,0,0,0,0,0,0,1,12,67,119,110,55,12,2,0,0,0,0,0,0,0,0,0,0,2,8,51,107,133,69,13,4],[0,0,2,8,22,42,19,3,0,0,0,0,0,0,0,0,0,0,0,0,3,9,18,26,22,6,1,0,0,0,0,0,0,0,0,0,0,0,0,4,17,18,36,10,4,0,1,0,0,0,0,0,0,0,0,0,0,4,9,32,35,21,4,2],[0,0,0,0,2,5,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,5,6,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,3,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,4,3,1,0]];
	cnst = reset_constl(cnst);
	draw_surface_plot(cnst);
	connect_to_websocket_host();
	
	///////////////////////////////////////////////////////////////////////				
	$.getJSON('/cmd/', "cmd=get_power", function(data) {
		console_response_msg(data.res);
	});
	
	///////////////////////////////////////////////////////////////////////
	//
	// BUTTONS
	//

	$("#button_connect").click(function() {	
		connect_to_websocket_host();
	});

	$("#button_clear_debug_console").click(function() {
		$("#debug_console").text("");
	});

	$("#button_power_up").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			dbg("button_power_up");
			cmd = 'power_up';
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				console_response_msg(data.res);
			});
		}
		else{
			dbg("Power control disabled");
		}
		});
	
	$("#button_power_down").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			dbg("button_power_down");
			cmd = 'power_down';			
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				console_response_msg(data.res);
			});
		}
		else{
			dbg("Power control disabled");
		}
		});

		$("#power_control_enabled").click(function(){
		if ($('#power_control_enabled').prop("checked")) {
			$('#button_power_up').show();
			$('#button_power_down').show();
		} else {
			$('#button_power_up').hide();
			$('#button_power_down').hide();
		}

	});
	
	$("#const_rotate").click(function(){
		data_surf.rotate(90,0,0);
	});
	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {			
			$("#cmd_status").text(data.cmd);
		});
	}

});

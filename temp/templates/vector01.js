var debug_websocket = false;
var debug_js = true;
var debug_all = true;
var plot_height = 600;
var chart;
var plot;
var power = -5;
var constl_plot_1;
var constl_plot_2;
/////////////////////////////////////////////////////////////////////
// UTILITY FUNCTIONS
//
//

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

				for( i = -99; i <= 0; i++) {
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
			min : 22,
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
						update_const_plot(JsonData.val.id, JsonData.val.data);
						break;
					}
					case 'launch_power':{
						power = JsonData.val;
						plot.series[1].update({ data : [[power, 22],[power, 34]]});
						break;
					}					
					case 'accum':{	
						//pdate_const_plot(JsonData.val.id, JsonData.val.data);
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
	$("#page_header").css("background-color",'#C71C2C');
	dbg('Document ready');

	debug_websocket = $('#debug_websocket').prop("checked");
	debug_js        = $('#debug_js').prop("checked");
	debug_all       = $('#debug_all').prop("checked");
	
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );	
	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);
	

	chart         = draw_chart('chart');
	plot          = draw_plot('power_plot');
	constl_plot_1 = draw_constl_plot('constl_plot_1');
	constl_plot_2 = draw_constl_plot('constl_plot_2');
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

	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {			
			$("#cmd_status").text(data.cmd);
		});
	}

});

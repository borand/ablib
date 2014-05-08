var debug_websocket = false;
var debug_js = true;
var debug_all = false;
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

function console_response_msg(message) {	
	$("#json_res").html($("#json_res").text() + "cmd [" + message[1] + "]: " + message[2].data + '\n');
	var psconsole = $('#json_res');
	psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
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

function draw_chart() {

	
	Highcharts.setOptions({
		global : {
			useUTC : false
		}
	});
	
	// Create the chart
	chart = new Highcharts.StockChart({
		chart : {
			renderTo : 'plot',
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
}

function draw_plot_2(render_to) {
	plot2 = new Highcharts.Chart({
		chart : {
			renderTo : render_to,
			defaultSeriesType : 'scatter',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : 'Flex 3'
		},
		subtitle : {
			text : ''
		},
		xAxis : {
			title : {
				enabled : true,
				text : 'I'
			},
			startOnTick : true,
			endOnTick : true,
			showLastLabel : true,
			min : -255,
			max : 255,
		},
		yAxis : {
			title : {
				text : 'Q'
			},
			min : -255,
			max : 255,			
		},		
		plotOptions : {
			scatter : {
				marker : {
					radius : 3,					
				},
			}
		},
		series : [{
			name : 'X-POL',
			color : 'rgba(255, 0, 0, .5)',
			data : [[-1, 1],[0, 2],[1, 3],[2, 3.5],[3, 3],[4, 2],[5, 1],[6, 0]]

		}, {
			name : 'Y-POL',
			color : 'rgba(0, 0, 255, .5)',
			data : [[-1, 2],[0, 3],[1, 4],[2, 5],[3, 4],[4, 3],[5, 2],[6, 1]]

		}]
	});
	return plot2;
}

function draw_heatmap(render_to) {
	chart = new Highcharts.Char({
		chart : {
			renderTo : render_to,
			type : 'heatmap',
			marginTop : 40,
			marginBottom : 40,
		},

		colorAxis : {
			min : 0,
			minColor : '#FFFFFF',
			maxColor : Highcharts.getOptions().colors[0]
		},

		series : [{
			data : [[0, 0, 10], [0, 1, 19], [0, 2, 8], [0, 3, 24]],
		}]
	});
	return chart;
}

function draw_plot() {
	plot = new Highcharts.Chart({
		chart : {
			renderTo : 'plot2',
			defaultSeriesType : 'spline',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : '10 Span TrueWave Classic Link'
		},
				
		xAxis : {
			title : {
				enabled : true,
				text : 'Launch Power [dBm]'
			},
			startOnTick : true,
			endOnTick : true,
			showLastLabel : true
		},
		yAxis : {
			title : {
				text : 'OSNR [dB]'
			},
			min : 22,
			max : 34,			
		},
		// tooltip : {
			// formatter : function() {
				// return '' + this.x + ' ' + this.y + ' ';
			// }
		// },
		// plotOptions : {
			// scatter : {
				// marker : {
					// radius : 2,
				// },				
			// }
		// },
		series : [{
			name : 'Flex 3',
			color : 'rgba(223, 83, 83, .5)',
			data : [[-7.3, 22.6],[-5.9, 24.5],[-4.7, 25.8],[-3.6, 26.9],[-2.6, 27.8],[-1.6, 28.6],[-0.6, 29.5],[0.4, 30.3],[1.4, 31.0],[2.4, 31.7],[3.4, 32.3],[4.3, 32.9],[5.4, 33.4]],

		},{
			name : 'Power',			
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
	
	//series = chart.series[1];
	//series.addPoint([t, value[1]], true, true);
}

function update_const_plot(plot_id, data) {	
	switch(plot_id) {
		case 'constl_plot_1': {
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
					case 'debug_console':
					{
						console_response_msg(JsonData.data);
						break;
					}	
					case 'plot2':
					{
						plot.addSeries(JsonData.data);
						break;
					}	
					case 'const2':
					{	
						update_const_plot(JsonData.val.id, JsonData.val.data);
						break;
					}
					case 'accum':
					{	
						//pdate_const_plot(JsonData.val.id, JsonData.val.data);
						break;
					}
					default:
					{	
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

	dbg('Document ready');

	debug_websocket = $('#debug_websocket').prop("checked");
	debug_js        = $('#debug_js').prop("checked");
	debug_all       = $('#debug_all').prop("checked");
	
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );
	
	$('#json_res').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#json_res').textinput("option", "autogrow", false);
	//$('#launch_power').​​​attr('style', 'background-color:White; font-size:14px; width: 5em;');

	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);
		
	$('#server_msg').textinput("option", "autogrow", false);
	
	draw_chart();
	plot = draw_plot();
	constl_plot_1 = draw_plot_2('constl_plot_1');
	constl_plot_2 = draw_plot_2('constl_plot_2');
	connect_to_websocket_host();
	
	///////////////////////////////////////////////////////////////////////
	$('#json_cmd').keydown(function(e) {
		if (e.keyCode == 13) {
			var cmd = $("#json_cmd").val();
			$(this).val("");
			if (cmd == "clc") {
				console.log('Clear screen');
				$("#json_res").text("");
			} else {
				if (cmd == '') {
					console.log('Sending empty command');
					cmd = ' ';
				} else {
					console.log('Sending command: ' + cmd);
				}

				$("#json_res").append("cmd>" + cmd + "\n");

				$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
					//console.log(String(data));
					$("#json_res").html($("#json_res").text() + data.res + '\n');					
					var psconsole = $('#json_res');
					psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
				});
			}
		}
	});

	///////////////////////////////////////////////////////////////////////
	//
	// BUTTONS
	//
	$(".custom").change(function() {	
		debug_all = $( "#debug_all" ).prop("checked");
		dbg("debug_all = " + debug_all);
		//alert( "Handler for .change() called." );
		//$("#debug_all").prop("checked", true).checkboxradio("refresh");
	});

	$("#button_connect").click(function() {	
		connect_to_websocket_host();
	});

	$("#button_clear_debug_console").click(function() {
		$("#debug_console").text("");
	});

	$("#button_power_up").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			cmd = 'power_up';
			power = power + 1;		
			plot.series[1].update({ data : [[power, 22],[power, 34]]});
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				//console.log(String(data));
				$("#json_res").html($("#json_res").text() + data.res + '\n');
				var psconsole = $('#json_res');
				psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
			});
		}
		else{
			dbg("Power control disabled");
		}
		});
	
	$("#button_power_down").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			dbg("Power Down");
			
			cmd = 'power_down';			
			power = power - 1;
			plot.series[1].update({ data : [[power, 22],[power, 34]]});			
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				//console.log(String(data));
				$("#json_res").html($("#json_res").text() + data.res + '\n');
				var psconsole = $('#json_res');
				psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
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

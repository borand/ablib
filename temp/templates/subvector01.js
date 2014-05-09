var debug_websocket = false;
var debug_js = true;
var debug_all = false;
var plot_height = 600;
var card_chart;
var card_const;	
var card_1_chart;
var card_2_chart;
var card_1_const;
var card_2_const;

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

function draw_const_plot(render_to) {
	plot = new Highcharts.Chart({
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
			data : [[0, 0]]

		}, {
			name : 'Y-POL',
			color : 'rgba(0, 0, 255, .5)',
			data : [[0, 1]]

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
					case 'console':{
						console_response_msg(JsonData.val);
						break;
					}
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
	
	card_1_chart = draw_chart('card_1_chart');
	card_2_chart = draw_chart('card_2_chart');
	card_1_const = draw_const_plot('card_1_const');
	card_2_const = draw_const_plot('card_2_const');	
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

	$("#button_connect").click(function() {	
		connect_to_websocket_host();
	});

	$("#button_clear_debug_console").click(function() {
		$("#debug_console").text("");
	});
	
	///////////////////////////////////////////////////////////////////////
	//
	// BUTTONS
	//
	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {			
			$("#cmd_status").text(data.cmd);
		});
	}

});

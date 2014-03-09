///////////////////////////////////////////////////////////////////////
// UTILITY FUNCTIONS
//
//
function dbg(message) {
	console.log(message);
	show_server_msg(message);
	//$('#jsdbg').text(message);
}

function show_server_msg(message) {
	//dbg('show_server_msg: ' + message);
	//$("#server_msg").html(message);
	//$("#server_msg").html($("#server_msg").text() + message);
	//$("#server_msg").html($("#server_msg").text() + message);
	//var psconsole = $('#server_msg');
	//psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	$("#debug_console").html($("#debug_console").text() + message + '\n');					
	var psconsole = $('#debug_console');
	psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
}

///////////////////////////////////////////////////////////////////////
// HIGHCHARTS
//
//
var chart;
function draw_chart() {
	chart = new Highcharts.Chart({
		chart : {
			renderTo : 'plot',
			defaultSeriesType : 'line',
			marginRight : 130,
			marginBottom : 25
		},
		title : {
			text : 'Monthly Average Temperature',
			x : -20 //center
		},
		subtitle : {
			text : 'Source: WorldClimate.com',
			x : -20
		},
		xAxis : {
			categories : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		},
		yAxis : {
			title : {
				text : 'Temperature (°C)'
			},
			plotLines : [{
				value : 0,
				width : 1,
				color : '#808080'
			}]
		},
		tooltip : {
			formatter : function() {
				return '<b>' + this.series.name + '</b><br/>' + this.x + ': ' + this.y + '°C';
			}
		},
		legend : {
			layout : 'vertical',
			align : 'right',
			verticalAlign : 'top',
			x : -10,
			y : 100,
			borderWidth : 0
		},
		series : [{
			name : 'Tokyo',
			data : [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
		}, {
			name : 'New York',
			data : [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
		}, {
			name : 'Berlin',
			data : [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
		}, {
			name : 'London',
			data : [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
		}]
	})
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
		dbg('incomming message');
		var JsonData;
		try {
			JsonData = JSON.parse(event.data);
			if (JsonData.hasOwnProperty('id')) {
				console.log(JsonData.id);
				$('#' + JsonData.id).val(JsonData.val).slider("refresh");
			}

		} catch(e) {
			dbg('JSON.parse error: "' + e + '". JsonData = ' + JsonData);			
		}
		show_server_msg(event.data);
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
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );
	
	$('#json_res').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#json_res').textinput("option", "autogrow", false);

	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);
		
	$('#server_msg').textinput("option", "autogrow", false);
	
	draw_chart();
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

	$("#options_ping").click(function() {		
		SendCmd('ping', 0)
		$("#cmd_status").text("Pressed options_ping button");
	});

	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {			
			$("#cmd_status").text(data.cmd);
		});
	}

});

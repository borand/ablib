///////////////////////////////////////////////////////////////////////
// UTILITY FUNCTIONS
//
//
function dbg(message) {
	console.log(message);
	$('#jsdbg').text(message);
}

function show_server_msg(message) {
	//dbg('show_server_msg: ' + message);
	$("#server_msg").html(message);
	//$("#server_msg").html($("#server_msg").text() + message);
	//$("#server_msg").html($("#server_msg").text() + message);
	//var psconsole = $('#server_msg');
	//psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
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
function open_websocket() {

	dbg('Attempting to open web socket');
	function show_message(message) {
		show_server_msg(message);
		// $("#json_res").html($("#json_res").text() + message + '\n');
		// var psconsole = $('#json_res');
		// psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	}

	var ws = new WebSocket("ws://127.0.0.1:8888/track");
	ws.onopen = function() {
		dbg('web socket open');
		$('#live').val('CONNECTED').slider("refresh");
	};
	ws.onmessage = function(event) {
		dbg('incomming message');
		show_server_msg(event.data);
		var JsonData;
		try {
			JsonData = JSON.parse(event.data);
			if (JsonData.hasOwnProperty('id')) {
				console.log(JsonData.id);
				$('#' + JsonData.id).val(JsonData.val).slider("refresh");
			}

		} catch(e) {
			console.log('JSON.parse error: "' + e + '". JsonData = ' + JsonData);
		}
		show_message(event.data);
	};
	ws.onclose = function() {
		dbg('closing websockets');
		$('#live').val('CONNECT').slider("refresh");
	};
}

///////////////////////////////////////////////////////////////////////
// MAIN GUI - jQUERY
//
//
$(document).ready(function() {

	dbg('Document ready');
	console.log('Document ready');
	$('#json_res').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#json_res').textinput("option", "autogrow", false);
	$("#json_res").textinput({
		clearBtn : true
	});
	//$("#json_res").textinput( "disable" );

	$('#server_msg').textinput("option", "autogrow", false);

	open_websocket();
	draw_chart();
	///////////////////////////////////////////////////////////////////////
	$('#json_cmd').keydown(function(e) {
		if (e.keyCode == 13) {
			var cmd = $("#json_cmd").val();
			$(this).val("");
			// $("#json_res").text("");

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
					console.log(String(data));
					$("#json_res").html($("#json_res").text() + data.res + '\n');
					//$('#scratchpad').text(data);
					var psconsole = $('#json_res');
					psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
				});

			}
		}
	});
	///////////////////////////////////////////////////////////////////////
	$("#console_clear").click(function() {
		console.log('Pressed clear console button');
		$("#cmd_status").text("");
	});

	$("#options_threading").click(function() {
		console.log('Pressed options_threading button');
		SendCmd('options_threading', 0)
		$("#cmd_status").text("Pressed options_ping button");
	});

	$("#options_ping").click(function() {
		console.log('Pressed options_ping button');
		SendCmd('ping', 0)
		$("#cmd_status").text("Pressed options_ping button");
	});

	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {
			// //alert(data);
			$("#cmd_status").text(data.cmd);
		});
	}

});

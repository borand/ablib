///////////////////////////////////////////////////////////////////////
// WEB SOCKET HANDLING
//
//
function open_websocket() {
	
	function show_message(message) {
		$("#json_res").html($("#json_res").text() + message + '\n');		
		var psconsole = $('#json_res');
		psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	}

	var ws = new WebSocket("ws://127.0.0.1:8888/track");
	ws.onopen = function() {
		$('#live').val('CONNECTED').slider("refresh");
		//show_message('Connected.');
	};
	ws.onmessage = function(event) {
		var JsonData;
		try {
			JsonData = JSON.parse(event.data);
			if (JsonData.hasOwnProperty('id'))			
			{
				console.log(JsonData.id);
				$('#'+JsonData.id).val(JsonData.val).slider("refresh");
			}
			
		} catch(e) {			
			console.log('JSON.parse error: "' + e + '". JsonData = ' + JsonData);
		}
		show_message(event.data);
	};
	ws.onclose = function() {
		$('#live').val('CONNECT').slider("refresh");
		//show_message("Closed.");
	};
}

///////////////////////////////////////////////////////////////////////
// MAIN GUI - jQUERY
//
//
$(document).ready(function() {

	console.log('Document ready');
	$('#json_res').attr('style', 'background-color:White; font-size:14px; height: 20em;');

	open_websocket();

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

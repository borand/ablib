

$(document).ready(function() {
	console.log('Document ready');	
	$('#json_res').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	
	///////////////////////////////////////////////////////////////////////
	function open_websocket(){
		function show_message(message){
			// var el = document.createElement('div');
			// el.innerHTML = message;
			// document.body.appendChild(el);
			$("#json_res").html($("#json_res").text() + message + '\n');
					//$('#scratchpad').text(data);
					var psconsole = $('#json_res');
					psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
		}

		var ws = new WebSocket("ws://127.0.0.1:8888/track");
		ws.onopen = function() {
			show_message('Connected.');
		};
		ws.onmessage = function(event) {
	     // var point = JSON.parse(event.data);
	     // console.log(point[1][1] + point[1][2]);
	     show_message(event.data);
	 };
	 ws.onclose = function() {
	 	show_message("Closed.");
	 };
	}

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
				if (cmd == ''){
					console.log('Sending empty command');
					cmd = ' ';
				}
				else{
					console.log('Sending command: ' + cmd);
				}
					
				console.log('Sending command: ' + cmd);
				$("#json_res").append("cmd>" + cmd + "\n");

				$.post( "/msg", { msg: "hello redis"} );

				$.getJSON('/msg/' + cmd, "", function(data) {
					console.log(String(data));
					$("#json_res").html($("#json_res").text() + data + '\n');
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
		SendCmd('options_threading',0)
		$("#cmd_status").text("Pressed options_ping button");
	});
	
	
	$("#options_ping").click(function() {
		console.log('Pressed options_ping button');
		SendCmd('ping',0)
		$("#cmd_status").text("Pressed options_ping button");
	});
	

	function SendCmd(cmd, val) {
		return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {
			// //alert(data);
			$("#cmd_status").text(data);
		});
	}


}); 
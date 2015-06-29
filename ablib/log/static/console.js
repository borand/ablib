///////////////////////////////////////////
// Global variables
var active_tab;
var debug_websocket = true;
var debug_js = true;
var debug_all = true;

var ws;
/////////////////////////////////////////////////////////////////////
// UTILITY FUNCTIONS
//
function dbg(message, show) {	
	if (show){
		console.log(message);
	}
}

function show_server_msg(message, show) {	
	if (show)
	{			
		$("#debug_console").html( $("#debug_console").text() + message + '\n');
	    var psconsole = $('#debug_console');
	    psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	}
}


function open_websocket(hostname, hostport, hosturl) {

	dbg('Attempting to open web socket',true);
	function show_message(message) {
		show_server_msg(message);		
	}

	var websocket_address = "ws://" + hostname + ":" + hostport + "/websocket/" + hosturl;
	ws = new WebSocket(websocket_address);
	
	ws.onopen = function() {		
		dbg('web socket open', true);
		$('#live').text('CONNECTED');
		$("#live").css("background-color",'#B2BB1E');
	};

	ws.onmessage = function(event) {		
		//dbg('incomming message', true);
		server_message_handler(event.data);
	};
	ws.onclose = function() {
		debug_websocket = $('#debug_websocket').prop("checked");
		dbg('closing websockets', debug_websocket);
		$('#live').text('OFFLINE');
		$("#live").css("background-color",'#FF0000');
	};
}

function server_message_handler(data){	
	var JsonData;	
	try {
		JsonData = JSON.parse(data);
		console.log(JsonData);
		msg_text = ' | '+ JsonData.level + ' | ' + JsonData.filename + ':'+ JsonData.funcname+ ':'+ JsonData.line_no + ' | ' + JsonData.msg
		show_server_msg(msg_text, true);
	} catch(e) {
		dbg('JSON.parse error: "' + e + '". JsonData = ' + JsonData);
		return;
	}	
}

function connect_to_websocket_host(){
	var hostname = $('#hostname').val();
	var hostport = $('#hostport').val();
	var hosturl  = $('#hosturl').val();	
	dbg('Pressed button: button_connect: [host, port] ' + hostname +':' + hostport + '/' + 'websocket/' + hosturl, true);
	open_websocket(hostname, hostport, hosturl);

}
///////////////////////////////////////////////////////////////////////
// MAIN GUI - jQUERY
//
//
$(document).ready(function() {

	dbg('Document ready', true);
	
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );
	
	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);

	$('#console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#console').textinput("option", "autogrow", false);	
		
	$('#server_msg').textinput("option", "autogrow", false);
	$("#live").css("background-color",'#C71C2C');
	
	connect_to_websocket_host();

	///////////////////////////////////////////////////////////////////////
	//
	// BUTTONS
	//

	$("#button_connect").click(function() {	
		connect_to_websocket_host();
	});

	$("#button_disconnect").click(function() {	
		ws.close();
	});

	$("#button_clear_debug_console").click(function() {
		$("#debug_console").text("");
	});
});

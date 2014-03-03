function open_websocket(){
	function show_message(message){
		var el = document.createElement('div');
		el.innerHTML = message;
		document.body.appendChild(el);
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
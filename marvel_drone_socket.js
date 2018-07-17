const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';
//var prompt = require('prompt');
var arDrone = require('ar-drone');

var client = arDrone.createClient();
var flight_value;

function fly_drone(flight_value) {
	console.log("YAAAAAY");
	console.log(flight_value);
	if(flight_value.power_x < 0) {
		client.left(flight_value.power_x);
	}
	else {
		client.right(flight_value.power_x);
	}
	if(flight_value.power_y < 0) {
		client.back(flight_value.power_y);
	}
	else {
		client.front(flight_value.power_y);
	}
}

const handler = (socket) => {
	socket.on('data', (bytes) => {
		const msg = bytes.toString();
		flight_value = JSON.parse(msg);
		//console.log(flight_value);
		fly_drone(flight_value);
	});
};
fs.unlink(
	socketPath,
	() => net.createServer(handler).listen(socketPath)
);

// function flight_value(current, desired) {
// 	var diff = current-desired;
// 	var margin = diff*0.05;
// 	if(diff <= margin) {
// 		return 0;
// 	}
// 	else {
// 		var power = 0.1*diff;
// 		if(power >= 0.6) {
// 			return 0.6;
// 		}
// 	}
// }

// function get_new_position() {
// 	prompt.start();
// 	prompt.get(['x'], function(err, result) {
// 		desired_x = result.x;
// 		//desired_y = result.y;
// 		console.log('Command-line input received:');
// 		console.log('x: ' + result.x);
// 		//console.log('y: ' + result.y);
// 	});
// }
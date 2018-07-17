const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';
var prompt = require('prompt');
var arDrone = require('ar-drone');

var client = arDrone.createClient();
var drone_position;
var desired_x;
var desired_y;

const handler = (socket) => {
	socket.on('data', (bytes) => {
		const msg = bytes.toString();
		drone_position = JSON.parse(msg);
		//console.log(drone_position);
	});
};
fs.unlink(
	socketPath,
	() => net.createServer(handler).listen(socketPath)
);

function flight_value(current, desired) {
	var diff = current-desired;
	var margin = diff*0.05;
	if(diff <= margin) {
		return 0;
	}
	else {
		var power = 0.1*diff;
		if(power >= 0.6) {
			return 0.6;
		}
	}
}

function get_new_position() {
	prompt.start();
	prompt.get(['x'], function(err, result) {
		desired_x = result.x;
		//desired_y = result.y;
		console.log('Command-line input received:');
		console.log('x: ' + result.x);
		//console.log('y: ' + result.y);
	});
}

function main() {
	console.log(drone_position);
	get_new_position();
	//console.log("Desired x: " + desired_x);
	//console.log("Desired y: " + desired_x);
	console.log(drone_position);
}

main();
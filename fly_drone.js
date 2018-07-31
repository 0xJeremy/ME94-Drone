const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';
var arDrone = require('ar-drone');

var client = arDrone.createClient();
var flight_value;

client.takeoff();

function fly_drone(flight_value) {
	console.log(flight_value);
	if(flight_value.power_x < 0) {
		console.log("Left " + flight_value.power_x);
		client.left(-flight_value.power_x);
	}
	else {
		console.log("Right " + flight_value.power_x);
		client.right(flight_value.power_x);
	}
	// if(flight_value.power_y < 0) {
	// 	console.log("Back " + flight_value.power_y);
	// 	client.back(-flight_value.power_y);
	// }
	// else {
	// 	console.log("Front " + flight_value.power_y);
	// 	client.front(flight_value.power_y);
	// }
}

const handler = (socket) => {
	socket.on('data', (bytes) => {
		const msg = bytes.toString();
		console.log(msg);
		flight_value = JSON.parse(msg);
		fly_drone(flight_value);
	});
};
fs.unlink(
	socketPath,
	() => net.createServer(handler).listen(socketPath)
);
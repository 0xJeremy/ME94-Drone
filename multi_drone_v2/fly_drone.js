const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';
var arDrone = require('ar-drone');

var flight_value;

drone1 = arDrone.createClient({'ip': '192.168.1.10'})
drone5 = arDrone.createClient({'ip': '192.168.1.11'})

function initialize_drone(drone) {
	drone.disableEmergency();
	drone.animateLeds('blinkRed', 5, 2);
	drone.takeoff();
	drone.back(0);
	drone.front(0);
	drone.left(0);
	drone.right(0);
}

function fly_drone(drone, flight_value) {
	console.log(flight_value);
	if(flight_value.power_x < 0) {
		console.log("Back " + flight_value.power_x);
		drone.back(-flight_value.power_x);
	}
	else {
		console.log("Front " + flight_value.power_x);
		drone.front(flight_value.power_x);
	}
	if(flight_value.power_y < 0) {
		console.log("Left " + flight_value.power_y);
		drone.left(-flight_value.power_y);
	}
	else {
		console.log("Right " + flight_value.power_y);
		drone.right(flight_value.power_y);
	}
}

const handler = (socket) => {
	socket.on('data', (bytes) => {
		const msg = bytes.toString();
		console.log(msg);
		flight_value = JSON.parse(msg);
		if(flight_value.drone_num == 1) {
			fly_drone(drone1, flight_value)
		}
		else if(flight_value.drone_num == 5) {
			fly_drone(drone5, flight_value)
		}
	});
};

fs.unlink(
	socketPath,
	() => net.createServer(handler).listen(socketPath)
);
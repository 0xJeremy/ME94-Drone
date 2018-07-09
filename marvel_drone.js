var arDrone = require('ar-drone');
var client = arDrone.createClient();
var https = require('https');
var XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;
var readline = require('readline-sync');
var spawn = require('child_process').spawnSync;
var py = spawn('python', ['example.py']);

var drone_position;

function get_position() {
	py.stdout.on('data', function(data) {
		drone_position = JSON.parse(data.toString());
		console.log(drone_position);
	});
	py.stdin.end();
	return drone_position;
}

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
x = get_position();
console.log("x is: " + x);
// while(true) {
// 	drone_position = get_position();
// 	var desired_x = readline.question("Enter a desired x location: ");
// 	var desired_y = readline.question("Enter a desired y location: ");
// 	var desired_z = readline.question("Enter a desired z location: ");
// 	var fly_x = flight_value(drone_position["x"], desired_x);
// 	var fly_y = flight_value(drone_position["y"], desired_y);
// 	var fly_z = flight_value(drone_position["z"], desired_y);
// 	console.log(fly_x + " " + fly_y + " " + fly_z);
// }

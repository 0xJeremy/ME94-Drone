const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';
var arDrone = require('ar-drone');
var client = arDrone.createClient();

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

var drone_position;

const handler = (socket) => {
  socket.on('data', (bytes) => {
    const msg = bytes.toString();
    drone_position = JSON.parse(msg);
    console.log(drone_position);

  });

};

fs.unlink(
  socketPath,
  () => net.createServer(handler).listen(socketPath)
);
const net = require('net');
const fs = require('fs');
const socketPath = '/tmp/node-python-sock';


const handler = (socket) => {
  socket.on('data', (bytes) => {
    const msg = bytes.toString();
    console.log(msg);

    // if (msg === 'python connected')
    //   return socket.write('hi');
    // socket.write('end');
    //return process.exit(0);

  });

};

fs.unlink(
  socketPath,
  () => net.createServer(handler).listen(socketPath)
);
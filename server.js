const net = require('net');
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('./config.json'));
const PORT = 8000;
let senderSocket = null;
let receiverSocket = null;
let reorderBuffer = [];

function log(...args) {
  console.log(new Date().toISOString(), ...args);
}

function simulateChannel(pduBuffer, callback) {
  if (Math.random() < config.lossRate) {
    log('Simulate loss of PDU');
    return;
  }
  if (Math.random() < config.duplicationRate) {
    log('Simulate duplication');
    callback(pduBuffer);
  }
  if (Math.random() < config.reorderRate) {
    const delay = Math.random() * config.maxDelayMs;
    log(`Simulate reorder/delay ${delay.toFixed(0)}ms`);
    setTimeout(() => callback(pduBuffer), delay);
  } else {
    callback(pduBuffer);
  }
}

const server = net.createServer((socket) => {
  log('Connection established from', socket.remoteAddress, socket.remotePort);

  socket.on('data', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      log('Received message', msg.type || msg.header?.type, msg);
      if (msg.type === 'HELLO') {
        if (msg.role === 'SENDER') senderSocket = socket;
        if (msg.role === 'RECEIVER') receiverSocket = socket;
        return;
      }
      // Route selon origine
      if (socket === senderSocket && receiverSocket) {
        simulateChannel(data, d => receiverSocket.write(d));
      } else if (socket === receiverSocket && senderSocket) {
        simulateChannel(data, d => senderSocket.write(d));
      }
    } catch (err) {
      log('Error parsing data:', err.message);
    }
  });

  socket.on('error', (err) => {
    if (err.code !== 'ECONNRESET') log('Socket error:', err);
    else log('Connection reset by peer');
  });

  socket.on('close', (hadError) => {
    log('Connection closed', hadError ? 'with error' : 'gracefully');
  });
});

server.on('error', (err) => {
  log('Server error:', err);
});

server.listen(PORT, () => log(`Server listening on port ${PORT}`));
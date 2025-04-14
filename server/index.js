const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

io.of('/rlc').on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  socket.on('send_packet', (pkt) => {
    socket.broadcast.emit('packet', pkt);
  });
  socket.on('ack', () => {
    socket.broadcast.emit('ack');
  });
  socket.on('disconnect', () => console.log('Client disconnected:', socket.id));
});

const PORT = 3000;
server.listen(PORT, () => console.log(`Server listening on port ${PORT}`));

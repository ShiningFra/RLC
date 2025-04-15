const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

io.of('/rlc').on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Métadonnées (taille et nombre de paquets)
  socket.on('metadata', (meta) => {
    console.log('🔖 Metadata received:', meta);
    // On broadcast pour tous les autres clients
    socket.broadcast.emit('metadata', meta);
  });

  // Envoi d’un paquet codé
  socket.on('send_packet', (pkt) => {
    socket.broadcast.emit('packet', pkt);
  });

  // ACK de fin de transmission
  socket.on('ack', () => {
    console.log('🔔 ACK received from', socket.id);
    socket.broadcast.emit('ack');
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = 3000;
server.listen(PORT, () => console.log(`Server listening on port ${PORT}`));

// server.js

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const axios = require('axios');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static('public'));

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

io.on('connection', (socket) => {
  console.log('A user connected');

  socket.on('chat message', async (msg) => {
    // Forward user message to Python server
    try {
      const response = await axios.post('https://test-048m.onrender.com/bot', { message: msg });
      const botReply = response.data.bot_reply;

      // Send bot reply to all connected clients
      io.emit('chat message', `Bot: ${botReply}`);
    } catch (error) {
      console.error('Error communicating with the Python server:', error.message);
    }
  });

  socket.on('disconnect', () => {
    console.log('User disconnected');
  });
});

server.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});

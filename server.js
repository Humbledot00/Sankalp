// server.js

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const axios = require('axios');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static('public'));
const PORT = process.env.PORT || 3000;


app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

const MONGODB_URI = 'mongodb+srv://workforshreyas:yiEOXA7G7qxY90Pf@cluster0.li4h8f5.mongodb.net/user-information?retryWrites=true&w=majority';
mongoose.connect(MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true });

// Define a schema for your data
const userSchema = new mongoose.Schema({
  username: String,
  email: String,
});

const User = mongoose.model('User', userSchema);

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.post('/submit', async (req, res) => {
  try {
    // Log the incoming data
    console.log('Incoming data:', req.body);

    // Extract data from the request body
    const { username, email } = req.body;

    // Create a new user document
    const newUser = new User({ username, email });

    // Log the new user document

    // Save the user document to MongoDB
    await newUser.save();

    // Respond with success
    res.status(200).json({ success: true, message: 'User information saved successfully' });
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
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

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

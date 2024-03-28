const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 80;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'intro_page.html'));
});

app.get('/chat', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'chat_page.html'));
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
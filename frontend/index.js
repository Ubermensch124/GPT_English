const express = require("express");
require("dotenv").config({ path: '../.env' });
const path = require("path");

const port = process.env.FRONTEND_PORT || 80;

const app = express();

app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "intro_page.html"));
});

app.get("/chat", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "chat_page.html"));
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

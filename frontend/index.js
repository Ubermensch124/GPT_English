const express = require("express");
// require("dotenv").config({ path: '../.env' });
require("dotenv").config();
const path = require("path");

const prod = process.env.PRODUCTION || "False";
let host;
let port;
if (prod === "True") {
  port = process.env.FRONTEND_PORT_PRODUCTION || 3000;
  host = process.env.FRONTEND_HOST_PRODUCTION || "frontend";
} else {
  port = process.env.FRONTEND_PORT_DEVELOPMENT || 80;
  host = process.env.FRONTEND_HOST_DEVELOPMENT || "localhost";
}

const app = express();

app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "intro_page.html"));
});

app.get("/chat", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "chat_page.html"));
});

app.listen(port, () => {
  console.log(`Server is running on http://${host}:${port}`);
});

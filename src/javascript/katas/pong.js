const express = require("express");

const app = express();
const port = process.env.PORT || 8080;

app.get("/ping", (req, res) => {
  res.type("text").send("pong");
});

app.listen(port, "127.0.0.1", () => {
  console.log(`Listening on http://localhost:${port}`);
});

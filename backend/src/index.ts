const express = require('express');
const http = require('http');

const app = express();
const port = 8080;

const server = http.createServer(app);

server.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});


app.use(express.json());






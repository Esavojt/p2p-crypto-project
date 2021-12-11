const http = require('http');
const net = require('net');


const httpServerPort = 8080;
const tcpServerPort = 8090;

// This array holds "registered" clients public key and ip address 
var connectedClients = {}

// Create http server object that returns the connectedClients array
var httpServer = http.createServer(function(req, res) {
	res.write(JSON.stringify(connectedClients));
	res.end();
});

// Create http server for monitoring registered hosts (only for debugging, should not be accessible from the internet)
console.log("Starting http server on port %d", httpServerPort);
httpServer.listen(httpServerPort);

// Create tcp server object that handles all the client registration and connections
var tcpServer = net.createServer(function(socket) {
	socket.write("Hello\r\n");
	socket.on("data", function(data) {
		console.log(data.toString("utf-8"));
		if(data.toString().trim() == "exit"){
			socket.end();
		}
	});
});

// Create TCP server that listens on tcpServerPort
console.log("Starting tcp server on port %d", tcpServerPort);
tcpServer.listen(tcpServerPort);



'use strict';
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
	socket.on("data", function(data) {
		var ipAddress = socket.remoteAddress;

		if (ipAddress.startsWith("::ffff:")) {
			ipAddress = ipAddress.substring(7)
		}

		data = data.toString("utf-8").trim();

		if(data.startsWith("REGISTER")){
			// REGISTER,srcPubKey
			let client = data.split(",");

			console.log("Client registered from %s", ipAddress);
			connectedClients[client[1]] = {address: ipAddress, socketObject: socket, publicKey: client[1]};

			socket.write("OK\n");
		}else if(data.startsWith("CONNECT")){
			// CONNECT,srcPubKey,receiverPubKey
			let parsedData = data.split(",");

			var srcPort = generatePort()
			var dstPort = generatePort()

			if(!connectedClients[parsedData[2]]){
				socket.write("NO\n")
			}else{
				var receiver = connectedClients[parsedData[2]];

				var srcSocket = socket;
				var receiverSocket = receiver.socketObject;

				var srcIP = ipAddress;
				var receiverIP = receiver.address;

				console.log("Connection between: %s:%s -> %s:%s", srcIP, srcPort, receiverIP, dstPort)
				srcSocket.write("OK," + receiverIP + "," + dstPort + "," + srcPort);

				receiverSocket.write("OK," + srcIP + "," + srcPort + "," + dstPort);

			}
			
		}
	});

	socket.on("error", function(err) {
		console.log("An error has occured", err.name);
		var keys = Object.keys(connectedClients)
		keys.forEach(key => {
			if(connectedClients[key].socket == socket){
				console.log(connectedClients[key].address, "disconnected, removing from db")
				delete connectedClients[key]
			}
		});
	});

	socket.on("end", function(){
		connectedClients.forEach(element => {
			if(element.socket == socket){
				console.log(element.address, "disconnected, removing from db")
				delete connectedClients[element.publicKey]
			}
		});
	})
});

// Create TCP server that listens on tcpServerPort
console.log("Starting tcp server on port %d", tcpServerPort);
tcpServer.listen(tcpServerPort);


var generatePort = function(){
	return Math.floor(Math.random() * 10000) + 15000;
}
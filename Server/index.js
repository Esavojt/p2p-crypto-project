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

	let handler = function(data) {
		var ipAddress = socket.remoteAddress;

		if (ipAddress.startsWith("::ffff:")) {
			ipAddress = ipAddress.substring(7)
		}

		switch (data[0]) {
			case 0x11:
				var publicKey = data.subarray(1, 393).toString("ascii");
				var hostname = data.subarray(393).toString("ascii");

				console.log("Client registered from %s with hostname '%s'", ipAddress, hostname);
				connectedClients[publicKey] = {address: ipAddress, publicKey: publicKey, hostname: hostname, socketObject: socket};

				socket.write(Buffer.from([0x00]));
				break;

			case 0x12:
				// TODO: Implement
				const localPublicKey = data.subarray(1, 393).toString("ascii");
				const remotePublicKey = data.subarray(393, 786).toString("ascii");
				console.log(localPublicKey);
				console.log(remotePublicKey);

				let remoteClient = connectedClients[remotePublicKey]

				if (remoteClient == null) {
					console.warn(`${remotePublicKey} couldn't be found`);
					socket.write(Buffer.from([0x01]));
					break;
				}

				remoteClient.socketObject.write(Buffer.from([0x13])+Buffer.from(remotePublicKey));

				remoteClient.socketObject.on("data", function(remoteData){
					if(remoteData[0] != 0x00){
						socket.write(Buffer.from([0x01]));
						remoteClient.socketObject.on("data", handler);
						return;
					}
					const ipAddressRegex = /(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/;
					let matchLocal = ipAddressRegex.exec(ipAddress); // TODO: IP address
					let matchRemote = ipAddressRegex.exec(remoteClient.address); // TODO: Implement
	
					if (matchLocal == null || matchRemote == null) {
						console.warn(`No ip present for: ${remotePublicKey}:${ipAddress} or ${localPublicKey}:${"remote ip"}`);
						socket.write(Buffer.from([0x01]));
					}else{
						socket.write(Buffer.from([0x14, parseInt(matchLocal[1]), 
														parseInt(matchLocal[2]), 
														parseInt(matchLocal[3]), 
														parseInt(matchLocal[4])]));
						// TODO: remote socket write ip address 
						remoteClient.socketObject.write(Buffer.from([0x14,  parseInt(matchRemote[1]), 
																			parseInt(matchRemote[2]), 
																			parseInt(matchRemote[3]), 
																			parseInt(matchRemote[4])]));
					}
					remoteClient.socketObject.on("data", handler);
				});				
				break;

		}
		return;

		if(data[0] == 0x11){
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
			
		}else{
			console.log("Someone sent wrong data! %s: %s", socket.remoteAddress, data);
		}
	};

	socket.on("error", function(err) {
		console.log("An error has occured '%s'", err.message);
		var keys = Object.keys(connectedClients);
		var ipAddress = socket.remoteAddress;

		if (ipAddress.startsWith("::ffff:")) {
			ipAddress = ipAddress.substring(7)
		}

		keys.forEach(key => {
			if(connectedClients[key].address == ipAddress){
				console.log(connectedClients[key].address, "disconnected, removing from db")
				delete connectedClients[key]
			}
		});
	});
	socket.on("data", handler);

	socket.on("end", function(){
		var keys = Object.keys(connectedClients);
		var ipAddress = socket.remoteAddress;

		if (ipAddress.startsWith("::ffff:")) {
			ipAddress = ipAddress.substring(7)
		}

		keys.forEach(key => {
			if(connectedClients[key].address == ipAddress){
				console.log(connectedClients[key].address, "disconnected, removing from db")
				delete connectedClients[key]
			}
		});

	});
});

// Create TCP server that listens on tcpServerPort
console.log("Starting tcp server on port %d", tcpServerPort);
tcpServer.listen(tcpServerPort);


var generatePort = function(){
	return Math.floor(Math.random() * 10000) + 15000;
}
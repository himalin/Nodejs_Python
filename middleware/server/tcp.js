"use strict";
var util = require('util');
var net = require('net');
var exchange = require('./exchange');


exports.createServer = function(port, maxFrameSize) {
    
	    var tcpServer = net.createServer(function (socket) {
	    var frame = '';
	
		socket.on('data',function(data){
			console.log(data.toString())
			exchange.push(data.toString(), 'test');
		})
	});

	tcpServer.listen(port);
	console.log('TCP server listening at port:%d',tcpServer.address().port)
	
	return tcpServer;
};
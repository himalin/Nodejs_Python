"use strict";

var websocket = require('websocket');
var http = require('http');
var util = require('util');
var exchange = require('./exchange');

// create WebSocket server, returns server instance
exports.createServer = function(port, maxFrameSize) {
    var httpServer = http.createServer();

    httpServer.on('listening', function() {
		console.log('WS Server listening at port:%d',httpServer.address().port)
    });

    var wsServer = new websocket.server({
        httpServer: httpServer,
        maxReceivedMessageSize: maxFrameSize
    });

    wsServer.on('request', function(request) {
        var connection = request.accept(null, request.origin);

        var address = util.format(
            '%s:%d',
            connection.socket.remoteAddress,
            connection.socket.remotePort
        );

        var subscriptions = {};

        var handleSubscribe = function(parsed) {
            var destination = parsed.destination;
            if (destination in subscriptions) {
                throw new Error(util.format('Destination \'%s\' already exists', destination));
            } else {
                var id = exchange.add(destination, deliver);
                subscriptions[destination] = id;
            }
        };

        var deliver = function(content, match) {
            connection.sendUTF(JSON.stringify({
									type: 'message',
									match: match,
									content: content
									}));
			};

        connection.on('message', function(message) {
            try {
                if (message.type != 'utf8') {
                    throw new Error('Must be utf-8 format');
                }
                var parsed = JSON.parse(message.utf8Data);
                handleSubscribe(parsed);
            } catch (e) {
 
            }
        });

        connection.on('close', function(reasonCode, description) {
            for (var destination in subscriptions) {
                var id = subscriptions[destination];
                exchange.remove(id);
            }
            subscriptions = {};
        });
    });

    httpServer.listen(port);
    return httpServer;
};
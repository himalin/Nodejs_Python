"use strict";

var config = require('./config');
var tcp = require('./tcp');
var ws = require('./ws');

tcp.createServer(config.tcpPort, config.maxFrameSize);
ws.createServer(config.wsPort, config.maxFrameSize);

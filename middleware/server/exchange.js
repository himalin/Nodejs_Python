"use strict";

var uuid = require('node-uuid');
var receivers = {};

// push a message with destination and call matched receivers
function push(message, destination) {
    for (var key in receivers) {
        var receiver = receivers[key];
        var destinationRegex = receiver['destination'];
        var callback = receiver['callback'];
        var matchResult = destinationRegex.exec(destination);
        if (matchResult != null) {
            try {
                callback(message, matchResult);
            } catch(e) {
            }
        }
    }
}

function add(destinationRegex, callback) {
    try {
        var receiver = {};
        receiver['destination'] = new RegExp(destinationRegex);
        if (!(callback instanceof Function)) {
            throw new Error('Callback is not a function');
        }
        receiver['callback'] = callback;
        var key = uuid();
        receivers[key] = receiver;
        return key
    } catch (e) {
        throw e;
    }
}

// remove a message receiver by it's key
function remove(key) {
    delete receivers[key];
}

module.exports = {
    push: push,
    add: add,
    remove: remove
};


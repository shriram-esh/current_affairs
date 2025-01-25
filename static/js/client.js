import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io('http://localhost:5000');

    socket.on('after connect', function(msg) {
        console.log('After connect', msg);
    });
});
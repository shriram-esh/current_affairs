import { io } from 'socket.io-client';
import { updateGraph } from './index.js';

$(document).ready(function() {

    const socket = io("/game");

    $('#bid-form').submit((e) => {
        e.preventDefault();
        const formData = $('#bid-form').serialize();
        socket.emit('submit_bid', { data: formData });
        $('#bid-form')[0].reset();
    });

    socket.on('round_over', (data) => {
        console.log(`Round Over! Data: ${data}`)
        updateGraph(data);
    });

    socket.on('bid_status', (data) => {
        console.log(data["message"])
    });
});
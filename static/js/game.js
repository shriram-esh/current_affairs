import { io } from 'socket.io-client';
import { updateGraph } from './index.js';

$(document).ready(function() {

    const socket = io("/game");

    $('#leave-btn').on("click", () => {
        location.href = "/logout";
    });

    $('#bid-form').submit((e) => {
        e.preventDefault();
        const formData = $('#bid-form').serialize();
        socket.emit('submit_bid', { data: formData });
        $('#bid-form')[0].reset();
    });

    socket.on('round_over', (data) => {
        // console.log(`Round Over! Data: ${data.graphData}`)
        // console.log(`Player Bids: ${data.playerProfits}`)
        console.log(data.playerProfits)
        $('#bidMsg').empty();
        $('#demandCutOff').html(`<p>Demand Cut Off: ${data["graphData"]["demandCutOff"]}</p>`);
        $('#priceCutOff').html(`<p>Price Cut Off: ${data["graphData"]["priceCutOff"]}</p>`);
        const profits = data["playerProfits"].map(p => `<li>${p["player"]}: ${p["total"]}</li>`).join("");
        $('#playerProfits').html(profits);
        updateGraph(data["graphData"]);
    });

    socket.on('bid_status', (data) => {
        $('#bidMsg').html(`<p>${data.message}</p>`);
    });
});
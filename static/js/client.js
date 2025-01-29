import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io();

    socket.on('user_change', (data) => {
        $("#player-total").html(data["players"].length);

        $('#player-list').empty();
        $.each(data["players"], function (index, player) {
            $('#player-list').append(`<li>${player}</li>`); 
        });
    });
});
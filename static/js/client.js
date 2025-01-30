import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io("http://localhost:5000/lobby");

    socket.emit("join_room", {
        room: "{{ ctx['room'] }}",
        name: "{{ ctx['name'] }}"
    });

    socket.on('user_change', (data) => {
        $("#player-total").html(data["players"].length);

        $('#player-list').empty();
        $.each(data["players"], function (index, player) {
            $('#player-list').append(`<li>${player}</li>`); 
        });
    });
});
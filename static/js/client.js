import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io("/lobby");

    socket.on('player_left', (data) => {
        console.log("Last player")
        location.href = '/logout'; 
    });

    socket.on('user_change', (data) => {
        console.log(data);
        $("#player-total").html(data["players"].length);

        $('#player-list').empty();
        $.each(data["players"], function (index, player) {
            $('#player-list').append(`<li>${player["username"]}</li>`); 
        });
    });

    $('#start').click(function(e) {
        e.preventDefault();
        socket.emit('start_game', { message: 'Start the game' });
    });

    socket.on('game_start', (data) => {
        location.href = '/game'; 
    });
});
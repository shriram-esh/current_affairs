import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

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
        console.log(data)
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

    function updateGraph(in_data) {
        const graph = document.querySelector('.bidGraph');
        console.log(in_data["demand"])
        const demand = in_data["demand"]
        const marketPrice = in_data["marketPrice"]
        const xList = in_data["xList"] // Center of Bar (to[0] - from[0] / 2)
        const widthBar = in_data["widthBar"] // Width from left to right
        const barHeight = in_data["barHeight"] // Height of bar
        const colors = in_data["colors"]
    
        var data = [
            {
            x: xList,
            y: barHeight,
            width: widthBar,
            marker: {
                color: colors
            },
            type: 'bar'
            }
        ];
    
        var layout = {
            title: {
                text: "Electricity Market"
            },
            dragmode: false,
            shapes: [
                // Horizontal line (Market Price)
                {
                    type: "line",
                    x0: 0,  // Start at the min X value
                    x1: Math.max(widthBar.reduce((acc, cur) => acc + cur, 0) * 1.2, demand),  // End at the max X value
                    y0: marketPrice,
                    y1: marketPrice,
                    line: {
                        color: "red",
                        width: 3,
                        dash: "dash"
                    }
                },
                // Vertical line (Demand)
                {
                    type: "line",
                    x0: demand,
                    x1: demand,
                    y0: 0,  // Start at the min Y value
                    y1: Math.max(...barHeight) * 1.2,  // Extend a bit beyond max Y
                    line: {
                        color: "black",
                        width: 3,
                        dash: "dash"
                    }
                }
            ]
        };
    
        var config = {
            displayModeBar: false, // This removes the toolbar
            displaylogo: false, // This removes the Plotly logo
            scrollZoom: false, // Disable zoom on scroll
            staticPlot: false, // Allow hover interactions without panning or zooming
            editable: false  // Disable editing
        };
        
        Plotly.newPlot(graph, data, layout, config);
    } 
});
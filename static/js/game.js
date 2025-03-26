import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io("/game");

    // Get Initial Game Info
    socket.emit('get_stats');

    socket.on('send_stats', (data) => {
        console.log(data);
        $('#round').html(data[0]["currentRound"]);
        const assets = data.map(a => {
            return `
                <p><b>Asset Type:</b> ${a['asset']}</p>
                <p><b>Total MegaWatts:</b> ${a['units']}</p>
                <p><b>Dollars per MegaWatt Hour:</b> ${a['generation']}</p>
                <br>
            `
        });
        console.log(assets)
        $('#assets-list').html(assets);
    });

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
        const profits = data["playerProfits"].map(p => `<li id="${p["player"]}" class="bid-unready">${p["player"]}: $${p["total"].toLocaleString()}</li>`).join("");
        $('#playerProfits').html(profits);
        $('#round').html(data["roundNumber"]);
        updateGraph(data); 
    });

    socket.on('bid_status', (data) => {
        $('#bidMsg').html(`<p>${data.message}</p>`);
    });

    socket.on('all_bids_status', (data) => {
        console.log(`${data["name"]} is ready`);
        const player = $(`#${data["name"]}`);
        if (player.hasClass("bid-unready")) {
            player.removeClass("bid-unready").addClass("bid-ready");
        }
    });

    function updateGraph(data) {
        const in_data = data["graphData"]
        const graph = document.querySelector('.bidGraph');
        console.log(in_data["demand"])
        const demand = in_data["demand"]
        const marketPrice = in_data["marketPrice"]
        const xList = in_data["xList"] // Center of Bar (to[0] - from[0] / 2)
        const widthBar = in_data["widthBar"] // Width from left to right
        const barHeight = in_data["barHeight"] // Height of bar
        const colors = in_data["colors"]
        const players = in_data["players"]
        const roundNumber = data["roundNumber"]
        console.log(0, Math.max(...barHeight))
    
        var data = [
            {
                x: xList,
                y: barHeight,
                width: widthBar,
                marker: {
                    color: colors
                },
                type: 'bar',
                hovertext: widthBar.map((w, i) => `<b>${players[i]}</b><br>Quantity: ${w}<br>Price: ${barHeight[i]}`), 
                hoverinfo: "text"
            }
        ];
    
        var layout = {
            title: {
                text: `Electricity Market Round ${roundNumber - 1}`
            },
            yaxis: {
                type: 'log',
                range: [Math.log10(1), Math.log10(100000)],
                tickmode: 'array',
                tickvals: [1, 10, 100, 1000, 10000], // The values at which to show ticks
                ticktext: ['1', '10', '100', '1000', '10000'], // Custom labels for the ticks
            },
            dragmode: false,
            shapes: [
                // Horizontal line (Market Price)
                {
                    type: "line",
                    x0: 0,  // Start at the min X value
                    x1: Math.max(widthBar.reduce((acc, cur) => acc + cur, 0), demand),  // End at the max X value
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
                    y0: 0,  // Start at the minimum y value (log(1) = 0)
                    y1: 100000,  // Extend beyond max y value in log scale
                    line: {
                        color: "black",
                        width: 3,
                        dash: "dash"
                    }
                }
            ],
            annotations: [
                {
                    x: Math.max(widthBar.reduce((acc, cur) => acc + cur, 0), demand),  
                    y: Math.log10(marketPrice),
                    xanchor: "left",
                    yanchor: "middle",
                    text: `Market Price: ${marketPrice}`,
                    showarrow: true,
                    arrowcolor: "red",
                    ax: 20,  // Move the arrowhead to the right
                    ay: 0,  // Keep the arrow aligned horizontally
                    font: {
                        color: "red",
                        size: 14
                    }
                },
                // Demand Label
                {
                    x: demand,
                    y: Math.log10(10000),  
                    xanchor: "right",
                    yanchor: "bottom",
                    text: `Demand: ${demand}`,
                    showarrow: true,
                    arrowcolor: "black",
                    ax: -20,  // Move the arrowhead to the right
                    ay: -10,  // Keep the arrow aligned horizontally
                    font: {
                        color: "black",
                        size: 14
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
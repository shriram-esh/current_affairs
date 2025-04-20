import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

$(document).ready(function() {

    const socket = io("/game");

    // Get Initial Game Info
    socket.emit('get_stats');

    socket.on('send_stats', (data) => {
        $('#round').html(data["currentRound"]);
        const assets = data["bids"].map(a => {
            return `
                <p><b>Asset Type:</b> ${a['asset']}</p>
                <p><b>Generation Capacity:</b> ${a['units']} MW</p>
                <p><b>Generation Cost:</b> $${a['generation']} / MWh</p>
                <br>
            `
        });
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

    $('#default-form').submit((e) => {
        e.preventDefault();
        const formData = $('#default-form').serialize();
        socket.emit('submit_bid', { data: formData });
        $('#bid-form')[0].reset();
    });

    socket.on('round_over', (data) => {
        $('#errMsg').empty();
        const profits = data["playerProfits"].map(p => `<li id="${p["id"]}" class="bid-unready">${p["player"]}: $${p["total"].toLocaleString()}</li>`).join("");
        const gains = data["playerGains"].map(g => {
            let color = ""
            if (g["gain"] > 0) {
                color = "positive"
            } else if (g["gain"] < 0) {
                color = "negative"
            }
            return `<li>${g["player"]}: <span class=${color}>$${g["gain"].toLocaleString()}</span></li>`
        }).join("");

        $('#playerProfits').html(profits);
        $('#playerGains').html(gains);
        $('#round').html(data["roundNumber"]);
        $('#form-submit').html("<h1>Waiting for all bids...</h1>");
        updateGraph(data); 
    });

    socket.on('bid_status', (data) => {
        $('#errMsg').html(`<p>${data.message}</p>`);
    });

    socket.on('all_bids_status', (data) => {
        console.log(`Received Data: ${data["allBid"]}`)
        const player = $(`#${data["player_id"]}`);
        if (player.hasClass("bid-unready")) {
            player.removeClass("bid-unready").addClass("bid-ready");
        }

        if (data["allBid"]) { 
            const form = `
                <form method="POST" id="round-form">
                    <label for="slider">Slider:</label>
                    <input type="range" id="slider" name="slider" min="0" max="${data["marketUnits"]}" value="${Math.trunc(data["marketUnits"] / 2)}">
                    <label for="demand">Demand:</label>
                    <input type="number" id="demand" name="demand" min="0" max="${data["marketUnits"]}" value="${Math.trunc(data["marketUnits"] / 2)}">
                    <input type="submit" id="submit" name="round-submit" value="Run Round">
                </form>
            `;
            $('#form-submit').html(form);
        }
    });

    // Admin Functionality

    // Run Round

    $(document).on('submit', '#round-form', (e) => {
        e.preventDefault();
        const formData = $('#round-form').serialize();
        console.log("Submit");
        console.log(formData);
        socket.emit('run_round', { data: formData });
    });

    $(document).on("input", "#slider", function () {
        $("#demand").val($(this).val());
    });
    
    $(document).on("input", "#demand", function () {
        let value = parseInt($(this).val(), 10);
        let min = parseInt($(this).attr("min"), 10);
        let max = parseInt($(this).attr("max"), 10);

        if (value < min) $(this).val(min);
        if (value > max) $(this).val(max);
        
        $("#slider").val($(this).val()); // Keep slider in sync
    });

    function updateGraph(data) {
        const in_data = data["graphData"]
        const graph = document.querySelector('.bidGraph');
        const demand = in_data["demand"]
        const marketPrice = in_data["marketPrice"]
        const xList = in_data["xList"] // Center of Bar (to[0] - from[0] / 2)
        const widthBar = in_data["widthBar"] // Width from left to right
        const barHeight = in_data["barHeight"] // Height of bar
        const colors = in_data["colors"]
        const players = in_data["players"]
        const costs = in_data["costs"] // Total cost for each player
        const roundNumber = data["roundNumber"]
    
        var data = [
            {
                type: 'bar',
                x: xList,
                y: barHeight,
                width: widthBar,
                name: "Profits",
                marker: {
                    color: colors
                },
                hovertext: widthBar.map((w, i) => `<b>${players[i]}</b><br>Quantity: ${w}<br>Price: ${barHeight[i]}`), 
                hoverinfo: "text"
            },
            {
                type: 'bar',
                x: xList,
                y: costs,
                width: widthBar,
                name: "Cost",
                marker: { color: 'red' },
                opacity: 0.6,
                text: costs,
                textposition: 'outside',
                textfont: {
                    color: 'black',
                    size: 14
                },
                hovertext: costs.map((w, i) => `<b>${players[i]}</b><br>Cost: ${w}`), 
                hoverinfo: "text"
            }
        ];
    
        var layout = {
            barmode: 'overlay',
            title: {
                text: `Electricity Market Round ${roundNumber - 1}`
            },
            xaxis: {
                title: {
                    text: 'Quantity (MW)'  // 🡐 Your custom x-axis label
                }
            },
            yaxis: {
                title: {
                    text: 'Price ($/MWh)'  // 🡐 Your custom y-axis label
                },
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
                    } // This is important
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
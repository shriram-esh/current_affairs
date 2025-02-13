import Chart from 'chart.js/auto';
import annotationPlugin from 'chartjs-plugin-annotation';
import { config } from './chartSetup.js';

Chart.register(annotationPlugin);

const chart = new Chart(document.getElementById('acquisitions'), config);

export function updateGraph(inData) {
    //  Format: 
    //  {
    //      demandCutOff: 20,
    //      priceCutOff: 50,
    //      bids: [
    //              {bidQuantity: 'quantity1', bidPrice: price1, player: 'User1'},
    //              {bidQuantity: 'quantity2', bidPrice: price2, player: 'User2'}
    //            ]
    //  }

    //  User Auction Bids
    console.log(`Update Graph Data: \n${inData.demandCutOff}\n${inData.priceCutOff}`)

    const inputData = inData["bids"];
    const labels = [];
    inputData.forEach(bid => {
        labels.push(`${bid["player"]} Quantity: ${bid["bidQuantity"]}`)
    });

    console.log(inputData)
    console.log(labels)
    chart.data.datasets[0].data = inputData;
    chart.data.labels = labels

    // Market Price Line
    const marketPrice = chart.options.plugins.annotation.annotations[Object.keys(chart.options.plugins.annotation.annotations)[0]];
    // const marketDemand = chart.options.plugins.annotation.annotations[Object.keys(chart.options.plugins.annotation.annotations)[1]];
    marketPrice.value = inData["priceCutOff"];
    // marketDemand.value = inData["marketDemand"];

    chart.update();
    
    // document.getElementById('changeDataButton').addEventListener('click', changeChartData);
}
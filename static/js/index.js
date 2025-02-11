import Chart from 'chart.js/auto';
import annotationPlugin from 'chartjs-plugin-annotation';
import { config, updateChartData } from './chartSetup.js';

Chart.register(annotationPlugin);

new Chart(document.getElementById('acquisitions'), config);

export function updateGraph(data) {
    // // Example of changing the chart's data
    // function changeChartData() {
    //     const newData = [
    //       {x: 'Sales', y: 30}, 
    //       {x: 'Revenue', y: 40}
    //     ];
    
    //     // Update the chart data
    //     updateChartData(newData);
    
    //     // Update the chart view
    //     myChart.update();
    //   }
    
    //   // Trigger changeChartData when needed
    //   document.getElementById('changeDataButton').addEventListener('click', changeChartData);
}
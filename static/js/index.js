import Chart from 'chart.js/auto';
import annotationPlugin from 'chartjs-plugin-annotation';
import { config } from './chartSetup.js';

Chart.register(annotationPlugin);

new Chart(document.getElementById('acquisitions'), config);

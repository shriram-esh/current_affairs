const data = {
  labels: [],
  datasets: [{
    label: 'Electricity Market Round 1',
    data: [],
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(255, 159, 64, 0.2)',
      'rgba(255, 205, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(201, 203, 207, 0.2)'
    ],
    borderColor: [
      'rgb(255, 99, 132)',
      'rgb(255, 159, 64)',
      'rgb(255, 205, 86)',
      'rgb(75, 192, 192)',
      'rgb(54, 162, 235)',
      'rgb(153, 102, 255)',
      'rgb(201, 203, 207)'
    ],
    maxBarThickness: 100,
    borderWidth: 1,
  }]
};
// </block:setup>

// <block:annotation:1>
const annotation1 = {
    type: 'line',
    borderColor: 'black',
    borderWidth: 3,
    scaleID: 'y',
    value: 0
};

/* <block:config:0> */
const config = {
  type: 'bar',
  data: data,
  options: {
    indexAxis: 'x',
    datasets: {
      bar: {
        barPercentage: 1,
        categoryPercentage: 1
      }
    },
    scales: {
      y: {
        max: 150,
        beginAtZero: true
      }
    },
    parsing: {
      xAxisKey: 'bidQuantity',
      yAxisKey: 'bidPrice'
    },
    plugins: {
      annotation: {
        annotations: {
          annotation1,
          // annotation2
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.raw.bidPrice;
            return `$${value}`;
          }
        }
      }
    }
  }
};
/* </block:config> */

export { config };
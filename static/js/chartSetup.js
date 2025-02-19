// categoryPercentage is 1 
// barPercentage is 1 
// 1 * 1 * 1 = 1
// 1 / 2 = 0.5


function indexToMin(index) {
  return index - 0.5;
}

function indexToMax(index) {
  return index + 0.5;
}

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
    borderWidth: 1
  }]
};
// </block:setup>

// <block:annotation:1>
const annotation1 = {
    type: 'line',
    borderColor: 'black',
    borderWidth: 3,
    borderDash: [5, 5],
    scaleID: 'y',
    value: 0
};

const annotation2 = {
  type: 'line',
  borderColor: 'green',
  borderWidth: 3,
  xMax: indexToMin(1), // corresponds to first bar. 1 will be 2nd... so on
  xMin: indexToMin(1),
  xScaleID: 'x',
  yMax: 10000,
  yMin: 0,
  yScaleID: 'y',
  label: {
    display: false,
    backgroundColor: 'green',
    borderRadius: 0,
    color: 'white',
    content: '10'
  },
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
          annotation2 
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
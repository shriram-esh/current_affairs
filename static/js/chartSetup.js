// <block:setup:2>
const nums = [65, 59, 80, 81, 56, 55, 40];

const labels = [];
for (let i = 0; i < nums.length; ++i) {
  labels.push('' + i);
}

const data = {
  datasets: [{
    label: 'Electricity Market Round 1',
    data: [{x: 'Sales', y: 20}, {x: 'Revenue', y: 10}],
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
    borderWidth: 1,
    barPercentage: 1.0,
    categoryPercentage: 1.0
  }]
};
// </block:setup>

// <block:annotation:1>
const annotation = {
    type: 'line',
    borderColor: 'black',
    borderWidth: 3,
    scaleID: 'y',
    value: 10
};
// </block:annotation>

/* <block:config:0> */
const config = {
  type: 'bar',
  data: data,
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      annotation: {
        annotations: {
          annotation
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.raw.y;
            return `${value} units`;
          }
        }
      }
    }
  }
};
/* </block:config> */

export { config };
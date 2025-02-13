const path = require('path');
// Remove debug from socket.io library

module.exports = {  
    mode: 'development',  
    entry: './static/js/game.js',  
    output: {  
      filename: 'marketGame.js',
      path: path.resolve(__dirname, 'static/js'),  
      publicPath: '/static/js/'  
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          },
        },
      ],
    },
    resolve: {
      extensions: ['.js'],
    },
  };
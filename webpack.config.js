const path = require('path');

module.exports = {  
    mode: 'development',  
    entry: './static/js/index.js',  
    output: {  
      filename: 'main.js',
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
const path = require('path');

module.exports = {
  entry: './static/js/main.js', // Pfad zu deiner Haupt-JS-Datei
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static', 'dist')
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // Optional: Falls du ES6+ Code verwenden möchtest
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'static'),
    },
    compress: true,
    port: 9000,
  }
};
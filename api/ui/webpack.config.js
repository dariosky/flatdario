const combineLoaders = require('webpack-combine-loaders')
const webpack = require('webpack')
const config = {
  entry: __dirname + '/js/index.js',
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: ['babel-loader']
      },

      {
        test: /\.scss$/,
        exclude: /node_modules/,
        loader: combineLoaders(
          [
            {
              loader: 'style-loader',
            },
            {
              loader: 'css-loader',
              query: {
                modules: true,
                localIdentName: '[name]__[local]___[hash:base64:5]'
              },
            },
            {
              loader: 'sass-loader',
              query: {
                modules: true,
                localIdentName: '[name]__[local]___[hash:base64:5]'
              },
            }
          ])
      }
    ]
  }
}
module.exports = config

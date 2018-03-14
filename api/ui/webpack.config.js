const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')

const config = {
  entry: __dirname + '/src/index.js',
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
        use: [
          {loader: "style-loader"},
          {
            loader: "css-loader", options: {
              sourceMap: true,
              modules: true,
            }
          },
          {
            loader: "sass-loader", options: {
              sourceMap: true,
              modules: true
            }
          }]
      }
    ]
  },
  devtool: 'inline-source-map',
  devServer: {
    contentBase: './dist',
    hot: true
  },
  plugins: [
    new CopyWebpackPlugin([
      {from: 'assets'}
    ]),
  ]
}


module.exports = {
  ...config,
}

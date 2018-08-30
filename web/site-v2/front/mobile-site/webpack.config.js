var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {

    entry: path.resolve(__dirname, './js/app.js'),

    output: {
        path: path.resolve(__dirname, '../output/mobile/public'),
        filename: '[name]-[hash].js'
    },

    module: {
        loaders: [
            { test: /\.js$/, loader: 'babel-loader!jsx-loader?harmony', exclude: 'node_modules'}
        ]
    },

    resolve:{
        extensions:['','.js','.json']
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: path.resolve(__dirname, '../output/mobile/index.html')
        }),
        new webpack.optimize.UglifyJsPlugin({sourceMap: false, minimize: true})
    ]

};

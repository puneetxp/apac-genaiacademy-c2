const path = require('path');

module.exports = {
 mode: "production",
 entry: './Resource/Js/index.js',
 output: {
  path: path.resolve(__dirname, './public/assets/js'),
  filename: 'index.js',
 },
};
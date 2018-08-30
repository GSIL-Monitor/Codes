var Reflux = require('reflux');

const SearchActions = Reflux.createActions([
    'init',
    'initMobile',
    'get',
    {change: { sync: true }},
    'select',
    'unselect',
    {keydown: { sync: true }},
    'clickSearch'
]);

module.exports = SearchActions;
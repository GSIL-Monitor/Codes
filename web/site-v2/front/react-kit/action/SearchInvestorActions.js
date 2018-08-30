var Reflux = require('reflux');

const LocationActions = Reflux.createActions([
    'init',
    'get',
    {change: { sync: true }},
    'select',
    'unselect',
    {keydown: { sync: true }},
    'clickSearch'
]);

module.exports = LocationActions;
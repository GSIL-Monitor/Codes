var Reflux = require('reflux');

const NewsActions = Reflux.createActions([
    'get',
    'showAll',
    'select',
    'initNewsDetail'
]);

module.exports = NewsActions;
var Reflux = require('reflux');

const ProductActions = Reflux.createActions([
    'get',
    'changeType',
    'showAll',
    'update',
    'getTrends',
    'cleanChart',
    'changeNav',
    'changeView',
    'changeExpand'
]);

module.exports = ProductActions;
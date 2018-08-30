var Reflux = require('reflux');

const CollectionActions = Reflux.createActions([
    'init',
    'getCollection',
    'filter',
    'comfirmFilter',
    'dealUserScore',
    'listMore',
    'follow',
    'unFollow'
]);

module.exports = CollectionActions;
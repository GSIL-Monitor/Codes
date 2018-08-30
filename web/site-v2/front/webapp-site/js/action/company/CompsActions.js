var Reflux = require('reflux');

const CompsActions = Reflux.createActions([
    'get',
    'showAll',
    'update',
    'submit',
    'delete',
    'deleteNew',
    'addNew',
]);

module.exports = CompsActions;
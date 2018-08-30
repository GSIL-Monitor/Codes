var Reflux = require('reflux');

const UserHomeActions = Reflux.createActions([
    'init',
    'countTODO',
    'changeTask',
]);

module.exports = UserHomeActions;
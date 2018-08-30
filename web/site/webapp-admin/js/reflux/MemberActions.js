var Reflux = require('reflux');

const MemberActions = Reflux.createActions([
    'get',
    'change',
    'add',
    'update',
    'delete'
]);

module.exports = MemberActions;
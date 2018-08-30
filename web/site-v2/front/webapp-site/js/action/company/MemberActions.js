var Reflux = require('reflux');

const MemberActions = Reflux.createActions([
    'get',
    'showAll',
    'select',
    'update'
]);

module.exports = MemberActions;
var Reflux = require('reflux');

const InvestorActions = Reflux.createActions([
    'get',
    {change: { sync: true }},
    'add',
    'clean',
    'update',
    'delete'
]);

module.exports = InvestorActions;
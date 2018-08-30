var Reflux = require('reflux');

const ColdCallActions = Reflux.createActions([
    'getInitData',
    {change: { sync: true }},
    'listMore',
    'changeType'

]);

module.exports = ColdCallActions;
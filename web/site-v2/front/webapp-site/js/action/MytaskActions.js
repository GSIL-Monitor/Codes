var Reflux = require('reflux');

const MytaskActions = Reflux.createActions([
    'getTask',
    'getPublishTask',
    'getDiscovery',

    'countTODO',
    'listMore',
    'changeType',
    'changeFilter',

    'changeTaskFilterType',
    'changeTaskFilterStatus',
    'changePublishFilterStatus',
    'changeDiscoveryFilterStatus'
]);

module.exports = MytaskActions;
var Reflux = require('reflux');

const ColdcallActions = Reflux.createActions([
    'init',
    'getColdCall',
    'getCandidates',
    'getCompanies',
    'select',
    'remove',
    'extend',
    'decline',

    'selectForwardUser',
    'forward'
]);

module.exports = ColdcallActions;
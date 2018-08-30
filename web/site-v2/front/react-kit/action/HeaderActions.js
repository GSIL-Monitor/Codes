var Reflux = require('reflux');

const HeaderActions = Reflux.createActions([
    'router',
    'init',
    'initSearch',
    'clickMobileSearch',
    'clickSearchClose',
    'clickMobileHeader'
]);

module.exports = HeaderActions;
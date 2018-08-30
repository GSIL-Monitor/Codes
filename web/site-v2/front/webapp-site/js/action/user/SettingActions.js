var Reflux = require('reflux');

const SettingActions = Reflux.createActions([
    'initSectors',
    'selectSector',
    'init',
    'update',
    'changeRecommendNum'
]);

module.exports = SettingActions;
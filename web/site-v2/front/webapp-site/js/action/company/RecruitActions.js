var Reflux = require('reflux');

const RecruitActions = Reflux.createActions([
    'get',
    'showAll',
    'select',
    'update'
]);

module.exports = RecruitActions;
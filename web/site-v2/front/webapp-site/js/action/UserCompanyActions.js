var Reflux = require('reflux');

const UserCompanyActions = Reflux.createActions([
    'init',
    'addDeal',
    'getScore',
    'score',
    'getNote',
    'note',
    'showNoteAll',
    'update',
    'delete',
    {change:{ sync: true }},

]);

module.exports = UserCompanyActions;
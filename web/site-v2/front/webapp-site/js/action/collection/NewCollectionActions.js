var Reflux = require('reflux');

const NewCollectionActions = Reflux.createActions([
    'init',
    'select',
    {changeName: { sync: true }},
    'add'
]);

module.exports = NewCollectionActions;
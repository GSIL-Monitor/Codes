var Reflux = require('reflux');

const UserActions = Reflux.createActions([
    'checkLoginStatus',
    'logout'
]);

module.exports = UserActions;
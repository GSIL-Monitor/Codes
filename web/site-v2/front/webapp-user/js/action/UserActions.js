var Reflux = require('reflux');

const UserActions = Reflux.createActions([
    'login',
    {change: { sync: true }},
    'autoLogin',
    'setReturnurl'

]);

module.exports = UserActions;
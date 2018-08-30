var Reflux = require('reflux');

const ForgetpwdActions = Reflux.createActions([
    {change: { sync: true }},
    'next',
    'reset',
]);

module.exports = ForgetpwdActions;
var Reflux = require('reflux');

const ValidateCompanyActions = Reflux.createActions([
    'validateDate',

    {submit: { sync: true }}

]);

module.exports = ValidateCompanyActions;
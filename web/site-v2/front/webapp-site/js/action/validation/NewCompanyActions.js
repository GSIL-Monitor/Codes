var Reflux = require('reflux');

const NewCompanyActions = Reflux.createActions([
    'getInitData',
    'change',
    'name',
    'fullName',
    'brief',
    'date',
    'investment',
    'shareRatio',
    'remindInvestment',
    'preMoney',
    'postMoney',
    'phone',
    'round',
    'clean',
    'sector',
    'product',
    'productWebsite',
    'locationId',
    'uploadBp'

]);

module.exports = NewCompanyActions;
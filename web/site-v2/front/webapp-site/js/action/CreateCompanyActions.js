var Reflux = require('reflux');

const CreateCompanyActions = Reflux.createActions([
    'getInitData',
    {change: { sync: true }},
    'add',
    'clean',
    'upload',
    'addUploadedFile',
    'createConfirm',
    'updatePrePostMoney',
    'selectProduct',
    'getCompany',
    'getSecondSector',
    'addSector',
    'teamSizeChange',
    {memberChange:{sync:true}},
    'addTag',
    'deleteNewTag',
    'addProduct',
    {addProductName:{sync:true}},
    'deleteFile',
    'changeSector',
    'changeSubSector',
    'changeEstablishDate',
    'changeSource',

    {changeNote:{sync:true}}
]);

module.exports = CreateCompanyActions;
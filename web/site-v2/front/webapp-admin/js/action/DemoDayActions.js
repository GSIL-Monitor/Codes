var Reflux = require('reflux');

const DemoDayActions = Reflux.createActions([
    'getInitData',
    'getOrgList',
    'new',
    {change: { sync: true }},
    'add',
    'selectOrg',
    'update',
    'updateDate',
    'updateDemoday',
    'removeDemodayOrg',
    'addDemodayOrgs',
    'updateCompany',
    'updateStatus',
    'allPreScores',
    'getPreScores',
    'preScoreResult',
    'selectedIds',
    'batchOperate',
    'batchOperateChange',
    'removeDemodayCompany',
    'batchJoinOrNot',
    'getSysCompanies',
    'sysCompanyBatch',
    'selectSysCompAll',
    'sysCompanyBatchOperate'


]);

module.exports = DemoDayActions;
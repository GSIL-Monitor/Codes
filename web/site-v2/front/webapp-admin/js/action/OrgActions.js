var Reflux = require('reflux');

const OrgActions = Reflux.createActions([
    'getInitData',
    'new',
    {change: { sync: true }},
    'add',
    'update',
    'deleteOrg',
    {updateOrg: { sync: true }},
    'cloneOrg',
    'confirm',
    {user: { sync: true }},
    'addUser',
    'deleteUser',
    'cloneUser',
    'updateUser',
    {updateOrgUser: { sync: true }},
    'getUserByEmail',
    'modify',
    'cancel',
    'selectType',
    'listMore',
    'getInitUsersInfo'

]);

module.exports = OrgActions;
var Reflux = require('reflux');

const DemoDayActions = Reflux.createActions([
    'getDemoDay',
    'getDemoDayNav',
    'getPreScores',
    'getScores',
    'initScore',
    'getPreScore',
    'getScore',
    'getDecision',
    'rating',
    'submitScore',
    'decide',

    'submitCompany',
    'changeRecommendation',
    {changeDemoDayCompany: { sync: true }},
    'update',
    'comfirm',

    'getNOPasses'


]);

module.exports = DemoDayActions;
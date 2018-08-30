var Reflux = require('reflux');

const CompanyActions = Reflux.createActions([

    'update',
    {changeCompany: { sync: true }},
    'validateDate',
    'comfirm',

    'deleteSector',
    'deleteTag',
    'deleteFunding',
    'deleteFootprint',
    'deleteDocument',

    'deleteNewTag',
    'deleteNewFunding',
    'deleteNewFootprint',
    'deleteNewDocument',

    'selectFunding',
    'selectFIR',
    'selectFootprint',

    {changeSelectedFootprint: { sync: true }},


    'updateSelectedFootprint',

    //'addSectorBtn',
    //'addTagBtn',
    //'addFundingBtn',
    //'addFIRBtn',
    //'addFootprintBtn',

    'addSector',
    'addTag',
    'addFunding',
    'addFootprint',
    'addFIR',
    'addNewFIR',

    'addUploadedFile',

    {changeNewFootprint: { sync: true }},

    'changeSector',
    'changeSubSector',
    'changeCompanySector',
    'changeCompanySubSector',
    {changeInvestment: { sync: true }},
    {changeShareRatio: { sync: true }},
    {changeMoney: { sync: true }},
    {changeHeadCount: {sync: true}},
    {changeEstablishDate: {sync: true}},

    'showFundingAll',
    'showFootprintAll',
    'showDevelopAll',

    'init',
    'getCompany',
    {change: { sync: true }},

    'searchTag',
    'deleteTagDB',
    'addTagDB',

    {changeSelectedFunding: { sync: true }},
    'updateFundingAndInvestor',
    'deleteFIR',
    'changeAddFIR',
    'addNewFIRConfirm',
    {changeFunding: { sync: true }}

]);

module.exports = CompanyActions;
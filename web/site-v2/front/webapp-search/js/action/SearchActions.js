var Reflux = require('reflux');

const SearchActions = Reflux.createActions([
    'search',
    'get',
    {changeSearch: { sync: true }},
    'changeSort',
    'loadMore',

    'filterSector',
    'filterRound',
    'filterLocation',
    'filterDate',

    'cleanFilters',
    'comfirmFilters',
    'cancelFilters',
    'removeFilterItem'
]);

module.exports = SearchActions;
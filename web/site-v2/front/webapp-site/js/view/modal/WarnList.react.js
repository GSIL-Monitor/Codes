var React = require('react');

var DeleteCompanyWarn = require('../company/modal/DeleteCompanyWarn.react');
var CompanyWarn = require('../company/modal/CompanyWarn.react');
var NewCollectionWarn = require('../collection/new/NewCollectionWarn.react');

var WarnList= React.createClass({
    render(){
        return(
            <div>
                <DeleteCompanyWarn />
                <CompanyWarn />
                <NewCollectionWarn />
            </div>
        )
    }
});

module.exports = WarnList;
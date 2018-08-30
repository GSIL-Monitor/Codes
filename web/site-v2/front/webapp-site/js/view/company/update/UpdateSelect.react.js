var React = require('react');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');

var UpdateSelect = React.createClass({

    render() {
        if(this.props.select == null) return null;

        //console.log(this.props.select);

        return (
            <select className={this.props.className}
                    name={this.props.name}
                    value={this.props.value}
                    onChange={this.handleChange}>

                {this.props.select.map(function(result, index){
                        return  <Option key={index} name={result.name} value={result.value} />;
                }.bind(this))}

            </select>
        );
    },

    handleChange(e){
        var name = e.target.name;
        var value = e.target.value;
        if(name == 'parentSector')
            CompanyActions.changeSector(value);
        else if(name == 'subSector')
            CompanyActions.changeSubSector(value);
        else if(name == 'headCount')
            CompanyActions.changeHeadCount(value);
        else if(name == 'year' || name == 'month')
            CompanyActions.changeEstablishDate(name, value);
        else if(name == 'companySector')
            CompanyActions.changeCompanySector(value);
        else if(name == 'companySubSector')
            CompanyActions.changeCompanySubSector(value);
        else
            CompanyActions.changeCompany(name, value);

    }
});

var Option = React.createClass({
    render(){
        return(
            <option value={this.props.value}>
                {this.props.name}
            </option>
        )
    }
});

module.exports = UpdateSelect;

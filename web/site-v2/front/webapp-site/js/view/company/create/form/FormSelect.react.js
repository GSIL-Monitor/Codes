/**
 * Created by haiming on 16/2/4.
 */
var React = require('react');

var CreateCompanyStore = require('../../../../store/CreateCompanyStore');
var CreateCompanyActions = require('../../../../action/CreateCompanyActions');
var CreateCompanyUtil = require('../../../../util/CreateCompanyUtil');
var ValidateActions = require('../../../../action/validation/NewCompanyActions');

var FormSelect = React.createClass({

    render() {

        return (
            <select className={this.props.className}
                    name={this.props.name}
                    value={this.props.value}
                    onChange={this.handleChange}>

                {this.props.select.map(function (result, index) {
                    return <Option key={index} name={result.name} value={result.value}/>;
                }.bind(this))}

            </select>
        );
    },

    handleChange(e){
        var name = e.target.name;
        var value = e.target.value;
        if (name == 'parentSector') {
            ValidateActions.sector(value);
            CreateCompanyActions.changeSector(value);
        }
        else if (name == 'subSector')
            CreateCompanyActions.changeSubSector(value);
        else if (name == 'headCount')
            CreateCompanyActions.changeHeadCount(value);
        else if (name == 'round') {
            ValidateActions.round(value);
            CreateCompanyActions.change('round', value);
        }
        else if (name == 'currency')
            CreateCompanyActions.change('currency', value);
        else if (name == 'teamSize') {
            var memberNums = CreateCompanyUtil.getMemberNums(value);
            var headCountMin = memberNums.headCountMin;
            var headCountMax = memberNums.headCountMax;
            CreateCompanyActions.teamSizeChange(value, headCountMin, headCountMax);
        }
        else if(name == 'year' || name == 'month'){
            CreateCompanyActions.changeEstablishDate(name,value);
        }
        else if(name=='source'){
            CreateCompanyActions.changeSource(value);
        }
    }
});

var Option = React.createClass({
    render(){
        return (
            <option value={this.props.value}>
                {this.props.name}
            </option>
        )
    }
});

module.exports = FormSelect;

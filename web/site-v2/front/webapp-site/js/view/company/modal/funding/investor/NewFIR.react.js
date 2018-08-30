var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../../react-kit/form/FormSelect.react.js');
var FormInput = require('../../../../../../../react-kit/form/FormInput.react.js');
var Functions = require('../../../../../../../react-kit/util/Functions');

var CompanyStore = require('../../../../../store/CompanyStore');
var CompanyActions = require('../../../../../action/CompanyActions');
var FundingInvestor = require('./FundingInvestor.react.js');

const NewFIR = React.createClass({

    render(){

        return(
            <div className="new-fir">
                <FundingInvestor funding={this.props.funding} data={this.props.data} />
                <div className=" text-right m-t-20">
                    <button className="btn btn-navy btn-site m-r-10 m-b-10" onClick={this.cancel}>取消</button>
                    <button className="btn btn-navy btn-site m-r-10 m-b-10" onClick={this.add}>新增</button>
                </div>
            </div>
        )
    },
    add(){
        CompanyActions.addNewFIRConfirm(this.props.type);
    },
    cancel(){
        CompanyActions.addNewFIR(false);
    }

});




module.exports = NewFIR;

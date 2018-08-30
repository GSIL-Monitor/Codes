var React = require('react');
var $ = require('jquery');

var FormSelect = require('../../../../../../../react-kit/form/FormSelect.react.js');
var FormInput = require('../../../../../../../react-kit/form/FormInput.react.js');
var Functions = require('../../../../../../../react-kit/util/Functions');
var InvestorInput = require('../../../../../../../react-kit/basic/search/InvestorInput.react');

var CompanyActions = require('../../../../../action/CompanyActions');

const FundingInvestor = React.createClass({
    render(){
        var data = this.props.data;
        if(Functions.isNull(data))
            return null;

        var fir = data.fir;
        var funding = this.props.funding;
        if(Functions.isNull(fir.currency))
            fir.currency = funding.currency;

        if(Functions.isNull(fir.precise))
            fir.precise = funding.precise;

        return (
            <div>
                <FormInput label='投资金额'
                           name='investment'
                           className='input-short'
                           value={fir.investment}
                           onChange={this.handleChange}/>

                <FormSelect label='货币'
                            name='currency'
                            select={Functions.currencySelect()}
                            value={fir.currency}
                            onChange={this.handleChange}/>

                <FormSelect label='精确性'
                            name='precise'
                            select={Functions.preciseSelect()}
                            value={fir.precise}
                            onChange={this.handleChange}/>

                <div className="form-part">
                    <label className="investor-label">
                        <span className='left-required'>*</span>
                        <span>投资方</span>
                    </label>
                    <div className="div-investor">
                        <InvestorInput className="search-investor-input"
                                       value = {data.investor.name}
                                       from="updateInvestor"/>
                    </div>

                </div>
            </div>
        )
    },

    handleChange(event){
        CompanyActions.changeAddFIR(event.target.name, event.target.value);
    },

    investorChange(val){
        //FundingAction.changeAddFIR('investorId',val);
        //this.setState({investorId: val})
    },

    handleClickInvestor(){
        $('#find-investor').show();
        event.stopPropagation();
    }
});



module.exports = FundingInvestor;